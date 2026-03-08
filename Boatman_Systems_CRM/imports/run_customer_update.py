"""
Bulk update Customer records from the prepared CSV.
Run via: bench --site erp.aaairrigationservice.com execute run_customer_update.main
Or pipe into bench console.

This script is designed to be executed inside the Frappe/bench environment
where `frappe` is available as a global.
"""
import csv
import os


def main():
    csv_path = "/tmp/customers_update.csv"
    if not os.path.exists(csv_path):
        print(f"ERROR: {csv_path} not found")
        return

    updated = 0
    skipped = 0
    errors = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Data starts at row 15 (index 14) per the template format
    data_rows = rows[14:]

    for i, row in enumerate(data_rows, start=15):
        if len(row) < 5:
            continue
        # Columns: 0=blank, 1=name, 2=mobile_no, 3=email_id, 4=custom_city
        customer_name = (row[1] or "").strip()
        mobile_no = (row[2] or "").strip()
        email_id = (row[3] or "").strip()
        custom_city = (row[4] or "").strip()

        if not customer_name:
            continue

        # Check if customer exists
        if not frappe.db.exists("Customer", customer_name):
            skipped += 1
            errors.append(f"Row {i}: Customer '{customer_name}' not found - skipped")
            continue

        try:
            updates = {}
            if mobile_no:
                updates["mobile_no"] = mobile_no
            if email_id:
                updates["email_id"] = email_id
            if custom_city:
                updates["custom_city"] = custom_city

            if updates:
                for field, value in updates.items():
                    frappe.db.set_value("Customer", customer_name, field, value, update_modified=False)
                updated += 1
        except Exception as e:
            skipped += 1
            errors.append(f"Row {i}: Customer '{customer_name}' error: {str(e)}")

    frappe.db.commit()

    print(f"\n=== Customer Update Complete ===")
    print(f"Total data rows processed: {len(data_rows)}")
    print(f"Successfully updated: {updated}")
    print(f"Skipped/errors: {skipped}")
    if errors:
        print(f"\nFirst 20 errors:")
        for e in errors[:20]:
            print(f"  {e}")
    print("================================\n")
