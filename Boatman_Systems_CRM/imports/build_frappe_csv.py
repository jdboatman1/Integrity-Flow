"""
Build a Frappe Data Import-compatible CSV for the Item doctype.
Input:  items_import.csv  (our cleaned flat CSV)
Output: items_frappe_import.csv  (Frappe multi-row template format)

Frappe data-import CSV structure:
  Row 1: "Data Import Template"
  Row 2: "Table:", "Item"
  Rows 3-7: notes / blank
  Row 8: "DocType:", "Item", ...column headers...
  Row 9: "Column Labels:", ...human labels...
  Row 10: "Column Name:", ...field names...   ← this is the key row
  Row 11: "Mandatory:", ...Yes/No...
  Row 12: "Type:", ...field types...
  Row 13: "Info:", ...hints...
  Row 14: "Start entering data below this line"
  Row 15+: data rows (first column blank = new record)

We only need the minimal set of columns we have data for.
stock_uom is mandatory → default "Nos" for all rows.
"""

import csv

SOURCE = "/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_import.csv"
OUTPUT = "/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_frappe_import.csv"

# Columns we will populate (order matches template expectation)
# (name is left blank = insert new record)
COLUMNS = [
    ("ID",                      "name",           "No",  "Data",     ""),
    ("Item Code",               "item_code",      "Yes", "Data",     ""),
    ("Item Group",              "item_group",     "Yes", "Link",     "Valid Item Group"),
    ("Default Unit of Measure", "stock_uom",      "Yes", "Link",     "Valid UOM"),
    ("Item Name",               "item_name",      "No",  "Data",     ""),
    ("Description",             "description",    "No",  "Text Editor", ""),
    ("Standard Selling Rate",   "standard_rate",  "No",  "Currency", ""),
    ("Disabled",                "disabled",       "No",  "Check",    "0 or 1"),
    ("Maintain Stock",          "is_stock_item",  "No",  "Check",    "0 or 1"),
    ("Allow Sales",             "is_sales_item",  "No",  "Check",    "0 or 1"),
    ("Allow Purchase",          "is_purchase_item","No", "Check",    "0 or 1"),
]

labels    = [c[0] for c in COLUMNS]
fieldnames= [c[1] for c in COLUMNS]
mandatory = [c[2] for c in COLUMNS]
types     = [c[3] for c in COLUMNS]
infos     = [c[4] for c in COLUMNS]

# Read our clean flat CSV
data_rows = []
with open(SOURCE, newline="", encoding="utf-8") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        data_rows.append(row)

with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, quoting=csv.QUOTE_ALL)

    # Header block
    w.writerow(["Data Import Template"])
    w.writerow(["Table:", "Item"])
    w.writerow([])
    w.writerow([])
    w.writerow(["Notes:"])
    w.writerow(["Please do not change the template headings."])
    w.writerow(["First data column must be blank."])
    w.writerow(["If you are uploading new records, leave the \"name\" (ID) column blank."])
    w.writerow(["DocType:", "Item"] + [""] * (len(COLUMNS) - 2))
    w.writerow(["Column Labels:"] + labels)
    w.writerow(["Column Name:"] + fieldnames)
    w.writerow(["Mandatory:"] + mandatory)
    w.writerow(["Type:"] + types)
    w.writerow(["Info:"] + infos)
    w.writerow(["Start entering data below this line"])

    # Data rows — first column (name/ID) left blank for insert
    for row in data_rows:
        out = [
            "",                             # name (blank = new record)
            row["item_code"],
            row["item_group"],
            "Nos",                          # stock_uom — mandatory default
            row["item_name"],
            row["description"],
            row["standard_rate"],
            row["disabled"],
            row["is_stock_item"],
            row["is_sales_item"],
            row["is_purchase_item"],
        ]
        w.writerow(out)

print(f"Written {len(data_rows)} data rows to {OUTPUT}")
