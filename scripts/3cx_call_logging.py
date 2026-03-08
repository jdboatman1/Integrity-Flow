# Integrity Flow Powered by Boatman Systems™
# Server Script: 3CX Call Logging Automation
# Trigger: On Communication Save (Phone Call)

def log_3cx_call(doc, method):
    """
    Automatically links incoming 3CX calls to existing Customers or Leads
    within Integrity Flow Powered by Boatman Systems™.
    """
    
    # Extract Caller ID from the incoming 3CX data
    caller_id = doc.phone_number
    
    # 1. Search for existing Customer
    customer = frappe.db.get_value("Customer", {"mobile_no": caller_id}, "name")
    
    if customer:
        # Link to existing Customer Dashboard
        doc.reference_doctype = "Customer"
        doc.reference_name = customer
        doc.content = f"Incoming call from {customer} via 3CX Integration (Integrity Flow)"
        frappe.msgprint(f"Boatman Systems™: Recognized Customer {customer}")
    else:
        # 2. Search for existing Lead
        lead = frappe.db.get_value("Lead", {"mobile_no": caller_id}, "name")
        
        if lead:
            doc.reference_doctype = "Lead"
            doc.reference_name = lead
            doc.content = f"Incoming call from Lead {lead} via 3CX"
        else:
            # 3. New Caller Logic: Prepare data for a new Lead
            doc.content = f"New Caller ID: {caller_id}. System prompted for new Lead creation in Integrity Flow."

    # Standard Metadata for the "Integrity Flow" Communication Log
    doc.communication_type = "Phone"
    doc.status = "Linked"
    
    # Log the Boatman Systems™ metadata
    doc.add_comment("Integrity Flow", f"Call metadata captured: {doc.duration} seconds on {doc.communication_date}")
