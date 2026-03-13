import re
import frappe

def normalize(number):
    digits = re.sub(r"\D+", "", number or "")
    return digits[-10:] if len(digits) > 10 else digits

def get_context(context):
    raw = frappe.form_dict.get("number") or ""
    n = normalize(raw)

    # 1️⃣ Check Contact Phone child table
    rows = frappe.db.sql(
        "select parent from `tabContact Phone` where phone like %s limit 1",
        (f"%{n}%",),
    )
    if rows:
        contact = rows[0][0]
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"] = f"/app/contact/{contact}"
        return

    # 2️⃣ Check Lead table
    for field in ("phone", "mobile_no"):
        lead = frappe.db.get_value("Lead", {field: ["like", f"%{n}%"]}, "name")
        if lead:
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = f"/app/lead/{lead}"
            return

    # 3️⃣ No match → Open NEW Lead form with phone prefilled
    frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = f"/app/lead/new-lead-1?phone={raw}"
