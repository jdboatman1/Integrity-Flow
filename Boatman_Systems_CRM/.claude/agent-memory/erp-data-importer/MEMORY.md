# ERP Data Importer — Agent Memory

## Item Import Patterns
See `item-import.md` for full detail.

- QuickBooks tab-delimited exports use column order: Active Status, Type, Item, Description, Sales Tax Code, Account, COGS Account, Price
- Type → item_group mapping: Service→"Services", Non-inventory Part→"Products", Other Charge→"Services"
- Price "-100%" and "war"-style percentage discounts must be coerced to 0 and flagged (not hard errors)
- Negative dollar prices (e.g. -20 for Promo/Ref discount items) also coerced to 0 and flagged
- Blank Description → fall back to item_code for item_name
- All QB item types here are non-stock (is_stock_item=0), sales only (is_sales_item=1, is_purchase_item=0)
- Z1–Z24 zone line items: valid at $0 rate, keep all; note Z14–Z24 have "Non" tax code unlike Z1–Z13

## Confirmed Import File Locations
- Source: `/home/john/boatman-systems/Boatman_Systems_CRM/imports/CUSTOMERLIST.txt`
- Items import CSV: `/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_import.csv`
- Items failed log: `/home/john/boatman-systems/Boatman_Systems_CRM/imports/items_failed.csv`
- Transform script: `/home/john/boatman-systems/Boatman_Systems_CRM/imports/transform_items.py`

## Integrity Flow Site on Linode B
- Frappe runs in Docker via frappe_docker compose stack (NOT a bare bench install)
- Backend container: `frappe_docker-backend-1`
- Site name: `erp.aaairrigationservice.com`
- Sites volume: `frappe_docker_sites` (mounted at `/home/frappe/frappe-bench/sites` inside container)
- Bench commands run as: `sudo docker exec frappe_docker-backend-1 bench --site erp.aaairrigationservice.com <cmd>`
- ERPNext version: v16.5.0

## Item Groups Confirmed in Integrity Flow
Both required groups already exist — no creation needed before import:
- "Services" (confirmed 2026-03-06)
- "Products" (confirmed 2026-03-06)

## Owner Decisions Applied 2026-03-06
- CTR removed, CTRL kept (Controller $150) — merge decision
- "w" removed, "war" kept (Covered under warranty $0) — merge decision
- Z1–Z24 zone items removed from import CSV entirely
- BD / WRITE OFF accounting items: left as-is at $0

## Final items_import.csv State (post-owner-decisions)
- 99 data rows (125 original − 24 zones − 1 CTR − 1 w)
- Ready to import to erp.aaairrigationservice.com

## Workflow: Do Not Import Until User Reviews CSV
Always produce cleaned CSV + failed log first. User reviews, then we SSH to Linode B and run bench import.
