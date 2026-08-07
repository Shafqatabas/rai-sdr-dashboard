import modal
import re
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, urljoin

app = modal.App("rai-lead-agent")

image = modal.Image.debian_slim().pip_install(
    "requests", "beautifulsoup4", "openai", "supabase", "ddgs"
)

# Skip non-business sites, directories, gov sites, and junk blogs
SKIP_DOMAINS = [
    "rocketreach.co", "aeroleads.com", "rentechdigital.com", "spherescout.io",
    "linkedin.com", "facebook.com", "instagram.com", "yelp.com", "yellowpages.com",
    "threebestrated.de", "companydata.com", "ensun.io", "pinterest.com", "kompass.com",
    "cybo.com", "near-place.com", "zoominfo.com", "apollo.io", "bbb.org", "reddit.com",
    "youtube.com", "tiktok.com", "clutch.co", "ibisworld.com", "investopedia.com",
    "canada.ca", "gov.uk", "enests.co", "europages.co.uk", "europages.com", "cosuno.com",
    "poidata.io", "airteam.ai", "homeimprovement-guide.com"
]

# Invalid emails that shouldn't be inserted into Supabase
INVALID_EMAIL_PATTERNS = [
    "sentry.io", "wixpress.com", "example.com", "domain.com", "john.doe",
    "yourname@", "email@site.com", "info@example.com", "test@test.com", "schema.org"
]

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    email_lower = email.lower()
    if any(pattern in email_lower for pattern in INVALID_EMAIL_PATTERNS):
        return False
    if email_lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif')):
        return False
    return True

def clean_company_name(title: str, domain: str) -> str:
    # Clean up page titles to get the real business name
    clean_title = re.sub(r'(?i)(roofing|contractors|inc|llc|ltd|co|group|specialists).*$', r'\1', title).strip()
    if len(clean_title) > 50 or "top" in clean_title.lower() or "best" in clean_title.lower():
        # Fallback to domain name if title looks like a blog post
        parts = domain.replace("www.", "").split(".")
        return parts[0].capitalize() + " Roofing"
    return clean_title if clean_title else domain

@app.function(image=image, secrets=[modal.Secret.from_name("rai-secrets")])
def run_sdr_pipeline(business_type: str = "roofing contractor"):
    from supabase import create_client
    
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        from ddgs import DDGS

    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

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
        print(f"Loaded {len(existing_websites)} existing websites and {len(existing_emails)} existing emails from Supabase.")
    except Exception as err:
        print(f"Warning fetching existing records: {err}")

    # Explicit B2B search queries targeting local business owners
    target_countries = ["USA", "UK", "Canada", "Australia"]
    
    print("Starting Directory-Filtered Lead Pipeline...")

    for country in target_countries:
        query = f'"{business_type}" "contact" "{country}"'
        print(f"\n--- Searching for: '{query}' ---")
        
        results = []
        try:
            ddgs = DDGS()
            search_res = ddgs.text(query, max_results=30)
            for r in search_res:
                results.append({"title": r.get("title"), "link": r.get("href")})
        except Exception as err:
            print(f"Search Error for {country}: {err}")
            continue

        for item in results:
            raw_title = item.get("title", "")
            website = item.get("link", "")
            
            if not website or not website.startswith(('http://', 'https://')):
                continue

            parsed_url = urlparse(website)
            domain = parsed_url.netloc.lower()

            if any(skip_domain in domain for skip_domain in SKIP_DOMAINS):
                print(f"SKIPPED DIRECTORY/GOV: {domain}")
                continue

            normalized_website = website.strip().lower()
            if normalized_website in existing_websites:
                print(f"SKIPPED DUPLICATE WEBSITE: {domain}")
                continue

            company_name = clean_company_name(raw_title, domain)
            print(f"Inspecting Real Business: {company_name} ({website})")

            found_email = "Not Found"
            found_phone = "Not Found"
            found_address = "Not Found"

            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                site_req = requests.get(website, timeout=8, headers=headers)
                soup = BeautifulSoup(site_req.text, 'html.parser')
                page_text = site_req.text

                # Extract emails
                emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_text)
                valid_emails = [e for e in emails if is_valid_email(e)]
                
                if valid_emails:
                    found_email = valid_emails[0]

                # Check Contact Page if missing on Homepage
                if found_email == "Not Found":
                    contact_link = None
                    for a in soup.find_all('a', href=True):
                        href = a['href'].lower()
                        if 'contact' in href or 'about' in href:
                            contact_link = urljoin(website, a['href'])
                            break
                    
                    if contact_link and contact_link.startswith(('http://', 'https://')):
                        try:
                            contact_req = requests.get(contact_link, timeout=6, headers=headers)
                            c_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", contact_req.text)
                            valid_c_emails = [e for e in c_emails if is_valid_email(e)]
                            if valid_c_emails:
                                found_email = valid_c_emails[0]
                        except Exception:
                            pass

                # Phone extraction
                phones = re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", page_text)
                if phones:
                    found_phone = phones[0]

            except Exception as err:
                print(f"Scraping warning for {website}: {err}")

            if found_email == "Not Found" or not found_email:
                print(f"SKIPPED: {company_name} (Reason: No Valid Email Found)")
                continue

            normalized_email = found_email.strip().lower()
                
            if normalized_email in existing_emails:
                print(f"SKIPPED DUPLICATE EMAIL: {found_email}")
                continue

            record = {
                "company_name": company_name,
                "website": website,
                "email": found_email,
                "phone": found_phone,
                "address": found_address,
                "country": country,
                "industry": business_type.title(),
                "source_url": website,
                "status": "New"
            }
            
            try:
                supabase.table("leads").insert(record).execute()
                print(f"✅ SAVED HIGH-QUALITY LEAD: {company_name} | Email: {found_email} | Country: {country}")
                existing_websites.add(normalized_website)
                existing_emails.add(normalized_email)
            except Exception as e:
                print(f"Supabase Insert Error: {e}")

    return "Pipeline Completed Successfully!"

@app.local_entrypoint()
def main():
    result = run_sdr_pipeline.remote("roofing contractor")
    print(result)