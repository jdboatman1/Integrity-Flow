# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Documentation, blueprints, and data import tooling for **AAA Irrigation Service Powered by Boatman Systems™** — a Field Service Management & CRM system built on **Integrity Flow** (Frappe/ERPNext v16.5.0).

Key documents:
- `CRM=Powered-By-Boatman-systems.md` — Master blueprint; authoritative reference for architecture, progress log, and next steps
- `Email-Setup-Guide.md` — SMTP/Yahoo/Cloudflare configuration for Integrity Flow outgoing mail

## Integrity Flow (Linode B) Access

```bash
ssh -i ~/.ssh/id_gemini_cli deploy@100.106.12.60
sudo docker exec frappe_docker-backend-1 bench --site erp.aaairrigationservice.com <cmd>
```

- Container: `frappe_docker-backend-1` | Site: `erp.aaairrigationservice.com`
- Sites volume: `frappe_docker_sites` (mounted at `/home/frappe/frappe-bench/sites` inside container)
- `frappe.db.get_all()` — use this in bench execute; `frappe.client.get_list()` does not accept kwargs in v16
- **Never `import frappe`** — it is a global inside Server Scripts only

## Data Import Workflow

Source data lives in `imports/`. The standard flow:

1. Run the transform script to produce a cleaned CSV and `*_failed.csv` log
2. Owner reviews both files before any bench import runs
3. SSH to Linode B and run bench import only after approval

Transform scripts:
- `imports/transform_items.py` — QuickBooks tab-delimited export → `items_import.csv` / `items_failed.csv`
- `imports/transform_customers.py` — Customer list → Frappe Customer CSV
- `imports/build_frappe_csv.py` — Generic Frappe CSV builder helper
- `imports/run_customer_update.py` — Incremental customer update (patches existing records)

**Bench import command:**
```bash
sudo docker exec frappe_docker-backend-1 bench --site erp.aaairrigationservice.com import-csv \
  /home/frappe/frappe-bench/sites/erp.aaairrigationservice.com/<file>.csv --doctype <Doctype>
```

Use the `erp-data-importer` sub-agent (`.claude/agents/erp-data-importer.md`) for all bulk import tasks — it carries institutional knowledge from prior import runs in `.claude/agent-memory/erp-data-importer/`.

### QuickBooks Source File Notes

`imports/CUSTOMERLIST.txt` is tab-delimited (despite the name, it contains items). Column → Frappe field mapping:

| QB Column | Frappe Field | Notes |
|---|---|---|
| Active Status | `disabled` | "Not-active" → 1 |
| Type | `item_group` | Service/Other Charge → "Services"; Non-inventory Part → "Products" |
| Item | `item_code` | Required, unique |
| Description | `item_name` + `description` | Blank → fall back to `item_code` |
| Sales Tax Code | `is_taxable` | "Tax" → 1, "Non" → 0 |
| Price | `standard_rate` | Percentage strings and negatives → coerce to 0, log as soft warning |

All QB items imported as non-stock, sales-only (`is_stock_item=0`, `is_sales_item=1`, `is_purchase_item=0`).

## CRM Pipeline (never skip stages)

`Lead` → `Quotation` (Estimate) → `Sales Order` → `Sales Invoice`

- Signed estimate auto-triggers Sales Order + Invoice creation
- Sales Invoice creation pushes to technician's Google Calendar

**Full pipeline spec** (custom fields, automation, open items): [`ERP-Pipeline.md`](./ERP-Pipeline.md)

## Core Doctypes

`Lead`, `Opportunity`, `Quotation`, `Sales Order`, `Sales Invoice`, `Communication`, `Customer`

## Custom Fields

- **Customer:** `custom_controller_brand`, `custom_controller_model`, `custom_zone_count`, `custom_backflow_type`, `custom_tceq_license_number`, `custom_property_size`
- **Communication:** call start time, duration, date (populated by 3CX script at `../scripts/3cx_call_logging.py`)

`mobile_no` on Customer must match what 3CX sends for caller ID lookup — keep format consistent.

## Roles & Permissions

| Role | Access |
|---|---|
| Technician | Mobile/job view only — no financials |
| Office Admin | Full pipeline |
| Customer | Portal only (estimates, invoices, work history) |
| Owner | Full access + reporting |

## Branding

- Colors: `#1b7abf` (primary blue), `#059669` (TCEQ trust green), `#ea580c` (CTA orange)
- Typography: Inter Black, heavy italic, uppercase headings
- All UI, print formats, and portal pages must display **"Powered by Boatman Systems™"**
