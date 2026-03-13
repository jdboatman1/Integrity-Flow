import frappe
from frappe import _

def on_quotation_update(doc, method):
    """
    Auto-convert signed quotation to Sales Order and Invoice
    """
    # Check if quotation was just approved/signed
    if doc.status == "Submitted" and doc.get("custom_signature_captured"):
        try:
            # Create Sales Order from Quotation
            sales_order = create_sales_order_from_quotation(doc)
            
            # Create Sales Invoice from Sales Order
            sales_invoice = create_sales_invoice_from_order(sales_order)
            
            # Add comment to quotation
            doc.add_comment(
                "Comment",
                f"✅ Auto-converted to Sales Order {sales_order.name} and Invoice {sales_invoice.name} - Powered by Boatman Systems™"
            )
            
            frappe.msgprint(
                f"✅ Success! Created Sales Order {sales_order.name} and Invoice {sales_invoice.name}",
                indicator="green"
            )
            
        except Exception as e:
            frappe.log_error(f"Auto-conversion failed: {str(e)}", "Quotation Auto-conversion")
            frappe.msgprint(f"Failed to auto-convert: {str(e)}", indicator="red")

def create_sales_order_from_quotation(quotation):
    """
    Create Sales Order from approved Quotation
    """
    # Create Sales Order
    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": quotation.party_name,
        "customer_address": quotation.customer_address,
        "address_display": quotation.address_display,
        "transaction_date": frappe.utils.today(),
        "delivery_date": quotation.get("custom_scheduled_date") or frappe.utils.add_days(None, 7),
        "custom_scheduled_date": quotation.get("custom_scheduled_date"),
        "custom_scheduled_time": quotation.get("custom_scheduled_time"),
        "custom_technician": quotation.get("custom_technician"),
        "custom_service_description": quotation.get("custom_service_description"),
        "items": []
    })
    
    # Copy items from quotation
    for item in quotation.items:
        sales_order.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "qty": item.qty,
            "rate": item.rate,
            "amount": item.amount,
            "delivery_date": quotation.get("custom_scheduled_date") or frappe.utils.add_days(None, 7)
        })
    
    sales_order.insert(ignore_permissions=True)
    sales_order.submit()
    
    # Link back to quotation
    quotation.db_set("custom_sales_order", sales_order.name)
    
    return sales_order

def create_sales_invoice_from_order(sales_order):
    """
    Create Sales Invoice from Sales Order
    """
    # Create Sales Invoice
    sales_invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": sales_order.customer,
        "customer_address": sales_order.customer_address,
        "address_display": sales_order.address_display,
        "posting_date": frappe.utils.today(),
        "due_date": frappe.utils.add_days(None, 30),
        "custom_scheduled_date": sales_order.get("custom_scheduled_date"),
        "items": []
    })
    
    # Copy items from sales order
    for item in sales_order.items:
        sales_invoice.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "qty": item.qty,
            "rate": item.rate,
            "amount": item.amount,
            "sales_order": sales_order.name
        })
    
    sales_invoice.insert(ignore_permissions=True)
    
    # Link back to sales order
    sales_order.db_set("custom_sales_invoice", sales_invoice.name)
    
    return sales_invoice

def on_quotation_signature_captured(doc, method):
    """
    Called when signature is captured on quotation
    """
    if doc.get("custom_signature_captured") and doc.docstatus == 0:
        # Submit the quotation (approve it)
        doc.submit()
        frappe.db.commit()
        
        # Trigger auto-conversion
        on_quotation_update(doc, method)
