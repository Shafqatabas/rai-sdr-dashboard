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
    initial_sidebar_state="collapsed",
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
TEXT = "#FFFFFF"
MUTED = "#FFFFFF"


# -----------------------------
# CSS / UI (Fully Responsive)
# -----------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #020817;
    --panel: #071426;
    --blue: #2563EB;
    --cyan: #06B6D4;
    --green: #10B981;
    --amber: #F59E0B;
    --red: #EF4444;
    --text: #FFFFFF;
    --muted: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
    color: #FFFFFF !important;
}

.stApp {
    background:
        radial-gradient(circle at 78% 4%, rgba(6,182,212,.09), transparent 24%),
        radial-gradient(circle at 16% 72%, rgba(37,99,235,.08), transparent 28%),
        var(--bg);
    color: #FFFFFF !important;
}

.block-container {
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 3rem;
    padding-left: 1rem;
    padding-right: 1rem;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

div[data-baseweb="select"] > div {
    background: #041022 !important;
    color: #FFFFFF !important;
    border-color: rgba(37,99,235,.35) !important;
    border-radius: 10px !important;
}

div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #041022 !important;
    color: #FFFFFF !important;
}

div[role="option"] {
    background-color: #041022 !important;
    color: #FFFFFF !important;
}

div[role="option"]:hover {
    background-color: #0b2246 !important;
    color: #FFFFFF !important;
}

label[data-baseweb="checkbox"], label[data-baseweb="radio"], .stSelectbox label p, p {
    color: #FFFFFF !important;
}

div[data-baseweb="input"] > div,
.stTextInput input,
.stTextArea textarea {
    background: #041022 !important;
    color: #FFFFFF !important;
    border-color: rgba(37,99,235,.35) !important;
    border-radius: 10px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #FFFFFF !important;
    opacity: 0.8;
}

.stButton > button {
    border: 1px solid rgba(6,182,212,.35) !important;
    border-radius: 10px !important;
    background: linear-gradient(90deg, #2563EB, #06B6D4) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    min-height: 42px !important;
    width: 100% !important;
    box-shadow: 0 8px 24px rgba(6,182,212,.12) !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 30px rgba(6,182,212,.22) !important;
}

.client-card {
    background: rgba(7,20,38,.88);
    border: 1px solid rgba(37,99,235,.34);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
    color: #FFFFFF !important;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(37,99,235,.52);
    border-radius: 18px;
    padding: 24px;
    margin-bottom: 14px;
    background:
        radial-gradient(circle at 82% 50%, rgba(6,182,212,.13), transparent 25%),
        linear-gradient(135deg, #07182D, #041021);
    color: #FFFFFF !important;
}

.hero-inner {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.brand-title {
    font-size: clamp(22px, 4vw, 40px);
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin: 0;
    color: #FFFFFF !important;
}

.brand-title span {
    color: #06B6D4;
}

.logo-container {
    width: 65px;
    height: 65px;
}

.country-card {
    display: block;
}

.ce-heading-title {
    font-size: 20px;
    font-weight: 800;
    color: #FFFFFF !important;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}

.ce-heading-sub {
    font-size: 12px;
    color: #38BDF8 !important;
    margin-bottom: 14px;
}

.ce-field-label {
    font-size: 11px;
    font-weight: 700;
    color: #38BDF8 !important;
    margin-bottom: 5px;
}

.ce-engine-box {
    background: rgba(7,20,38,.90);
    border: 1px solid rgba(37,99,235,.38);
    border-radius: 15px;
    padding: 17px;
    height: 100%;
}

.ce-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 13px;
    color: #FFFFFF !important;
    font-weight: 700;
    flex-wrap: wrap;
    gap: 8px;
}

.ce-online {
    color: #34D399 !important;
    font-size: 9px;
    background: rgba(16,185,129,.10);
    border: 1px solid rgba(16,185,129,.25);
    padding: 5px 8px;
    border-radius: 20px;
}

.ce-ai-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 8px;
}

.ce-ai {
    background: #041022;
    border: 1px solid rgba(37,99,235,.28);
    border-radius: 10px;
    padding: 10px;
    min-height: 68px;
    color: #FFFFFF !important;
}

.ce-ai-icon {
    font-size: 18px;
}

.ce-ai-name {
    font-size: 10px;
    margin-top: 4px;
    color: #FFFFFF !important;
    font-weight: 700;
}

.ce-ai-active {
    color: #34D399 !important;
    font-size: 8px;
    margin-top: 2px;
}

.ce-kpi {
    position: relative;
    overflow: hidden;
    padding: 12px;
    min-height: 85px;
    border-radius: 13px;
    background: linear-gradient(145deg,#081a31,#051225);
    border: 1px solid rgba(37,99,235,.38);
    color: #FFFFFF !important;
    margin-bottom: 8px;
}
.ce-kpi-icon { font-size: 18px; }
.ce-kpi-value { font-size: 20px; font-weight: 800; margin-top: 4px; color: #FFFFFF !important; }
.ce-kpi-name { color: #FFFFFF !important; font-size: 10px; }
.ce-kpi-growth { color: #38BDF8 !important; font-size: 8px; margin-top: 4px; }

.ce-panel {
    background: rgba(7,20,38,.90);
    border: 1px solid rgba(37,99,235,.38);
    border-radius: 15px;
    padding: 17px;
    box-shadow: 0 12px 35px rgba(0,0,0,.16);
    color: #FFFFFF !important;
    margin-bottom: 12px;
}
.ce-panel-title { font-size: 16px; font-weight: 750; color: #FFFFFF !important; }

.ce-funnel { display: flex; flex-direction: column; align-items: center; gap: 4px; margin-top: 14px; }
.ce-funnel-item { height: 27px; display: grid; place-items: center; font-size: 9px; font-weight: 700; border-radius: 5px; color: #FFFFFF !important; width: 100%; }
.ce-f1 { background: #2563eb; }
.ce-f2 { background: #0891b2; }
.ce-f3 { background: #14b8a6; }
.ce-f4 { background: #8b5cf6; }
.ce-f5 { background: #f59e0b; }
.ce-f6 { background: #ef4444; }

.ce-country { margin-top: 12px; }
.ce-country-row { display: flex; justify-content: space-between; align-items: center; font-size: 10px; margin: 10px 0; color: #FFFFFF !important; gap: 10px; }
.ce-country-track { height: 5px; margin-top: 5px; background: #17243a; border-radius: 20px; overflow: hidden; width: 100%; }
.ce-country-fill { height: 100%; border-radius: 20px; background: linear-gradient(90deg,#2563eb,#06b6d4); }

.ce-op { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,.10); font-size: 10px; color: #FFFFFF !important; gap: 10px; }
.ce-event { display: flex; gap: 10px; padding: 9px 0; border-bottom: 1px solid rgba(255,255,255,.10); color: #FFFFFF !important; }
.ce-event-dot { width: 27px; height: 27px; border-radius: 50%; display: grid; place-items: center; background: rgba(37,99,235,.16); color: #FFFFFF !important; flex-shrink: 0; }
.ce-event-text { font-size: 10px; color: #FFFFFF !important; }
.ce-event-text span { display: block; color: #38BDF8 !important; margin-top: 3px; font-size: 9px; }

/* Mobile Responsive Adjustments */
@media (max-width: 768px) {
    .hero-inner {
        flex-direction: column;
        align-items: flex-start;
    }
    .brand-title {
        font-size: 20px;
    }
    .logo-container {
        width: 50px;
        height: 50px;
    }
    .country-card {
        display: none !important;
    }
    .top-bar-container {
        flex-direction: column;
        align-items: stretch !important;
        gap: 8px;
        height: auto !important;
    }
}

footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


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


@st.cache_data(ttl=10)
def fetch_leads():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return [], "Supabase credentials are not configured."
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = client.table("leads").select("*").order("created_at", desc=True).execute()
        return result.data or [], None
    except Exception as exc:
        return [], str(exc)


def status_counts(leads):
    counts = {"new": 0, "pending": 0, "sent": 0, "completed": 0, "replied": 0, "failed": 0}
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
    candidates = [PIPELINE_FILE, "master_pipeline.py", "sdr_agent.py"]
    for name in candidates:
        path = Path(name)
        if path.exists():
            return str(path)
    return None


st.markdown('<p style="color: #FFFFFF; font-weight: 600; margin-bottom: 4px;">Navigation Menu</p>', unsafe_allow_html=True)
menu = st.selectbox(
    "Navigation Menu",
    ["Dashboard", "Find Leads", "Lead Database", "AI Outreach", "Follow-ups", "Campaigns", "Analytics", "Email Templates", "Settings"],
    label_visibility="collapsed",
)

all_leads, db_error = fetch_leads()
counts = status_counts(all_leads)
total_leads = len(all_leads)
sent_emails = counts["sent"] + counts["completed"]
pending_queue = counts["new"] + counts["pending"]
replies = counts["replied"]

# Top bar
st.markdown(
    """
    <div class="top-bar-container" style="display:flex; align-items:center; justify-content:space-between; margin:0 0 10px; padding:0 4px; flex-wrap:wrap; gap:10px;">
        <div style="color:#38BDF8; font-size:12px; letter-spacing:.2px;">Find. Engage. Convert. Grow.</div>
        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:8px; border:1px solid rgba(37,99,235,.45); border-radius:9px; background:#061225; color:#FFFFFF; padding:6px 12px; font-size:11px;"><span>Search leads...</span><span style="color:#38BDF8;">⌘K</span></div>
            <div style="display:flex; align-items:center; gap:8px; font-size:11px; color:#FFFFFF;"><div style="width:34px; height:34px; border-radius:50%; display:grid; place-items:center; background:linear-gradient(135deg,#0ea5e9,#2563eb); color:#FFFFFF; font-size:12px; font-weight:800;">SA</div><div><strong>Shafqat Abbas</strong><small style="display:block; color:#38BDF8; font-size:9px;">Founder</small></div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Hero
st.markdown(
    f"""
    <div class="hero">
      <div class="hero-inner">
        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
          <div class="logo-container" style="display:grid; place-items:center; border-radius:14px; flex-shrink:0; background:linear-gradient(145deg,rgba(37,99,235,.16),rgba(6,182,212,.08)); border:1px solid rgba(6,182,212,.45); box-shadow:0 0 28px rgba(6,182,212,.20);">{logo_svg(54)}</div>
          <div>
            <div class="brand-title">ClientEngine <span>AI</span></div>
            <div style="color:#38BDF8; font-size:14px; margin-top:4px;">AI-Powered Lead Generation &amp; Outreach Platform</div>
          </div>
        </div>
        <div class="country-card" style="padding:12px 16px; border:1px solid rgba(37,99,235,.38); border-radius:14px; background:rgba(3,13,28,.72);">
          <div style="font-size:12px; font-weight:700; margin-bottom:6px; color:#FFFFFF;">Global Coverage</div>
          <div style="font-size:18px; letter-spacing:4px;">🇺🇸 🇬🇧 🇨🇦 🇩🇪</div>
          <small style="color:#38BDF8; display:block; margin-top:4px;">4 Countries Active</small>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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

    top_col1, top_col2 = st.columns([3.2, 1], gap="small")

    with top_col1:
        st.markdown('<div class="ce-heading-title">Find Your Next Customers</div>', unsafe_allow_html=True)
        st.markdown('<div class="ce-heading-sub">Tell us your industry and location, and let AI find &amp; analyze potential clients.</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 1.05], gap="small")
        with c1:
            st.markdown('<div class="ce-field-label">Industry / Niche</div>', unsafe_allow_html=True)
            industry_default = industries.index(url_niche) if url_niche in industries else 0
            selected_industry = st.selectbox("Industry / Niche", industries, index=industry_default, label_visibility="collapsed")
            if selected_industry == "Custom Industry...":
                final_niche = st.text_input("Custom industry", value="" if url_niche in industries else url_niche, placeholder="e.g. commercial cleaning")
            else:
                final_niche = selected_industry
        with c2:
            st.markdown('<div class="ce-field-label">Location / Country</div>', unsafe_allow_html=True)
            country_default = countries.index(url_location) if url_location in countries else 0
            selected_country = st.selectbox("Location / Country", countries, index=country_default, label_visibility="collapsed")
            if selected_country == "Custom Location...":
                final_location = st.text_input("Custom location", value="" if url_location in countries else url_location, placeholder="e.g. Dallas, Texas")
            elif selected_country == "Worldwide / Global":
                final_location = "Global"
            else:
                final_location = selected_country
        with c3:
            st.markdown('<div style="height:22px"></div>', unsafe_allow_html=True)
            run_pipeline = st.button("Find Potential Customers", use_container_width=True, type="primary")
            refresh = st.button("Refresh Database", use_container_width=True)

        clean_niche = clean_target(final_niche)
        clean_location = clean_target(final_location)
        st.markdown(
            '<div style="display:flex; flex-wrap:wrap; gap:7px; margin-top:10px;">'
            '<span style="border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#34D399; padding:5px 8px; border-radius:20px; font-size:9px;">Auto Search</span>'
            '<span style="border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#34D399; padding:5px 8px; border-radius:20px; font-size:9px;">Verify Emails</span>'
            '<span style="border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#34D399; padding:5px 8px; border-radius:20px; font-size:9px;">Analyze Websites</span>'
            '<span style="border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#34D399; padding:5px 8px; border-radius:20px; font-size:9px;">Score Leads</span>'
            '<span style="border:1px solid rgba(16,185,129,.18); background:rgba(16,185,129,.08); color:#34D399; padding:5px 8px; border-radius:20px; font-size:9px;">Generate Emails</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    with top_col2:
        st.markdown(
            f"""
            <div class="ce-engine-box">
                <div class="ce-status"><span>AI Engine Status</span><span class="ce-online">All Systems Online</span></div>
                <div class="ce-ai-grid">
                  <div class="ce-ai"><div class="ce-ai-icon">🌐</div><div class="ce-ai-name">Web Scraping</div><div class="ce-ai-active">{'Active' if (MODAL_TOKEN_ID or MODAL_TOKEN_SECRET) else 'Offline'}</div></div>
                  <div class="ce-ai"><div class="ce-ai-icon">🧠</div><div class="ce-ai-name">AI Analysis</div><div class="ce-ai-active">{'Active' if get_secret("OPENAI_API_KEY") else 'Offline'}</div></div>
                  <div class="ce-ai"><div class="ce-ai-icon">✉</div><div class="ce-ai-name">Email Generation</div><div class="ce-ai-active">{'Active' if get_secret("OPENAI_API_KEY") else 'Offline'}</div></div>
                  <div class="ce-ai"><div class="ce-ai-icon">▥</div><div class="ce-ai-name">Lead Scoring</div><div class="ce-ai-active">Active</div></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    # Metrics display: Desktop pe 5 columns (ek row), Mobile pe 3 and 2 rows
    custom_kpi_data = [
        ("👥", 245, "Leads Found", "Live database"),
        ("✓", 195, "Verified Leads", "Email detected"),
        ("✉", 145, "Email Ready", "Queue"),
        ("➤", 95, "Email Send", "Outreach"),
        ("●", 65, "Reply", "Responses"),
    ]
    
    # Desktop View (5 columns in 1 row)
    desktop_cols = st.columns(5, gap="small")
    for idx, (icon, value, name, growth) in enumerate(custom_kpi_data):
        with desktop_cols[idx]:
            st.markdown(
                f'<div class="desktop-kpi" style="display: block;"><div class="ce-kpi"><div class="ce-kpi-icon">{icon}</div><div class="ce-kpi-value">{value}</div><div class="ce-kpi-name">{name}</div><div class="ce-kpi-growth">{growth}</div></div></div>',
                unsafe_allow_html=True,
            )

    if run_pipeline:
        st.markdown('<div id="execution-logs"></div>', unsafe_allow_html=True)
        if not clean_niche or not clean_location:
            st.error("Please enter both an industry and a location.")
        else:
            pipeline = find_pipeline_file()
            st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
            st.markdown("### Live Cloud Execution")
            
            st.markdown("""
                <script>
                    const element = document.getElementById('execution-logs');
                    if (element) {
                        element.scrollIntoView({ behavior: 'smooth' });
                    }
                </script>
            """, unsafe_allow_html=True)

            if not pipeline:
                st.error("No pipeline file was found.")
            else:
                status_box = st.empty()
                status_box.info(f"Running {Path(pipeline).name} for {clean_niche} -> {clean_location}")
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
                    status_box.error("Modal CLI was not found.")
                except Exception as exc:
                    status_box.error(f"Execution error: {exc}")
            st.markdown('</div>', unsafe_allow_html=True)

    a1, a2, a3 = st.columns([1.05, 1, 1], gap="small")
    
    with a1:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Lead Generation Pipeline</div>', unsafe_allow_html=True)
        funnel = [
            ("Found", "245", "ce-f1", "92%"),
            ("Verified", "195", "ce-f2", "78%"),
            ("Qualified", "145", "ce-f3", "65%"),
            ("Contacted", "95", "ce-f4", "52%"),
            ("Replied", "65", "ce-f5", "38%"),
            ("Meetings", "12", "ce-f6", "25%"),
        ]
        st.markdown('<div class="ce-funnel">' + ''.join(f'<div class="ce-funnel-item {cls}" style="width: {width};">{name} — {value}</div>' for name, value, cls, width in funnel) + '</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Country Distribution</div>', unsafe_allow_html=True)
        top_countries_mock = [("United States", 120), ("United Kingdom", 65), ("Canada", 40), ("Germany", 20)]
        total_for_pct = max(sum([v for _, v in top_countries_mock]), 1)
        html = '<div class="ce-country">'
        for country, n in top_countries_mock:
            pct = round((n / total_for_pct) * 100)
            flag = {"United States":"US","United Kingdom":"UK","Canada":"CA","Germany":"DE"}.get(country, "INT")
            html += f'<div class="ce-country-row"><div style="width:76%;">[{flag}] {country}<div class="ce-country-track"><div class="ce-country-fill" style="width:{pct}%;"></div></div></div><strong>{n} ({pct}%)</strong></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with a3:
        st.markdown('<div class="ce-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Top Opportunities</div>', unsafe_allow_html=True)
        top_opps_mock = [
            ("No/weak Google presence", "45 leads"),
            ("Weak Website / CTA", "38 leads"),
            ("Poor SEO signals", "30 leads"),
            ("Missing contact path", "22 leads"),
            ("Social media opportunity", "15 leads"),
        ]
        for name, count_str in top_opps_mock:
            st.markdown(f'<div class="ce-op"><span>{name}</span><span>{count_str}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    act, qa = st.columns([2.1, 1], gap="small")
    with act:
        st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Recent Activity <span style="float:right;color:#34D399;font-size:9px;">Live</span></div>', unsafe_allow_html=True)
        recent = all_leads[:5]
        if recent:
            icons = ["+", "V", "*", ">", "o"]
            labels = ["New lead added", "Lead verified", "AI analysis update", "Outreach ready", "Reply update"]
            for i, row in enumerate(recent):
                company = safe_text(row.get("company_name"), "Lead")
                email = safe_text(row.get("email"), "No email")
                st.markdown(f'<div class="ce-event"><div class="ce-event-dot">{icons[i % len(icons)]}</div><div class="ce-event-text"><b>{labels[i % len(labels)]}</b><span>{company} · {email}</span></div></div>', unsafe_allow_html=True)
        else:
            mock_activities = [
                ("New lead added", "Apex Roofing · contact@apexroofing.com"),
                ("Lead verified", "Metro Dental · info@metrodental.co"),
                ("Outreach ready", "Elite Builders · sales@elitebuilders.us"),
            ]
            icons = ["+", "V", "*"]
            for i, (label, detail) in enumerate(mock_activities):
                st.markdown(f'<div class="ce-event"><div class="ce-event-dot">{icons[i]}</div><div class="ce-event-text"><b>{label}</b><span>{detail}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with qa:
        st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
        st.markdown('<div class="ce-panel-title">Quick Actions</div>', unsafe_allow_html=True)
        st.markdown('<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px;">', unsafe_allow_html=True)
        st.markdown('<div style="padding:14px 8px;border:1px solid rgba(139,92,246,.45);border-radius:10px;text-align:center;background:rgba(139,92,246,.08); color:#FFFFFF;">+<br><small>New Campaign</small></div>', unsafe_allow_html=True)
        st.markdown('<div style="padding:14px 8px;border:1px solid rgba(37,99,235,.45);border-radius:10px;text-align:center;background:rgba(37,99,235,.08); color:#FFFFFF;">v<br><small>Export Leads</small></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ce-panel" style="margin-top:12px;">', unsafe_allow_html=True)
    st.markdown('<div class="ce-panel-title">Recent High-Value Leads <span style="float:right;color:#38BDF8;font-size:10px;">View All</span></div>', unsafe_allow_html=True)
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
            rows.append({"Company": company, "Location": country, "Email": email or "—", "AI Score": f"{score}/100", "Opportunity": "Website / lead review", "Status": status_label, "Website": website})
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No leads found yet. Launch a campaign above.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Lead Database":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Lead Database")
    st.caption("Live records loaded from Supabase.")
    search = st.text_input("Search", placeholder="Company, email, country, industry...")
    filtered = all_leads
    if search:
        needle = search.lower().strip()
        filtered = [
            row for row in all_leads
            if needle in " ".join([
                safe_text(row.get("company_name"), ""),
                safe_text(row.get("email"), ""),
                safe_text(row.get("country"), ""),
                safe_text(row.get("industry"), ""),
                safe_text(row.get("status"), ""),
                safe_text(row.get("website"), "")
            ]).lower()
        ]
    st.write(f"Showing **{len(filtered)}** records.")
    if filtered:
        table = [{
            "Company": safe_text(r.get("company_name")),
            "Email": safe_text(r.get("email")),
            "Industry": safe_text(r.get("industry")),
            "Country": safe_text(r.get("country")),
            "Status": safe_text(r.get("status")),
            "Website": safe_text(r.get("website")),
        } for r in filtered]
        st.dataframe(table, use_container_width=True, hide_index=True)
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=table[0].keys())
        writer.writeheader()
        writer.writerows(table)
        st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="clientengine_leads.csv", mime="text/csv")
    else:
        st.info("No matching leads.")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "AI Outreach":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### AI Outreach Workspace")
    st.caption("Generate personalized outreach from stored lead info.")
    if not all_leads:
        st.info("Add leads first from Find Leads.")
    else:
        options = [f"{i}: {safe_text(row.get('company_name'))} — {safe_text(row.get('email'))}" for i, row in enumerate(all_leads[:200])]
        selected = st.selectbox("Lead", options)
        index = int(selected.split(":", 1)[0])
        lead = all_leads[index]
        st.markdown(f"**Company:** {safe_text(lead.get('company_name'))}  \n**Email:** {safe_text(lead.get('email'))}")
        service = st.text_input("Offer / service", value="Google Ads, Meta Ads, Social Media Management and Local SEO")
        problem = st.text_area("Known problem / observation", placeholder="Example: weak Google visibility, slow website...")
        if st.button("Generate Outreach Draft", use_container_width=True):
            company = safe_text(lead.get("company_name"), "your company")
            subject = f"Ideas to help {company} generate more qualified leads"
            body = f"Hi {company} team,\n\nI came across your business and noticed opportunities to improve your online lead generation.\n\nBest,\nRai Marketing Agency"
            st.success("Draft generated.")
            st.code(f"Subject: {subject}\n\n{body}", language="text")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Follow-ups":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Follow-ups")
    followups = [r for r in all_leads if str(r.get("status", "")).lower() in {"sent", "contacted", "follow-up"}]
    if followups:
        st.dataframe([{"Company": safe_text(r.get("company_name")), "Email": safe_text(r.get("email")), "Status": safe_text(r.get("status"))} for r in followups], use_container_width=True, hide_index=True)
    else:
        st.info("No follow-up records currently marked.")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Campaigns":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Campaigns")
    st.text_input("Campaign name", placeholder="USA Roofing — August")
    if st.button("Save Campaign Plan", use_container_width=True):
        st.success("Campaign plan prepared.")
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Analytics":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Leads", total_leads)
    c2.metric("Ready / Pending", pending_queue)
    c3.metric("Sent / Completed", sent_emails)
    c4.metric("Replies", replies)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Email Templates":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Email Templates")
    st.selectbox("Template", ["First outreach", "Follow-up #1", "Follow-up #2", "Audit offer"])
    st.text_input("Subject", value="Quick idea for improving your lead generation")
    st.text_area("Body", value="Hi {{company_name}},\n\nI came across your business...\n\nBest,\nRai Marketing Agency", height=200)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Settings":
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Settings")
    st.code(f"Pipeline file: {PIPELINE_FILE}\nDetected file: {find_pipeline_file() or 'None'}", language="text")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align:center;color:#38BDF8;font-size:9px;padding:20px 0 4px;">
        ClientEngine AI · Rai Marketing Agency · Find. Analyze. Engage. Grow.
    </div>
    """,
    unsafe_allow_html=True,
)
