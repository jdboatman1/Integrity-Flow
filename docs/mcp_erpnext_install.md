# ERPNext MCP Server — Install Summary

## Purpose

Connects Claude Code directly to the Integrity Flow ERPNext instance via MCP, enabling
creation and management of Customers, Contacts, Addresses, and other doctypes without a
custom import script.

## Instance Details

| Field       | Value                              |
|-------------|------------------------------------|
| Site name   | `erp.aaairrigationservice.com`     |
| Frappe URL  | `http://100.106.12.60:8080` (Tailscale) |
| Alt URL     | `http://96.126.117.73:8080` (public)    |
| Version     | Frappe/ERPNext v16.5.0 (Docker, Linode B) |

## MCP Server

- **Source:** `rakeshgangwar/erpnext-mcp-server` (TypeScript, API key auth)
- **Install path:** `/home/john/.local/share/mcp/erpnext-mcp-server`
- **Entry point:** `build/index.js`

### Why this server

Chosen over `Frappe_Assistant_Core` because it requires only API key credentials — no bench
app installation or OAuth setup needed.

## Installation Steps

```bash
# 1. Clone
mkdir -p ~/.local/share/mcp
cd ~/.local/share/mcp
git clone https://github.com/rakeshgangwar/erpnext-mcp-server.git

# 2. Build
cd erpnext-mcp-server
npm install
npm run build

# 3. Register with Claude Code
claude mcp add erpnext-integrity-flow \
  -e ERPNEXT_URL=http://100.106.12.60:8080 \
  -e ERPNEXT_API_KEY=<api-key> \
  -e ERPNEXT_API_SECRET=<api-secret> \
  -- node /home/john/.local/share/mcp/erpnext-mcp-server/build/index.js
```

Credentials are stored in `/home/john/.claude.json` (not committed to version control).

## Verification

In a new Claude Code session, the server `erpnext-integrity-flow` should be listed and the
following tools will be available:

- `get_doctypes` — list available doctypes
- `get_doctype_fields` — inspect fields for a doctype
- `get_documents` — query/list documents
- `create_document` — create a new document
- `update_document` — update an existing document
- `run_report` — run a saved ERPNext report

## Credentials

API key and secret are redacted here. Retrieve from:
- ERPNext: **Settings > My Profile > API Access**
- Or ask the Boatman Systems admin.
