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

def on_quotation_insert(doc, method):
    """
    Auto-populate customer address and setup for approval workflow
    """
    # Auto-populate customer address - only for Customers
    if doc.quotation_to == "Customer" and doc.party_name and not doc.customer_address:
        try:
            # Get primary address for customer
            address = frappe.get_all(
                "Dynamic Link",
                filters={
                    "link_doctype": "Customer",
                    "link_name": doc.party_name,
                    "parenttype": "Address"
                },
                fields=["parent"],
                limit=1
            )
            
            if address:
                doc.customer_address = address[0].parent
                
                # Also set address display
                addr_doc = frappe.get_doc("Address", address[0].parent)
                doc.address_display = f"{addr_doc.address_line1}\\n{addr_doc.city}, {addr_doc.state} {addr_doc.pincode}"
                
                frappe.msgprint(f"✅ Address auto-populated from customer record")
        except Exception as e:
            frappe.log_error(f"Failed to auto-populate address: {str(e)}", "Address Auto-populate")

def send_schedule_portal_invite(doc, method):
    """
    Send portal invite when customer schedules appointment
    """
    # Only for Customers
    if doc.quotation_to != "Customer":
        return

    # Only send if this is a new quotation with scheduling info
    if not doc.get("custom_scheduled_date"):
        return
    
    # Get customer
    try:
        if not frappe.db.exists("Customer", doc.party_name):
            return
        customer = frappe.get_doc("Customer", doc.party_name)
    except:
        return
    
    # Check if customer has email
    if not customer.email_id:
        return
    
    # Check if we've already sent an invite
    existing_invites = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": "Customer",
            "reference_name": customer.name,
            "content": ["like", "%Portal invite email sent%"]
        }
    )
    
    if existing_invites:
        return
    
    # Get portal URL
    portal_url = frappe.db.get_single_value("Integrity Flow Settings", "portal_url") or "https://portal.aaairrigationservice.com"
    
    # Format scheduled date/time
    scheduled_date = frappe.format(doc.custom_scheduled_date, {'fieldtype': 'Date'})
    scheduled_time = doc.get("custom_scheduled_time") or "TBD"
    
    email_content = f"""
    <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background: #f4f7f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; padding: 40px;">
                <h1 style="color: #1b7abf; text-align: center;">AAA Irrigation Service</h1>
                <div style="background: #d1fae5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: #065f46;">✅ Appointment Scheduled!</h2>
                    <p>Thank you, {customer.customer_name}!</p>
                    <p><strong>Date:</strong> {scheduled_date}</p>
                    <p><strong>Time:</strong> {scheduled_time}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{portal_url}" style="background: #ea580c; color: white; padding: 15px 40px; text-decoration: none; border-radius: 10px; font-weight: 700;">Access Portal</a>
                </div>
                <p style="text-align: center; color: #a0aec0; font-size: 12px;">Powered by Boatman Systems™</p>
            </div>
        </body>
    </html>
    """
    
    try:
        frappe.sendmail(
            recipients=[customer.email_id],
            subject=f"Appointment Scheduled - Access Your Portal",
            message=email_content,
            delayed=False
        )
        
        customer.add_comment(
            "Comment",
            f"Portal invite email sent to {customer.email_id} (quotation {doc.name})"
        )
    except Exception as e:
        frappe.log_error(f"Failed to send schedule portal invite: {str(e)}", "Portal Invite Error")

def sync_to_gcal(doc, method):
    """
    Sync quotation to Google Calendar
    """
    if not doc.get("custom_scheduled_date"):
        return
    
    try:
        _sync_quotation_to_gcal(doc)
    except Exception as e:
        frappe.log_error(f"GCal sync failed for {doc.name}: {str(e)}", "GCal Sync Error")

def _load_creds():
    with open(CREDS_PATH) as f:
        return json.load(f)

def _b64(data):
    if isinstance(data, str):
        data = data.encode()
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _get_token(creds):
    """Mint a short-lived OAuth2 access token"""
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
        frappe.log_error(f"GCal API error {e.code}: {e.read().decode()}", "GCal Sync")
        return None

def _sync_quotation_to_gcal(doc):
    """Create or update Google Calendar event for quotation"""
    try:
        creds = _load_creds()
        token = _get_token(creds)
    except Exception as e:
        frappe.log_error(f"GCal auth failed: {e}", "GCal Sync")
        return

    # Build event datetime
    start_dt = str(doc.custom_scheduled_date) + "T09:00:00"
    end_dt = str(doc.custom_scheduled_date) + "T11:00:00"
    
    if doc.get("custom_scheduled_time"):
        time_map = {
            "9AM-11AM": ("09:00:00", "11:00:00"),
            "11AM-1PM": ("11:00:00", "13:00:00"),
            "1PM-3PM": ("13:00:00", "15:00:00"),
            "3PM-5PM": ("15:00:00", "17:00:00"),
        }
        times = time_map.get(doc.custom_scheduled_time, ("09:00:00", "11:00:00"))
        start_dt = str(doc.custom_scheduled_date) + "T" + times[0]
        end_dt = str(doc.custom_scheduled_date) + "T" + times[1]

    tz = "America/Chicago"

    customer = doc.party_name or ""
    
    # Get customer phone
    phone = ""
    if doc.quotation_to == "Customer":
        try:
            if frappe.db.exists("Customer", customer):
                cust_doc = frappe.get_doc("Customer", customer)
                phone = cust_doc.mobile_no or cust_doc.phone or ""
        except:
            pass
    elif doc.quotation_to == "Lead":
        try:
            if frappe.db.exists("Lead", customer):
                lead_doc = frappe.get_doc("Lead", customer)
                phone = lead_doc.mobile_no or lead_doc.phone_ext or ""
        except:
            pass

    # Get address
    address = ""
    if doc.get("customer_address"):
        try:
            addr_doc = frappe.get_doc("Address", doc.customer_address)
            address = f"{addr_doc.address_line1}, {addr_doc.city}, {addr_doc.state} {addr_doc.pincode}"
        except:
            pass

    addr_encoded = quote(address) if address else ""
    nav_links = ""
    if address:
        nav_links = f"\n📍 Google Maps: https://maps.google.com/?q={addr_encoded}\n🚗 Waze: https://waze.com/ul?q={addr_encoded}"

    event = {
        "summary": f"[{doc.name}] {customer}",
        "description": (
            f"Estimate: {doc.name}\n"
            f"Customer: {customer}\n"
            f"📞 Phone: {phone}\n"
            f"Address: {address}"
            f"{nav_links}\n\n"
            f"ERP Link: https://erp.aaairrigationservice.com/app/quotation/{doc.name}"
        ),
        "location": address,
        "start": {"dateTime": start_dt, "timeZone": tz},
        "end": {"dateTime": end_dt, "timeZone": tz},
        "colorId": "5",
    }

    base_url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    existing_event_id = doc.get("custom_gcal_event_id")

    if existing_event_id:
        result = _gcal_request("PUT", f"{base_url}/{existing_event_id}", token, event)
    else:
        result = _gcal_request("POST", base_url, token, event)
        if result and result.get("id"):
            frappe.db.set_value("Quotation", doc.name, "custom_gcal_event_id", result["id"])
            frappe.db.commit()
