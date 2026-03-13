import frappe
from frappe import _

def before_insert(doc, method):
    """
    Auto-populate addresses and add default line items BEFORE saving
    """
    # Populate addresses from customer_address field
    populate_addresses(doc)
    
    # Auto-add line items based on service address
    add_default_line_items(doc)

def before_save(doc, method):
    """
    Validate before saving
    """
    # Ensure addresses are present
    if not doc.get("custom_service_address"):
        # Try to get from address_display or customer_address
        if doc.get("address_display"):
            doc.custom_service_address = doc.address_display
            doc.custom_billing_address = doc.address_display
        else:
            frappe.throw("Service Address is required. Please enter the service location.")
    
    # Ensure at least one line item
    if not doc.items or len(doc.items) == 0:
        frappe.throw("Please add at least one line item to the estimate")

def populate_addresses(doc):
    """
    Populate billing and service addresses from address_display or Lead
    """
    # Skip if already populated
    if doc.get("custom_service_address"):
        return
    
    address = ""
    
    # Try to get address from multiple sources
    if doc.get("address_display"):
        # Use the address_display field if available
        address = doc.address_display
    elif doc.quotation_to == "Lead" and doc.party_name:
        # Get from STANDARD Lead fields (not custom)
        try:
            lead = frappe.get_doc("Lead", doc.party_name)
            address_parts = []
            
            # Standard ERPNext Lead fields
            if lead.get("address_line1"):
                address_parts.append(lead.address_line1)
            if lead.get("address_line2"):
                address_parts.append(lead.address_line2)
            if lead.get("city"):
                address_parts.append(lead.city)
            if lead.get("state"):
                address_parts.append(lead.state)
            if lead.get("pincode"):
                address_parts.append(lead.pincode)
            
            address = ", ".join([p for p in address_parts if p])
        except Exception as e:
            frappe.log_error(f"Failed to get Lead address: {str(e)}", "Address Population")
            pass
    elif doc.quotation_to == "Customer" and doc.party_name:
        # Get primary address for Customer
        try:
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
                addr_doc = frappe.get_doc("Address", address_links[0].parent)
                address_parts = []
                if addr_doc.address_line1:
                    address_parts.append(addr_doc.address_line1)
                if addr_doc.city:
                    address_parts.append(addr_doc.city)
                if addr_doc.state:
                    address_parts.append(addr_doc.state)
                if addr_doc.pincode:
                    address_parts.append(addr_doc.pincode)
                address = ", ".join([p for p in address_parts if p])
        except:
            pass
    
    # Set both billing and service address to same value
    if address:
        doc.custom_service_address = address
        doc.custom_billing_address = address
        doc.custom_billing_different = 0
        frappe.msgprint(f"✅ Addresses auto-populated: {address}")

def add_default_line_items(doc):
    """
    Auto-add line items based on service address location
    """
    # Only add if no items exist yet
    if doc.items and len(doc.items) > 0:
        return
    
    service_address = doc.get("custom_service_address") or doc.get("address_display") or ""
    
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

# Keep other functions for portal invites and GCal sync
def send_portal_invite(doc, method):
    """
    Send portal invite when customer schedules appointment
    """
    if not doc.get("custom_scheduled_date"):
        return
    
    try:
        if doc.quotation_to == "Customer":
            customer = frappe.get_doc("Customer", doc.party_name)
        else:
            return
    except:
        return
    
    if not customer.email_id:
        return
    
    # Portal URL
    portal_url = "https://portal.aaairrigationservice.com"
    
    # Format scheduled date/time
    scheduled_date = frappe.format(doc.custom_scheduled_date, {'fieldtype': 'Date'})
    scheduled_time = doc.get("custom_scheduled_time") or "TBD"
    
    email_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #1b7abf;">AAA Irrigation Service</h1>
            <p>Appointment scheduled for {scheduled_date} at {scheduled_time}</p>
            <a href="{portal_url}" style="background: #ea580c; color: white; padding: 15px 30px; text-decoration: none; border-radius: 10px;">Access Portal</a>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">Powered by Boatman Systems™</p>
        </body>
    </html>
    """
    
    try:
        frappe.sendmail(
            recipients=[customer.email_id],
            subject="Appointment Scheduled",
            message=email_content,
            delayed=False
        )
    except:
        pass
