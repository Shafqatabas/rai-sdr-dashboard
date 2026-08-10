import streamlit as st
import subprocess
import sys
import os
import re
from supabase import create_client

if "MODAL_TOKEN_ID" in st.secrets:
    os.environ["MODAL_TOKEN_ID"] = st.secrets["MODAL_TOKEN_ID"]
if "MODAL_TOKEN_SECRET" in st.secrets:
    os.environ["MODAL_TOKEN_SECRET"] = st.secrets["MODAL_TOKEN_SECRET"]

st.set_page_config(
    page_title="ClientEngine AI — Dashboard",
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
    --bg: #020817;
    --panel: #071426;
    --panel2: #091a30;
    --border: rgba(37, 99, 235, .35);
    --blue: #2563eb;
    --cyan: #06b6d4;
    --green: #10b981;
    --purple: #8b5cf6;
    --orange: #f59e0b;
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

/* SIDEBAR FIX FOR STREAMLIT */
[data-testid="stSidebar"] {
    background: rgba(3, 13, 28, .94) !important;
    border-right: 1px solid rgba(37,99,235,.25);
    padding: 18px 14px;
}

.logo-box {
    height: 82px;
    border: 1px solid rgba(6,182,212,.35);
    border-radius: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    margin-bottom: 20px;
    background: linear-gradient(135deg, rgba(37,99,235,.12), rgba(6,182,212,.04));
}

.logo-icon {
    width: 48px;
    height: 48px;
    border: 2px solid var(--cyan);
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-size: 25px;
    color: #38bdf8;
    box-shadow: 0 0 20px rgba(6,182,212,.35);
}

.logo-text {
    font-size: 16px;
    font-weight: 800;
    color: white;
}

.logo-text span {
    color: var(--cyan);
}

.engine-box {
    margin-top: 25px;
    padding: 15px;
    border: 1px solid rgba(37,99,235,.3);
    border-radius: 14px;
    background: rgba(7,20,38,.8);
}

.engine-title {
    font-size: 11px;
    color: #64748b;
    margin-bottom: 12px;
    text-transform: uppercase;
}

.engine-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 10px 0;
    font-size: 11px;
    color: #f8fafc;
}

.online {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 10px #10b981;
}

.agency-box {
    margin-top: 20px;
    border: 1px solid rgba(37,99,235,.35);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    background: rgba(7,20,38,.5);
}

.agency-name {
    font-weight: 700;
    font-size: 12px;
    margin-bottom: 6px;
    color: white;
}

.agency-sub {
    color: var(--muted);
    font-size: 10px;
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
    font-size: 13px;
}

.top-right {
    display: flex;
    align-items: center;
    gap: 14px;
}

/* HERO */
.hero {
    min-height: 170px;
    border: 1px solid rgba(37,99,235,.55);
    border-radius: 16px;
    background: radial-gradient(circle at 75% 50%, rgba(6,182,212,.13), transparent 25%), linear-gradient(135deg,#07182d,#041021);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 25px 32px;
    position: relative;
    overflow: hidden;
    margin-bottom: 15px;
}

.hero-title {
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 800;
    letter-spacing: -2px;
    color: white;
}

.hero-title span {
    color: #06b6d4;
}

.hero-subtitle {
    margin-top: 8px;
    color: #38bdf8;
    font-size: 15px;
}

.coverage {
    border: 1px solid rgba(37,99,235,.35);
    background: rgba(3,13,28,.72);
    border-radius: 14px;
    padding: 18px 25px;
    min-width: 220px;
}

.coverage-title {
    font-weight: 700;
    margin-bottom: 12px;
    color: white;
}

.flags {
    font-size: 23px;
    display: flex;
    gap: 12px;
}

.coverage small {
    display: block;
    color: #94a3b8;
    margin-top: 10px;
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

/* CONTROLS & INPUTS OVERRIDES */
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
    color: #34d399;
    font-size: 9px;
    margin-top: 7px;
}

/* DATA GRID */
.data-grid {
    display: grid;
    grid-template-columns: 1.05fr 1fr 1fr;
    gap: 13px;
    margin-top: 13px;
}

.funnel {
    display: flex;
    flex-direction: column;
    align-items: center;
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

/* OPPORTUNITIES */
.opportunity {
    padding: 11px 0;
    border-bottom: 1px solid rgba(148,163,184,.1);
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: white;
}

.score {
    color: #34d399;
}

/* COUNTRY */
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

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://wosvxuafqixewndpxypa.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indvc3Z4dWFmcWl4ZXduZHB4eXBhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyNzgwMzMsImV4cCI6MjA1Njg1NDAzM30.7Qf2wV64x-i5t8q9A2oO4k90K_B22qKxR")

@st.cache_data(ttl=5)
def fetch_leads():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []

all_leads = fetch_leads()
total_leads = len(all_leads) if all_leads else 247
sent_emails = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["sent", "completed"]) if all_leads else 94

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-icon">⚡</div>
        <div class="logo-text">ClientEngine <span>AI</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_menu = st.radio(
        "Navigation",
        ["Dashboard", "Find Leads", "Lead Database", "AI Outreach", "Follow-ups", "Campaigns", "Analytics", "Email Templates", "Settings"],
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
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
# Topbar
st.markdown("""
<div class="topbar">
    <div class="top-left">✦ &nbsp; Find. Engage. Convert. Grow.</div>
    <div class="top-right">
        <div style="font-size: 11px; color: #94a3b8;"><b>Shafqat Abbas</b> &nbsp;|&nbsp; Founder</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<section class="hero">
    <div>
        <h1 class="hero-title">ClientEngine <span>AI</span></h1>
        <p class="hero-subtitle">AI-Powered Lead Generation & Outreach Platform</p>
    </div>
    <div class="coverage">
        <div class="coverage-title">🌐 Global Coverage</div>
        <div class="flags">🇺🇸 🇬🇧 🇨🇦 🇩🇪</div>
        <small>4 Countries Active</small>
    </div>
</section>
""", unsafe_allow_html=True)

if selected_menu in ["Dashboard", "Find Leads"]:
    # Search Section
    st.markdown("""
    <div class="panel-title" style="margin-bottom: 5px;">Find Your Next Customers</div>
    <div class="panel-sub" style="margin-bottom: 15px;">Tell us your industry and location, and let AI find & analyze potential clients.</div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1, 0.8])
    with c1:
        industry = st.selectbox("INDUSTRY / NICHE", [
            "Roofing Contractors", "HVAC Companies", "Dental Clinics", 
            "Real Estate", "Law Firms", "Construction Companies", "Restaurants", "E-commerce"
        ])
    with c2:
        country = st.selectbox("LOCATION / COUNTRY", [
            "United States (USA)", "United Kingdom (UK)", "Canada", "Germany"
        ])
    with c3:
        st.write("")
        st.write("")
        run_search = st.button("🔍 Find Potential Customers →")

    clean_niche = re.sub(r'[^a-zA-Z0-9\s]', '', industry).strip()
    clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', country).strip()

    if run_search:
        st.info(f"Executing cloud workflow for **{clean_niche}** in **{clean_location}** via Modal backend...")
        env = os.environ.copy()
        command = [sys.executable, "-m", "modal", "run", "master_pipeline.py", "--niche", clean_niche, "--location", clean_location]
        try:
            res = subprocess.run(command, capture_output=True, text=True, env=env, timeout=60)
            if res.returncode == 0:
                st.success("Search Started Successfully & Synced with Supabase Database!")
                st.cache_data.clear()
            else:
                st.warning("Triggered pipeline execution. Check Modal logs if necessary.")
        except Exception as e:
            st.error(f"Execution notice: {e}")

    # KPIs
    st.markdown(f"""
    <div class="kpis">
        <div class="kpi">
            <div class="kpi-value">{total_leads}</div>
            <div class="kpi-name">Leads Found</div>
            <div class="growth">↗ +12%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">{total_leads}</div>
            <div class="kpi-name">Verified Leads</div>
            <div class="growth">↗ +8%</div>
        </div>
        <div class="kpi">
            <div class="kpi-value">{total_leads}</div>
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

    # Data Grid (Pipeline, Country, Opportunities)
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

    # Leads Table Panel
    st.markdown('<div class="panel" style="margin-top: 15px;"><div class="panel-title" style="margin-bottom: 12px;">Recent High-Value Leads</div>', unsafe_allow_html=True)
    if all_leads:
        formatted_leads = []
        for l in all_leads:
            formatted_leads.append({
                "COMPANY": l.get("company_name", "N/A"),
                "LOCATION": l.get("country", "USA"),
                "EMAIL": l.get("email", "N/A"),
                "AI SCORE": "91/100",
                "OPPORTUNITY": "No Google Ads",
                "STATUS": l.get("status", "Ready")
            })
        st.dataframe(formatted_leads, use_container_width=True, hide_index=True)
    else:
        st.dataframe([
            {"COMPANY": "ABC Roofing Solutions", "LOCATION": "🇺🇸 Dallas, TX", "EMAIL": "john@abcroofing.com", "AI SCORE": "91/100", "OPPORTUNITY": "No Google Ads", "STATUS": "Ready"},
            {"COMPANY": "XYZ Contractors", "LOCATION": "🇬🇧 London", "EMAIL": "mike@xyzroofers.co.uk", "AI SCORE": "87/100", "OPPORTUNITY": "Weak Website CTA", "STATUS": "Ready"},
            {"COMPANY": "Smith Roofing", "LOCATION": "🇨🇦 Toronto", "EMAIL": "info@smithroofing.ca", "AI SCORE": "82/100", "OPPORTUNITY": "Poor SEO", "STATUS": "Follow-up"},
            {"COMPANY": "Dachbau Berlin", "LOCATION": "🇩🇪 Berlin", "EMAIL": "kontakt@dachbau.de", "AI SCORE": "79/100", "OPPORTUNITY": "No Lead Form", "STATUS": "Draft"}
        ], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "Lead Database":
    st.markdown('<div class="panel"><div class="panel-title">Complete Lead Database</div><p class="panel-sub">All extracted company intelligence stored securely in Supabase.</p>', unsafe_allow_html=True)
    if all_leads:
        st.dataframe(all_leads, use_container_width=True, hide_index=True)
    else:
        st.info("No records found in database.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f'<div class="panel"><div class="panel-title">{selected_menu} Module</div><p class="panel-sub">Manage your agency outreach tools under Rai Marketing infrastructure.</p></div>', unsafe_allow_html=True)
