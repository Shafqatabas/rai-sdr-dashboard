import modal
import os

app = modal.App("rai-email-generator")

image = modal.Image.debian_slim().pip_install(
    "openai", "supabase"
)

@app.function(image=image, secrets=[modal.Secret.from_name("rai-secrets")])
def process_new_leads_and_generate_emails():
    from supabase import create_client
    from openai import OpenAI

    supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    ai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Fetch leads with 'New' status that have a valid email
    try:
        response = supabase.table("leads").select("*").eq("status", "New").execute()
        leads = response.data
    except Exception as err:
        print(f"Error fetching leads: {err}")
        return "Failed to fetch leads."

    if not leads:
        print("No new leads found to process.")
        return "No new leads available."

    print(f"Found {len(leads)} new leads. Generating custom cold emails using GPT-4o-Mini...")

    for lead in leads:
        lead_id = lead.get("id")
        company_name = lead.get("company_name", "Roofing Contractor")
        website = lead.get("website", "")
        country = lead.get("country", "your local area")
        notes = lead.get("notes", "") or f"Roofing services provider located in {country}."

        print(f"\nProcessing AI Email for: {company_name} ({website})")

        # OpenAI Prompt strictly tailored to your 3-part layout requirement
        prompt = f"""
        You are Rai Shafqat Abbas, Founder & CEO of Rai Marketing Agency.
        Write a highly tailored, professional B2B cold email to a roofing business owner.

        TARGET BUSINESS DETAILS:
        Company Name: {company_name}
        Website: {website}
        Location/Country: {country}
        Website Insights/Scraped Context: {notes}

        AGENCY CONTACT INFO TO INCLUDE IN SIGNATURE:
        Name: Rai Shafqat Abbas
        Role: Founder & CEO
        Agency: Rai Marketing Agency
        Email: hello@raimarketingagency.online
        Phone: +92 316 6025651
        WhatsApp: https://wa.me/923166025651
        Website: https://raimarketingagency.online

        EMAIL STRUCTURE REQUIREMENTS:
        1. Subject Line: High-converting, direct, including their exact company name.
        2. Body Part 1 (Text Overview): Compliment their roofing work specifically based on their website context and state why you reached out.
        3. Body Part 2 (Problems & Solutions): Mention 3 specific digital growth challenges they likely face in {country} and explain exactly how Rai Marketing Agency solves them (Custom Landing Pages, Local SEO, Google/Meta Ads, AI Chatbots, CRM Follow-ups).
        4. Body Part 3 (Offer & Contact): Offer a FREE Roofing Marketing Audit with zero obligation. Include full signature details with links.

        STRICT RULES:
        - Professional, human tone.
        - Do NOT use emojis.
        - Format clear separate paragraphs.
        - Output JSON format with two keys: "subject" and "body".
        """

        try:
            ai_response = ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=700
            )

            import json
            result_json = json.loads(ai_response.choices[0].message.content)
            subject = result_json.get("subject", f"Helping {company_name} Generate More Qualified Roofing Projects")
            draft_email = result_json.get("body", "")

            # Update Supabase record with generated email and change status
            supabase.table("leads").update({
                "email_subject": subject,
                "draft_email": draft_email,
                "status": "Ready to Send"
            }).eq("id", lead_id).execute()

            print(f"SUCCESS: Generated email for {company_name} -> Saved as 'Ready to Send'")

        except Exception as err:
            print(f"Error generating email for {company_name}: {err}")

    return "All emails generated successfully!"

@app.local_entrypoint()
def main():
    res = process_new_leads_and_generate_emails.remote()
    print(res)