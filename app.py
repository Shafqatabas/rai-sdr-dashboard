import streamlit as st
import subprocess
import sys
import os
import re
from supabase import create_client

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if "MODAL_TOKEN_ID" in st.secrets:
    os.environ["MODAL_TOKEN_ID"] = st.secrets["MODAL_TOKEN_ID"]
if "MODAL_TOKEN_SECRET" in st.secrets:
    os.environ["MODAL_TOKEN_SECRET"] = st.secrets["MODAL_TOKEN_SECRET"]

st.set_page_config(
    page_title="ClientEngine AI — AI Sales Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --bg: #020617;
    --panel: #071426;
    --border: rgba(37, 99, 235, .35);
    --blue: #2563eb;
    --cyan: #06b6d4;
    --green: #10b981;
    --text: #f8fafc;
    --muted: #94a3b8;
}

.stApp {
    font-family: "Inter", sans-serif;
    background: 
        radial-gradient(circle at 70% 10%, rgba(6,182,212,.10), transparent 25%),
        radial-gradient(circle at 20% 80%, rgba(37,99,235,.08), transparent 25%),
        var(--bg);
    color: var(--text);
    min-height: 100vh;
}

/* EXACT SIDEBAR STYLING MATCHING DEMO */
[data-testid="stSidebar"] {
    background: rgba(3, 13, 28, .94) !important;
    border-right: 1px solid rgba(37,99,235,.25);
    padding: 16px 12px;
}

.logo-box {
    height: 75px;
    border: 1px solid rgba(6,182,212,.35);
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    margin-bottom: 18px;
    background: linear-gradient(135deg, rgba(37,99,235,.15), rgba(6,182,212,.05));
}

.logo-icon {
    width: 42px;
    height: 42px;
    border: 2px solid var(--cyan);
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 22px;
    color: #38bdf8;
    box-shadow: 0 0 15px rgba(6,182,212,.35);
}

.logo-text {
    font-size: 15px;
    font-weight: 800;
    color: white;
}

.logo-text span {
    color: var(--cyan);
}

/* SIDEBAR NAVIGATION BUTTONS OVERRIDE */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    color: #94a3b8 !important;
    padding: 10px 12px !important;
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease;
    width: 100%;
    display: flex;
    align-items: center;
}

[data-testid="stSidebar"] .stRadio label:hover {
    color: white !important;
    background: rgba(37,99,235,0.15) !important;
}

/* ENGINE STATUS BOX */
.engine-box {
    margin-top: 18px;
    padding: 14px;
    border: 1px solid rgba(37,99,235,.3);
    border-radius: 14px;
    background: rgba(7,20,38,.85);
}

.engine-title {
    font-size: 10px;
    color: #64748b;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 700;
}

.engine-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0;
    font-size: 11px;
    color: #f8fafc;
}

.online {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 8px #10b981;
}

/* AGENCY CARD BOX */
.agency-box {
    margin-top: 15px;
    border: 1px solid rgba(37,99,235,.35);
    border-radius: 14px;
    padding: 14px;
    text-align: center;
    background: rgba(7,20,38,.6);
}

.agency-name {
    font-weight: 700;
    font-size: 11px;
    color: white;
}

.agency-sub {
    color: var(--muted);
    font-size: 9px;
    margin-top: 2px;
}

.version-text {
    text-align: center;
    color: #64748b;
    font-size: 9px;
    margin-top: 10px;
}

/* TOPBAR */
.topbar {
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.top-left {
    color: #38bdf8;
    font-size: 12px;
}

/* PANELS & CARDS */
.panel {
    background: rgba(7,20,38,.85);
    border: 1px solid rgba(37,99,235,.4);
    border-radius: 15px;
    padding: 18px;
    margin-bottom: 15px;
}

.panel-title {
    font-size: 17px;
    font-weight: 700;
    color: white;
}

.panel-sub {
    color: #64748b;
    font-size: 11px;
    margin-top: 5px;
}

/* INPUTS & BUTTONS */
.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background-color: #041022 !important;
    color: white !important;
    border: 1px solid rgba(37,99,235,.35) !important;
    border-radius: 9px !important;
}

.stButton>button {
    background: linear-gradient(90deg,#2563eb,#06b6d4) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: 0 !important;
    width: 100% !important;
    padding: 11px !important;
    box-shadow: 0 4px 15px rgba(6,182,212,0.25) !important;
}

/* KPIS */
.kpis {
    display: grid;
    grid-template-columns: repeat(5,1fr);
    gap: 12px;
    margin-top: 13px;
    margin-bottom: 15px;
}

.kpi {
    padding: 16px;
    border-radius: 13px;
    background: linear-gradient(145deg,#081a31,#051225);
    border: 1px solid rgba(37,99,235,.4);
}

.kpi-value {
    font-size: 23px;
    font-weight: 800;
    margin-top: 9px;
    color: white;
}

.kpi-name {
    color: #94a3b8;
    font-size: 10px;
}

.growth {
    color: #10b981;
    font-size: 9px;
    margin-top: 7px;
    font-weight: 600;
}

/* PIPELINE FUNNEL */
.funnel {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 15px;
}

.funnel-item {
    height: 28px;
    display: grid;
    place-items: center;
    font-size: 10px;
    font-weight: 600;
    border-radius: 5px;
    color: white;
}

.f1 { width: 90%; background:#2563eb; }
.f2 { width: 75%; background:#0891b2; }
.f3 { width: 60%; background:#14b8a6; }
.f4 { width: 45%; background:#8b5cf6; }
.f5 { width: 30%; background:#f59e0b; }
.f6 { width: 18%; background:#ef4444; }

/* OPPORTUNITIES & COUNTRIES */
.opportunity {
    padding: 11px 0;
    border-bottom: 1px solid rgba(148,163,184,.1);
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: white;
}
.opportunity:last-child { border-bottom: 0; }

.score { color: #10b981; font-weight: 600; }

.country {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 13px 0;
    font-size: 11px;
    color: white;
}

.country-bar {
    height: 5px;
    background: #17243a;
    border-radius: 20px;
    margin-top: 5px;
}

.country-progress {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg,#2563eb,#06b6d4);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=5)
def fetch_leads():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []

all_leads = fetch_leads()
total_leads = len(all_leads) if all_leads else 247
sent_emails = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["sent", "completed"]) if all_leads else 94

# --- EXACT SIDEBAR FROM DEMO ---
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">ClientEngine <span>AI</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_menu = st.radio(
        "Navigation",
        [
            "⌂  Dashboard", 
            "⌕  Find Leads", 
            "▤  Lead Database", 
            "➤  AI Outreach", 
            "◴  Follow-ups", 
            "▥  Campaigns", 
            "◔  Analytics", 
            "✉  Email Templates", 
            "⚙  Settings"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("""
    <div class="engine-box">
        <div class="engine-title">AI Engine Status</div>
        <div class="engine-item"><span class="online"></span>OpenAI GPT-4o</div>
        <div class="engine-item"><span class="online"></span>Modal</div>
        <div class="engine-item"><span class="online"></span>Supabase</div>
        <div class="engine-item"><span class="online"></span>SMTP / Resend</div>
    </div>
    
    <div class="agency-box">
        <div class="agency-name">Rai Marketing Agency</div>
        <div class="agency-sub">Digital Growth Solutions</div>
    </div>
    
    <div class="version-text">v1.0.0</div>
    """, unsafe_allow_html=True)

# --- TOPBAR ---
clean_menu = selected_menu.split("  ")[-1].strip()

st.markdown("""
<div class="topbar">
    <div class="top-left">✦ &nbsp; Find. Engage. Convert. Grow.</div>
    <div class="right-user" style="font-size:11px; color:#94a3b8;">
        <b style="color:white;">Shafqat Abbas</b> &nbsp;|&nbsp; Founder
    </div>
</div>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
st.markdown("""
<section style="min-height: 150px; border: 1px solid rgba(37,99,235,.55); border-radius: 16px; background: radial-gradient(circle at 75% 50%, rgba(6,182,212,.13), transparent 25%), linear-gradient(135deg,#07182d,#041021); display: flex; align-items: center; justify-content: space-between; padding: 25px 32px; margin-bottom: 15px;">
    <div>
        <h1 style="font-size: 38px; font-weight: 800; letter-spacing: -1.5px; color: white;">ClientEngine <span style="color: #06b6d4;">AI</span></h1>
        <p style="margin-top: 6px; color: #38bdf8; font-size: 14px;">AI-Powered Lead Generation & Outreach Platform</p>
    </div>
    <div style="border: 1px solid rgba(37,99,235,.35); background: rgba(3,13,28,.72); border-radius: 14px; padding: 15px 22px; min-width: 200px;">
        <div style="font-weight: 700; margin-bottom: 8px; color: white; font-size: 12px;">🌐 Global Coverage</div>
        <div style="font-size: 20px; display: flex; gap: 10px;">🇺🇸 🇬🇧 🇨🇦 🇩🇪</div>
        <small style="display: block; color: #94a3b8; margin-top: 8px; font-size: 10px;">4 Countries Active</small>
    </div>
</section>
""", unsafe_allow_html=True)

# --- VIEW ROUTING ---
if clean_menu in ["Dashboard", "Find Leads"]:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Find Your Next Customers</div>
        <div class="panel-sub">Tell us your industry and location, and let AI find & analyze potential clients.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns([1, 1, 0.7])
    with col_f1:
        industry = st.selectbox("INDUSTRY / NICHE", [
            "Roofing Contractors", "HVAC Companies", "Dental Clinics", 
            "Real Estate", "Law Firms", "Construction Companies", "Restaurants", "E-commerce"
        ])
    with col_f2:
        country = st.selectbox("LOCATION / COUNTRY", [
            "United States (USA)", "United Kingdom (UK)", "Canada", "Germany"
        ])
    with col_f3:
        st.write("")
        st.write("")
        run_search = st.button("🔍 Find Potential Customers →")

    clean_niche = re.sub(r'[^a-zA-Z0-9\s]', '', industry).strip()
    clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', country).strip()

    if run_search:
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.info(f"Triggering pipeline for **{clean_niche}** in **{clean_location}** (Preview Mode)...")
        else:
            env = os.environ.copy()
            command = [sys.executable, "-m", "modal", "run", "master_pipeline.py", "--niche", clean_niche, "--location", clean_location]
            try:
                subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
                st.success("Autonomous search pipeline started successfully!")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Execution notice: {e}")

    # KPIS
    st.markdown(f"""
    <div class="kpis">
        <div class="kpi">
            <div class="kpi-value">{total_leads}</div>
            <div class="kpi-name">Leads Found</div>
            <div class="growth">↗ +12%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">183</div>
            <div class="kpi-name">Verified Leads</div>
            <div class="growth">↗ +8%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">126</div>
            <div class="kpi-name">Emails Ready</div>
            <div class="growth">↗ +15%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">{sent_emails}</div>
            <div class="kpi-name">Emails Sent</div>
            <div class="growth">↗ +12%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">17</div>
            <div class="kpi-name">Replies</div>
            <div class="growth">↗ +6%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Analytics Grid
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("""
        <div class="panel" style="height: 100%;">
            <div class="panel-title">Lead Generation Pipeline</div>
            <div class="funnel">
                <div class="funnel-item f1">Found — 247</div>
                <div class="funnel-item f2">Verified — 183</div>
                <div class="funnel-item f3">Qualified — 152</div>
                <div class="funnel-item f4">Contacted — 94</div>
                <div class="funnel-item f5">Replied — 17</div>
                <div class="funnel-item f6">Meetings — 5</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown("""
        <div class="panel" style="height: 100%;">
            <div class="panel-title">Country Distribution</div>
            <div style="margin-top: 15px;">
                <div class="country"><span>🇺🇸 USA</span><strong>35%</strong></div>
                <div class="country-bar"><div class="country-progress" style="width:35%;"></div></div>
                
                <div class="country" style="margin-top:12px;"><span>🇬🇧 UK</span><strong>25%</strong></div>
                <div class="country-bar"><div class="country-progress" style="width:25%;"></div></div>
                
                <div class="country" style="margin-top:12px;"><span>🇨🇦 Canada</span><strong>22%</strong></div>
                <div class="country-bar"><div class="country-progress" style="width:22%;"></div></div>
                
                <div class="country" style="margin-top:12px;"><span>🇩🇪 Germany</span><strong>18%</strong></div>
                <div class="country-bar"><div class="country-progress" style="width:18%;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_d3:
        st.markdown("""
        <div class="panel" style="height: 100%;">
            <div class="panel-title">Top Opportunities</div>
            <div style="margin-top: 10px;">
                <div class="opportunity"><span>Weak Google Ads</span><span class="score">72 leads →</span></div>
                <div class="opportunity"><span>No Lead Form</span><span class="score">58 leads →</span></div>
                <div class="opportunity"><span>Poor SEO</span><span class="score">49 leads →</span></div>
                <div class="opportunity"><span>Slow Website</span><span class="score">41 leads →</span></div>
                <div class="opportunity"><span>No Social Media</span><span class="score">37 leads →</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Leads Table
    st.markdown('<div class="panel"><div class="panel-title" style="margin-bottom: 12px;">Recent High-Value Leads</div>', unsafe_allow_html=True)
    table_data = [
        {"COMPANY": "ABC Roofing Solutions", "LOCATION": "🇺🇸 Dallas, TX", "EMAIL": "john@abcroofing.com", "AI SCORE": "91/100", "OPPORTUNITY": "No Google Ads", "STATUS": "Ready"},
        {"COMPANY": "XYZ Contractors", "LOCATION": "🇬🇧 London", "EMAIL": "mike@xyzroofers.co.uk", "AI SCORE": "87/100", "OPPORTUNITY": "Weak Website CTA", "STATUS": "Ready"},
        {"COMPANY": "Smith Roofing", "LOCATION": "🇨🇦 Toronto", "EMAIL": "info@smithroofing.ca", "AI SCORE": "82/100", "OPPORTUNITY": "Poor SEO", "STATUS": "Follow-up"},
        {"COMPANY": "Dachbau Berlin", "LOCATION": "🇩🇪 Berlin", "EMAIL": "kontakt@dachbau.de", "AI SCORE": "79/100", "OPPORTUNITY": "No Lead Form", "STATUS": "Draft"}
    ]
    st.dataframe(table_data, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif clean_menu == "Lead Database":
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Complete Lead Database</div>
        <div class="panel-sub">All enterprise prospects synced securely from Supabase storage.</div>
    </div>
    """, unsafe_allow_html=True)
    if all_leads:
        st.dataframe(all_leads, use_container_width=True, hide_index=True)
    else:
        st.info("Database storage is currently empty.")

else:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-title">{clean_menu} Module</div>
        <div class="panel-sub">ClientEngine AI automation module running under Rai Marketing infrastructure.</div>
    </div>
    """, unsafe_allow_html=True)
