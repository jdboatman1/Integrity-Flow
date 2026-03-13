"""
Frappe Server Script — Queue Spring Startup Emails
Run via: bench --site erp.aaairrigationservice.com execute queue_spring_campaign.main
Requires: /tmp/spring_startup_campaign.csv and /tmp/spring_startup_campaign.html
"""

import frappe
import csv
import os

CAMPAIGN_CSV = "/tmp/spring_startup_campaign.csv"
TEMPLATE_PATH = "/tmp/spring_startup_campaign.html"
PORTAL_URL = "https://erp.aaairrigationservice.com"  # Base portal URL

def main():
    if not os.path.exists(CAMPAIGN_CSV):
        print(f"Error: Campaign CSV {CAMPAIGN_CSV} not found.")
        return

    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: Template HTML {TEMPLATE_PATH} not found.")
        return

    with open(TEMPLATE_PATH, "r") as f:
        template_html = f.read()

    count = 0
    with open(CAMPAIGN_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer_name = row["customer_name"]
            email_id = row["email_id"]
            
            if not email_id or "@" not in email_id:
                continue

            # Personalize template
            # In a real system, we might generate a real magic link token here
            # For now, we point to the portal login page
            msg = template_html.replace("{{ PORTAL_URL }}", PORTAL_URL)
            msg = msg.replace("{doc.customer_name}", customer_name) # Fallback for common templates

            try:
                # Queue the email via Frappe
                frappe.sendmail(
                    recipients=[email_id],
                    subject="Time for Your Annual Spring Startup - AAA Irrigation Service",
                    message=msg,
                    delayed=True,  # Queue it to avoid timing out the script
                    reference_doctype="Customer",
                    reference_name=customer_name if frappe.db.exists("Customer", customer_name) else None
                )
                count += 1
                if count % 100 == 0:
                    print(f"Queued {count} emails...")
                    frappe.db.commit() # Commit periodically
            except Exception as e:
                print(f"Failed to queue email for {email_id}: {str(e)}")

    frappe.db.commit()
    print(f"Successfully queued {count} Spring Startup emails.")
