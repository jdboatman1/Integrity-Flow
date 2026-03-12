# ERP Pipeline — AAA Irrigation Service Powered by Boatman Systems™

## Pipeline Overview

```
Lead → Quotation (Estimate) → Sales Order → Sales Invoice
```

Never skip stages. Each stage has automation that depends on the prior stage being complete.

---

## Stage 1: Lead

**Doctype:** `Lead`

### Custom Fields
| Field | Type | Purpose |
|---|---|---|
| `custom_address_line1` | Data | Street address |
| `custom_city` | Data | City |
| `custom_state` | Data | State |
| `custom_zip` | Data | ZIP code |
| `custom_email` | Data | CC email |
| `custom_service_description` | Small Text | What the customer needs |

### Automation
- **3CX inbound call** → `scripts/3cx_call_logging.py` (Server Script on `Communication` `before_save`):
  1. Looks up caller ID against `Customer.mobile_no`
  2. Falls back to `Lead.mobile_no`
  3. If no match → auto-creates new Lead (uses CNAM name, never phone number as name)
- **Boatman AI™ website chat** → `POST /api/lead` on the AI proxy auto-creates a Lead from the contact form

---

## Stage 2: Quotation (Estimate)

**Doctype:** `Quotation`

### Custom Fields
| Field | Type | Purpose |
|---|---|---|
| `custom_scheduled_date` | Date | Appointment date |
| `custom_scheduled_time` | Select | Time slot: 9AM–11AM, 11AM–1PM, 1PM–3PM, 3PM–5PM |
| `custom_scheduled_time_open` | Time | Exact time (alternative to slot) |
| `custom_technician` | Link | Assigned technician |
| `custom_gcal_event_id` | Data | Google Calendar event ID (for update tracking) |
| `custom_same_as_service_address` | Check | Address shortcut |
| `custom_service_description` | Small Text | Job notes / scope of work |
| `parent_customer` | Link | Parent account (for multi-property customers) |

### Automation
- **`sync_estimate_to_gcal()`** in `erpnext_3cx/api.py` (whitelisted):
  - Fires from Server Script on Quotation save
  - Pushes appointment to Google Calendar with customer phone, address, Maps/Waze nav links, ERP deep link
  - Stores event ID in `custom_gcal_event_id` — subsequent saves update the event instead of creating duplicates
- **Tech Schedule page** (`/app/tech-schedule`):
  - Day/Week grid view of all Quotations by technician and time slot
  - Available cells clickable to create new Quotation with pre-filled date/time/tech
  - Unassigned jobs (no `custom_technician`) shown in warning section

---

## Stage 3: Sales Order

**Doctype:** `Sales Order`

### Custom Fields
| Field | Type | Purpose |
|---|---|---|
| `exempt_from_sales_tax` | Check | Tax exemption flag |

### Automation
- Triggered by signed/submitted Quotation → auto-creates Sales Order
- *(Full auto-trigger not yet wired — currently manual)*

---

## Stage 4: Sales Invoice

**Doctype:** `Sales Invoice`

### Custom Fields
| Field | Type | Purpose |
|---|---|---|
| `custom_same_as_service_address` | Check | Address shortcut |
| `exempt_from_sales_tax` | Check | Tax exemption flag |
| `parent_customer` | Link | Parent account |
| `custom_gcal_event_id` | Data | Google Calendar event ID |

### Automation
- GCal sync fires on `after_insert` and `on_update` (script: `scripts/gcal_work_order_sync.py` — to be re-targeted to Sales Invoice)
- Final billable document — pipeline ends here

---

## Supporting Systems

### 3CX Call Logging
- **Script:** `scripts/3cx_call_logging.py`
- **Deployment:** Integrity Flow → Server Script → Doctype: `Communication` → Event: `before_save`
- **Status:** Needs deployment

### Google Calendar Sync (Estimate)
- **Function:** `erpnext_3cx.api.sync_estimate_to_gcal`
- **Deployment:** Live — `@frappe.whitelist()` confirmed on `api.py`
- **Calendar:** `svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com`
- **Credentials:** `/home/frappe/gcal_credentials.json` (service account, JWT/OAuth2 via OpenSSL)

### Google Calendar Sync (Invoice/Job)
- **Script:** `scripts/gcal_work_order_sync.py`
- **Deployment:** Integrity Flow → Server Script → Doctype: `Sales Invoice` → Events: `after_insert`, `on_update`
- **Status:** Needs deployment (and re-targeting from Work Order to Sales Invoice)

### Tech Schedule Page
- **URL:** `/app/tech-schedule`
- **App:** `erpnext_3cx`
- **Roles:** System Manager, Sales Manager, Sales User
- **Status:** Live

---

## Customer Custom Fields

These live on the `Customer` doctype and carry over to all pipeline documents:

| Field | Purpose |
|---|---|
| `custom_controller_brand` | Irrigation controller brand |
| `custom_controller_model` | Controller model |
| `custom_zone_count` | Number of irrigation zones |
| `custom_backflow_type` | Backflow preventer type |
| `custom_tceq_license_number` | TCEQ license on file |
| `custom_property_size` | Property size |

---

## Roles & Permissions

| Role | Access |
|---|---|
| Technician | Mobile/job view only — no financials |
| Office Admin | Full pipeline |
| Customer | Portal only (estimates, invoices, job history) |
| Owner | Full access + reporting |

---

## Open Items

| Item | Status |
|---|---|
| 3CX Server Script deployment | Pending |
| GCal sync → Sales Invoice re-target | Pending |
| Signed Quotation → auto Sales Order + Invoice | Pending |
| Synology backup pipeline (Linode B → NAS) | Pending |

---

*Last updated: 2026-03-12 — Work Order removed from pipeline; Sales Invoice is the terminal stage.*
