import frappe
from frappe import _

def on_quotation_insert(doc, method):
    """
    Auto-populate addresses and add default line items
    """
    # Fix the "CRM lead not found" error
    # ERPNext requires either Lead or Customer
    if doc.quotation_to == "Lead":
        validate_lead_exists(doc)
        populate_addresses_from_lead(doc)
    elif doc.quotation_to == "Customer":
        populate_addresses_from_customer(doc)
    
    # Auto-add line items based on service address
    add_default_line_items(doc)

def validate_lead_exists(doc):
    """
    Ensure Lead exists, or create one if needed
    """
    if not doc.party_name:
        frappe.throw("Please select a Lead or Customer")
        
    # Check if Lead exists
    if not frappe.db.exists("Lead", doc.party_name):
        frappe.throw(f"Lead {doc.party_name} not found. Please create the Lead first or select an existing Customer.")

def populate_addresses_from_lead(doc):
    """
    Populate billing and service addresses from Lead
    """
    try:
        lead = frappe.get_doc("Lead", doc.party_name)
        
        # Build address from Lead fields
        address_parts = []
        if lead.get("custom_address_line1"):
            address_parts.append(lead.custom_address_line1)
        if lead.get("custom_city"):
            address_parts.append(lead.custom_city)
        if lead.get("custom_state"):
            address_parts.append(lead.custom_state)
        if lead.get("custom_zip"):
            address_parts.append(lead.custom_zip)
        
        full_address = ", ".join([p for p in address_parts if p])
        
        # Set both billing and service address to same value initially
        if full_address and not doc.get("custom_service_address"):
            doc.custom_service_address = full_address
            doc.custom_billing_address = full_address
            doc.custom_billing_different = 0
            
            frappe.msgprint(f"✅ Addresses auto-populated from Lead")
            
    except Exception as e:
        frappe.log_error(f"Failed to populate address from Lead: {str(e)}", "Address Population")

def populate_addresses_from_customer(doc):
    """
    Populate billing and service addresses from Customer
    """
    try:
        customer = frappe.get_doc("Customer", doc.party_name)
        
        # Get primary address
        address_links = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": doc.party_name,
                "parenttype": "Address"
            },
            fields=["parent"],
            limit=1
        )
        
        if address_links:
            address_doc = frappe.get_doc("Address", address_links[0].parent)
            
            # Build full address
            address_parts = []
            if address_doc.address_line1:
                address_parts.append(address_doc.address_line1)
            if address_doc.city:
                address_parts.append(address_doc.city)
            if address_doc.state:
                address_parts.append(address_doc.state)
            if address_doc.pincode:
                address_parts.append(address_doc.pincode)
            
            full_address = ", ".join([p for p in address_parts if p])
            
            # Set addresses
            if full_address and not doc.get("custom_service_address"):
                doc.custom_service_address = full_address
                doc.custom_billing_address = full_address
                doc.custom_billing_different = 0
                
                # Also set standard ERPNext fields
                doc.customer_address = address_links[0].parent
                doc.address_display = full_address
                
                frappe.msgprint(f"✅ Addresses auto-populated from Customer")
                
    except Exception as e:
        frappe.log_error(f"Failed to populate address from Customer: {str(e)}", "Address Population")

def add_default_line_items(doc):
    """
    Auto-add line items based on service address location
    """
    # Only add if no items exist yet
    if doc.items and len(doc.items) > 0:
        return
    
    service_address = doc.get("custom_service_address") or ""
    
    # Check if Frisco is in the service address
    is_frisco = "frisco" in service_address.lower()
    
    if is_frisco:
        # Frisco location - add Frisco System Inspection
        item_name = "Frisco System Inspection"
        item_code = "FRISCO-INSPECTION"
        rate = 125.00
    else:
        # Other location - add System Check
        item_name = "System Check"
        item_code = "SYSTEM-CHECK"
        rate = 95.00
    
    # Create the item if it doesn't exist
    if not frappe.db.exists("Item", item_code):
        create_service_item(item_code, item_name, rate)
    
    # Add line item to quotation
    doc.append("items", {
        "item_code": item_code,
        "item_name": item_name,
        "description": item_name,
        "qty": 1,
        "rate": rate,
        "amount": rate
    })
    
    frappe.msgprint(f"✅ Added line item: {item_name} - ${rate}")

def create_service_item(item_code, item_name, rate):
    """
    Create service item if it doesn't exist
    """
    try:
        # Create Item Group if needed
        if not frappe.db.exists("Item Group", "Services"):
            item_group = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "Services",
                "parent_item_group": "All Item Groups",
                "is_group": 0
            })
            item_group.insert(ignore_permissions=True)
        
        # Create Item
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": item_name,
            "item_group": "Services",
            "stock_uom": "Nos",
            "is_stock_item": 0,
            "is_sales_item": 1,
            "standard_rate": rate,
            "description": item_name
        })
        item.insert(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Failed to create item {item_code}: {str(e)}", "Item Creation")

def on_quotation_validate(doc, method):
    """
    Validate before saving
    """
    # Ensure addresses are present
    if not doc.get("custom_service_address"):
        frappe.throw("Service Address is required. Please enter the service location.")
    
    # If billing is different but no billing address, throw error
    if doc.get("custom_billing_different") and not doc.get("custom_billing_address"):
        frappe.throw("Please enter Billing Address or uncheck 'Billing Address is Different'")
    
    # Ensure at least one line item
    if not doc.items or len(doc.items) == 0:
        frappe.throw("Please add at least one line item to the estimate")

def send_schedule_portal_invite(doc, method):
    """
    Send portal invite when customer schedules appointment
    """
    # Only send if this is a new quotation with scheduling info
    if not doc.get("custom_scheduled_date"):
        return
    
    # Get customer
    try:
        if doc.quotation_to == "Customer":
            customer = frappe.get_doc("Customer", doc.party_name)
        elif doc.quotation_to == "Lead":
            # Convert lead to customer first if needed
            lead = frappe.get_doc("Lead", doc.party_name)
            if not lead.email_id:
                return
            # Check if customer already exists
            existing_customer = frappe.db.get_value("Customer", {"email_id": lead.email_id}, "name")
            if existing_customer:
                customer = frappe.get_doc("Customer", existing_customer)
            else:
                return  # Can't send invite without customer
        else:
            return
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

# Import GCal sync functions
from integrity_flow_custom.events.sales_invoice import (
    _load_creds,
    _get_token,
    _gcal_request
)

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
    try:
        if doc.quotation_to == "Customer":
            cust_doc = frappe.get_doc("Customer", customer)
            phone = cust_doc.mobile_no or cust_doc.phone or ""
        elif doc.quotation_to == "Lead":
            lead_doc = frappe.get_doc("Lead", customer)
            phone = lead_doc.mobile_no or lead_doc.phone or ""
    except:
        pass

    # Use service address
    address = doc.get("custom_service_address") or ""
    
    from urllib.parse import quote
    addr_encoded = quote(address) if address else ""
    nav_links = ""
    if address:
        nav_links = f"\n📍 Google Maps: https://maps.google.com/?q={addr_encoded}\n🚗 Waze: https://waze.com/ul?q={addr_encoded}"

    CALENDAR_ID = "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
    
    event = {
        "summary": f"[{doc.name}] {customer}",
        "description": (
            f"Estimate: {doc.name}\n"
            f"Customer: {customer}\n"
            f"📞 Phone: {phone}\n"
            f"Service Address: {address}"
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
