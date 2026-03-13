"""
Transform march7.csv (QuickBooks export) into a Frappe Data Import UPDATE CSV
for the Customer doctype.

Updates existing customers with: contact info and address fields.
Matches on document name (ID) = Customer column from QB export.

Input:  march7.csv
Output: customers_update.csv   — Frappe Data Import format (Update mode)
        customers_failed.csv   — rows skipped and why
"""

import csv
import re
import os

SOURCE  = "Boatman_Systems_CRM/imports/march7.csv"
OUTPUT  = "Boatman_Systems_CRM/imports/customers_update.csv"
FAILED  = "Boatman_Systems_CRM/imports/customers_failed.csv"

# QB column indices (0-based)
COL_CUSTOMER   = 1
COL_ALT_PHONE  = 5
COL_EMAIL      = 6
COL_FIRST      = 9
COL_LAST       = 10
COL_MAIN_PHONE = 11
COL_MOBILE     = 14
COL_STREET1    = 15
COL_STREET2    = 16
COL_CITY       = 17
COL_STATE      = 18
COL_ZIP        = 19

# Garbage customer names to skip - very targeted
GARBAGE = {"", ".", "+", "dl", "k\\", r"=\]p;[", "name"}

def clean_phone(raw):
    """Strip everything except digits; return 10-digit string or empty."""
    digits = re.sub(r"\D", "", str(raw) or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits if len(digits) == 10 else ""

def get(row, idx):
    try:
        val = row[idx].strip()
        # Some QB exports have placeholders like "N/A"
        if val.upper() in ["N/A", "NONE", "UNKNOWN"]:
            return ""
        return val
    except IndexError:
        return ""

# --- Read source ---
data_rows = []
failed_rows = []

if not os.path.exists(SOURCE):
    print(f"Error: Source file {SOURCE} not found.")
    exit(1)

with open(SOURCE, encoding="utf-8-sig", newline="") as fh:
    reader = csv.reader(fh)
    next(reader)  # skip header

    for i, row in enumerate(reader, start=2):
        name = get(row, COL_CUSTOMER)

        # Skip only the most obvious garbage
        if name in GARBAGE:
            failed_rows.append({"source_row": i, "customer": name, "reason": "garbage name placeholder"})
            continue

        # Suspect very short names that aren't letters
        if len(name) < 2 and not name.isalpha():
            failed_rows.append({"source_row": i, "customer": name, "reason": "suspect short name"})
            continue

        # Phone: prefer Mobile, fall back to Main Phone, then Alt Phone
        phone = clean_phone(get(row, COL_MOBILE)) \
             or clean_phone(get(row, COL_MAIN_PHONE)) \
             or clean_phone(get(row, COL_ALT_PHONE))

        email = get(row, COL_EMAIL)
        
        # Address parts
        street1 = get(row, COL_STREET1)
        street2 = get(row, COL_STREET2)
        city    = get(row, COL_CITY)
        state   = get(row, COL_STATE)
        zip_code= get(row, COL_ZIP)
        
        address = street1
        if street2:
            address += f", {street2}"

        # We keep the row even if it's "low data" now, to ensure ERP coverage
        data_rows.append({
            "name":       name,
            "mobile_no":  phone,
            "email_id":   email,
            "address":    address,
            "city":       city,
            "state":      state,
            "zip":        zip_code,
        })

# --- Write Frappe Data Import CSV (Update) ---
COLUMNS = [
    # (label,          fieldname,    mandatory, type,   info)
    ("ID",             "name",       "Yes", "Data",     "Must match existing Customer name"),
    ("Mobile No",      "mobile_no",  "No",  "Data",     "10 digits"),
    ("Email Id",       "email_id",   "No",  "Data",     ""),
    ("Address Line 1", "custom_address_line1","No", "Data", ""),
    ("City",           "custom_city", "No", "Data", ""),
    ("State",          "custom_state","No", "Data", ""),
    ("ZIP Code",       "custom_zip",  "No", "Data", ""),
]

labels    = [c[0] for c in COLUMNS]
fieldnames= [c[1] for c in COLUMNS]
mandatory = [c[2] for c in COLUMNS]
types     = [c[3] for c in COLUMNS]
infos     = [c[4] for c in COLUMNS]

with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL)
    w.writerow(["Data Import Template"])
    w.writerow(["Table:", "Customer"])
    w.writerow([])
    w.writerow([])
    w.writerow(["Notes:"])
    w.writerow(["Update mode — ID must match existing Customer name exactly."])
    w.writerow(["First data column must be blank."])
    w.writerow(["DocType:", "Customer"] + [""] * (len(COLUMNS) - 2))
    w.writerow(["Column Labels:"] + labels)
    w.writerow(["Column Name:"] + fieldnames)
    w.writerow(["Mandatory:"] + mandatory)
    w.writerow(["Type:"] + types)
    w.writerow(["Info:"] + infos)
    w.writerow(["Start entering data below this line"])

    for row in data_rows:
        w.writerow([
            "",                  # first column blank (required by Frappe template)
            row["name"],
            row["mobile_no"],
            row["email_id"],
            row["address"],
            row["city"],
            row["state"],
            row["zip"],
        ])

# --- Write failed log ---
with open(FAILED, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["source_row", "customer", "reason"])
    w.writeheader()
    w.writerows(failed_rows)

# --- Summary ---
has_phone = sum(1 for r in data_rows if r["mobile_no"])
has_email = sum(1 for r in data_rows if r["email_id"])
has_addr  = sum(1 for r in data_rows if r["address"])

print(f"Source rows:     {len(data_rows) + len(failed_rows)}")
print(f"Valid rows:      {len(data_rows)}")
print(f"  with phone:    {has_phone}")
print(f"  with email:    {has_email}")
print(f"  with address:  {has_addr}")
print(f"Skipped (failed):{len(failed_rows)}")
print(f"Output:          {OUTPUT}")
print(f"Failed log:      {FAILED}")
