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
    page_title="Rai Marketing OS - Global SDR Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

query_params = st.query_params
url_niche = query_params.get("niche", "")
url_location = query_params.get("location", "")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: #080511;
        color: #f8fafc;
    }

    .header-container {
        display: flex;
        align-items: center;
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        padding: 24px 32px;
        border-radius: 20px;
        border: 1px solid rgba(168, 85, 247, 0.25);
        margin-bottom: 25px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
    }
    .brand-logo { 
        font-size: 20px; 
        font-weight: 800;
        margin-right: 18px; 
        background: linear-gradient(135deg, #a855f7, #6366f1);
        padding: 10px 16px;
        border-radius: 12px;
        color: #ffffff;
    }
    .brand-name { 
        font-size: 22px; 
        font-weight: 800; 
        color: #ffffff; 
        margin: 0;
    }
    .brand-sub {
        font-size: 12px;
        color: #c084fc;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .operator-badge {
        font-size: 12px;
        color: #cbd5e1;
        margin-left: auto;
        text-align: right;
        background: rgba(15, 23, 42, 0.8);
        padding: 10px 16px;
        border-radius: 10px;
        border: 1px solid rgba(168, 85, 247, 0.15);
    }

    .custom-card {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(168, 85, 247, 0.15);
        backdrop-filter: blur(20px);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }

    .metric-row {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }
    .metric-card {
        flex: 1;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
    }
    .metric-value {
        font-size: 30px;
        font-weight: 800;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 11px;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: rgba(3, 7, 18, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #9333ea 0%, #4f46e5 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        box-shadow: 0 8px 20px rgba(147, 51, 234, 0.4) !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] {
        background-color: #05030a !important;
        border-right: 1px solid rgba(168, 85, 247, 0.1);
    }
</style>
""", unsafe_allow_html=True)

COUNTRIES_LIST = [
    "Worldwide / Global", "United States", "United Kingdom", "Canada", 
    "Australia", "United Arab Emirates", "Saudi Arabia", "Germany", 
    "France", "Spain", "Italy", "Netherlands", "Pakistan", "India", "Singapore", "Custom Location..."
]

INDUSTRIES_LIST = [
    "Construction", "Plumbing", "Real Estate Agencies", "Roofing Contractors", 
    "Dental Practices", "Solar Energy", "Digital Marketing Agencies", "E-commerce", 
    "Law Firms", "Healthcare Practices", "Software Companies", "Hotels", "Accounting Services", "Custom Industry..."
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

st.markdown("""
<div class="header-container">
    <div class="brand-logo">RAI</div>
    <div>
        <div class="brand-name">Rai Marketing Agency</div>
        <div class="brand-sub">Global SDR Lead Engine & AI Dispatcher</div>
    </div>
    <div class="operator-badge">
        Active Operator<br><b>Rai Shafqat Abbas</b>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navigation")
    menu = st.radio("Go to", ["Dashboard Overview", "Extraction Pipeline", "Database Records"], label_visibility="collapsed")
    
    st.divider()
    st.markdown("### System Setup")
    agent_name = st.text_input("Active Model Name", value="Rai_SDR_v1")
    st.markdown(
        f"<div style='background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 8px 12px; border-radius: 8px; color: #4ade80; font-size: 11px; font-weight: 600; margin-top: 8px;'>"
        f"Model Status: <b>{agent_name} [Online]</b>"
        "</div>",
        unsafe_allow_html=True
    )
    st.divider()
    st.markdown("### Global Scope")
    st.caption("Multi-country and multi-industry autonomous pipeline engine.")

all_leads = fetch_analytics()
total_leads = len(all_leads)
sent_emails = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["sent", "completed"])
pending_queue = sum(1 for d in all_leads if str(d.get("status", "")).lower() in ["new", "pending", "ready to send"])

if menu == "Dashboard Overview":
    st.markdown("### Executive Overview")
    st.caption("Real-time telemetry and performance metrics across global outreach infrastructure.")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_leads}</div><div class="metric-label">Total Extracted Leads</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#4ade80;">{sent_emails}</div><div class="metric-label">Outbound Emails Sent</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#facc15;">{pending_queue}</div><div class="metric-label">Pending in Queue</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### Recent System Activity")
    st.caption("Live feed of the latest database entries.")
    if all_leads:
        recent_rows = []
        for row in all_leads[:5]:
            recent_rows.append({
                "Company": row.get("company_name", "N/A"),
                "Email": row.get("email", "N/A"),
                "Industry": row.get("industry", "N/A"),
                "Country": row.get("country", "N/A"),
                "Status": row.get("status", "N/A")
            })
        st.dataframe(recent_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No logs available yet.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Extraction Pipeline":
    st.markdown("### Target Selection Launchpad")
    st.caption("Configure target filters and initialize cloud-backed extraction execution.")
    
    col_l, col_r = st.columns([1.2, 1.8], gap="large")
    
    with col_l:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        industry_index = INDUSTRIES_LIST.index(url_niche) if url_niche in INDUSTRIES_LIST else (0 if not url_niche else INDUSTRIES_LIST.index("Custom Industry..."))
        selected_industry_option = st.selectbox("Select Target Industry:", INDUSTRIES_LIST, index=industry_index)
        
        if selected_industry_option == "Custom Industry...":
            final_niche = st.text_input("Enter Custom Industry:", value=url_niche if url_niche not in INDUSTRIES_LIST else "", placeholder="e.g. HVAC, Car Rental")
        else:
            final_niche = selected_industry_option if not url_niche else url_niche

        country_index = COUNTRIES_LIST.index(url_location) if url_location in COUNTRIES_LIST else (5 if not url_location else COUNTRIES_LIST.index("Custom Location..."))
        selected_country_option = st.selectbox("Select Target Country / Scope:", COUNTRIES_LIST, index=country_index)
        
        if selected_country_option == "Custom Location...":
            final_location = st.text_input("Enter Custom Location:", value=url_location if url_location not in COUNTRIES_LIST else "", placeholder="e.g. Dubai, London")
        elif selected_country_option == "Worldwide / Global":
            final_location = "Global"
        else:
            final_location = selected_country_option if not url_location else url_location

        clean_niche = re.sub(r'[^a-zA-Z0-9\s]', '', final_niche).strip()
        clean_location = re.sub(r'[^a-zA-Z0-9\s]', '', final_location).strip()

        st.markdown(
            f"<div style='color:#c084fc; font-size:11px; margin: 15px 0; background: rgba(3, 7, 18, 0.8); padding: 10px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.2); font-family: monospace;'>"
            f"Query: <code>\"{clean_niche}\" \"contact\" \"{clean_location}\"</code>"
            f"</div>", 
            unsafe_allow_html=True
        )
        
        run_pipeline = st.button("Initialize Pipeline Execution", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if run_pipeline:
            if not clean_niche or not clean_location:
                st.error("Please ensure both industry and location parameters are valid.")
            else:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.markdown("### Live Cloud Execution Terminal")
                status_box = st.empty()
                status_box.info(f"Executing cloud workflow for **{clean_niche.upper()}** in **{clean_location.upper()}**...")
                
                log_box = st.empty()
                env = os.environ.copy()
                if "MODAL_TOKEN_ID" in st.secrets:
                    env["MODAL_TOKEN_ID"] = st.secrets["MODAL_TOKEN_ID"]
                if "MODAL_TOKEN_SECRET" in st.secrets:
                    env["MODAL_TOKEN_SECRET"] = st.secrets["MODAL_TOKEN_SECRET"]
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"
                
                command = [sys.executable, "-m", "modal", "run", "master_pipeline.py", "--niche", clean_niche, "--location", clean_location]
                
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', env=env)
                    output_logs = ""
                    for line in process.stdout:
                        output_logs += line
                        log_box.code(output_logs, language="bash")
                    process.wait()
                    if process.returncode == 0:
                        status_box.success("Success! Pipeline executed successfully.")
                        st.cache_data.clear()
                    else:
                        status_box.error("Pipeline execution failed. Check terminal logs.")
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="custom-card" style="text-align: center; padding: 60px 20px; color: #64748b;">', unsafe_allow_html=True)
            st.markdown("<h4>Pipeline Standby</h4><p style='font-size: 13px;'>Configure parameters on the left and click initialize to run live cloud dispatchers.</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Database Records":
    st.markdown("### Live Database Records")
    st.caption("Complete rows of scraped companies, contact details, and outbound status synced from Supabase.")
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if all_leads:
        clean_table = []
        for row in all_leads:
            clean_table.append({
                "Company Name": row.get("company_name", "N/A"),
                "Verified Email": row.get("email", "N/A"),
                "Industry": row.get("industry", "N/A"),
                "Country": row.get("country", "N/A"),
                "Status": row.get("status", "N/A"),
                "Website": row.get("website", "N/A")
            })
        st.dataframe(clean_table, use_container_width=True, hide_index=True)
    else:
        st.info("No records found in the database.")
    st.markdown('</div>', unsafe_allow_html=True)
