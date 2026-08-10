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
TEXT = "#F8FAFC"
MUTED = "#94A3B8"


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
    --text: {TEXT};
    --muted: {MUTED};
}}

html, body, [class*="css"] {{
    font-family: "Inter", sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at 78% 4%, rgba(6,182,212,.09), transparent 24%),
        radial-gradient(circle at 16% 72%, rgba(37,99,235,.08), transparent 28%),
        var(--bg);
    color: var(--text);
}}

.block-container {{
    max-width: 1500px;
    padding-top: 1rem;
    padding-bottom: 3rem;
}}

[data-testid="stSidebar"] {{
    background: #030D1C !important;
    border-right: 1px solid rgba(37,99,235,.24);
}}

[data-testid="stSidebar"] .block-container {{
    padding: 1rem .8rem;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stTextInput input,
.stTextArea textarea {{
    background: #041022 !important;
    color: white !important;
    border-color: rgba(37,99,235,.35) !important;
    border-radius: 10px !important;
}}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {{
    color: #64748B !important;
}}

.stButton > button {{
    border: 1px solid rgba(6,182,212,.35) !important;
    border-radius: 10px !important;
    background: linear-gradient(90deg, {BLUE}, {CYAN}) !important;
    color: white !important;
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
}}

div[data-testid="stMetricLabel"] {{
    color: #94A3B8 !important;
}}

div[data-testid="stMetricValue"] {{
    color: #38BDF8 !important;
}}

.client-card {{
    background: rgba(7,20,38,.88);
    border: 1px solid rgba(37,99,235,.34);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 12px 35px rgba(0,0,0,.18);
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
}}

.brand-title span {{
    color:{CYAN};
}}

.brand-subtitle {{
    color:#38BDF8;
    font-size:14px;
    margin-top:8px;
}}

.small-muted {{
    color:#64748B;
    font-size:11px;
}}

.status-online {{
    color:#34D399;
    font-size:11px;
    font-weight:700;
}}

.badge {{
    display:inline-block;
    padding:5px 9px;
    border-radius:999px;
    background:rgba(16,185,129,.10);
    color:#34D399;
    border:1px solid rgba(16,185,129,.18);
    font-size:10px;
    font-weight:700;
}}

.pipeline-log {{
    background:#020B16;
    border:1px solid rgba(37,99,235,.25);
    border-radius:12px;
    padding:12px;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid rgba(37,99,235,.22);
    border-radius: 12px;
}}

hr {{
    border-color: rgba(148,163,184,.10) !important;
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


# -----------------------------
# Logo SVG
# -----------------------------
def logo_svg(size=48):
    return f"""
<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="ceg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{BLUE}"/>
      <stop offset="100%" stop-color="{CYAN}"/>
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

        # tolerate common alternative status values
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
        <div class="brand-row" style="margin-bottom:18px;">
            <div class="brand-mark">{logo_svg(38)}</div>
            <div>
                <div style="font-size:16px;font-weight:800;">
                    ClientEngine <span style="color:{CYAN};">AI</span>
                </div>
                <div class="small-muted">Lead generation & outreach</div>
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

    st.divider()

    st.markdown("**AI ENGINE**")
    engine_items = [
        ("OpenAI", bool(get_secret("OPENAI_API_KEY"))),
        ("Modal", bool(MODAL_TOKEN_ID or MODAL_TOKEN_SECRET)),
        ("Supabase", bool(SUPABASE_URL and SUPABASE_KEY)),
        ("Email", bool(get_secret("SMTP_HOST") or get_secret("RESEND_API_KEY"))),
    ]

    for name, connected in engine_items:
        color = "#34D399" if connected else "#F59E0B"
        label = "Connected" if connected else "Not configured"
        st.markdown(
            f"""
            <div style="display:flex;justify-content:space-between;
                        padding:6px 0;font-size:11px;">
                <span>{name}</span>
                <span style="color:{color};font-weight:700;">● {label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        f"""
        <div style="border:1px solid rgba(37,99,235,.28);
                    border-radius:12px;padding:12px;text-align:center;
                    background:rgba(37,99,235,.05);">
            <div style="font-weight:800;font-size:12px;">Rai Marketing Agency</div>
            <div class="small-muted">ClientEngine AI</div>
            <div style="color:#38BDF8;font-size:9px;margin-top:5px;">v2.0</div>
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


# -----------------------------
# Header
# -----------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-content">
            <div class="brand-row">
                <div class="brand-mark">{logo_svg(48)}</div>
                <div>
                    <div class="brand-title">
                        ClientEngine <span>AI</span>
                    </div>
                    <div class="brand-subtitle">
                        AI-Powered Lead Generation & Outreach Platform
                    </div>
                </div>
            </div>
            <div style="margin-top:18px;color:#94A3B8;font-size:12px;">
                Find prospects, collect public business contact data,
                analyze opportunities, generate personalized outreach,
                and manage follow-ups from one control center.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Dashboard / Find Leads
# -----------------------------
if menu in {"Dashboard", "Find Leads"}:
    query_params = st.query_params
    url_niche = query_params.get("niche", "")
    url_location = query_params.get("location", "")

    industries = [
        "Roofing Contractors",
        "HVAC Companies",
        "Construction Companies",
        "Plumbing Companies",
        "Dental Practices",
        "Real Estate Agencies",
        "Law Firms",
        "Solar Companies",
        "Restaurants",
        "E-commerce",
        "Digital Marketing Agencies",
        "Software Companies",
        "Hotels",
        "Accounting Services",
        "Custom Industry...",
    ]

    countries = [
        "United States",
        "United Kingdom",
        "Canada",
        "Germany",
        "Australia",
        "United Arab Emirates",
        "Saudi Arabia",
        "Pakistan",
        "France",
        "Italy",
        "Netherlands",
        "Worldwide / Global",
        "Custom Location...",
    ]

    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Find Your Next Customers")
    st.caption(
        "Give ClientEngine AI an industry and location. "
        "The configured Modal pipeline will perform the actual search."
    )

    c1, c2 = st.columns(2, gap="medium")

    with c1:
        industry_default = (
            industries.index(url_niche) if url_niche in industries else 0
        )
        selected_industry = st.selectbox(
            "Industry / Niche",
            industries,
            index=industry_default,
        )

        if selected_industry == "Custom Industry...":
            final_niche = st.text_input(
                "Custom industry",
                value="" if url_niche in industries else url_niche,
                placeholder="e.g. commercial cleaning",
            )
        else:
            final_niche = selected_industry

    with c2:
        country_default = (
            countries.index(url_location) if url_location in countries else 0
        )
        selected_country = st.selectbox(
            "Location / Country",
            countries,
            index=country_default,
        )

        if selected_country == "Custom Location...":
            final_location = st.text_input(
                "Custom location",
                value="" if url_location in countries else url_location,
                placeholder="e.g. Dallas, Texas",
            )
        elif selected_country == "Worldwide / Global":
            final_location = "Global"
        else:
            final_location = selected_country

    clean_niche = clean_target(final_niche)
    clean_location = clean_target(final_location)

    st.markdown(
        f"""
        <div style="margin-top:14px;padding:10px 12px;border-radius:10px;
                    background:#020B16;border:1px solid rgba(37,99,235,.25);
                    color:#38BDF8;font-family:monospace;font-size:11px;">
            Query preview:
            "{clean_niche}" + "{clean_location}" + public business contact data
        </div>
        """,
        unsafe_allow_html=True,
    )

    b1, b2 = st.columns([2, 1])
    with b1:
        run_pipeline = st.button(
            "⚡ Find Potential Customers",
            use_container_width=True,
            type="primary",
        )
    with b2:
        refresh = st.button("↻ Refresh Database", use_container_width=True)

    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5, gap="small")
    k1.metric("Leads Found", total_leads)
    k2.metric("Emails Ready", pending_queue)
    k3.metric("Emails Sent", sent_emails)
    k4.metric("Replies", replies)
    k5.metric("Failed", counts["failed"])

    # Pipeline execution
    if run_pipeline:
        if not clean_niche or not clean_location:
            st.error("Please enter both an industry and a location.")
        else:
            pipeline = find_pipeline_file()

            st.markdown('<div class="client-card">', unsafe_allow_html=True)
            st.markdown("### Live Cloud Execution")

            if not pipeline:
                st.error(
                    "No pipeline file was found. Put master_pipeline.py or "
                    "sdr_agent.py in the same folder as app.py."
                )
            else:
                status_box = st.empty()
                status_box.info(
                    f"Running {Path(pipeline).name} for "
                    f"{clean_niche} → {clean_location}"
                )

                log_box = st.empty()
                env = os.environ.copy()
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"

                command = [
                    sys.executable,
                    "-m",
                    "modal",
                    "run",
                    pipeline,
                    "--niche",
                    clean_niche,
                    "--location",
                    clean_location,
                ]

                output_logs = ""

                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        env=env,
                    )

                    if process.stdout:
                        for line in process.stdout:
                            output_logs += line
                            log_box.code(output_logs, language="text")

                    return_code = process.wait()

                    if return_code == 0:
                        status_box.success(
                            "Pipeline completed successfully. "
                            "Refreshing lead database..."
                        )
                        st.cache_data.clear()
                    else:
                        status_box.error(
                            f"Pipeline stopped with exit code {return_code}."
                        )

                except FileNotFoundError:
                    status_box.error(
                        "Modal CLI was not found. Install it with: "
                        "pip install modal"
                    )
                except Exception as exc:
                    status_box.error(f"Execution error: {exc}")

            st.markdown("</div>", unsafe_allow_html=True)

    # Dashboard analytics
    a1, a2, a3 = st.columns([1.15, 1, 1.15], gap="medium")

    with a1:
        st.markdown('<div class="client-card">', unsafe_allow_html=True)
        st.markdown("### Lead Pipeline")
        st.write(f"Found — **{total_leads}**")
        st.write(f"Ready — **{pending_queue}**")
        st.write(f"Contacted — **{sent_emails}**")
        st.write(f"Replies — **{replies}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="client-card">', unsafe_allow_html=True)
        st.markdown("### Lead Status")
        st.write(f"New: **{counts['new']}**")
        st.write(f"Pending: **{counts['pending']}**")
        st.write(f"Sent: **{counts['sent']}**")
        st.write(f"Completed: **{counts['completed']}**")
        st.write(f"Failed: **{counts['failed']}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with a3:
        st.markdown('<div class="client-card">', unsafe_allow_html=True)
        st.markdown("### Engine Capabilities")
        st.write("✓ Public web lead discovery")
        st.write("✓ Contact email extraction")
        st.write("✓ Supabase lead storage")
        st.write("✓ Modal cloud execution")
        st.write("✓ AI outreach layer")
        st.markdown("</div>", unsafe_allow_html=True)

    # Recent leads
    st.markdown('<div class="client-card">', unsafe_allow_html=True)
    st.markdown("### Recent Leads")

    if db_error:
        st.warning(f"Supabase: {db_error}")

    if all_leads:
        table = []
        for row in all_leads[:100]:
            table.append(
                {
                    "Company": safe_text(row.get("company_name")),
                    "Email": safe_text(row.get("email")),
                    "Industry": safe_text(row.get("industry")),
                    "Country": safe_text(row.get("country")),
                    "Status": safe_text(row.get("status")),
                    "Website": safe_text(row.get("website")),
                }
            )

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No leads found yet. Launch a campaign above.")

    st.markdown("</div>", unsafe_allow_html=True)


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
    ClientEngine AI · Rai Marketing Agency · Find. Analyze. Engage. Grow.
    """,
    unsafe_allow_html=True,
)
