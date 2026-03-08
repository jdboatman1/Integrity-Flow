# Item Import — Detailed Patterns & Notes

## Source File Format
- File: CUSTOMERLIST.txt (despite name, contains items not customers)
- Encoding: UTF-8, tab-delimited, single header row
- 125 data rows in the 2026-03-06 import run

## Column → Frappe Field Mapping
| QB Column       | Frappe Field      | Notes |
|----------------|-------------------|-------|
| Active Status  | disabled          | "Not-active" → 1, "Active" → 0 |
| Type           | item_group        | See group map below |
| Item           | item_code         | Required, unique |
| Description    | item_name + description | Blank → use item_code as fallback for item_name |
| Sales Tax Code | is_taxable        | "Tax" → 1, "Non" → 0 |
| Account        | (informational)   | Not mapped to Frappe field in current import |
| COGS Account   | (informational)   | Not mapped; only populated on a few rows |
| Price          | standard_rate     | See price cleaning rules |

## Type → item_group
- Service → "Services"
- Non-inventory Part → "Products"
- Other Charge → "Services"

## Price Cleaning Rules
- Blank or "0" → 0.0, no flag
- Percentage string (e.g. "-100%", "25%") → 0.0, soft warning in failed log
- Negative dollar value (e.g. "-20") → 0.0, soft warning in failed log
- Non-numeric string → 0.0, soft warning in failed log
- Positive numeric → use as-is

## Soft vs Hard Errors
- SOFT (flagged in failed log, still imported): price coercion issues
- HARD (excluded from import): missing item_code, missing/unknown Type, duplicate item_code
- If >10% hard errors: stop and report before proceeding

## Notable Items Requiring Attention Post-Import
- BD, war, WRITE OFF: QuickBooks write-off/bad debt items set to $0. Confirm with owner whether these should be disabled.
- Promo, Ref: Discount line items (-$20 in QB). Set to $0 in Frappe; may need a "Discount" item_group or pricing rule instead.
- CTR vs CTRL: Both are "Controller" items at different prices ($0 vs $150). Verify intended use with owner.
- w vs war: Both "Covered under warranty" at $0. Near-duplicate — may want to merge.
- Rotor vs rotor2: rotor2 is Not-active; both are "Hunter Rotor" at $55. rotor2 can stay disabled.
- Z16 description has trailing space: "(ZONE 16 )" — harmless but worth knowing.
- peb 150 has a space in item_code — valid in Frappe but unusual; confirm no import issues.

## Static Fields for All Items in This Import
- is_stock_item: 0
- is_sales_item: 1
- is_purchase_item: 0

## 2026-03-06 Run Results
- Total rows: 125
- Ready to import: 125 (0 hard errors)
- Soft warnings: 5 (BD, Promo, Ref, war, WRITE OFF — all price coercion)
- Disabled: 2 (rotor2, VALVE 2400T)
- item_group breakdown: Services=120, Products=5
- Taxable: 107 | Non-taxable: 18
- Items at $0 rate: 37
