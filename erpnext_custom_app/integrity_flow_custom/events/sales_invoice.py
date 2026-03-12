import frappe
import json
import time
import base64
import subprocess
import tempfile
import os
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote
from urllib.error import HTTPError

CREDS_PATH = "/home/frappe/gcal_credentials.json"
CALENDAR_ID = "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
SCOPES = "https://www.googleapis.com/auth/calendar"

def sync_to_gcal(doc, method):
    """
    Sync sales invoice to Google Calendar
    """
    try:
        _sync_invoice_to_gcal(doc)
    except Exception as e:
        frappe.log_error(f"GCal sync failed for invoice {doc.name}: {str(e)}", "GCal Sync Error")

def _load_creds():
    with open(CREDS_PATH) as f:
        return json.load(f)

def _b64(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _get_token(creds):
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
        frappe.log_error(f"GCal API error {e.code}", "GCal Sync")
        return None

def _sync_invoice_to_gcal(doc):
    """Create or update Google Calendar event for invoice"""
    try:
        creds = _load_creds()
        token = _get_token(creds)
    except Exception as e:
        frappe.log_error(f"GCal auth failed: {e}", "GCal Sync")
        return

    start_dt = str(doc.posting_date) + "T09:00:00"
    end_dt = str(doc.posting_date) + "T17:00:00"
    tz = "America/Chicago"

    customer = doc.customer or ""
    phone = ""
    try:
        cust_doc = frappe.get_doc("Customer", customer)
        phone = cust_doc.mobile_no or cust_doc.phone or ""
    except:
        pass

    address = ""
    if doc.get("customer_address"):
        try:
            addr_doc = frappe.get_doc("Address", doc.customer_address)
            address = f"{addr_doc.address_line1}, {addr_doc.city}, {addr_doc.state} {addr_doc.pincode}"
        except:
            pass

    event = {
        "summary": f"[INV-{doc.name}] {customer}",
        "description": (
            f"Invoice: {doc.name}\n"
            f"Customer: {customer}\n"
            f"📞 Phone: {phone}\n"
            f"Amount: ${doc.grand_total}\n"
            f"Status: {doc.status}\n\n"
            f"ERP Link: https://erp.aaairrigationservice.com/app/sales-invoice/{doc.name}"
        ),
        "location": address,
        "start": {"dateTime": start_dt, "timeZone": tz},
        "end": {"dateTime": end_dt, "timeZone": tz},
        "colorId": "2" if doc.status == "Paid" else "5",
    }

    base_url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    existing_event_id = doc.get("custom_gcal_event_id")

    if existing_event_id:
        _gcal_request("PUT", f"{base_url}/{existing_event_id}", token, event)
    else:
        result = _gcal_request("POST", base_url, token, event)
        if result and result.get("id"):
            frappe.db.set_value("Sales Invoice", doc.name, "custom_gcal_event_id", result["id"])
            frappe.db.commit()
