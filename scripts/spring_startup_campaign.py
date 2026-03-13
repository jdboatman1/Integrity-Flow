"""
Spring Startup Campaign — AAA Irrigation Service Powered by Boatman Systems™
Processes march7.csv to identify customers for the Spring Startup email campaign.
Generates a 'campaign_list.csv' and a Frappe-ready script to queue emails.
"""

import csv
import os

SOURCE = "Boatman_Systems_CRM/imports/march7.csv"
CAMPAIGN_CSV = "Boatman_Systems_CRM/imports/spring_startup_campaign.csv"
TEMPLATE_PATH = "templates/spring_startup_campaign.html"

# QB column indices
COL_CUSTOMER = 1
COL_EMAIL = 6
COL_MOBILE = 14
COL_MAIN_PHONE = 11

def get(row, idx):
    try:
        return row[idx].strip()
    except IndexError:
        return ""

def load_template():
    with open(TEMPLATE_PATH, "r") as f:
        return f.read()

def main():
    if not os.path.exists(SOURCE):
        print(f"Error: Source file {SOURCE} not found.")
        return

    campaign_data = []
    total_processed = 0

    with open(SOURCE, encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        next(reader)  # skip header

        for i, row in enumerate(reader, start=2):
            name = get(row, COL_CUSTOMER)
            email = get(row, COL_EMAIL)
            
            if not name or not email or "@" not in email:
                continue

            phone = get(row, COL_MOBILE) or get(row, COL_MAIN_PHONE)
            
            campaign_data.append({
                "customer_name": name,
                "email_id": email,
                "phone": phone
            })
            total_processed += 1

    # Write campaign CSV
    with open(CAMPAIGN_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["customer_name", "email_id", "phone"])
        writer.writeheader()
        writer.writerows(campaign_data)

    print(f"Campaign Data Generated:")
    print(f"  Total Customers with Emails: {total_processed}")
    print(f"  Output: {CAMPAIGN_CSV}")
    print(f"  Template: {TEMPLATE_PATH}")
    print("\nNext Step: Run the following script on Linode B to queue emails.")

if __name__ == "__main__":
    main()
