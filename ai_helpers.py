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
from groq import Groq

import db

DEFAULT_MODEL = "llama-3.3-70b-versatile"


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


def get_model() -> str:
    return _get_config("GROQ_MODEL", DEFAULT_MODEL)


def get_client() -> Groq:
    api_key = _get_config("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Add it to your .env file locally, or "
            "to your app's Secrets if deployed on Streamlit Cloud."
        )
    return Groq(api_key=api_key)


def _generate_with_retry(client: Groq, max_retries: int = 3, **kwargs):
    """Calls client.chat.completions.create with retry + backoff for
    transient errors. Raises a friendly RuntimeError if all retries are exhausted."""
    delay = 2  # seconds
    last_err = None
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise
    raise RuntimeError(
        "Groq API is currently busy or experiencing high demand. "
        f"Please try again in a minute. Details: {last_err}"
    ) from last_err


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
    client = get_client()
    model = get_model()

    prompt = f"""You are a business analyst. Using ONLY the data below, write a concise
executive summary (4-6 sentences) of company performance. Mention overall
revenue/profit trend, any notable month-over-month changes, and the
strongest and weakest performing products or regions. Be specific with
numbers. Do not invent data not present below.

DATA:
{context}
"""
    resp = _generate_with_retry(
        client,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content


def generate_recommendations() -> str:
    context = _build_business_context()
    client = get_client()
    model = get_model()

    prompt = f"""You are a business consultant. Using ONLY the data below, give 3-5
specific, actionable recommendations for next quarter. Format as a
numbered list. Each recommendation should reference a specific number,
product, or region from the data to justify it. Do not invent data.

DATA:
{context}
"""
    resp = _generate_with_retry(
        client,
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return resp.choices[0].message.content


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
    client = get_client()
    model = get_model()

    system_instruction = (
        "You are a business intelligence assistant embedded in a "
        "company dashboard. Answer the user's question using ONLY "
        "the data provided below. If the data doesn't contain the "
        "answer, say so clearly instead of guessing. Be concise, "
        "cite specific numbers, and use plain English suitable for "
        "a non-technical manager.\n\nDATA:\n" + context
    )

    messages = [{"role": "system", "content": system_instruction}]
    if history:
        for turn in history:
            role = "assistant" if turn.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": turn.get("content", "")})
    messages.append({"role": "user", "content": question})

    resp = _generate_with_retry(
        client,
        model=model,
        messages=messages,
        temperature=0.3,
    )
    return resp.choices[0].message.content


if __name__ == "__main__":
    print(_build_business_context()[:1000])
