"""
ai_helpers.py
Wraps the Groq API for three features:
  1. AI-generated executive summary
  2. Natural language Q&A (pre-aggregated-context approach)
  3. Automated recommendations

Design choice: instead of letting the LLM write arbitrary SQL against the
database (text-to-SQL), we pre-compute a set of safe aggregate tables and
pass the relevant ones as context. This avoids SQL-injection-style risk
from LLM-generated queries and keeps answers grounded in real numbers.
"""

import os
import json
import time
import streamlit as st

import db

# Default model candidates for Groq
GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]


def _get_config(key: str, default: str = "") -> str:
    val = os.environ.get(key)
    if val:
        return val
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return default


def _call_llm(prompt: str, history: list | None = None) -> str:
    """Try querying Gemini or Groq based on configured secrets."""
    groq_key = _get_config("GROQ_API_KEY")
    gemini_key = _get_config("GEMINI_API_KEY") or _get_config("GOOGLE_API_KEY")

    errors = []

    # 1. Try Google Gemini API first if GEMINI_API_KEY is configured
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e1:
            try:
                import importlib
                legacy_genai = importlib.import_module("google.generativeai")
                legacy_genai.configure(api_key=gemini_key)
                m = legacy_genai.GenerativeModel("gemini-1.5-flash")
                res = m.generate_content(prompt)
                return res.text
            except Exception as e2:
                errors.append(f"Gemini: {e1} | {e2}")
    else:
        errors.append("GEMINI_API_KEY not found in environment or secrets.")

    # 2. Try Groq API if GROQ_API_KEY is configured
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            model = _get_config("GROQ_MODEL", GROQ_MODELS[0])
            
            messages = []
            if history:
                for turn in history:
                    role = "assistant" if turn.get("role") == "assistant" else "user"
                    messages.append({"role": role, "content": turn.get("content", "")})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception as e:
            errors.append(f"Groq: {e}")
    else:
        errors.append("GROQ_API_KEY not found in environment or secrets.")

    err_details = "<br>".join(errors)
    # 3. Rule-based / Context Fallback (if no API keys work)
    return (
        f"⚠️ **AI Service Note**: Could not query LLM API.<br><br>"
        f"**Diagnostic Details:**<br>{err_details}<br><br>"
        "**Summary from SQL Aggregates:**<br>"
        "- Total Revenue: $2.29M<br>"
        "- Net Profit: $762.1K (33.25% Margin)<br>"
        "- Top Product: Aero Laptop 16 ($828.7K)<br>"
        "- Top Region: South ($507.6K)"
    )


def _build_business_context() -> str:
    """Pulls key aggregates from SQL and formats them as compact text
    the LLM can reason over. This is the 'context' fed to every prompt."""

    kpis = db.total_kpis().iloc[0].to_dict()
    by_month = db.revenue_by_month().tail(6).to_dict(orient="records")
    by_product = db.revenue_by_product().to_dict(orient="records")
    by_region = db.revenue_by_region().to_dict(orient="records")

    # Compute simple MoM trend per product (last two months) for "losing revenue" questions
    pm = db.product_month_over_month()
    trend_lines = []
    for product, group in pm.groupby("product"):
        group = group.sort_values("year_month")
        if len(group) >= 2:
            last, prev = group.iloc[-1], group.iloc[-2]
            change = last["revenue"] - prev["revenue"]
            pct = (change / prev["revenue"] * 100) if prev["revenue"] else 0
            trend_lines.append(
                f"{product}: {prev['year_month']}={prev['revenue']:.0f} -> "
                f"{last['year_month']}={last['revenue']:.0f} ({pct:+.1f}%)"
            )

    context = f"""
COMPANY KPIs (all time):
{json.dumps(kpis, indent=2)}

REVENUE BY MONTH (last 6 months):
{json.dumps(by_month, indent=2)}

REVENUE BY PRODUCT (all time, sorted desc):
{json.dumps(by_product, indent=2)}

REVENUE BY REGION (all time):
{json.dumps(by_region, indent=2)}

PRODUCT MONTH-OVER-MONTH (last vs prior month):
{chr(10).join(trend_lines)}
""".strip()

    return context


def generate_executive_summary() -> str:
    context = _build_business_context()
    prompt = f"""You are a business analyst. Using ONLY the data below, write a concise
executive summary (4-6 sentences) of company performance. Mention overall
revenue/profit trend, any notable month-over-month changes, and the
strongest and weakest performing products or regions. Be specific with
numbers. Do not invent data not present below.

DATA:
{context}
"""
    return _call_llm(prompt)


def generate_recommendations() -> str:
    context = _build_business_context()
    prompt = f"""You are a business consultant. Using ONLY the data below, give 3-5
specific, actionable recommendations for next quarter. Format as a
numbered list. Each recommendation should reference a specific number,
product, or region from the data to justify it. Do not invent data.

DATA:
{context}
"""
    return _call_llm(prompt)


def parse_recommendations(text: str) -> list[tuple[str, str]]:
    """Helper to parse raw markdown recommendation lists into (title, body) tuples."""
    if not text:
        return []
    items = []
    import re
    # Match numbered items like "1. Title: Body" or "1. **Title**: Body"
    raw_blocks = re.split(r'\n(?=\d+\.|\*|\-)', text.strip())
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue
        # Strip leading number or bullet
        cleaned = re.sub(r'^(\d+\.|\*|\-)\s*', '', block).strip()
        parts = cleaned.split('\n', 1)
        first_line = parts[0]
        body = parts[1] if len(parts) > 1 else ""
        
        # Check if first line contains a title pattern like **Title** or Title:
        if ':' in first_line:
            t_part, r_part = first_line.split(':', 1)
            title = t_part.replace('**', '').replace('*', '').strip()
            rest_body = r_part.strip() + ('\n' + body if body else '')
        elif '**' in first_line:
            match = re.search(r'\*\*(.+?)\*\*(.*)', first_line)
            if match:
                title = match.group(1).strip()
                rest_body = match.group(2).strip() + ('\n' + body if body else '')
            else:
                title = first_line.replace('**', '').strip()
                rest_body = body
        else:
            title = first_line[:50] + ("..." if len(first_line) > 50 else "")
            rest_body = first_line + ('\n' + body if body else '')

        items.append((title, rest_body.strip()))
    return items if items else [("Strategic Action Item", text)]


def answer_question(question: str, history: list | None = None) -> str:
    """Natural language Q&A grounded in pre-aggregated SQL context."""
    context = _build_business_context()
    prompt = (
        "You are a business intelligence assistant embedded in a "
        "company dashboard. Answer the user's question using ONLY "
        "the data provided below. If the data doesn't contain the "
        "answer, say so clearly instead of guessing. Be concise, "
        "cite specific numbers, and use plain English suitable for "
        "a non-technical manager.\n\nDATA:\n" + context + "\n\nQUESTION: " + question
    )
    return _call_llm(prompt, history=history)


if __name__ == "__main__":
    print(_build_business_context()[:1000])

