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

This rsyncs `setup_site/` to Linode B (`96.126.117.73`) as the `deploy` user via the SSH key at `/home/john/.ssh/id_gemini_cli`, then fixes permissions for `www-data`.

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

### `scripts/3cx_call_logging.py` — Frappe Server Script
This is a **Frappe/ERPNext server-side script**, not a standalone Python file. It must be pasted into an Integrity Flow "Server Script" doctype triggered on `Communication` save (`doc_event: on_submit` or `before_save`). It uses the `frappe` global — do not `import frappe`. Logic flow:
1. Look up `caller_id` against `Customer.mobile_no`
2. Fall back to `Lead.mobile_no`
3. If neither matches, flag as new caller for manual Lead creation

### `Boatman_Systems_CRM/` — Documentation
Blueprint and guides for the Integrity Flow CRM configuration. See `Boatman_Systems_CRM/CLAUDE.md` for details.

## Branding Standards (apply to all UI work)
| Token | Value | Use |
|---|---|---|
| `--primary-blue` | `#1b7abf` | Primary UI, headers, links |
| `--trust-green` | `#059669` | TCEQ/licensed badges |
| `--action-orange` | `#ea580c` | CTA buttons |
| Typography | Inter, weight 900, italic | All headings, uppercase |

Every user-facing surface must display **"Powered by Boatman Systems™"**.

## Key Open Items
- **Lead form backend:** Wire the `#lead-form` POST to the Integrity Flow REST API to create Leads automatically
- **Boatman AI proxy:** Proxy script at `scripts/ai_proxy.py` (Python stdlib, port `11436`). Deploy with `bash scripts/deploy_proxy.sh` — it installs the systemd service and prints the Nginx `location` block to add manually
- **3CX script deployment:** The script in `scripts/3cx_call_logging.py` needs to be entered into Integrity Flow as a Server Script
- **Synology backup pipeline:** Linode B → Synology NAS via Tailscale (not yet configured)
