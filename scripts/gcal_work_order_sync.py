# ============================================================
# Frappe Server Script — Work Order → Google Calendar Sync
# DocType:   Work Order
# Event:     after_insert, on_update
#
# Paste this into ERPNext:
#   ERPNext → Settings → Server Script → New
#   DocType: Work Order
#   DocEvent: after_insert  (create a second one for on_update)
# ============================================================

import json, time, base64, hashlib, hmac
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError

CREDS_PATH = "/home/frappe/gcal_credentials.json"
CALENDAR_ID = "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
SCOPES = "https://www.googleapis.com/auth/calendar"


def _load_creds():
    with open(CREDS_PATH) as f:
        return json.load(f)


def _b64(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _get_token(creds):
    """Mint a short-lived OAuth2 access token from the service account."""
    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}))
    claim = _b64(json.dumps({
        "iss": creds["client_email"],
        "scope": SCOPES,
        "aud": creds["token_uri"],
        "iat": now,
        "exp": now + 3600,
    }))
    signing_input = f"{header}.{claim}".encode()

    # Sign with the private key using Python's built-in ssl / rsa via subprocess
    import subprocess, tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as kf:
        kf.write(creds["private_key"].encode())
        key_path = kf.name
    try:
        sig_b64 = subprocess.check_output(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=signing_input
        )
    finally:
        os.unlink(key_path)

    jwt = f"{header}.{claim}.{_b64(sig_b64)}"

    body = urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()
    req = Request(creds["token_uri"], data=body,
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = json.loads(urlopen(req).read())
    return resp["access_token"]


def _gcal_request(method, url, token, payload=None):
    data = json.dumps(payload).encode() if payload else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    req = Request(url, data=data, headers=headers, method=method)
    try:
        resp = urlopen(req)
        return json.loads(resp.read())
    except HTTPError as e:
        frappe.log_error(f"GCal API error {e.code}: {e.read().decode()}", "GCal Sync")
        return None


def sync_work_order_to_gcal(doc):
    """Create or update a Google Calendar event for this Work Order."""
    try:
        creds = _load_creds()
        token = _get_token(creds)
    except Exception as e:
        frappe.log_error(f"GCal auth failed: {e}", "GCal Sync")
        return

    # Build event datetimes — use scheduled_start_datetime if set, else today
    start_dt = str(getattr(doc, "scheduled_start_datetime", None) or
                   frappe.utils.now_datetime())
    end_dt   = str(getattr(doc, "scheduled_end_datetime", None) or
                   frappe.utils.add_to_date(start_dt, hours=2))

    # If date-only, convert to datetime
    if len(start_dt) == 10:
        start_dt += "T08:00:00"
        end_dt   += "T10:00:00"

    tz = "America/Chicago"

    customer = getattr(doc, "customer", "") or ""
    address  = getattr(doc, "customer_address", "") or ""
    tech     = getattr(doc, "assignee", "") or getattr(doc, "technician", "") or ""
    wo_type  = getattr(doc, "work_order_type", "") or getattr(doc, "custom_service_type", "") or ""

    # Look up customer phone number from Customer doctype
    phone = ""
    if customer:
        try:
            cust_doc = frappe.get_doc("Customer", customer)
            phone = (getattr(cust_doc, "mobile_no", "") or
                     getattr(cust_doc, "phone", "") or "")
        except Exception:
            pass

    # Build navigation links for the address
    from urllib.parse import quote
    addr_encoded = quote(address)
    maps_link  = f"https://maps.google.com/?q={addr_encoded}" if address else ""
    waze_link  = f"https://waze.com/ul?q={addr_encoded}" if address else ""

    nav_links = ""
    if address:
        nav_links = f"\n📍 Google Maps: {maps_link}\n🚗 Waze: {waze_link}"

    # Pull notes from common Work Order note fields
    notes = (getattr(doc, "notes", "") or
             getattr(doc, "description", "") or
             getattr(doc, "custom_notes", "") or "").strip()
    notes_section = f"\n\n📝 Notes:\n{notes}" if notes else ""

    event = {
        "summary": f"[WO-{doc.name}] {wo_type} — {customer}",
        "description": (
            f"Work Order: {doc.name}\n"
            f"Customer: {customer}\n"
            f"📞 Phone: {phone}\n"
            f"Address: {address}"
            f"{nav_links}\n"
            f"Technician: {tech}\n"
            f"Status: {doc.status}"
            f"{notes_section}\n\n"
            f"ERP Link: https://erp.aaairrigationservice.com/app/work-order/{doc.name}"
        ),
        "location": address,
        "start": {"dateTime": start_dt, "timeZone": tz},
        "end":   {"dateTime": end_dt,   "timeZone": tz},
        "colorId": "2" if doc.status == "Completed" else "5",  # green/yellow
    }

    base_url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"

    # Check if we already synced this WO (stored in custom field)
    existing_event_id = getattr(doc, "custom_gcal_event_id", None)

    if existing_event_id:
        result = _gcal_request("PUT", f"{base_url}/{existing_event_id}", token, event)
        action = "updated"
    else:
        result = _gcal_request("POST", base_url, token, event)
        action = "created"
        if result and result.get("id"):
            # Save the GCal event ID back to the Work Order (requires custom field)
            frappe.db.set_value("Work Order", doc.name,
                                "custom_gcal_event_id", result["id"])
            frappe.db.commit()

    if result:
        frappe.logger().info(f"GCal event {action} for WO {doc.name}: {result.get('id')}")


# ── Entry point called by Frappe ──
sync_work_order_to_gcal(doc)
