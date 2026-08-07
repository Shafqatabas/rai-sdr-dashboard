import streamlit as st
import subprocess
import sys
import os
import re
from supabase import create_client

# Streamlit Secrets سے Modal Tokens کو Environment میں سیٹ کرنا
if "MODAL_TOKEN_ID" in st.secrets:
    os.environ["MODAL_TOKEN_ID"] = st.secrets["MODAL_TOKEN_ID"]
if "MODAL_TOKEN_SECRET" in st.secrets:
    os.environ["MODAL_TOKEN_SECRET"] = st.secrets["MODAL_TOKEN_SECRET"]

# Page Config
st.set_page_config(
    page_title="Rai Marketing OS - Global SDR Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: #090d16;
        color: #f8fafc;
    }

    .header-container {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        padding: 24px 32px;
        border-radius: 20px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .brand-logo { 
        font-size: 24px; 
        font-weight: 800;
        margin-right: 20px; 
        background: rgba(99, 102, 241, 0.2);
        padding: 10px 16px;
        border-radius: 14px;
        border: 1px solid #6366f1;
        color: #818cf8;
    }
    .brand-name { 
        font-size: 26px; 
        font-weight: 800; 
        color: #ffffff; 
        letter-spacing: -0.5px; 
        margin: 0;
    }
    .brand-sub {
        font-size: 13px;
        color: #818cf8;
        font-weight: 600;
        margin-top: 2px;
    }
    .welcome-text { 
        font-size: 15px; 
        color: #cbd5e1; 
        margin-left: auto; 
        text-align: right;
        background: rgba(15, 23, 42, 0.6);
        padding: 10px 18px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .custom-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 14px 24px !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

COUNTRIES_LIST = [
    "Worldwide / Global",
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "United Arab Emirates",
    "Saudi Arabia",
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Netherlands",
    "Pakistan",
    "India",
    "Singapore",
    "Custom Location..."
]

INDUSTRIES_LIST = [
    "Construction",
    "Plumbing",
    "Real Estate Agencies",
    "Roofing Contractors",
    "Dental Practices",
    "Solar Energy",
    "Digital Marketing Agencies",
    "E-commerce",
    "Law Firms",
    "Healthcare Practices",
    "Software Companies",
    "Hotels",
    "Accounting Services",
    "Custom Industry..."
]

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://wosvxuafqixewndpxypa.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indvc3Z4dWFmcWl4ZXduZHB4eXBhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDEyNzgwMzMsImV4cCI6MjA1Njg1NDAzM30.7Qf2wV64x-i5t8q9A2oO4k90K_B22qKxR")

@st.cache_data(ttl=5)
def fetch_analytics():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supabase.table("leads").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception:
        return []

# --- TOP CORPORATE HEADER ---
st.markdown("""
<div class="header-container">
    <div class="brand-logo">RAI</div>
    <div>
        <div class="brand-name">Rai Marketing Agency</div>
        <div class="brand-sub">Worldwide SDR Lead Engine & AI Dispatcher</div>
    </div>
    <div class="welcome-text">
        Welcome back, <br><b>Rai Shafqat Abbas</b>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### System Setup")
    st.caption("Core Infrastructure Control")
    st.divider()
    
    agent_name = st.text_input("Active Model Name", value="Rai_SDR_v1")
    st.success(f"Model ID: **{agent_name}** [Online]")
    st.divider()
    st.markdown("### Global Scope")
    st.info("System is configured for multi-country & multi-industry outreach.")

# --- FETCH METRICS ---
all_leads = fetch_analytics()
total_leads = len(all_leads)
sent_emails = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["sent", "completed"])
pending_queue = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["new", "pending", "ready to send"])

# --- MAIN DASHBOARD LAYOUT ---
col_left, col_right = st.columns([1.3, 1.7], gap="large")

with col_left:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### Target Selection Launchpad")
    st.caption("Select your target industry and location filters.")
    
    selected_industry_option = st.selectbox("Select Target Industry:", INDUSTRIES_LIST, index=0)
    
    if selected_industry_option == "Custom Industry...":
        final_niche = st.text_input("Enter Custom Industry:", placeholder="e.g. HVAC, Car Rental")
    else:
        final_niche = selected_industry_option

    st.write("")

    selected_country_option = st.selectbox("Select Target Country / Scope:", COUNTRIES_LIST, index=5)
    
    if selected_country_option == "Custom Location...":
        final_location = st.text_input("Enter Custom Location:", placeholder="e.g. Dubai, London")
    elif selected_country_option == "Worldwide / Global":
        final_location = "Global"
    else:
        final_location = selected_country_option

    # Clean special characters like & for search safety
    clean_niche = re.sub(r'[^a-zA-Z0-9\s]', '', final_niche).strip()
    clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', final_location).strip()

    st.markdown(
        f"<div style='color:#a5b4fc; font-size:12px; margin: 15px 0; background: #0f172a; padding: 10px; border-radius: 8px; border: 1px solid #334155;'>"
        f"Generated Query: <code>\"{clean_niche}\" \"contact\" \"{clean_location}\"</code>"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    run_pipeline = st.button("Initialize Pipeline Execution", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### Agent Performance Analytics")
    st.caption(f"Real-time data metrics from model: **{agent_name}**")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-value">{total_leads}</div><div class="metric-label">Total Leads</div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-value" style="color:#4ade80;">{sent_emails}</div><div class="metric-label">Emails Sent</div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-value" style="color:#facc15;">{pending_queue}</div><div class="metric-label">In Queue</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- EXECUTION TERMINAL SECTION ---
if run_pipeline:
    if not clean_niche or not clean_location:
        st.error("Please ensure both industry and location parameters are valid.")
    else:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### Live Cloud Execution Output")
        
        status_box = st.empty()
        status_box.info(f"Executing cloud workflow for **{clean_niche.upper()}** in **{clean_location.upper()}** using **{agent_name}**...")
        
        log_box = st.empty()
        
        env = os.environ.copy()
        if "MODAL_TOKEN_ID" in st.secrets:
            env["MODAL_TOKEN_ID"] = st.secrets["MODAL_TOKEN_ID"]
        if "MODAL_TOKEN_SECRET" in st.secrets:
            env["MODAL_TOKEN_SECRET"] = st.secrets["MODAL_TOKEN_SECRET"]
            
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        
        command = [
            sys.executable, "-m", "modal", "run", "master_pipeline.py",
            "--niche", clean_niche,
            "--location", clean_location
        ]
        
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )
            
            output_logs = ""
            for line in process.stdout:
                output_logs += line
                log_box.code(output_logs, language="bash")
            
            process.wait()
            
            if process.returncode == 0:
                status_box.success("Success! Pipeline executed successfully.")
                st.cache_data.clear()
            else:
                status_box.error("Pipeline execution failed. Please check the logs above.")
                
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
            
        st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# --- DATABASE LEADS TABLE SECTION ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown("### Live Database Records")
st.caption("Latest scraped companies, contact details, and outbound status from Supabase.")

if all_leads:
    clean_table = []
    for row in all_leads:
        clean_table.append({
            "Company": row.get("company_name", "N/A"),
            "Email": row.get("email", "N/A"),
            "Industry": row.get("industry", "N/A"),
            "Country": row.get("country", "N/A"),
            "Status": row.get("status", "N/A"),
            "Website": row.get("website", "N/A")
        })
    st.dataframe(clean_table, use_container_width=True, hide_index=True)
else:
    st.info("No records found in the database yet. Launch your first campaign above.")

st.markdown('</div>', unsafe_allow_html=True)
