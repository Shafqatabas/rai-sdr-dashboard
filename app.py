import streamlit as st
import subprocess
import os
from supabase import create_client

# Page Config
st.set_page_config(
    page_title="Rai Marketing OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Professional Corporate SaaS Design)
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

    /* Top Corporate Header */
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
        font-size: 42px; 
        margin-right: 20px; 
        background: rgba(99, 102, 241, 0.2);
        padding: 10px 16px;
        border-radius: 14px;
        border: 1px solid #6366f1;
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

    /* Custom Card Containers */
    .custom-card {
        background: #1e293b;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Metric Display */
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

    /* Input & Button Overrides */
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

# Supabase Credentials
SUPABASE_URL = "https://xdiduoutcswibfmdkroa.supabase.co"
SUPABASE_KEY = "sb_publishable_zUTFg8RqHqlEe6V2Jy2wfg_FxNRaixl"

@st.cache_data(ttl=10)
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
    <div class="brand-logo">🚀</div>
    <div>
        <div class="brand-name">Rai Marketing Agency</div>
        <div class="brand-sub">Autonomous SDR Lead Engine & AI Dispatcher</div>
    </div>
    <div class="welcome-text">
        Welcome back, <br><b>Rai Shafqat Abbas</b>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### ⚙️ System Setup")
    st.caption("Core Infrastructure Control")
    st.divider()
    
    agent_name = st.text_input("Active Model Name", value="Rai_SDR_v1")
    st.success(f"Model ID: **{agent_name}** [Online 🟢]")
    
    st.divider()
    st.markdown("### 🎯 Quick Presets")
    preset = st.selectbox("Select Target Industry:", ["Custom Input", "Dental USA", "Real Estate UK", "Roofing Canada", "Solar USA"])

# Preset Mapping
default_niche, default_location = "dental", "USA"
if preset == "Dental USA":
    default_niche, default_location = "dentist", "USA"
elif preset == "Real Estate UK":
    default_niche, default_location = "real estate agency", "UK"
elif preset == "Roofing Canada":
    default_niche, default_location = "roofing contractor", "Canada"
elif preset == "Solar USA":
    default_niche, default_location = "solar installer", "USA"

# --- FETCH METRICS ---
all_leads = fetch_analytics()
total_leads = len(all_leads)
sent_emails = sum(1 for d in all_leads if d.get("status") == "Sent")
pending_queue = sum(1 for d in all_leads if d.get("status") in ["New", "Ready to Send"])

# --- MAIN DASHBOARD LAYOUT (CARDS) ---
col_left, col_right = st.columns([1.2, 1.8], gap="large")

with col_left:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Campaign Launchpad")
    st.caption("Configure search targets for the AI agent.")
    
    niche = st.text_input("Target Industry / Keyword:", value=default_niche, placeholder="e.g. dentist, lawyer, roofing")
    location = st.text_input("Target Location / Country:", value=default_location, placeholder="e.g. USA, UK, UAE")
    
    st.markdown(f"<div style='color:#a5b4fc; font-size:12px; margin: 10px 0;'>Query: <code>\"{niche}\" \"contact\" \"{location}\"</code></div>", unsafe_allow_html=True)
    
    run_pipeline = st.button("🚀 Initialize Pipeline Execution", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Agent Performance Analytics")
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
    if not niche or not location:
        st.error("Please provide both target industry and location parameters.")
    else:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Live Cloud Execution Output")
        
        command = f'python -m modal run master_pipeline.py --niche "{niche}" --location "{location}"'
        
        status_box = st.empty()
        status_box.info(f"🔄 Executing cloud workflow for **{niche.upper()}** in **{location.upper()}** using **{agent_name}**...")
        
        log_box = st.empty()
        
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        
        try:
            process = subprocess.Popen(
                command, 
                shell=True, 
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
                status_box.success("🎉 **Success!** Pipeline executed successfully. Outbound emails dispatched.")
                st.cache_data.clear()
            else:
                status_box.error("❌ Pipeline execution failed. Please check the logs above.")
                
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
            
        st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# --- DATABASE LEADS TABLE SECTION ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown("### 🗂️ Live Database Records")
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