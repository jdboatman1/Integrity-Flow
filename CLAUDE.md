# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the **master workspace** for the **AAA Irrigation Service Powered by Boatman Systems™** project. It is a hybrid of operational scripts, a static marketing site prototype, and documentation — not a traditional application codebase with a build system.

## Deployment

### Static Site → Linode B
The `setup_site/` directory is the prototype for `setup.aaairrigationservice.com`. Deploy it with:

```bash
bash scripts/deploy_to_linode.sh
```

Rsyncs `setup_site/` to `/var/www/setup.aaairrigationservice.com/` on Linode B (`96.126.117.73`) as the `deploy` user via SSH key at `/home/john/.ssh/id_gemini_cli`, then fixes permissions for `www-data`.

### Boatman AI™ Proxy → Linode B

```bash
bash scripts/deploy_proxy.sh
```

Uploads `scripts/ai_proxy.py` to `/opt/boatman/ai_proxy.py` and installs the systemd service `boatman-ai-proxy` (unit file: `scripts/ai_proxy.service`). After deployment, the script prints the Nginx `location` block you must manually add to the site config, then reload nginx. Check service logs with `journalctl -u boatman-ai-proxy`.

### SSH Access (Tailscale)
- **ERP Server (Linode B):** `ssh -i ~/.ssh/id_gemini_cli deploy@100.106.12.60`
- **User:** `deploy` (passwordless sudo)
- **AI Server (Linode A):** `100.68.151.50`, Ollama on port `11434` (host) / `11435` (Docker)

## Architecture

### `setup_site/` — Static Marketing Site
Vanilla HTML/CSS/JS. No framework, no build step. Key patterns:
- **Header:** Fixed 150px full-width stretched logo (`logo.svg`) with glassmorphism backdrop (`backdrop-filter: blur`)
- **Boatman AI™ widget:** Floating chat bubble (bottom-right) that POSTs to `https://setup.aaairrigationservice.com/api/ai/chat` and streams responses from Ollama on Linode A
- **Lead form:** Client-side only — on submit it hides the form and shows a success message. **No backend submission is wired up yet.**
- **CSS variables** defined in `:root` in `style.css` — always use these for colors, never hardcode

### `scripts/ai_proxy.py` — Boatman AI™ Proxy
Python stdlib HTTP server running on port `11436`. Two endpoints:
- `POST /api/ai/chat` — forwards `{message}` to Ollama (`tinyllama:latest`) and returns `{response}`
- `POST /api/lead` — creates a Frappe `Lead` via `http://127.0.0.1:8080/api/resource/Lead` using a hardcoded API token; requires `full_name` and `phone`

CORS is open (`*`). Logging goes to journald (silent `log_message`).

### `scripts/3cx_call_logging.py` — Frappe Server Script
Paste into Integrity Flow as a Server Script on `Communication` save. Uses the `frappe` global — **never `import frappe`**. Logic:
1. Look up `caller_id` against `Customer.mobile_no`
2. Fall back to `Lead.mobile_no`
3. If neither matches, flag as new caller for manual Lead creation

### `scripts/gcal_work_order_sync.py` — Frappe Server Script
Paste into Integrity Flow as a Server Script on `Work Order` `after_insert` and `on_update`. Uses a Google service account JSON at `/home/frappe/gcal_credentials.json` and mints OAuth2 tokens via `openssl` subprocess signing. Syncs to the calendar specified by `CALENDAR_ID`. Stores the created event ID in `custom_gcal_event_id` to enable updates instead of duplicates on subsequent saves.

### `Boatman_Systems_CRM/` — Documentation & Data Import
Blueprint and guides for the Integrity Flow CRM configuration. See `Boatman_Systems_CRM/CLAUDE.md` for full details. Key import scripts in `Boatman_Systems_CRM/imports/`:
- `transform_items.py` — QuickBooks tab-delimited export → `items_import.csv` / `items_failed.csv`
- `transform_customers.py` — Customer list → Frappe Customer CSV
- `build_frappe_csv.py` — Generic Frappe CSV builder helper
- `run_customer_update.py` — Incremental customer update (patches existing records)

Use the `erp-data-importer` sub-agent (`.claude/agents/erp-data-importer.md`) for all bulk import tasks — it carries institutional memory in `.claude/agent-memory/erp-data-importer/`.

## Branding Standards (apply to all UI work)
| Token | Value | Use |
|---|---|---|
| `--primary-blue` | `#1b7abf` | Primary UI, headers, links |
| `--trust-green` | `#059669` | TCEQ/licensed badges |
| `--action-orange` | `#ea580c` | CTA buttons |
| Typography | Inter, weight 900, italic | All headings, uppercase |

Every user-facing surface must display **"Powered by Boatman Systems™"**.

## Key Open Items
- **Lead form backend:** Wire the `#lead-form` POST to `POST /api/lead` on the AI proxy (already implemented in `ai_proxy.py`) to create Leads automatically
- **3CX script deployment:** The script in `scripts/3cx_call_logging.py` needs to be entered into Integrity Flow as a Server Script
- **GCal sync deployment:** `scripts/gcal_work_order_sync.py` needs to be entered into Integrity Flow as a Server Script (two entries: `after_insert` and `on_update`); requires `custom_gcal_event_id` custom field on Work Order
- **Synology backup pipeline:** Linode B → Synology NAS via Tailscale (not yet configured)
