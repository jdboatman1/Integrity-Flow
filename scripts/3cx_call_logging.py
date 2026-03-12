# Integrity Flow Powered by Boatman Systems™
# Server Script: 3CX Call Logging Automation
# Trigger: On Communication Save (Phone Call)

def log_3cx_call(doc, method):
    """
    Automatically links incoming 3CX calls to existing Customers or Leads
    within Integrity Flow Powered by Boatman Systems™.
    """
    
    # Extract Caller ID and CNAM name from 3CX
    caller_id = doc.get("phone_no") or doc.get("phone_number") or ""
    cnam_name = (doc.get("sender_full_name") or doc.get("from_name") or "").strip()

    # Format phone number as (XXX) XXX-XXXX
    digits = "".join(c for c in caller_id if c.isdigit())[-10:]
    display_phone = f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else caller_id

    # 1. Search for existing Customer by phone
    customer = frappe.db.get_value("Customer", {"mobile_no": caller_id}, ["name", "customer_name"], as_dict=True)

    if customer:
        doc.reference_doctype = "Customer"
        doc.reference_name = customer.name
        doc.content = f"Incoming call from {customer.customer_name} ({display_phone}) via 3CX — Integrity Flow"
        frappe.msgprint(f"Boatman Systems™: Recognized Customer {customer.customer_name}")
    else:
        # 2. Search for existing Lead by phone
        lead = frappe.db.get_value("Lead", {"mobile_no": caller_id}, ["name", "lead_name"], as_dict=True)

        if lead:
            doc.reference_doctype = "Lead"
            doc.reference_name = lead.name
            doc.content = f"Incoming call from {lead.lead_name} ({display_phone}) via 3CX — Integrity Flow"
        else:
            # 3. New caller — use CNAM name from 3CX/Flowroute, never use phone number as name
            # cnam_name comes from sender_full_name which 3CX populates via Flowroute CNAM lookup
            lead_name = cnam_name if cnam_name else f"New Caller {display_phone}"

            new_lead = frappe.get_doc({
                "doctype": "Lead",
                "lead_name": lead_name,
                "mobile_no": display_phone,
                "status": "Open",
                "source": "Phone",
                "notes": f"Auto-created from incoming 3CX call. Caller ID: {caller_id}"
            })
            new_lead.insert(ignore_permissions=True)

            doc.reference_doctype = "Lead"
            doc.reference_name = new_lead.name
            doc.content = f"New caller: {lead_name} ({display_phone}) — Lead {new_lead.name} auto-created by Integrity Flow."

    # Standard Metadata for the "Integrity Flow" Communication Log
    doc.communication_type = "Phone"
    doc.status = "Linked"
    
    # Log the Boatman Systems™ metadata
    doc.add_comment("Integrity Flow", f"Call metadata captured: {doc.duration} seconds on {doc.communication_date}")
