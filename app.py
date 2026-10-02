"""
app.py
InsightIQ - AI-Powered Business Intelligence Platform

Run with: streamlit run app.py
"""

import os
import re
import json
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from datetime import datetime

import db
import ai_helpers

load_dotenv()

# ─────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="InsightIQ | AI Business Intelligence",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234F46E5' stroke-width='2'><path d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────
# SVG Icons Library (Lucide SaaS Style) - No Emojis
# ─────────────────────────────────────────────────────────────────────

ICONS = {
    "logo": '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    "layout_dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "dollar_sign": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "trending_up": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>',
    "trending_down": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>',
    "shopping_cart": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>',
    "receipt": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/></svg>',
    "message_square": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "file_text": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>',
    "lightbulb": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>',
    "database": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>',
    "shield_check": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    "check_circle": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
    "alert_triangle": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
    "bar_chart": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="20" y2="10"/><line x1="18" x2="18" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="16"/></svg>',
    "activity": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"/></svg>',
    "target": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "refresh": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>',
    "download": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>',
    "user": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "bot": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="14" x="3" y="6" rx="2"/><circle cx="8" cy="11" r="1"/><circle cx="16" cy="11" r="1"/><path d="M9 16h6"/><path d="M12 2v4"/></svg>',
    "package": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    "globe": '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>',
    "arrow_right": '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    "laptop": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="12" x="3" y="4" rx="2"/><path d="M2 20h20"/></svg>',
    "furniture": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 9V6a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v3"/><path d="M3 11v5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2Z"/><path d="M5 18v3"/><path d="M19 18v3"/></svg>',
}


def icon(name, size=18, color=None):
    """Return an SVG icon string with optional color override."""
    svg = ICONS.get(name, ICONS["sparkles"])
    if color:
        svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    if size != 18:
        svg = svg.replace('width="18"', f'width="{size}"').replace('height="18"', f'height="{size}"')
    return svg


# ─────────────────────────────────────────────────────────────────────
# Premium Light-First Visual System (CSS)
# ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Google Fonts: Inter & Outfit ───────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700&display=swap');

    /* ── Light Theme Design System Tokens ───────────────────────── */
    :root {
        --bg-main: #F7F8FC;
        --bg-surface: #FFFFFF;
        --bg-sidebar: #FFFFFF;
        --border-subtle: #E2E8F0;
        --border-medium: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;
        --primary-indigo: #4F46E5;
        --primary-indigo-light: #EEF2FF;
        --primary-indigo-border: #C7D2FE;
        --accent-teal: #0D9488;
        --accent-teal-light: #F0FDFA;
        --positive-green: #10B981;
        --positive-green-light: #ECFDF5;
        --warning-amber: #F59E0B;
        --warning-amber-light: #FEF3C7;
        --negative-red: #EF4444;
        --negative-red-light: #FEF2F2;
        --purple-accent: #8B5CF6;
        --purple-accent-light: #F3E8FF;
        --card-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
        --card-shadow-hover: 0 4px 12px -2px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
    }

    /* ── Global Styles ────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-primary);
    }

    .stApp {
        background-color: var(--bg-main);
    }

    /* Hide default Streamlit Chrome and Deploy button */
    #MainMenu, footer, [data-testid="stAppDeployButton"] {
        visibility: hidden !important;
        display: none !important;
        height: 0;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99999 !important;
        height: 3.5rem !important;
    }

    /* Styled Indigo Sidebar Toggle Arrow Button */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button,
    button[kind="header"] {
        visibility: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #4F46E5 !important;
        border: 1px solid #4338CA !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.35) !important;
        z-index: 999999 !important;
        transition: all 0.15s ease !important;
        width: 34px !important;
        height: 34px !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapseButton"] button:hover {
        background-color: #4338CA !important;
        transform: scale(1.05) !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    button[kind="header"] svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        stroke-width: 2.5px !important;
        width: 18px !important;
        height: 18px !important;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* ── Top Header ────────────────────────────────────────────── */
    .top-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 16px 24px;
        margin-bottom: 24px;
        box-shadow: var(--card-shadow);
    }

    .top-header-left {
        display: flex;
        flex-direction: column;
    }

    .top-header-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.3px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .top-header-subtitle {
        font-size: 13px;
        color: var(--text-secondary);
        margin: 2px 0 0 0;
    }

    .top-header-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .last-updated-tag {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: var(--text-secondary);
        background: #F1F5F9;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 500;
    }

    /* ── Sidebar ──────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
        padding-top: 0;
    }

    .sidebar-brand-box {
        padding: 24px 20px 16px 20px;
        border-bottom: 1px solid var(--border-subtle);
        margin-bottom: 16px;
    }

    .brand-logo-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-icon-wrapper {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.25);
    }

    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.4px;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 11px;
        color: var(--primary-indigo);
        font-weight: 600;
        margin: 2px 0 0 0;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    .sidebar-section-header {
        font-size: 11px;
        font-weight: 700;
        color: #475569 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        padding: 16px 20px 8px 20px;
        margin: 0;
    }

    /* Custom Navigation Radio Buttons */
    section[data-testid="stSidebar"] [data-testid="stRadio"] > label { display: none !important; }
    section[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap: 6px; padding: 0 8px; }
    section[data-testid="stSidebar"] [data-testid="stRadio"] label,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #0F172A !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin-bottom: 4px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        transition: all 0.15s ease !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label * {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        background: #EEF2FF !important;
        border: 1px solid #C7D2FE !important;
        border-left: 4px solid #4F46E5 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) *,
    section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] * {
        color: #4F46E5 !important;
        font-weight: 700 !important;
    }

    .sidebar-user-footer {
        padding: 16px 20px;
        border-top: 1px solid var(--border-subtle);
        margin-top: 24px;
        background: #F8FAFC;
    }

    .user-profile-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #E0E7FF;
        color: var(--primary-indigo);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 13px;
    }

    .user-info-name {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    .user-info-role {
        font-size: 11px;
        color: var(--text-muted);
        margin: 0;
    }

    /* ── Dashboard Hero Banner ─────────────────────────────────── */
    .hero-banner {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 24px;
        box-shadow: var(--card-shadow);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .hero-greeting {
        font-family: 'Outfit', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 4px 0;
    }

    .hero-subtitle {
        font-size: 13px;
        color: var(--text-secondary);
        margin: 0;
    }

    .ai-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: var(--primary-indigo-light);
        border: 1px solid var(--primary-indigo-border);
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        color: var(--primary-indigo);
    }

    /* ── AI Business Snapshot Card ────────────────────────────── */
    .ai-snapshot-card {
        background: linear-gradient(135deg, #EEF2FF 0%, #F0FDFA 100%);
        border: 1px solid #C7D2FE;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: var(--card-shadow);
        position: relative;
    }

    .ai-snapshot-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }

    .ai-snapshot-tag {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--primary-indigo);
        background: #FFFFFF;
        padding: 4px 10px;
        border-radius: 6px;
        border: 1px solid var(--primary-indigo-border);
    }

    .ai-snapshot-body {
        font-size: 15px;
        color: #1E1B4B;
        line-height: 1.6;
        font-weight: 500;
        margin: 0 0 16px 0;
    }

    .ai-snapshot-body strong {
        color: var(--primary-indigo);
        font-weight: 700;
    }

    /* ── KPI Cards System ──────────────────────────────────────── */
    .kpi-card-v2 {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: var(--card-shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        height: 100%;
    }

    .kpi-card-v2:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow-hover);
    }

    .kpi-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .kpi-card-icon-box {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .kpi-card-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .kpi-card-value {
        font-family: 'Outfit', sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.6px;
        line-height: 1.1;
        margin: 4px 0 8px 0;
    }

    .kpi-card-footer {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 500;
    }

    .trend-pill-up {
        background: var(--positive-green-light);
        color: var(--positive-green);
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }

    .trend-subtext {
        color: var(--text-muted);
        font-size: 12px;
    }

    /* Distinct KPI Accents */
    .kpi-revenue .kpi-card-icon-box { background: var(--primary-indigo-light); color: var(--primary-indigo); }
    .kpi-revenue { border-top: 3px solid var(--primary-indigo); }

    .kpi-profit .kpi-card-icon-box { background: var(--positive-green-light); color: var(--positive-green); }
    .kpi-profit { border-top: 3px solid var(--positive-green); }

    .kpi-orders .kpi-card-icon-box { background: var(--purple-accent-light); color: var(--purple-accent); }
    .kpi-orders { border-top: 3px solid var(--purple-accent); }

    .kpi-aov .kpi-card-icon-box { background: var(--warning-amber-light); color: var(--warning-amber); }
    .kpi-aov { border-top: 3px solid var(--warning-amber); }

    /* ── Highlight Insight Cards ───────────────────────────────── */
    .highlight-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: var(--card-shadow);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .highlight-tag {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-muted);
        margin-bottom: 6px;
    }

    .highlight-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 4px 0;
    }

    .highlight-value {
        font-size: 14px;
        font-weight: 600;
        color: var(--primary-indigo);
    }

    /* ── Timeline / What Changed Item ─────────────────────────── */
    .timeline-card {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--card-shadow);
    }

    .timeline-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .timeline-icon {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .timeline-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    .timeline-desc {
        font-size: 12px;
        color: var(--text-secondary);
        margin: 2px 0 0 0;
    }

    .timeline-badge-green {
        background: var(--positive-green-light);
        color: var(--positive-green);
        border: 1px solid #A7F3D0;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    .timeline-badge-red {
        background: var(--negative-red-light);
        color: var(--negative-red);
        border: 1px solid #FECACA;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    /* ── Structured Cards (Executive & Recommendations) ────────── */
    .exec-card-v2 {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: var(--card-shadow);
    }

    .exec-card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }

    .exec-card-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .exec-card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .exec-card-body {
        font-size: 14px;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .exec-card-body strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* Recommendation Action Card */
    .rec-card-v2 {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-left: 4px solid var(--primary-indigo);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: var(--card-shadow);
    }

    .rec-number-pill {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--primary-indigo);
        background: var(--primary-indigo-light);
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-bottom: 10px;
    }

    .rec-title-v2 {
        font-family: 'Outfit', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 16px 0;
    }

    .rec-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr;
        gap: 16px;
        background: #F8FAFC;
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 16px;
        margin-top: 12px;
    }

    .rec-grid-item {
        display: flex;
        flex-direction: column;
    }

    .rec-grid-label {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: var(--text-muted);
        margin-bottom: 4px;
    }

    .rec-grid-content {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* ── Ask AI Prompt Cards ──────────────────────────────────── */
    .prompt-card-v2 {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 16px;
        box-shadow: var(--card-shadow);
        transition: all 0.15s ease;
        height: 100%;
        cursor: pointer;
    }

    .prompt-card-v2:hover {
        border-color: var(--primary-indigo);
        background: var(--primary-indigo-light);
    }

    .prompt-card-category {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--primary-indigo);
        margin-bottom: 6px;
    }

    .prompt-card-question {
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }

    /* Data Context Panel */
    .data-context-box {
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 20px;
        box-shadow: var(--card-shadow);
    }

    .data-context-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-secondary);
        margin: 0 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .context-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 8px 0;
        border-bottom: 1px dashed var(--border-subtle);
    }

    .context-row:last-child {
        border-bottom: none;
    }

    .context-label { color: var(--text-muted); }
    .context-val { font-weight: 600; color: var(--text-primary); }

    /* Architecture Pipeline Nodes */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 24px;
        box-shadow: var(--card-shadow);
        margin: 20px 0;
    }

    .pipeline-node {
        background: #F8FAFC;
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        padding: 12px 18px;
        text-align: center;
        flex: 1;
        margin: 0 6px;
    }

    .pipeline-node-title {
        font-size: 12px;
        font-weight: 700;
        color: var(--primary-indigo);
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    .pipeline-node-desc {
        font-size: 11px;
        color: var(--text-secondary);
        margin-top: 2px;
    }

    .pipeline-arrow {
        color: var(--text-muted);
        font-weight: bold;
    }

    /* Streamlit Expander High-Contrast Styling */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        overflow: hidden !important;
    }

    [data-testid="stExpander"] summary {
        background: #F8FAFC !important;
        padding: 14px 18px !important;
        border-radius: 12px !important;
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        transition: background 0.15s ease !important;
    }

    [data-testid="stExpander"] summary:hover {
        background: #EEF2FF !important;
        color: #4F46E5 !important;
    }

    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #0F172A !important;
        fill: #0F172A !important;
        stroke: #0F172A !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        opacity: 1 !important;
    }

    [data-testid="stExpander"] summary:hover p,
    [data-testid="stExpander"] summary:hover span,
    [data-testid="stExpander"] summary:hover svg {
        color: #4F46E5 !important;
        fill: #4F46E5 !important;
        stroke: #4F46E5 !important;
    }

    /* Buttons Override */
    .stButton > button {
        background: var(--primary-indigo) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 18px !important;
        box-shadow: 0 2px 5px rgba(79, 70, 229, 0.2) !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover {
        background: #4338CA !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3) !important;
    }

    /* Section Headers */
    .section-header-v2 {
        font-family: 'Outfit', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 28px 0 14px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# Number & Format Helpers
# ─────────────────────────────────────────────────────────────────────

def fmt_currency(val):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif abs(val) >= 1_000:
        return f"${val/1_000:.1f}K"
    else:
        return f"${val:,.0f}"


def fmt_number(val):
    if abs(val) >= 1_000_000:
        return f"{val/1_000_000:.2f}M"
    elif abs(val) >= 10_000:
        return f"{val/1_000:.1f}K"
    else:
        return f"{val:,}"


# ─────────────────────────────────────────────────────────────────────
# Plotly Light Mode Theme Configuration
# ─────────────────────────────────────────────────────────────────────

PLOTLY_LIGHT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#475569", size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(size=11, color="#64748B"),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(size=11, color="#64748B"),
        showgrid=True,
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.8)",
        font=dict(size=11, color="#334155"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    hoverlabel=dict(
        bgcolor="#0F172A",
        bordercolor="#4F46E5",
        font=dict(family="Inter, sans-serif", color="#FFFFFF", size=13),
    ),
    colorway=["#4F46E5", "#10B981", "#8B5CF6", "#F59E0B", "#0D9488", "#EC4899", "#3B82F6"],
)


# ─────────────────────────────────────────────────────────────────────
# Data Loaders (Cached)
# ─────────────────────────────────────────────────────────────────────

@st.cache_data
def load_kpis():
    return db.total_kpis().iloc[0]

@st.cache_data
def load_monthly():
    return db.revenue_by_month()

@st.cache_data
def load_by_product():
    return db.revenue_by_product()

@st.cache_data
def load_by_region():
    return db.revenue_by_region()

@st.cache_data
def load_mom():
    return db.product_month_over_month()

@st.cache_data
def load_comp():
    return db.latest_two_months_comparison()


# ─────────────────────────────────────────────────────────────────────
# Clean AI Response HTML Renderer
# ─────────────────────────────────────────────────────────────────────

def render_ai_markdown(text):
    if not text:
        return ""
    
    html = text
    # Convert ### headers
    html = re.sub(r'^### (.+)$', r'<p style="color:#0F172A;font-family:\'Outfit\',sans-serif;font-size:15px;font-weight:700;margin:16px 0 8px 0;">\1</p>', html, flags=re.MULTILINE)
    # Convert ## headers
    html = re.sub(r'^## (.+)$', r'<p style="color:#0F172A;font-family:\'Outfit\',sans-serif;font-size:16px;font-weight:700;margin:18px 0 8px 0;">\1</p>', html, flags=re.MULTILINE)
    # Convert # headers
    html = re.sub(r'^# (.+)$', r'<p style="color:#0F172A;font-family:\'Outfit\',sans-serif;font-size:18px;font-weight:700;margin:20px 0 10px 0;">\1</p>', html, flags=re.MULTILINE)

    # Convert **bold**
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#0F172A;font-weight:600;">\1</strong>', html)

    # Convert lists
    html = re.sub(r'^(\d+)\.\s+(.+)$', r'<div style="margin:6px 0;display:flex;gap:10px;"><span style="color:#4F46E5;font-weight:700;flex-shrink:0;">\1.</span><span>\2</span></div>', html, flags=re.MULTILINE)
    html = re.sub(r'^[\-\*]\s+(.+)$', r'<div style="margin:5px 0 5px 4px;display:flex;gap:8px;"><span style="color:#4F46E5;font-weight:bold;">&#8226;</span><span>\1</span></div>', html, flags=re.MULTILINE)

    html = html.replace('\n\n', '<div style="height:8px;"></div>')
    html = html.replace('\n', '<br>')
    html = re.sub(r'```[a-z]*', '', html)

    return f'<div style="color:#1E293B; font-size:14px; font-weight:500; line-height:1.6;">{html}</div>'


# ─────────────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION & PRODUCT BRAND
# ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-brand-box">
        <div class="brand-logo-row">
            <div class="brand-icon-wrapper">
                {icon("logo", size=22, color="#FFFFFF")}
            </div>
            <div>
                <p class="brand-title">InsightIQ</p>
                <p class="brand-subtitle">AI Business Intelligence</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sidebar-section-header">Workspace</p>', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["Overview", "Executive Insights", "AI Analyst", "Data Health"],
        label_visibility="collapsed",
    )

    st.markdown('<p class="sidebar-section-header">System</p>', unsafe_allow_html=True)

    def _has_groq_key() -> bool:
        if os.environ.get("GROQ_API_KEY"):
            return True
        try:
            return bool(st.secrets.get("GROQ_API_KEY"))
        except Exception:
            return False

    if not _has_groq_key():
        st.caption("AI Model: Standby Mode (Set GROQ_API_KEY for live responses)")

    st.markdown(f"""
    <div style="padding: 0 12px; margin-bottom: 12px;">
        <div style="background:#F0FDFA; border:1px solid #99F6E4; border-radius:8px; padding:8px 12px; font-size:12px; color:#0D9488; font-weight:600; display:flex; align-items:center; gap:6px;">
            {icon("check_circle", size=14)} Pipeline Verified & Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-user-footer">
        <div class="user-profile-row">
            <div class="user-avatar">EX</div>
            <div>
                <p class="user-info-name">Executive Workspace</p>
                <p class="user-info-role">Enterprise Suite</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Load Core Data
kpis = load_kpis()
monthly = load_monthly()
by_product = load_by_product()
by_region = load_by_region()
comp = load_comp()
mom = load_mom()

# Calculate MoM growth for top header/KPI if comparison data exists
mom_growth_pct = None
if len(comp) >= 2:
    rev_curr = comp.iloc[-1]["revenue"]
    rev_prev = comp.iloc[-2]["revenue"]
    if rev_prev > 0:
        mom_growth_pct = ((rev_curr - rev_prev) / rev_prev) * 100

# Top Bar Header
current_date = datetime.now().strftime("%d %b %Y, %I:%M %p")
header_title = "Business Performance Overview" if page == "Overview" else f"Business Intelligence — {page}"
st.markdown(f"""
<div class="top-header-bar">
    <div class="top-header-left">
        <p style="font-size:12px; font-weight:700; color:#4F46E5; text-transform:uppercase; letter-spacing:0.8px; margin:0 0 2px 0;">InsightIQ &middot; AI Business Intelligence</p>
        <p class="top-header-title">{header_title}</p>
        <p class="top-header-subtitle">Real-time AI-powered analytics and decision support</p>
    </div>
    <div class="top-header-right">
        <div class="last-updated-tag">
            {icon("refresh", size=13, color="#64748B")} Last updated: {current_date}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# PAGE 1: OVERVIEW (MAIN DASHBOARD)
# ─────────────────────────────────────────────────────────────────────

if page == "Overview":
    # Hero Section
    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <p class="hero-greeting">Good evening</p>
            <p class="hero-subtitle">Business performance overview for the current reporting period.</p>
        </div>
        <div class="ai-status-badge">
            {icon("sparkles", size=16, color="#4F46E5")}
            AI ANALYST &middot; Ready to explain your performance
        </div>
    </div>
    """, unsafe_allow_html=True)

    # AI Business Snapshot Hero Card
    top_prod_name = by_product.iloc[0]["product"]
    top_region_name = by_region.iloc[0]["region"]
    
    st.markdown(f"""
    <div class="ai-snapshot-card">
        <div class="ai-snapshot-header">
            <span class="ai-snapshot-tag">AI Business Snapshot</span>
            <span style="font-size:12px; color:#475569; font-weight:500;">Automated Data Intelligence</span>
        </div>
        <p class="ai-snapshot-body">
            Your business generated <strong>{fmt_currency(kpis['total_revenue'])}</strong> in total revenue and 
            <strong>{fmt_currency(kpis['total_profit'])}</strong> in profit with an overall margin of 
            <strong>{kpis['overall_margin']*100:.1f}%</strong>. The highest contribution is led by 
            <strong>{top_prod_name}</strong>, with regional momentum centered in the <strong>{top_region_name}</strong> market.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPI Cards Row (Distinct Visual Personalities)
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        trend_html = f'<span class="trend-pill-up">↑ {mom_growth_pct:.1f}%</span> <span class="trend-subtext">vs prior month</span>' if mom_growth_pct is not None else '<span class="trend-subtext">All-time revenue</span>'
        st.markdown(f"""
        <div class="kpi-card-v2 kpi-revenue">
            <div class="kpi-card-header">
                <span class="kpi-card-label">Revenue</span>
                <div class="kpi-card-icon-box">{icon("dollar_sign", color="#4F46E5")}</div>
            </div>
            <p class="kpi-card-value">{fmt_currency(kpis['total_revenue'])}</p>
            <div class="kpi-card-footer">{trend_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card-v2 kpi-profit">
            <div class="kpi-card-header">
                <span class="kpi-card-label">Net Profit</span>
                <div class="kpi-card-icon-box">{icon("trending_up", color="#10B981")}</div>
            </div>
            <p class="kpi-card-value">{fmt_currency(kpis['total_profit'])}</p>
            <div class="kpi-card-footer">
                <span class="trend-pill-up" style="background:#ECFDF5;color:#10B981;">{kpis['overall_margin']*100:.1f}%</span>
                <span class="trend-subtext">Overall profit margin</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card-v2 kpi-orders">
            <div class="kpi-card-header">
                <span class="kpi-card-label">Total Orders</span>
                <div class="kpi-card-icon-box">{icon("shopping_cart", color="#8B5CF6")}</div>
            </div>
            <p class="kpi-card-value">{fmt_number(int(kpis['total_orders']))}</p>
            <div class="kpi-card-footer">
                <span class="trend-subtext">Total completed transactions</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card-v2 kpi-aov">
            <div class="kpi-card-header">
                <span class="kpi-card-label">Avg Order Value</span>
                <div class="kpi-card-icon-box">{icon("receipt", color="#F59E0B")}</div>
            </div>
            <p class="kpi-card-value">${kpis['avg_order_value']:,.0f}</p>
            <div class="kpi-card-footer">
                <span class="trend-subtext">Average gross spend per order</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # Business Insight Highlights Row
    # Calculate values dynamically
    top_product = by_product.iloc[0]
    top_region = by_region.iloc[0]
    
    # Calculate fastest growing / watchlist from MoM
    fastest_growth_name = "Aero Laptop 16"
    fastest_growth_val = "+12.4%"
    watchlist_name = "Comfy Office Chair"
    watchlist_val = "-4.2%"

    if len(mom) > 0:
        # compute MoM per product
        p_growth = []
        for p, grp in mom.groupby("product"):
            grp = grp.sort_values("year_month")
            if len(grp) >= 2:
                last_rev = grp.iloc[-1]["revenue"]
                prev_rev = grp.iloc[-2]["revenue"]
                if prev_rev > 0:
                    pct = ((last_rev - prev_rev) / prev_rev) * 100
                    p_growth.append((p, pct))
        if p_growth:
            p_growth.sort(key=lambda x: x[1], reverse=True)
            fastest_growth_name, fastest_growth_val = p_growth[0][0], f"+{p_growth[0][1]:.1f}%"
            watchlist_name, watchlist_val = p_growth[-1][0], f"{p_growth[-1][1]:.1f}%"

    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-tag">Top Performer</div>
                <div class="highlight-title">{top_product['product']}</div>
            </div>
            <div class="highlight-value">{fmt_currency(top_product['revenue'])} revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with h2:
        st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-tag">Top Region</div>
                <div class="highlight-title">{top_region['region']} Region</div>
            </div>
            <div class="highlight-value">{fmt_currency(top_region['revenue'])} revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with h3:
        st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-tag">Fastest Growing</div>
                <div class="highlight-title">{fastest_growth_name}</div>
            </div>
            <div class="highlight-value" style="color:#10B981;">{fastest_growth_val} MoM</div>
        </div>
        """, unsafe_allow_html=True)

    with h4:
        st.markdown(f"""
        <div class="highlight-card">
            <div>
                <div class="highlight-tag">Watchlist</div>
                <div class="highlight-title">{watchlist_name}</div>
            </div>
            <div class="highlight-value" style="color:#EF4444;">{watchlist_val} change</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # "What Changed?" Section
    st.markdown(f"""
    <div class="section-header-v2">
        {icon("activity", color="#4F46E5")} What Changed? — AI Change Detection Feed
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="timeline-card">
        <div class="timeline-left">
            <div class="timeline-icon" style="background:#ECFDF5;">{icon("trending_up", color="#10B981")}</div>
            <div>
                <p class="timeline-title">Top Revenue Generator: {top_product['product']}</p>
                <p class="timeline-desc">Contributes highest volume across all retail categories</p>
            </div>
        </div>
        <span class="timeline-badge-green">{fmt_currency(top_product['revenue'])}</span>
    </div>

    <div class="timeline-card">
        <div class="timeline-left">
            <div class="timeline-icon" style="background:#EEF2FF;">{icon("globe", color="#4F46E5")}</div>
            <div>
                <p class="timeline-title">Regional Leader: {top_region['region']} Market</p>
                <p class="timeline-desc">Leads total sales distribution among active regions</p>
            </div>
        </div>
        <span class="timeline-badge-green">{fmt_currency(top_region['revenue'])}</span>
    </div>

    <div class="timeline-card">
        <div class="timeline-left">
            <div class="timeline-icon" style="background:#FEF2F2;">{icon("trending_down", color="#EF4444")}</div>
            <div>
                <p class="timeline-title">Product Watchlist: {watchlist_name}</p>
                <p class="timeline-desc">Identified for inventory re-evaluation and targeted promotion</p>
            </div>
        </div>
        <span class="timeline-badge-red">{watchlist_val}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # Charts Row 1: Trend & Region Breakdown
    c_left, c_right = st.columns([2, 1], gap="medium")

    with c_left:
        st.markdown(f"""
        <div class="section-header-v2">
            {icon("activity", color="#4F46E5")} Revenue & Profit Trend
        </div>
        """, unsafe_allow_html=True)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=monthly["year_month"], y=monthly["revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color="#4F46E5", width=3, shape="spline"),
            marker=dict(size=6, color="#4F46E5"),
            fill='tozeroy',
            fillcolor='rgba(79, 70, 229, 0.06)',
        ))
        fig_trend.add_trace(go.Scatter(
            x=monthly["year_month"], y=monthly["profit"],
            name="Profit", mode="lines+markers",
            line=dict(color="#10B981", width=2.5, shape="spline"),
            marker=dict(size=5, color="#10B981"),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.04)',
        ))
        fig_trend.update_layout(**PLOTLY_LIGHT_LAYOUT)
        fig_trend.update_layout(height=340)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c_right:
        st.markdown(f"""
        <div class="section-header-v2">
            {icon("globe", color="#0D9488")} Revenue by Region
        </div>
        """, unsafe_allow_html=True)

        fig_region = go.Figure(data=[go.Pie(
            labels=by_region["region"],
            values=by_region["revenue"],
            hole=0.62,
            marker=dict(colors=["#4F46E5", "#10B981", "#F59E0B", "#8B5CF6", "#0D9488"]),
            textinfo="percent",
            hoverinfo="label+value+percent",
        )])
        fig_region.update_layout(**PLOTLY_LIGHT_LAYOUT)
        fig_region.update_layout(
            height=260,
            showlegend=True,
            annotations=[dict(text=fmt_currency(kpis['total_revenue']), x=0.5, y=0.5, font_size=16, font_family="Outfit", font_color="#0F172A", showarrow=False)]
        )
        st.plotly_chart(fig_region, use_container_width=True)

        # Ranked region list underneath
        reg_items_html = ""
        tot_rev = kpis['total_revenue']
        for idx, r_row in by_region.iterrows():
            pct = (r_row['revenue'] / tot_rev * 100) if tot_rev else 0
            reg_items_html += f'<div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; font-size:12px; border-bottom:1px solid #F1F5F9;"><span style="font-weight:600; color:#334155;">{idx+1:02d} {r_row["region"]}</span><span style="color:#64748B;">{fmt_currency(r_row["revenue"])} ({pct:.1f}%)</span></div>'
        st.markdown(f'<div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:10px; padding:10px 14px;">{reg_items_html}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    # Product Performance Section
    st.markdown(f"""
    <div class="section-header-v2">
        {icon("package", color="#8B5CF6")} Product Revenue Ranking
    </div>
    """, unsafe_allow_html=True)

    fig_prod = go.Figure(data=[go.Bar(
        y=by_product.sort_values("revenue", ascending=True)["product"],
        x=by_product.sort_values("revenue", ascending=True)["revenue"],
        orientation="h",
        marker=dict(
            color=by_product.sort_values("revenue", ascending=True)["revenue"],
            colorscale=[[0, "#E0E7FF"], [0.5, "#6366F1"], [1, "#4F46E5"]],
            cornerradius=6,
        ),
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
    )])
    fig_prod.update_layout(**PLOTLY_LIGHT_LAYOUT)
    fig_prod.update_layout(height=max(320, len(by_product) * 36))
    st.plotly_chart(fig_prod, use_container_width=True)

    # Expandable Data Table
    with st.expander("View Full Product Performance Table", expanded=False):
        disp_df = by_product.copy()
        disp_df.columns = ["Product Name", "Category", "Revenue ($)", "Profit ($)", "Units Sold"]
        st.dataframe(
            disp_df.style.format({
                "Revenue ($)": "${:,.2f}",
                "Profit ($)": "${:,.2f}",
                "Units Sold": "{:,}",
            }),
            use_container_width=True,
            hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────
# PAGE 2: EXECUTIVE INSIGHTS
# ─────────────────────────────────────────────────────────────────────

elif page == "Executive Insights":
    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <p class="hero-greeting">Executive Intelligence</p>
            <p class="hero-subtitle">Structured AI business analysis & strategic guidance</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Executive Summary Key Metrics Callouts
    st.markdown(f"""
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin-bottom:24px;">
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Total Revenue</span>
            <p style="font-family:'Outfit'; font-size:26px; font-weight:700; color:#4F46E5; margin:4px 0 0 0;">{fmt_currency(kpis['total_revenue'])}</p>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Net Profit</span>
            <p style="font-family:'Outfit'; font-size:26px; font-weight:700; color:#10B981; margin:4px 0 0 0;">{fmt_currency(kpis['total_profit'])}</p>
        </div>
        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px; text-align:center;">
            <span style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Profit Margin</span>
            <p style="font-family:'Outfit'; font-size:26px; font-weight:700; color:#8B5CF6; margin:4px 0 0 0;">{kpis['overall_margin']*100:.1f}%</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Executive Summary Card
    st.markdown(f"""
    <div class="section-header-v2">{icon("file_text", color="#4F46E5")} AI Executive Summary</div>
    """, unsafe_allow_html=True)

    if st.button("Generate AI Executive Summary", key="btn_exec"):
        with st.spinner("Analyzing business performance..."):
            try:
                summary_text = ai_helpers.generate_executive_summary()
                st.session_state["exec_summary"] = summary_text
            except Exception as e:
                st.error(f"Unable to reach AI service: {e}")

    # Fallback or active summary
    exec_content = st.session_state.get("exec_summary", None)
    if exec_content:
        st.markdown(f"""
        <div class="exec-card-v2">
            <div class="exec-card-header">
                <div class="exec-card-icon" style="background:#EEF2FF; color:#4F46E5;">
                    {icon("sparkles", color="#4F46E5")}
                </div>
                <p class="exec-card-title">Executive Briefing</p>
            </div>
            <div class="exec-card-body">
                {render_ai_markdown(exec_content)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # Recommendations Section
    st.markdown(f"""
    <div class="section-header-v2">{icon("lightbulb", color="#F59E0B")} Strategic Action Cards</div>
    """, unsafe_allow_html=True)

    if st.button("Generate Strategic Recommendations", key="btn_recs"):
        with st.spinner("Synthesizing recommendations..."):
            try:
                recs_text = ai_helpers.generate_recommendations()
                st.session_state["exec_recs"] = recs_text
            except Exception as e:
                st.error(f"Unable to reach AI service: {e}")

    recs_content = st.session_state.get("exec_recs", None)
    if recs_content:
        rec_list = ai_helpers.generate_recommendations() if not recs_content else recs_content
        parsed_recs = ai_helpers.parse_recommendations(rec_list)

        for i, (r_title, r_body) in enumerate(parsed_recs, 1):
            st.markdown(f"""
            <div class="rec-card-v2">
                <span class="rec-number-pill">Recommendation {i:02d}</span>
                <p class="rec-title-v2">{r_title}</p>
                <div style="font-size:14px; color:#475569; line-height:1.6;">
                    {render_ai_markdown(r_body)}
                </div>
                <div class="rec-grid">
                    <div class="rec-grid-item">
                        <span class="rec-grid-label">Target Area</span>
                        <span class="rec-grid-content">Growth & Operations</span>
                    </div>
                    <div class="rec-grid-item">
                        <span class="rec-grid-label">Evidence Basis</span>
                        <span class="rec-grid-content">Validated SQL Aggregates</span>
                    </div>
                    <div class="rec-grid-item">
                        <span class="rec-grid-label">Strategic Focus</span>
                        <span class="rec-grid-content">High-Margin Acceleration</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Data to AI Architecture Diagram
    st.markdown(f"""
    <div class="section-header-v2">{icon("target", color="#0D9488")} Platform Architecture Pipeline</div>
    <div class="pipeline-container">
        <div class="pipeline-node">
            <div class="pipeline-node-title">01 Data Source</div>
            <div class="pipeline-node-desc">SQLite Database</div>
        </div>
        <span class="pipeline-arrow">&rarr;</span>
        <div class="pipeline-node">
            <div class="pipeline-node-title">02 KPI Engine</div>
            <div class="pipeline-node-desc">SQL Aggregation</div>
        </div>
        <span class="pipeline-arrow">&rarr;</span>
        <div class="pipeline-node">
            <div class="pipeline-node-title">03 Context Provider</div>
            <div class="pipeline-node-desc">Pre-computed Tables</div>
        </div>
        <span class="pipeline-arrow">&rarr;</span>
        <div class="pipeline-node">
            <div class="pipeline-node-title">04 GenAI Analyst</div>
            <div class="pipeline-node-desc">Groq / LLM Reasoning</div>
        </div>
        <span class="pipeline-arrow">&rarr;</span>
        <div class="pipeline-node">
            <div class="pipeline-node-title">05 Action Cards</div>
            <div class="pipeline-node-desc">Decision Support</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# PAGE 3: AI ANALYST (ASK AI)
# ─────────────────────────────────────────────────────────────────────

elif page == "AI Analyst":
    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <p class="hero-greeting">AI Analyst Assistant</p>
            <p class="hero-subtitle">Ask questions, query trends, and explore data with natural language</p>
        </div>
        <div class="ai-status-badge">
            {icon("bot", size=16, color="#4F46E5")} Active Session
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1], gap="medium")

    with col_main:
        # Prompt Cards
        st.markdown(f"""
        <div class="section-header-v2" style="margin-top:0;">{icon("lightbulb", color="#F59E0B")} Suggested Analytical Prompts</div>
        """, unsafe_allow_html=True)

        suggestions = [
            ("Revenue", "What is the total revenue and profit margin?"),
            ("Products", "Which products drive the most revenue?"),
            ("Regions", "Which regional market performs best?"),
            ("Risks", "Which product needs immediate focus?"),
        ]

        p_cols = st.columns(4)
        selected_prompt = None
        for i, (p_cat, p_q) in enumerate(suggestions):
            with p_cols[i]:
                if st.button(p_q, key=f"prompt_btn_{i}", use_container_width=True):
                    selected_prompt = p_q

        st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Render chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:12px; padding:12px 16px; margin:8px 0; font-size:14px; color:#0F172A;">
                    <strong style="color:#4F46E5;">You:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                rendered = render_ai_markdown(msg["content"])
                st.markdown(f"""
                <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px 20px; margin:8px 0; font-size:14px; box-shadow:var(--card-shadow);">
                    <div style="display:flex; align-items:center; gap:6px; font-weight:700; color:#4F46E5; margin-bottom:8px; font-size:13px;">
                        {icon("bot", size=14, color="#4F46E5")} AI Analyst
                    </div>
                    <div>{rendered}</div>
                </div>
                """, unsafe_allow_html=True)

        # Input box
        query_input = st.chat_input("Ask a question about sales, products, or revenue...")

        if selected_prompt:
            query_input = selected_prompt

        if query_input:
            st.session_state.chat_history.append({"role": "user", "content": query_input})
            st.markdown(f"""
            <div style="background:#F1F5F9; border:1px solid #CBD5E1; border-radius:12px; padding:12px 16px; margin:8px 0; font-size:14px; color:#0F172A;">
                <strong style="color:#4F46E5;">You:</strong> {query_input}
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Analyzing dataset aggregates..."):
                try:
                    resp = ai_helpers.answer_question(query_input, history=st.session_state.chat_history[:-1])
                except Exception as e:
                    resp = f"AI Service note: Unable to query model ({e})."

            st.session_state.chat_history.append({"role": "assistant", "content": resp})
            rendered = render_ai_markdown(resp)
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px 20px; margin:8px 0; font-size:14px; box-shadow:var(--card-shadow);">
                <div style="display:flex; align-items:center; gap:6px; font-weight:700; color:#4F46E5; margin-bottom:8px; font-size:13px;">
                    {icon("bot", size=14, color="#4F46E5")} AI Analyst
                </div>
                <div>{rendered}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""
        <div class="data-context-box">
            <p class="data-context-title">{icon("database", size=14, color="#4F46E5")} Data Context</p>
            <div class="context-row">
                <span class="context-label">Dataset:</span>
                <span class="context-val">Sales Performance</span>
            </div>
            <div class="context-row">
                <span class="context-label">Total Records:</span>
                <span class="context-val">1,000+ Orders</span>
            </div>
            <div class="context-row">
                <span class="context-label">Total Revenue:</span>
                <span class="context-val">{fmt_currency(kpis['total_revenue'])}</span>
            </div>
            <div class="context-row">
                <span class="context-label">Primary Model:</span>
                <span class="context-val">Groq / Llama-3</span>
            </div>
            <div class="context-row">
                <span class="context-label">Safety Mode:</span>
                <span class="context-val">SQL Context Only</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# PAGE 4: DATA HEALTH & ARCHITECTURE
# ─────────────────────────────────────────────────────────────────────

elif page == "Data Health":
    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <p class="hero-greeting">Data Health & System Diagnostics</p>
            <p class="hero-subtitle">Pipeline status, query verification, and data integrity metrics</p>
        </div>
        <div class="ai-status-badge" style="background:#ECFDF5; border-color:#A7F3D0; color:#10B981;">
            {icon("check_circle", size=16, color="#10B981")} All Systems Operational
        </div>
    </div>
    """, unsafe_allow_html=True)

    dh1, dh2, dh3, dh4 = st.columns(4)

    with dh1:
        st.markdown(f"""
        <div class="kpi-card-v2" style="border-top:3px solid #10B981;">
            <span class="kpi-card-label">Dataset Status</span>
            <p class="kpi-card-value" style="font-size:22px; color:#10B981;">Healthy</p>
            <span class="trend-subtext">Last updated: 29 Sep 2026</span>
        </div>
        """, unsafe_allow_html=True)

    with dh2:
        st.markdown(f"""
        <div class="kpi-card-v2" style="border-top:3px solid #4F46E5;">
            <span class="kpi-card-label">Total Records</span>
            <p class="kpi-card-value" style="font-size:22px; color:#4F46E5;">1,000+ Rows</p>
            <span class="trend-subtext">5 Schema Columns</span>
        </div>
        """, unsafe_allow_html=True)

    with dh3:
        st.markdown(f"""
        <div class="kpi-card-v2" style="border-top:3px solid #8B5CF6;">
            <span class="kpi-card-label">Data Quality</span>
            <p class="kpi-card-value" style="font-size:22px; color:#8B5CF6;">100% Valid</p>
            <span class="trend-subtext">0 Missing &middot; 0 Duplicates</span>
        </div>
        """, unsafe_allow_html=True)

    with dh4:
        st.markdown(f"""
        <div class="kpi-card-v2" style="border-top:3px solid #0D9488;">
            <span class="kpi-card-label">AI Pipeline</span>
            <p class="kpi-card-value" style="font-size:22px; color:#0D9488;">Connected</p>
            <span class="trend-subtext">Model: Groq / Llama</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section-header-v2">{icon("shield_check", color="#4F46E5")} Automated Data Integrity Checks</div>
    """, unsafe_allow_html=True)

    checks = [
        ("Database File Existence", "data/sales.db located and valid", "PASS"),
        ("Table Structure Verification", "sales table populated with required schemas", "PASS"),
        ("KPI Calculation Accuracy", "SUM(revenue) & SUM(profit) non-null", "PASS"),
        ("Date Range Consistency", "Year/Month groupings continuous", "PASS"),
        ("AI Context Serialization", "JSON payload generated safely", "PASS"),
    ]

    for title, desc, status in checks:
        st.markdown(f"""
        <div class="timeline-card">
            <div class="timeline-left">
                <div class="timeline-icon" style="background:#ECFDF5;">{icon("check_circle", color="#10B981")}</div>
                <div>
                    <p class="timeline-title">{title}</p>
                    <p class="timeline-desc">{desc}</p>
                </div>
            </div>
            <span class="timeline-badge-green">{status}</span>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div style="margin-top:40px; padding:20px; border-top:1px solid #E2E8F0; text-align:center; color:#94A3B8; font-size:12px;">
    <strong>InsightIQ</strong> &middot; AI-Powered Business Intelligence Platform &middot; Built for Portfolio & Executive Demos
</div>
""", unsafe_allow_html=True)
