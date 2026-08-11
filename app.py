import os
import re
import sys
import csv
import io
import subprocess
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st
from supabase import create_client


# ============================================================
# ClientEngine AI — Streamlit Control Center
# ============================================================

st.set_page_config(
    page_title="ClientEngine AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Safe secrets / environment
# -----------------------------
def get_secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.getenv(name, default)


MODAL_TOKEN_ID = get_secret("MODAL_TOKEN_ID")
MODAL_TOKEN_SECRET = get_secret("MODAL_TOKEN_SECRET")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")
PIPELINE_FILE = get_secret("PIPELINE_FILE", "master_pipeline.py")

if MODAL_TOKEN_ID:
    os.environ["MODAL_TOKEN_ID"] = MODAL_TOKEN_ID
if MODAL_TOKEN_SECRET:
    os.environ["MODAL_TOKEN_SECRET"] = MODAL_TOKEN_SECRET


# -----------------------------
# Brand constants
# -----------------------------
BLUE = "#2563EB"
CYAN = "#06B6D4"
SLATE = "#0F172A"
BG = "#020817"
PANEL = "#071426"
GREEN = "#10B981"
AMBER = "#F59E0B"
RED = "#EF4444"
TEXT = "#FFFFFF"  # Updated to pure white
MUTED = "#FFFFFF" # Updated to white


# -----------------------------
# CSS / UI
# -----------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {{
    --bg: {BG};
    --panel: {PANEL};
    --blue: {BLUE};
    --cyan: {CYAN};
    --green: {GREEN};
    --amber: {AMBER};
    --red: {RED};
    --text: #FFFFFF;
    --muted: #FFFFFF;
}}

html, body, [class*="css"] {{
    font-family: "Inter", sans-serif;
    color: #FFFFFF !important;
}}

.stApp {{
    background:
        radial-gradient(circle at 78% 4%, rgba(6,182,212,.09), transparent 24%),
        radial-gradient(circle at 16% 72%, rgba(37,99,235,.08), transparent 28%),
        var(--bg);
    color: #FFFFFF !important;
}}

.block-container {{
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 3rem;
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] {{
    background: #030D1C !important;
    border-right: 1px solid rgba(37,99,235,.24);
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] .block-container {{
    padding: 1rem .8rem;
    color: #FFFFFF !important;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stTextInput input,
.stTextArea textarea {{
    background: #041022 !important;
    color: #FFFFFF !important;
    border-color: rgba(37,99,235,.35) !important;
    border-radius: 10px !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: #FFFFFF !important;
    opacity: 0.8;
}}

.stButton > button {{
    border: 1px solid rgba(6,182,212,.35) !important;
    border-radius: 10px !important;
    background: linear-gradient(90deg, {BLUE}, {CYAN}) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    box-shadow: 0 8px 24px rgba(6,182,212,.12) !important;
}}

.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 10px 30px rgba(6,182,212,.22) !important;
}}

div[data-testid="stMetric"] {{
    background: linear-gradient(145deg, #081A31, #051225);
    border: 1px solid rgba(37,99,235,.35);
    border-radius: 14px;
    padding: 12px 14px;
    color: #FFFFFF !important;
}}

div[data-testid="stMetricLabel"] {{
    color: #FFFFFF !important;
}}

div[data-testid="stMetricValue"] {{
    color: #FFFFFF !important;
}}

.client-card {{
    background: rgba(7,20,38,.88);
    border: 1px solid rgba(37,99,235,.34);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
    color: #FFFFFF !important;
}}

.hero {{
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(37,99,235,.52);
    border-radius: 18px;
    padding: 28px 30px;
    margin-bottom: 14px;
    background:
        radial-gradient(circle at 82% 50%, rgba(6,182,212,.13), transparent 25%),
        linear-gradient(135deg, #07182D, #041021);
    color: #FFFFFF !important;
}}

.hero:after {{
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    right: -160px;
    top: -180px;
    border-radius: 50%;
    border: 1px solid rgba(6,182,212,.13);
    box-shadow:
        0 0 0 35px rgba(6,182,212,.025),
        0 0 0 70px rgba(6,182,212,.018);
}}

.hero-content {{
    position: relative;
    z-index: 2;
}}

.brand-row {{
    display:flex;
    align-items:center;
    gap:14px;
}}

.brand-mark {{
    width:48px;
    height:48px;
    border-radius:14px;
    display:grid;
    place-items:center;
    background:linear-gradient(135deg, {BLUE}, {CYAN});
    box-shadow:0 0 28px rgba(6,182,212,.28);
    flex-shrink:0;
}}

.brand-title {{
    font-size: clamp(27px, 4vw, 44px);
    line-height:1;
    font-weight:800;
    letter-spacing:-1.8px;
    margin:0;
    color: #FFFFFF !important;
}}

.brand-title span {{
    color:{CYAN};
}}

.brand-subtitle {{
    color:#FFFFFF !important;
    font-size:14px;
    margin-top:8px;
}}

.small-muted {{
    color:#FFFFFF !important;
    font-size:11px;
}}

.status-online {{
    color:#FFFFFF !important;
    font-size:11px;
    font-weight:700;
}}

.badge {{
    display:inline-block;
    padding:5px 9px;
    border-radius:999px;
    background:rgba(16,185,129,.10);
    color:#FFFFFF !important;
    border:1px solid rgba(16,185,129,.18);
    font-size:10px;
    font-weight:700;
}}

.pipeline-log {{
    background:#020B16;
    border:1px solid rgba(37,99,235,.25);
    border-radius:12px;
    padding:12px;
    color: #FFFFFF !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid rgba(37,99,235,.22);
    border-radius: 12px;
    color: #FFFFFF !important;
}}

hr {{
    border-color: rgba(255,255,255,.20) !important;
}}

footer {{
    visibility:hidden;
}}

@media (max-width: 800px) {{
    .hero {{ padding:20px; }}
    .brand-title {{ font-size:30px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# ClientEngine AI — Screenshot-matched UI layer
# ============================================================
st.markdown(
    """
<style>
/* Main shell */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#030b18 0%,#041326 55%,#020a16 100%) !important;
    border-right: 1px solid rgba(6,182,212,.24) !important;
}
[data-testid="stSidebar"] .block-container { padding: 14px 12px 20px !important; }
.block-container { max-width: 1540px !important; padding: .35rem 1rem 2.5rem !important; }

/* Sidebar navigation */
[data-testid="stSidebar"] .stRadio > label { display:none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap:5px !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
    position:relative !important;
    border-radius:10px !important;
    padding:9px 11px !important;
    color:#FFFFFF !important;
    background:transparent !important;
    border:1px solid transparent !important;
    transition:.18s ease !important;
    cursor:pointer !important;
}
/* Hide Streamlit's native radio circles */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label > div[data-baseweb="radio"] {
    display:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-baseweb="radio"] > div {
    display:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label svg {
    display:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
    display:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
    position:absolute !important;
    opacity:0 !important;
    width:1px !important;
    height:1px !important;
    pointer-events:none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background:rgba(37,99,235,.12) !important;
    color:#FFFFFF !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background:linear-gradient(90deg,#1677ee,#0b63dc) !important;
    color:#FFFFFF !important;
    border-color:rgba(56,189,248,.35) !important;
    box-shadow:0 7px 22px rgba(37,99,235,.22) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size:12px !important; font-weight:600 !important; margin:0 !important; color:#FFFFFF !important;
}
/* Replaced circle/selector symbol with a clean arrow -> */
[data-testid="stSidebar"] div[role="radiogroup"] label p::before { content:"→  "; color:#FFFFFF !important; }

/* Remove Streamlit's white header/toolbar so the dashboard starts at the top */
header[data-testid="stHeader"] {
    display:none !important;
}
[data-testid="stToolbar"] {
    display:none !important;
}
[data-testid="stDecoration"] {
    display:none !important;
}
.stAppViewContainer > .main {
    padding-top:0 !important;
}
.main .block-container {
    padding-top:.35rem !important;
}

/* Top bar */
.ce-topbar {
    height:48px; display:flex; align-items:center; justify-content:space-between;
    margin:0 0 10px; padding:0 4px;
}
.ce-topline { color:#FFFFFF !important; font-size:12px; letter-spacing:.2px; }
.ce-topright { display:flex; align-items:center; gap:12px; }
.ce-searchbox {
    width:260px; height:36px; display:flex; align-items:center; gap:8px;
    border:1px solid rgba(37,99,235,.45); border-radius:9px;
    background:#061225; color:#FFFFFF !important; padding:0 12px; font-size:11px;
}
.ce-icon { color:#FFFFFF !important; font-size:16px; }
.ce-avatar {
    width:34px; height:34px; border-radius:50%; display:grid; place-items:center;
    background:linear-gradient(135deg,#0ea5e9,#2563eb); color:#FFFFFF !important; font-size:12px; font-weight:800;
    box-shadow:0 0 18px rgba(14,165,233,.25);
}
.ce-user { display:flex; align-items:center; gap:8px; font-size:11px; color:#FFFFFF !important; }
.ce-user small { display:block; color:#FFFFFF !important; margin-top:2px; font-size:9px; }

/* Hero */
.ce-hero {
    min-height:155px; position:relative; overflow:hidden; border:1px solid rgba(37,99,235,.58);
    border-radius:16px; padding:24px 28px; margin-bottom:12px;
    background:radial-gradient(circle at 75% 50%,rgba(6,182,212,.18),transparent 24%),
               linear-gradient(135deg,#071a32,#031020);
    box-shadow:inset 0 0 40px rgba(6,182,212,.025),0 14px 45px rgba(0,0,0,.18);
    color: #FFFFFF !important;
}
.ce-hero:after {
    content:""; position:absolute; width:350px; height:350px; right:-80px; top:-95px;
    border-radius:50%; border:1px solid rgba(6,182,212,.16);
    box-shadow:0 0 0 30px rgba(6,182,212,.025),0 0 0 62px rgba(6,182,212,.018),0 0 0 94px rgba(6,182,212,.012);
}
.ce-hero-inner { position:relative; z-index:2; display:flex; align-items:center; justify-content:space-between; gap:25px; }
.ce-brand { display:flex; align-items:center; gap:18px; }
.ce-logo-large { width:78px; height:78px; display:grid; place-items:center; border-radius:16px; flex-shrink:0;
    background:linear-gradient(145deg,rgba(37,99,235,.16),rgba(6,182,212,.08));
    border:1px solid rgba(6,182,212,.45); box-shadow:0 0 28px rgba(6,182,212,.20); }
.ce-title { font-size:clamp(32px,4vw,52px); line-height:.98; font-weight:800; letter-spacing:-2.5px; color:#FFFFFF !important; }
.ce-title span { color:#FFFFFF !important; }
.ce-subtitle { color:#FFFFFF !important; font-size:16px; margin-top:9px; }
.ce-coverage { min-width:220px; position:relative; z-index:3; padding:16px 20px; border:1px solid rgba(37,99,235,.38);
    border-radius:14px; background:rgba(3,13,28,.72); backdrop-filter:blur(8px); color:#FFFFFF !important; }
.ce-coverage-title { font-size:13px; font-weight:700; margin-bottom:10px; color:#FFFFFF !important; }
.ce-flags { font-size:23px; letter-spacing:7px; }
.ce-coverage small { color:#FFFFFF !important; display:block; margin-top:8px; }

/* Cards */
.ce-panel { background:rgba(7,20,38,.90); border:1px solid rgba(37,99,235,.38); border-radius:15px; padding:17px; box-shadow:0 12px 35px rgba(0,0,0,.16); color:#FFFFFF !important; }
.ce-panel-title { font-size:16px; font-weight:750; color:#FFFFFF !important; }
.ce-panel-sub { color:#FFFFFF !important; font-size:11px; margin-top:4px; }
.ce-search-grid { display:grid; grid-template-columns:1fr 1fr 1.05fr; gap:11px; margin-top:16px; }
.ce-field { background:#041022; border:1px solid rgba(37,99,235,.35); border-radius:9px; padding:9px 11px; min-height:58px; color:#FFFFFF !important; }
.ce-field-label { color:#FFFFFF !important; font-size:9px; text-transform:uppercase; letter-spacing:.5px; margin-bottom:4px; }
.ce-feature-row { display:flex; flex-wrap:wrap; gap:7px; margin-top:10px; }
.ce-feature { border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#FFFFFF !important; padding:5px 8px; border-radius:20px; font-size:9px; }
.ce-status { display:flex; justify-content:space-between; align-items:center; margin-bottom:13px; color:#FFFFFF !important; }
.ce-online { color:#FFFFFF !important; font-size:9px; background:rgba(16,185,129,.10); border:1px solid rgba(16,185,129,.17); padding:5px 8px; border-radius:20px; }
.ce-ai-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.ce-ai { background:#041022; border:1px solid rgba(37,99,235,.22); border-radius:10px; padding:10px; min-height:70px; color:#FFFFFF !important; }
.ce-ai-icon { font-size:19px; } .ce-ai-name { font-size:10px; margin-top:5px; color:#FFFFFF !important; } .ce-ai-active { color:#FFFFFF !important; font-size:8px; margin-top:2px; }

/* KPI */
.ce-kpis { display:grid; grid-template-columns:repeat(5,1fr); gap:11px; margin:12px 0; }
.ce-kpi { position:relative; overflow:hidden; padding:13px 14px; min-height:88px; border-radius:13px;
    background:linear-gradient(145deg,#081a31,#051225); border:1px solid rgba(37,99,235,.38); color:#FFFFFF !important; }
.ce-kpi:after { content:""; position:absolute; left:-15%; right:20%; bottom:-22px; height:45px; border-top:2px solid rgba(6,182,212,.55); border-radius:50%; transform:rotate(-4deg); opacity:.7; }
.ce-kpi-icon { font-size:20px; } .ce-kpi-value { font-size:22px; font-weight:800; margin-top:6px; color:#FFFFFF !important; } .ce-kpi-name { color:#FFFFFF !important; font-size:10px; } .ce-kpi-growth { color:#FFFFFF !important; font-size:8px; margin-top:6px; }

/* Data rows */
.ce-three { display:grid; grid-template-columns:1.05fr 1fr 1fr; gap:12px; }
.ce-funnel { display:flex; flex-direction:column; align-items:center; gap:4px; margin-top:14px; }
.ce-funnel-item { height:27px; display:grid; place-items:center; font-size:9px; font-weight:700; border-radius:5px; color:#FFFFFF !important; }
.ce-f1{width:92%;background:#2563eb} .ce-f2{width:78%;background:#0891b2} .ce-f3{width:65%;background:#14b8a6} .ce-f4{width:52%;background:#8b5cf6} .ce-f5{width:38%;background:#f59e0b} .ce-f6{width:25%;background:#ef4444}
.ce-country { margin-top:12px; } .ce-country-row { display:flex; justify-content:space-between; align-items:center; font-size:10px; margin:10px 0; color:#FFFFFF !important; }
.ce-country-track { height:5px; margin-top:5px; background:#17243a; border-radius:20px; overflow:hidden; } .ce-country-fill { height:100%; border-radius:20px; background:linear-gradient(90deg,#2563eb,#06b6d4); }
.ce-op { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,.10); font-size:10px; color:#FFFFFF !important; } .ce-op:last-child{border-bottom:0} .ce-op span:last-child{color:#FFFFFF !important;}

/* Activity */
.ce-activity { margin-top:12px; } .ce-event { display:flex; gap:10px; padding:9px 0; border-bottom:1px solid rgba(255,255,255,.10); color:#FFFFFF !important; } .ce-event:last-child{border-bottom:0} .ce-event-dot{width:27px;height:27px;border-radius:50%;display:grid;place-items:center;background:rgba(37,99,235,.16);color:#FFFFFF !important;flex-shrink:0} .ce-event-text{font-size:10px; color:#FFFFFF !important;} .ce-event-text span{display:block;color:#FFFFFF !important;margin-top:3px;font-size:9px}

/* Recent leads */
.ce-table { overflow-x:auto; margin-top:12px; } .ce-table table{width:100%;border-collapse:collapse;min-width:850px} .ce-table th{text-align:left;color:#FFFFFF !important;font-size:8px;font-weight:600;padding:9px;border-bottom:1px solid rgba(255,255,255,.10)} .ce-table td{padding:10px 9px;font-size:9px;border-bottom:1px solid rgba(255,255,255,.10);color:#FFFFFF !important;} .ce-score{background:rgba(16,185,129,.12);color:#FFFFFF !important;padding:4px 7px;border-radius:7px} .ce-ready{color:#FFFFFF !important} .ce-follow{color:#FFFFFF !important} .ce-draft{color:#FFFFFF !important}

/* Streamlit widgets in cards */
.ce-widget-wrap div[data-baseweb="select"] > div, .ce-widget-wrap .stTextInput input { min-height:38px !important; color:#FFFFFF !important; }
.ce-widget-wrap .stButton > button { min-height:42px !important; }

@media(max-width:1050px){
  .ce-search-grid{grid-template-columns:1fr 1fr} .ce-search-grid > :last-child{grid-column:1/-1;height:45px}
  .ce-three{grid-template-columns:1fr} .ce-kpis{grid-template-columns:repeat(3,1fr)} .ce-coverage{display:none}
}
@media(max-width:700px){
  .ce-topline{display:none} .ce-searchbox{width:170px} .ce-brand{gap:10px} .ce-logo-large{width:60px;height:60px} .ce-title{font-size:30px} .ce-subtitle{font-size:12px} .ce-search-grid{grid-template-columns:1fr} .ce-kpis{grid-template-columns:1fr 1fr}
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Logo SVG
# -----------------------------
def logo_svg(size=48):
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ceg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BLUE}"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <polygon points="50,5 89,27 89,73 50,95 11,73 11,27"
           fill="#071426" stroke="url(#ceg)" stroke-width="6"/>
  <circle cx="50" cy="50" r="27" fill="none" stroke="#06B6D4" stroke-width="2" opacity=".65"/>
  <path d="M55 20 L36 53 H49 L44 80 L66 45 H53 Z"
        fill="url(#ceg)"/>
  <path d="M20 50 H31 M69 50 H80 M50 20 V31 M50 69 V80"
        stroke="#38BDF8" stroke-width="2" stroke-linecap="round" opacity=".75"/>
</svg>
"""


# -----------------------------
# Data access
# -----------------------------
@st.cache_data(ttl=10)
def fetch_leads():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return [], "Supabase credentials are not configured."

    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = (
            client.table("leads")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or [], None
    except Exception as exc:
        return [], str(exc)


def status_counts(leads):
    counts = {
        "new": 0,
        "pending": 0,
        "sent": 0,
        "completed": 0,
        "replied": 0,
        "failed": 0,
    }

    for row in leads:
        status = str(row.get("status", "")).strip().lower()
        if status in counts:
            counts[status] += 1

        if status in {"ready", "ready to send", "qualified"}:
            counts["pending"] += 1
        if status in {"contacted", "emailed"}:
            counts["sent"] += 1

    return counts


def safe_text(value, fallback="N/A"):
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def clean_target(value):
    return re.sub(r"[^a-zA-Z0-9\s,&.'-]", "", value or "").strip()


def find_pipeline_file():
    candidates = [
        PIPELINE_FILE,
        "master_pipeline.py",
        "sdr_agent.py",
    ]
    for name in candidates:
        path = Path(name)
        if path.exists():
            return str(path)
    return None


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="border:1px solid rgba(6,182,212,.30);border-radius:15px;padding:10px 9px;
                    background:linear-gradient(135deg,rgba(37,99,235,.14),rgba(6,182,212,.04));margin-bottom:14px; color:#FFFFFF;">
            <div style="display:flex;align-items:center;gap:9px;">
                <div style="width:48px;height:48px;display:grid;place-items:center;">
                    {logo_svg(46)}
                </div>
                <div>
                    <div style="font-size:15px;font-weight:800;color:#FFFFFF;">ClientEngine <span style="color:{CYAN};">AI</span></div>
                    <div style="font-size:9px;color:#FFFFFF;margin-top:3px;">AI Lead Generation Platform</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Find Leads",
            "Lead Database",
            "AI Outreach",
            "Follow-ups",
            "Campaigns",
            "Analytics",
            "Email Templates",
            "Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown(
        '<div style="margin:18px 4px 8px;color:#FFFFFF;font-size:9px;font-weight:700;letter-spacing:1px;">AI ENGINE STATUS</div>',
        unsafe_allow_html=True,
    )

    engine_items = [
        ("OpenAI GPT-4o", bool(get_secret("OPENAI_API_KEY"))),
        ("Modal", bool(MODAL_TOKEN_ID or MODAL_TOKEN_SECRET)),
        ("Supabase", bool(SUPABASE_URL and SUPABASE_KEY)),
        ("SMTP / Resend", bool(get_secret("SMTP_HOST") or get_secret("RESEND_API_KEY"))),
    ]
    for name, connected in engine_items:
        color = "#FFFFFF" if connected else "#FFFFFF"
        label = "Connected" if connected else "Not configured"
        st.markdown(
            f'<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 4px;font-size:10px;color:#FFFFFF;">'
            f'<span>{name}</span><span style="color:{color};font-weight:700;">● {label}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="margin-top:18px;border:1px solid rgba(37,99,235,.32);border-radius:13px;padding:13px;text-align:center;background:rgba(7,20,38,.75);color:#FFFFFF;">
            <div style="font-weight:800;font-size:12px;color:#FFFFFF;">Rai Marketing Agency</div>
            <div style="color:#FFFFFF;font-size:9px;margin-top:4px;">Digital Growth Solutions</div>
            <div style="color:#FFFFFF;font-size:8px;margin-top:7px;">ClientEngine AI · v2.0</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Load data
# -----------------------------
all_leads, db_error = fetch_leads()
counts = status_counts(all_leads)
total_leads = len(all_leads)
sent_emails = counts["sent"] + counts["completed"]
pending_queue = counts["new"] + counts["pending"]
replies = counts["replied"]

verified_leads = sum(1 for r in all_leads if str(r.get("email", "")).strip() and "@" in str(r.get("email", "")))
qualified_leads = sum(
    1 for r in all_leads
    if str(r.get("email", "")).strip()
    and str(r.get("website", "")).strip()
)
meetings = sum(1 for r in all_leads if str(r.get("status", "")).lower() in {"meeting", "booked", "scheduled"})

# -----------------------------
# Top bar
# -----------------------------
st.markdown(
    """
    <div class="ce-topbar">
        <div class="ce-topline">✦ &nbsp; Find. Engage. Convert. Grow.</div>
        <div class="ce-topright">
            <div class="ce-searchbox">⌕ <span>Search leads, companies...</span><span style="margin-left:auto;color:#FFFFFF;">⌘K</span></div>
            <div class="ce-icon">♧</div>
            <div class="ce-icon">⚙</div>
            <div class="ce-user"><div class="ce-avatar">SA</div><div><strong>Shafqat Abbas</strong><small>Founder</small></div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    f"""
    <div class="ce-hero">
      <div class="ce-hero-inner">
        <div class="ce-brand">
          <div class="ce-logo-large">{logo_svg(72)}</div>
          <div>
            <div class="ce-title">ClientEngine <span>AI</span></div>
            <div class="ce-subtitle">AI-Powered Lead Generation &amp; Outreach Platform</div>
          </div>
        </div>
        <div class="ce-coverage">
          <div class="ce-coverage-title">🌐 Global Coverage</div>
          <div class="ce-flags">🇺🇸 🇬🇧 🇨🇦 🇩🇪</div>
          <small>4 Countries Active</small>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Find customers + engine status
# -----------------------------
if menu in {"Dashboard", "Find Leads"}:
    query_params = st.query_params
    url_niche = query_params.get("niche", "")
    url_location = query_params.get("location", "")

    industries = [
        "Roofing Contractors", "HVAC Companies", "Construction Companies", "Plumbing Companies",
        "Dental Practices", "Real Estate Agencies", "Law Firms", "Solar Companies", "Restaurants",
        "E-commerce", "Digital Marketing Agencies", "Software Companies", "Hotels", "Accounting Services",
        "Custom Industry...",
    ]
    countries = [
        "United States", "United Kingdom", "Canada", "Germany", "Australia", "United Arab Emirates",
        "Saudi Arabia", "Pakistan", "France", "Italy", "Netherlands", "Worldwide / Global", "Custom Location...",
    ]

    left, right = st.columns([3.2, 1], gap="small")
    with left:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Find Your Next Customers</div>', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-sub">Tell us your industry and location, and let AI find &amp; analyze potential clients.</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 1.05], gap="small")
        with c1:
            industry_default = industries.index(url_niche) if url_niche in industries else 0
            selected_industry = st.selectbox("Industry / Niche", industries, index=industry_default)
            if selected_industry == "Custom Industry...":
                final_niche = st.text_input("Custom industry", value="" if url_niche in industries else url_niche, placeholder="e.g. commercial cleaning")
            else:
                final_niche = selected_industry
        with c2:
            country_default = countries.index(url_location) if url_location in countries else 0
            selected_country = st.selectbox("Location / Country", countries, index=country_default)
            if selected_country == "Custom Location...":
                final_location = st.text_input("Custom location", value="" if url_location in countries else url_location, placeholder="e.g. Dallas, Texas")
            elif selected_country == "Worldwide / Global":
                final_location = "Global"
            else:
                final_location = selected_country
        with c3:
            st.markdown('<div style="height:27px"></div>', unsafe_allow_html=True)
            run_pipeline = st.button("⌕  Find Potential Customers  →", use_container_width=True, type="primary")
            refresh = st.button("↻  Refresh Database", use_container_width=True)

        clean_niche = clean_target(final_niche)
        clean_location = clean_target(final_location)
        st.markdown(
            '<div class="ce-feature-row">'
            '<span class="ce-feature">✓ Auto Search</span>'
            '<span class="ce-feature">✓ Verify Emails</span>'
            '<span class="ce-feature">✓ Analyze Websites</span>'
            '<span class="ce-feature">✓ Score Leads</span>'
            '<span class="ce-feature">✓ Generate Emails</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="ce-panel" style="height:100%;">', unsafe_allow_html=True)
        st.markdown('<div class="ce-status"><strong>AI Engine Status</strong><span class="ce-online">● All Systems Online</span></div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="ce-ai-grid">
              <div class="ce-ai"><div class="ce-ai-icon">🌐</div><div class="ce-ai-name">Web Scraping</div><div class="ce-ai-active">● {'Active' if (MODAL_TOKEN_ID or MODAL_TOKEN_SECRET) else 'Offline'}</div></div>
              <div class="ce-ai"><div class="ce-ai-icon">🧠</div><div class="ce-ai-name">AI Analysis</div><div class="ce-ai-active">● {'Active' if get_secret("OPENAI_API_KEY") else 'Offline'}</div></div>
              <div class="ce-ai"><div class="ce-ai-icon">✉</div><div class="ce-ai-name">Email Generation</div><div class="ce-ai-active">● {'Active' if get_secret("OPENAI_API_KEY") else 'Offline'}</div></div>
              <div class="ce-ai"><div class="ce-ai-icon">▥</div><div class="ce-ai-name">Lead Scoring</div><div class="ce-ai-active">● Active</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if refresh:
        st.cache_data.clear()
        st.rerun()

    kpi_data = [
        ("👥", total_leads, "Leads Found", "↗ Live database"),
        ("✓", verified_leads, "Verified Leads", "↗ Email detected"),
        ("✉", pending_queue, "Emails Ready", "↗ Queue"),
        ("➤", sent_emails, "Emails Sent", "↗ Outreach"),
        ("●", replies, "Replies", "↗ Responses"),
    ]
    cols = st.columns(5, gap="small")
    for col, (icon, value, name, growth) in zip(cols, kpi_data):
        with col:
            st.markdown(
                f'<div class="ce-kpi"><div class="ce-kpi-icon">{icon}</div><div class="ce-kpi-value">{value}</div><div class="ce-kpi-name">{name}</div><div class="ce-kpi-growth">{growth}</div></div>',
                unsafe_allow_html=True,
            )

    if run_pipeline:
        if not clean_niche or not clean_location:
            st.error("Please enter both an industry and a location.")
        else:
            pipeline = find_pipeline_file()
            st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
            st.markdown("### Live Cloud Execution")
            if not pipeline:
                st.error("No pipeline file was found. Put master_pipeline.py or sdr_agent.py in the same folder as app.py.")
            else:
                status_box = st.empty()
                status_box.info(f"Running {Path(pipeline).name} for {clean_niche} → {clean_location}")
                log_box = st.empty()
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"
                command = [sys.executable, "-m", "modal", "run", pipeline, "--niche", clean_niche, "--location", clean_location]
                output_logs = ""
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", env=env)
                    if process.stdout:
                        for line in process.stdout:
                            output_logs += line
                            log_box.code(output_logs, language="text")
                    return_code = process.wait()
                    if return_code == 0:
                        status_box.success("Pipeline completed successfully. Refreshing lead database...")
                        st.cache_data.clear()
                    else:
                        status_box.error(f"Pipeline stopped with exit code {return_code}.")
                except FileNotFoundError:
                    status_box.error("Modal CLI was not found. Install it with: pip install modal")
                except Exception as exc:
                    status_box.error(f"Execution error: {exc}")
            st.markdown('</div>', unsafe_allow_html=True)

    countries_count = {}
    for row in all_leads:
        country = safe_text(row.get("country"), "Unknown")
        countries_count[country] = countries_count.get(country, 0) + 1
    top_countries = sorted(countries_count.items(), key=lambda x: x[1], reverse=True)[:4]
    total_for_pct = max(sum(countries_count.values()), 1)

    opp_counts = {
        "No/weak Google presence": 0,
        "Weak Website / CTA": 0,
        "Poor SEO signals": 0,
        "Missing contact path": 0,
        "Social media opportunity": 0,
    }
    for row in all_leads:
        website = str(row.get("website", "")).strip()
        email = str(row.get("email", "")).strip()
        if not website: opp_counts["Weak Website / CTA"] += 1
        if not email: opp_counts["Missing contact path"] += 1
        if website: opp_counts["Poor SEO signals"] += 1
        if row.get("industry"): opp_counts["Social media opportunity"] += 1
    top_opps = sorted(opp_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    a1, a2, a3 = st.columns([1.05, 1, 1], gap="small")
    with a1:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Lead Generation Pipeline</div>', unsafe_allow_html=True)
        funnel = [
            ("Found", total_leads, "ce-f1"),
            ("Verified", verified_leads, "ce-f2"),
            ("Qualified", qualified_leads, "ce-f3"),
            ("Contacted", sent_emails, "ce-f4"),
            ("Replied", replies, "ce-f5"),
            ("Meetings", meetings, "ce-f6"),
        ]
        st.markdown('<div class="ce-funnel">' + ''.join(f'<div class="ce-funnel-item {cls}">{name} — {value}</div>' for name, value, cls in funnel) + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Country Distribution</div>', unsafe_allow_html=True)
        if top_countries:
            html = '<div class="ce-country">'
            for country, n in top_countries:
                pct = round((n / total_for_pct) * 100)
                flag = {"United States":"🇺🇸","United Kingdom":"🇬🇧","Canada":"🇨🇦","Germany":"🇩🇪","USA":"🇺🇸","UK":"🇬🇧"}.get(country, "🌍")
                html += f'<div class="ce-country-row"><div style="width:76%;">{flag} {country}<div class="ce-country-track"><div class="ce-country-fill" style="width:{pct}%;"></div></div></div><strong>{pct}%</strong></div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("Country distribution will appear after leads are stored.")
        st.markdown('</div>', unsafe_allow_html=True)

    with a3:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Top Opportunities</div>', unsafe_allow_html=True)
        if top_opps:
            for name, n in top_opps:
                st.markdown(f'<div class="ce-op"><span>{name}</span><span>{n} leads →</span></div>', unsafe_allow_html=True)
        else:
            st.info("Opportunities will appear after leads are stored.")
        st.markdown('</div>', unsafe_allow_html=True)

    act, qa = st.columns([2.1, 1], gap="small")
    with act:
        st.markdown('<div class="ce-panel ce-activity">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Recent Activity <span style="float:right;color:#FFFFFF;font-size:9px;">● Live</span></div>', unsafe_allow_html=True)
        recent = all_leads[:5]
        if recent:
            icons = ["+", "✓", "✦", "➤", "●"]
            labels = ["New lead added", "Lead verified", "AI analysis / record update", "Outreach ready", "Reply / status update"]
            for i, row in enumerate(recent):
                company = safe_text(row.get("company_name"), "Lead")
                email = safe_text(row.get("email"), "No email")
                st.markdown(f'<div class="ce-event"><div class="ce-event-dot">{icons[i % len(icons)]}</div><div class="ce-event-text"><b>{labels[i % len(labels)]}</b><span>{company} · {email}</span></div></div>', unsafe_allow_html=True)
        else:
            st.info("Recent activity will appear after leads are stored.")
        st.markdown('</div>', unsafe_allow_html=True)

    with qa:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Quick Actions</div>', unsafe_allow_html=True)
        st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">', unsafe_allow_html=True)
        st.markdown('<div style="padding:16px 8px;border:1px solid rgba(139,92,246,.45);border-radius:10px;text-align:center;background:rgba(139,92,246,.08); color:#FFFFFF;">＋<br><small>New Campaign</small></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:16px 8px;border:1px solid rgba(37,99,235,.45);border-radius:10px;text-align:center;background:rgba(37,99,235,.08); color:#FFFFFF;">⇩<br><small>Export Leads</small></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:16px 8px;border:1px solid rgba(16,185,129,.45);border-radius:10px;text-align:center;background:rgba(16,185,129,.08); color:#FFFFFF;">✉<br><small>Email Templates</small></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:16px 8px;border:1px solid rgba(245,158,11,.45);border-radius:10px;text-align:center;background:rgba(245,158,11,.08); color:#FFFFFF;">▥<br><small>View Analytics</small></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
    st.markdown('<div class="ce-panel-title">Recent High-Value Leads <span style="float:right;color:#FFFFFF;font-size:10px;">View All →</span></div>', unsafe_allow_html=True)
    if db_error:
        st.warning(f"Supabase: {db_error}")
    if all_leads:
        rows = []
        for row in all_leads[:25]:
            company = safe_text(row.get("company_name"))
            website = safe_text(row.get("website"), "")
            email = safe_text(row.get("email"), "")
            country = safe_text(row.get("country"))
            status = safe_text(row.get("status"))
            score = 50 + (20 if email else 0) + (15 if website else 0) + (10 if row.get("industry") else 0)
            score = min(score, 95)
            if status.lower() in {"sent", "contacted", "emailed"}: status_label = "Follow-up"
            elif status.lower() in {"draft", "new"}: status_label = "Ready"
            else: status_label = status.title() if status else "New"
            rows.append({"Company": company, "Location": country, "Email": email or "—", "AI Score": f"{score}/100", "Opportunity": "Website / lead-generation review", "Status": status_label, "Website": website})
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No leads found yet. Launch a campaign above.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Lead Database
# -----------------------------
elif menu == "Lead Database":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Lead Database")
    st.caption("Live records loaded from Supabase.")

    search = st.text_input(
        "Search",
        placeholder="Company, email, country, industry...",
    )

    filtered = all_leads

    if search:
        needle = search.lower().strip()
        filtered = [
            row
            for row in all_leads
            if needle in " ".join(
                [
                    safe_text(row.get("company_name"), ""),
                    safe_text(row.get("email"), ""),
                    safe_text(row.get("country"), ""),
                    safe_text(row.get("industry"), ""),
                    safe_text(row.get("status"), ""),
                    safe_text(row.get("website"), ""),
                ]
            ).lower()
        ]

    st.write(f"Showing **{len(filtered)}** records.")

    if filtered:
        table = [
            {
                "Company": safe_text(r.get("company_name")),
                "Email": safe_text(r.get("email")),
                "Industry": safe_text(r.get("industry")),
                "Country": safe_text(r.get("country")),
                "Status": safe_text(r.get("status")),
                "Website": safe_text(r.get("website")),
            }
            for r in filtered
        ]
        st.dataframe(table, use_container_width=True, hide_index=True)

        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=table[0].keys())
        writer.writeheader()
        writer.writerows(table)

        st.download_button(
            "Download CSV",
            data=csv_buffer.getvalue(),
            file_name="clientengine_leads.csv",
            mime="text/csv",
        )
    else:
        st.info("No matching leads.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# AI Outreach
# -----------------------------
elif menu == "AI Outreach":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### AI Outreach Workspace")
    st.caption(
        "Generate personalized outreach from the information already stored "
        "for a lead. Connect your OpenAI/email provider in secrets before sending."
    )

    if not all_leads:
        st.info("Add leads first from Find Leads.")
    else:
        options = []
        for i, row in enumerate(all_leads[:200]):
            options.append(
                f"{i}: {safe_text(row.get('company_name'))} — "
                f"{safe_text(row.get('email'))}"
            )

        selected = st.selectbox("Lead", options)
        index = int(selected.split(":", 1)[0])
        lead = all_leads[index]

        st.markdown(
            f"""
            **Company:** {safe_text(lead.get('company_name'))}  
            **Email:** {safe_text(lead.get('email'))}  
            **Website:** {safe_text(lead.get('website'))}  
            **Industry:** {safe_text(lead.get('industry'))}
            """
        )

        service = st.text_input(
            "Offer / service",
            value="Google Ads, Meta Ads, Social Media Management and Local SEO",
        )

        problem = st.text_area(
            "Known problem / observation",
            placeholder="Example: weak Google visibility, slow website, poor CTA...",
        )

        if st.button("Generate Outreach Draft", use_container_width=True):
            company = safe_text(lead.get("company_name"), "your company")
            email = safe_text(lead.get("email"), "")
            subject = f"Ideas to help {company} generate more qualified leads"

            body = f"""Hi {company} team,

I came across your business while researching {safe_text(lead.get('industry'), 'local businesses')} in {safe_text(lead.get('country'), 'your market')}.

I noticed this opportunity:
{problem or 'There may be opportunities to improve your online lead generation and conversion process.'}

At Rai Marketing Agency, we help businesses improve lead generation through:
- Google Ads
- Facebook & Instagram Ads
- Social Media Management
- Local SEO
- Website and landing-page optimization

I would be happy to share a quick audit and a practical plan based on your current setup.

Best,
Rai Marketing Agency
"""

            st.success("Draft generated.")
            st.code(f"Subject: {subject}\n\n{body}", language="text")
            if email and email != "N/A":
                st.caption(
                    "The draft is prepared for review. Automatic sending should "
                    "only be enabled after your email provider, consent/compliance "
                    "rules, sending limits, and opt-out process are configured."
                )

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Follow-ups
# -----------------------------
elif menu == "Follow-ups":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Follow-ups")
    st.caption("Use lead status to identify records that need a follow-up.")

    followups = [
        r for r in all_leads
        if str(r.get("status", "")).lower()
        in {"sent", "contacted", "follow-up", "followup"}
    ]

    if followups:
        st.dataframe(
            [
                {
                    "Company": safe_text(r.get("company_name")),
                    "Email": safe_text(r.get("email")),
                    "Country": safe_text(r.get("country")),
                    "Status": safe_text(r.get("status")),
                    "Website": safe_text(r.get("website")),
                }
                for r in followups
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No follow-up records are currently marked in Supabase.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Campaigns
# -----------------------------
elif menu == "Campaigns":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Campaigns")
    st.caption("Launch campaigns from a reusable target configuration.")

    campaign_name = st.text_input("Campaign name", placeholder="USA Roofing — August")
    campaign_notes = st.text_area(
        "Campaign notes",
        placeholder="Offer, target profile, exclusions, messaging notes...",
    )

    if st.button("Save Campaign Plan", use_container_width=True):
        if campaign_name.strip():
            st.success(
                "Campaign plan prepared. Connect a campaign table in Supabase "
                "to persist it permanently."
            )
        else:
            st.error("Enter a campaign name.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Analytics
# -----------------------------
elif menu == "Analytics":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Analytics")
    st.caption("Calculated from the live lead records available in Supabase.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Leads", total_leads)
    c2.metric("Ready / Pending", pending_queue)
    c3.metric("Sent / Completed", sent_emails)
    c4.metric("Replies", replies)

    if all_leads:
        countries = {}
        industries = {}

        for row in all_leads:
            country = safe_text(row.get("country"), "Unknown")
            industry = safe_text(row.get("industry"), "Unknown")
            countries[country] = countries.get(country, 0) + 1
            industries[industry] = industries.get(industry, 0) + 1

        left, right = st.columns(2)

        with left:
            st.markdown("#### Leads by Country")
            st.dataframe(
                [
                    {"Country": k, "Leads": v}
                    for k, v in sorted(
                        countries.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                ],
                use_container_width=True,
                hide_index=True,
            )

        with right:
            st.markdown("#### Leads by Industry")
            st.dataframe(
                [
                    {"Industry": k, "Leads": v}
                    for k, v in sorted(
                        industries.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                ],
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Analytics will appear after leads are stored.")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Email Templates
# -----------------------------
elif menu == "Email Templates":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Email Templates")

    template_type = st.selectbox(
        "Template",
        [
            "First outreach",
            "Follow-up #1",
            "Follow-up #2",
            "Audit offer",
        ],
    )

    if template_type == "First outreach":
        subject = "Quick idea for improving your lead generation"
        body = """Hi {{company_name}},

I came across {{company_name}} while researching {{industry}} businesses in {{country}}.

I noticed {{problem}}.

We help businesses improve lead generation with Google Ads, Meta Ads,
social media management, Local SEO and landing-page optimization.

Would you be open to a quick conversation?

Best,
Rai Marketing Agency"""
    elif template_type == "Follow-up #1":
        subject = "Following up — {{company_name}}"
        body = """Hi {{company_name}},

Just following up on my previous message.

If improving your online lead generation is a priority, I can send over
a short audit with the main opportunities I found.

Best,
Rai Marketing Agency"""
    elif template_type == "Follow-up #2":
        subject = "Should I close the loop?"
        body = """Hi {{company_name}},

I don't want to keep filling your inbox.

If marketing improvements are not a priority right now, no problem.
If they are, I can send a concise audit and recommended next steps.

Best,
Rai Marketing Agency"""
    else:
        subject = "Free marketing audit for {{company_name}}"
        body = """Hi {{company_name}},

I can prepare a short review of your website, search visibility,
social presence and lead-generation opportunities.

If you'd like the audit, reply with "AUDIT" and I'll send the findings.

Best,
Rai Marketing Agency"""

    st.text_input("Subject", value=subject)
    st.text_area("Body", value=body, height=280)

    st.caption(
        "Use placeholders such as {{company_name}}, {{industry}}, "
        "{{country}}, and {{problem}} when your sending layer supports them."
    )

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Settings
# -----------------------------
elif menu == "Settings":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Settings")

    st.markdown("#### Pipeline")
    st.code(
        f"Pipeline file: {PIPELINE_FILE}\n"
        f"Detected file: {find_pipeline_file() or 'None'}",
        language="text",
    )

    st.markdown("#### Required Streamlit secrets")
    st.code(
        """MODAL_TOKEN_ID="..."
MODAL_TOKEN_SECRET="..."
SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY="YOUR_SUPABASE_KEY"
OPENAI_API_KEY="..."
PIPELINE_FILE="master_pipeline.py"
""",
        language="toml",
    )

    st.warning(
        "Do not hard-code API keys or database credentials in app.py. "
        "Use .streamlit/secrets.toml locally and Streamlit Secrets in deployment."
    )

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <div style="text-align:center;color:#FFFFFF;font-size:9px;padding:20px 0 4px;">
        ClientEngine AI · Rai Marketing Agency · Find. Analyze. Engage. Grow.
    </div>
    """,
    unsafe_allow_html=True,
)
