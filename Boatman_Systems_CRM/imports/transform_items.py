"""
QuickBooks Item List → Frappe/Integrity Flow Item CSV transformer
Source: CUSTOMERLIST.txt (tab-delimited QuickBooks export)
Output: items_import.csv  (Frappe Data Import Tool format)
Errors: items_failed.csv  (rows with data quality issues)

Run with: python3 transform_items.py
"""

import csv
import re
import os
from datetime import datetime

SOURCE = "/home/john/boatman-systems/Boatman_Systems_CRM/imports/CUSTOMERLIST.txt"
OUT_IMPORT = "/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_import.csv"
OUT_FAILED = "/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_failed.csv"

# ── Field mappings ────────────────────────────────────────────────────────────
TYPE_TO_GROUP = {
    "Service":             "Services",
    "Non-inventory Part":  "Products",
    "Other Charge":        "Services",
}

FRAPPE_FIELDS = [
    "item_code",
    "item_name",
    "item_group",
    "description",
    "standard_rate",
    "is_stock_item",
    "is_sales_item",
    "is_purchase_item",
    "disabled",
    "is_taxable",
]

FAILED_FIELDS = FRAPPE_FIELDS + ["source_price", "failure_reason"]

# ── Price cleaner ─────────────────────────────────────────────────────────────
PERCENTAGE_PATTERN = re.compile(r"^-?\d+(\.\d+)?%$")

def clean_price(raw):
    """
    Returns (numeric_value, flag_note_or_None).
    - Percentage strings like '-100%' or '25%'  → 0, flag
    - Negative dollar values like '-20'          → 0, flag
    - Normal numeric                             → float, None
    - Blank / non-numeric                        → 0, flag
    """
    if raw is None:
        return 0.0, "blank price → defaulted to 0"
    raw = str(raw).strip()
    if raw == "" or raw == "0":
        return 0.0, None
    if PERCENTAGE_PATTERN.match(raw):
        return 0.0, f"percentage price '{raw}' → set to 0"
    try:
        val = float(raw)
    except ValueError:
        return 0.0, f"non-numeric price '{raw}' → set to 0"
    if val < 0:
        return 0.0, f"negative price '{raw}' → set to 0"
    return val, None

# ── Main transform ────────────────────────────────────────────────────────────
def transform():
    good_rows = []
    failed_rows = []
    seen_codes = {}   # item_code → first row number (duplicate detection)
    raw_rows = []

    with open(SOURCE, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for lineno, row in enumerate(reader, start=2):   # start=2 because row 1 is header
            raw_rows.append((lineno, row))

    for lineno, row in raw_rows:
        issues = []

        active_status = (row.get("Active Status") or "").strip()
        item_type     = (row.get("Type") or "").strip()
        item_code     = (row.get("Item") or "").strip()
        description   = (row.get("Description") or "").strip()
        tax_code      = (row.get("Sales Tax Code") or "").strip()
        account       = (row.get("Account") or "").strip()
        cogs_account  = (row.get("COGS Account") or "").strip()
        raw_price     = (row.get("Price") or "").strip()

        # ── Required field checks ────────────────────────────────────────────
        if not item_code:
            issues.append("missing item_code (Item column blank)")

        if not item_type:
            issues.append("missing Type")

        if item_type not in TYPE_TO_GROUP and item_type:
            issues.append(f"unknown Type '{item_type}'")

        # ── Duplicate detection ──────────────────────────────────────────────
        if item_code:
            if item_code in seen_codes:
                issues.append(
                    f"duplicate item_code — first seen on row {seen_codes[item_code]}"
                )
            else:
                seen_codes[item_code] = lineno

        # ── Price cleaning ───────────────────────────────────────────────────
        rate, price_note = clean_price(raw_price)
        if price_note:
            issues.append(price_note)

        # ── Build output row ─────────────────────────────────────────────────
        item_name   = description if description else item_code
        item_group  = TYPE_TO_GROUP.get(item_type, "Services")
        disabled    = 1 if active_status == "Not-active" else 0
        is_taxable  = 1 if tax_code.lower() == "tax" else 0

        out = {
            "item_code":        item_code,
            "item_name":        item_name,
            "item_group":       item_group,
            "description":      description,
            "standard_rate":    rate,
            "is_stock_item":    0,
            "is_sales_item":    1,
            "is_purchase_item": 0,
            "disabled":         disabled,
            "is_taxable":       is_taxable,
        }

        if issues:
            failed_row = dict(out)
            failed_row["source_price"]  = raw_price
            failed_row["failure_reason"] = "; ".join(issues)
            failed_rows.append(failed_row)
            # Only send to failed list if there is a hard error (missing required field, duplicate).
            # Soft warnings (price coercion, negative price) still go to import list too.
            hard_errors = [i for i in issues if
                           "missing item_code" in i or
                           "missing Type" in i or
                           "unknown Type" in i or
                           "duplicate" in i]
            if not hard_errors:
                # Soft issue only — include in import with cleaned data
                good_rows.append(out)
        else:
            good_rows.append(out)

    # ── Write import CSV ─────────────────────────────────────────────────────
    with open(OUT_IMPORT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FRAPPE_FIELDS)
        writer.writeheader()
        writer.writerows(good_rows)

    # ── Write failed CSV ─────────────────────────────────────────────────────
    with open(OUT_FAILED, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FAILED_FIELDS)
        writer.writeheader()
        writer.writerows(failed_rows)

    # ── Summary ──────────────────────────────────────────────────────────────
    total = len(raw_rows)
    n_good = len(good_rows)
    n_failed_hard = sum(
        1 for r in failed_rows
        if any(k in r["failure_reason"] for k in
               ("missing item_code", "missing Type", "unknown Type", "duplicate"))
    )
    n_soft = len(failed_rows) - n_failed_hard
    n_disabled = sum(1 for r in good_rows if r["disabled"] == 1)
    n_zero_rate = sum(1 for r in good_rows if r["standard_rate"] == 0.0)
    n_taxable = sum(1 for r in good_rows if r["is_taxable"] == 1)
    n_non_taxable = sum(1 for r in good_rows if r["is_taxable"] == 0)

    groups = {}
    for r in good_rows:
        g = r["item_group"]
        groups[g] = groups.get(g, 0) + 1

    print("=" * 60)
    print("  QuickBooks → Frappe Item Import Summary")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"  Source file     : {os.path.basename(SOURCE)}")
    print(f"  Total rows read : {total}")
    print(f"  Ready to import : {n_good}")
    print(f"  Hard errors     : {n_failed_hard}  (excluded from import)")
    print(f"  Soft warnings   : {n_soft}  (included in import, flagged in failed log)")
    print()
    print("  Item groups breakdown:")
    for g, cnt in sorted(groups.items()):
        print(f"    {g}: {cnt}")
    print()
    print(f"  Disabled items  : {n_disabled}")
    print(f"  Taxable         : {n_taxable}")
    print(f"  Non-taxable     : {n_non_taxable}")
    print(f"  Items at $0 rate: {n_zero_rate}  (including Z1-Z24 zone items and discounts)")
    print()
    print("  Flagged rows (see items_failed.csv):")
    for r in failed_rows:
        print(f"    [{r['item_code'] or 'BLANK'}] {r['failure_reason']}")
    print()
    print(f"  Output → {OUT_IMPORT}")
    print(f"  Errors → {OUT_FAILED}")
    print("=" * 60)

if __name__ == "__main__":
    transform()
