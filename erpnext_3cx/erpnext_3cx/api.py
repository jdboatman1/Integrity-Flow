import re
import json
import time
import base64
import frappe

@frappe.whitelist(allow_guest=True)
def screen_pop(number=None):
    raw = number or ""
    digits = re.sub(r"\D+", "", raw)
    n = digits[-10:] if len(digits) > 10 else digits

    rows = frappe.db.sql(
        "select parent from `tabContact Phone` where phone like %s limit 1",
        (f"%{n}%",),
    )
    if rows:
        contact = rows[0][0]
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/app/contact/{contact}"
        return

    for field in ("phone", "mobile_no"):
        lead = frappe.db.get_value("Lead", {field: ["like", f"%{n}%"]}, "name")
        if lead:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = f"/app/lead/{lead}"
            return

    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/app/lead/new?phone={raw}&mobile_no={raw}&first_name=&lead_name="


@frappe.whitelist()
def get_schedule_data(date=None, view_type='Day'):
    import datetime as dt
    if not date:
        date = frappe.utils.today()
    target = frappe.utils.getdate(date)
    if view_type == 'Week':
        day_of_week = target.weekday()
        start_date = target - dt.timedelta(days=day_of_week)
        end_date = start_date + dt.timedelta(days=6)
    else:
        start_date = target
        end_date = target

    time_slots = ['9AM - 11AM', '11AM - 1PM', '1PM - 3PM', '3PM - 5PM']
    tech_rows = frappe.db.sql("""
        SELECT DISTINCT custom_technician FROM `tabQuotation`
        WHERE custom_technician IS NOT NULL AND custom_technician != '' AND docstatus != 2
        ORDER BY custom_technician
    """, as_list=True)
    techs = [r[0] for r in tech_rows] if tech_rows else []
    bookings = frappe.db.sql("""
        SELECT name, party_name, custom_scheduled_date,
               custom_scheduled_time, custom_scheduled_time_open,
               custom_technician, order_type, status, shipping_address_name
        FROM `tabQuotation`
        WHERE docstatus != 2 AND custom_scheduled_date IS NOT NULL
          AND custom_scheduled_date BETWEEN %s AND %s
        ORDER BY custom_scheduled_date, custom_scheduled_time
    """, (start_date, end_date), as_dict=True)
    for b in bookings:
        if b.get('custom_scheduled_date'):
            b['custom_scheduled_date'] = str(b['custom_scheduled_date'])
    return {'techs': techs, 'bookings': bookings, 'time_slots': time_slots}


@frappe.whitelist()
def sync_estimate_to_gcal(doc):
    """Sync a Quotation to Google Calendar. Called from Server Script."""
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    from urllib.parse import urlencode, quote

    CREDS_PATH  = "/home/frappe/gcal_credentials.json"
    CALENDAR_ID = "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
    SCOPES      = "https://www.googleapis.com/auth/calendar"

    TIME_WINDOWS = {
        "9AM - 11AM":  ("09:00:00", "11:00:00"),
        "11AM - 1PM":  ("11:00:00", "13:00:00"),
        "1PM - 3PM":   ("13:00:00", "15:00:00"),
        "3PM - 5PM":   ("15:00:00", "17:00:00"),
    }

    if not getattr(doc, "custom_scheduled_date", None):
        return

    try:
        with open(CREDS_PATH) as f:
            creds = json.load(f)
    except Exception as e:
        frappe.log_error(f"GCal creds load failed: {e}", "GCal Estimate Sync")
        return

    # Mint OAuth2 token
    try:
        import subprocess, tempfile, os
        now = int(time.time())
        def b64enc(data):
            if isinstance(data, str): data = data.encode()
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()
        header = b64enc(json.dumps({"alg": "RS256", "typ": "JWT"}))
        claim  = b64enc(json.dumps({
            "iss": creds["client_email"], "scope": SCOPES,
            "aud": creds["token_uri"], "iat": now, "exp": now + 3600,
        }))
        signing_input = f"{header}.{claim}".encode()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pem") as kf:
            kf.write(creds["private_key"].encode())
            key_path = kf.name
        try:
            sig = subprocess.check_output(["openssl", "dgst", "-sha256", "-sign", key_path], input=signing_input)
        finally:
            os.unlink(key_path)
        jwt = f"{header}.{claim}.{b64enc(sig)}"
        body = urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}).encode()
        req  = Request(creds["token_uri"], data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = json.loads(urlopen(req).read())["access_token"]
    except Exception as e:
        frappe.log_error(f"GCal token failed: {e}", "GCal Estimate Sync")
        return

    tz = "America/Chicago"
    sched_date = str(doc.custom_scheduled_date)
    window = getattr(doc, "custom_scheduled_time", None)
    open_time = getattr(doc, "custom_scheduled_time_open", None)

    if window and window in TIME_WINDOWS:
        start_t, end_t = TIME_WINDOWS[window]
    elif open_time:
        t = str(open_time)[:8]
        h, m, s = [int(x) for x in t.split(":")]
        start_t = t
        end_t = f"{str(h+1).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}"
    else:
        start_t, end_t = "08:00:00", "10:00:00"

    start_dt = f"{sched_date}T{start_t}"
    end_dt   = f"{sched_date}T{end_t}"
    customer  = getattr(doc, "party_name", "") or getattr(doc, "customer_name", "") or ""
    addr_name = getattr(doc, "shipping_address_name", "") or ""

    phone = ""
    if customer:
        try:
            cust = frappe.get_doc("Customer", customer)
            phone = getattr(cust, "mobile_no", "") or getattr(cust, "phone", "") or ""
        except Exception:
            pass

    maps_link = f"https://maps.google.com/?q={quote(addr_name)}" if addr_name else ""
    waze_link = f"https://waze.com/ul?q={quote(addr_name)}" if addr_name else ""
    nav = f"\n📍 Google Maps: {maps_link}\n🚗 Waze: {waze_link}" if addr_name else ""
    notes = (getattr(doc, "custom_service_description", "") or "").strip()
    notes_section = f"\n\n📝 Notes:\n{notes}" if notes else ""

    event = {
        "summary": f"[EST-{doc.name}] Estimate — {customer}",
        "description": (
            f"Estimate: {doc.name}\nCustomer: {customer}\n"
            f"📞 Phone: {phone}\nAddress: {addr_name}"
            f"{nav}{notes_section}\n\n"
            f"ERP Link: https://erp.aaairrigationservice.com/app/quotation/{doc.name}"
        ),
        "location": addr_name,
        "start": {"dateTime": start_dt, "timeZone": tz},
        "end":   {"dateTime": end_dt,   "timeZone": tz},
        "colorId": "1",
    }

    base_url = f"https://www.googleapis.com/calendar/v3/calendars/{CALENDAR_ID}/events"
    existing = getattr(doc, "custom_gcal_event_id", None)

    def gcal_req(method, url, payload=None):
        data = json.dumps(payload).encode() if payload else None
        req  = Request(url, data=data, method=method,
                       headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            return json.loads(urlopen(req).read())
        except HTTPError as e:
            frappe.log_error(f"GCal {e.code}: {e.read().decode()}", "GCal Estimate Sync")
            return None

    if existing:
        result = gcal_req("PUT", f"{base_url}/{existing}", event)
        action = "updated"
    else:
        result = gcal_req("POST", base_url, event)
        action = "created"
        if result and result.get("id"):
            frappe.db.set_value("Quotation", doc.name, "custom_gcal_event_id", result["id"])
            frappe.db.commit()

    if result:
        frappe.logger().info(f"GCal {action} for Estimate {doc.name}: {result.get('id')}")
