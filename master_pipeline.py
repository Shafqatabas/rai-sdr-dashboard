import modal
import re
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, urljoin
from datetime import datetime, timezone
import json

app = modal.App("rai-master-sdr-pipeline")

image = modal.Image.debian_slim().pip_install(
    "requests", "beautifulsoup4", "openai", "supabase", "resend"
)

SKIP_DOMAINS = [
    "rocketreach.co", "aeroleads.com", "rentechdigital.com", "spherescout.io",
    "linkedin.com", "facebook.com", "instagram.com", "yelp.com", "yellowpages.com",
    "threebestrated.de", "companydata.com", "ensun.io", "pinterest.com", "kompass.com",
    "cybo.com", "near-place.com", "zoominfo.com", "apollo.io", "bbb.org", "reddit.com",
    "youtube.com", "tiktok.com", "clutch.co", "ibisworld.com", "investopedia.com",
    "canada.ca", "gov.uk", "enests.co", "europages.co.uk", "europages.com", "cosuno.com",
    "poidata.io", "airteam.ai", "homeimprovement-guide.com", "naver.com", "dentalarirang.com",
    "wikipedia.org", "google.com", "torproject.org", "fraud.tw", "uptogo.com.tw", "whois365.com",
    "npa.gov.tw", "ntpc.gov.tw", "sportsentry.ne.jp", "yahoo.co.jp", "goal.com", "olympics.com"
]

INVALID_EMAIL_PATTERNS = [
    "sentry.io", "wixpress.com", "example.com", "domain.com", "john.doe",
    "yourname@", "email@site.com", "test@test.com", "schema.org", "wix.com"
]

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    email_lower = email.lower()
    if any(pattern in email_lower for pattern in INVALID_EMAIL_PATTERNS):
        return False
    if email_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.js', '.css')):
        return False
    
    parts = email_lower.split('@')
    if len(parts) != 2:
        return False
    domain = parts[1]
    if not re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", domain):
        return False
    return True

def clean_company_name(title: str, domain: str) -> str:
    clean_title = re.sub(r'(?i)(contractors|inc|llc|ltd|co|group|specialists|immobilien).*$', r'', title).strip()
    if len(clean_title) > 40 or not clean_title:
        parts = domain.replace("www.", "").split(".")
        return parts[0].capitalize()
    return clean_title

def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.replace("\x00", "").encode('utf-8', 'ignore').decode('utf-8')

# Daily Cron Schedule: Runs automatically every day at 8:00 AM UTC
@app.function(image=image, secrets=[modal.Secret.from_name("rai-secrets")], schedule=modal.Cron("0 8 * * *"))
def run_full_sdr_workflow(niche: str = "Immobilien", location: str = "Germany"):
    from supabase import create_client
    from openai import OpenAI
    import resend

    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resend.api_key = os.environ["RESEND_API_KEY"]

    print(f"=== AUTOMATED CRON: SCRAPING LEADS FOR {niche} IN {location} ===")
    existing_websites = set()
    existing_emails = set()
    
    try:
        existing_data = supabase.table("leads").select("website, email").execute()
        if existing_data.data:
            for row in existing_data.data:
                if row.get("website"):
                    existing_websites.add(row.get("website").strip().lower())
                if row.get("email"):
                    existing_emails.add(row.get("email").strip().lower())
    except Exception as err:
        print(f"Warning fetching existing records: {err}")

    results = []

    target_portals = [
        "https://www.engelvoelkers.com/de/",
        "https://www.von-poll.com/",
        "https://www.immoscout24.de/",
        "https://www.immowelt.de/",
        "https://www.century21.de/",
        "https://www.homeday.de/",
        "https://www.mccarden.de/",
        "https://www.dahler-company.de/",
        "https://www.rieger-immobilien.de/",
        "https://www.1a-immobilien.de/"
    ]

    for link in target_portals:
        results.append({"title": "German Real Estate Agency", "link": link})

    for item in results:
        raw_title = item.get("title", "")
        website = item.get("link", "")
        if not website or not website.startswith(('http://', 'https://')):
            continue

        parsed_url = urlparse(website)
        domain = parsed_url.netloc.lower()
        if any(skip_domain in domain for skip_domain in SKIP_DOMAINS):
            continue

        normalized_website = website.strip().lower()
        if normalized_website in existing_websites:
            continue

        company_name = clean_company_name(raw_title, domain)
        found_email, found_phone, scraped_notes = "Not Found", "Not Found", ""

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            site_req = requests.get(website, timeout=10, headers=headers)
            soup = BeautifulSoup(site_req.text, 'html.parser')
            page_text = site_req.text
            scraped_notes = soup.get_text()[:1500]

            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_text)
            valid_emails = [e for e in emails if is_valid_email(e)]
            if valid_emails:
                found_email = valid_emails[0]

            if found_email == "Not Found":
                for a in soup.find_all('a', href=True):
                    href_val = a['href'].lower()
                    if 'contact' in href_val or 'kontakt' in href_val or 'impressum' in href_val or 'about' in href_val:
                        contact_link = urljoin(website, a['href'])
                        try:
                            c_req = requests.get(contact_link, timeout=6, headers=headers)
                            c_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", c_req.text)
                            valid_c = [e for e in c_emails if is_valid_email(e)]
                            if valid_c:
                                found_email = valid_c[0]
                                break
                        except Exception:
                            pass

            phones = re.findall(r"(\+49\s?[0-9\s\-]{6,15}|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})", page_text)
            if phones:
                found_phone = phones[0]
        except Exception as err:
            print(f"Scraping error on {website}: {err}")

        if not is_valid_email(found_email):
            found_email = f"kontakt@{domain.replace('www.', '')}"

        normalized_email = found_email.strip().lower()
        if normalized_email in existing_emails:
            continue

        record = {
            "company_name": sanitize_text(company_name),
            "website": sanitize_text(website),
            "email": sanitize_text(found_email),
            "phone": sanitize_text(found_phone),
            "country": sanitize_text(location),
            "industry": sanitize_text(niche.title()),
            "source_url": sanitize_text(website),
            "status": "New",
            "notes": sanitize_text(scraped_notes[:300])
        }
        try:
            supabase.table("leads").insert(record).execute()
            print(f"SAVED NEW LEAD: {company_name} | {found_email}")
            existing_websites.add(normalized_website)
            existing_emails.add(normalized_email)
        except Exception as e:
            print(f"Insert Error: {e}")

    # --- PHASE 2: AI EMAIL DRAFTING (LIMITED TO 100 DAILY) ---
    print("\n=== PHASE 2: GENERATING AI PERSONALIZED EMAILS ===")
    new_leads = supabase.table("leads").select("*").eq("status", "New").limit(100).execute().data or []
    
    for lead in new_leads:
        lead_id = lead.get("id")
        comp = lead.get("company_name", "Real Estate Partner")
        web = lead.get("website", "")
        cntry = lead.get("country", "")
        notes = lead.get("notes", "")

        prompt = f"""
        You are Rai Shafqat Abbas, Founder & CEO of Rai Marketing Agency.
        Write a professional B2B cold email in English to: {comp} ({web}, {cntry}).
        Website Context: {notes}

        SIGNATURE DETAILS TO USE EXACTLY:
        Rai Shafqat Abbas
        Founder & CEO
        Rai Marketing Agency
        Email: hello@raimarketingagency.online
        Phone: +92 316 6025651
        WhatsApp: https://wa.me/923166025651
        Website: https://raimarketingagency.online

        LAYOUT STRUCTURE REQUIRED:
        1. Subject Line: Helping {comp} Scale Client Acquisitions in {cntry}
        2. Text Overview: Introduce Rai Marketing Agency and acknowledge their professional presence in the {cntry} market.
        3. Problems & Solves: Highlight 3 major digital growth challenges (low digital lead conversion, high ad acquisition costs, slow follow-up response) and list how Rai Marketing solves them (High-converting web funnels, localized SEO, automated AI engagement).
        4. Contact & Free Offer: Offer a complimentary growth audit with full corporate contact signature.

        STRICT RULES:
        - Human professional tone, NO emojis.
        - Output JSON with keys: "subject" and "body".
        """

        try:
            ai_res = ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=650
            )
            res_json = json.loads(ai_res.choices[0].message.content)
            
            supabase.table("leads").update({
                "email_subject": res_json.get("subject"),
                "draft_email": res_json.get("body"),
                "status": "Ready to Send"
            }).eq("id", lead_id).execute()
            print(f"DRAFTED EMAIL FOR: {comp}")
        except Exception as err:
            print(f"AI Drafting Error: {err}")

    # --- PHASE 3: AUTOMATED EMAIL DISPATCH (MAX 100 DAILY) ---
    print("\n=== PHASE 3: DISPATCHING EMAILS VIA VERIFIED DOMAIN ===")
    ready_leads = supabase.table("leads").select("*").eq("status", "Ready to Send").neq("email", "Not Found").limit(100).execute().data or []

    for lead in ready_leads:
        lead_id = lead.get("id")
        to_email = lead.get("email")
        subj = lead.get("email_subject")
        body = lead.get("draft_email")
        comp = lead.get("company_name")

        if not is_valid_email(to_email):
            print(f"Skipping invalid email address: {to_email}")
            continue

        payload = {
            "from": "Rai Shafqat Abbas <hello@raimarketingagency.online>",
            "to": [to_email],
            "subject": subj,
            "text": body,
            "reply_to": "hello@raimarketingagency.online"
        }

        try:
            resend.Emails.send(payload)
            curr_time = datetime.now(timezone.utc).isoformat()
            supabase.table("leads").update({
                "status": "Sent",
                "sent_at": curr_time
            }).eq("id", lead_id).execute()
            print(f"SENT OUTBOUND EMAIL TO: {comp} ({to_email})")
        except Exception as err:
            print(f"Resend Sending Error for {to_email}: {err}")

    return "Automated Daily Pipeline Executed Successfully!"

@app.local_entrypoint()
def main(niche: str = "Immobilien", location: str = "Germany"):
    print(f"=== STARTING MANUAL TEST FOR: {niche} IN {location} ===")
    res = run_full_sdr_workflow.remote(niche=niche, location=location)
    print(res)