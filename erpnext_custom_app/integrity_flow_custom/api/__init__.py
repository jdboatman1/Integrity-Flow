import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_customer_portal_data(customer_id):
    """
    Get customer data for portal
    """
    try:
        customer = frappe.get_doc("Customer", customer_id)
        
        # Get quotations
        quotations = frappe.get_all(
            "Quotation",
            filters={"party_name": customer_id},
            fields=["name", "transaction_date", "grand_total", "status", "custom_service_description", "custom_scheduled_date"],
            order_by="creation desc"
        )
        
        # Get invoices
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={"customer": customer_id},
            fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status"],
            order_by="creation desc"
        )
        
        # Get customer equipment info
        equipment = {
            "controller_brand": customer.get("custom_controller_brand"),
            "controller_model": customer.get("custom_controller_model"),
            "zone_count": customer.get("custom_zone_count"),
            "backflow_type": customer.get("custom_backflow_type"),
        }
        
        return {
            "customer": {
                "id": customer.name,
                "name": customer.customer_name,
                "email": customer.email_id,
                "phone": customer.mobile_no,
                "equipment": equipment
            },
            "quotations": quotations,
            "invoices": invoices
        }
    except Exception as e:
        frappe.log_error(f"Portal data fetch error: {str(e)}", "Portal API")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def schedule_appointment(customer_email, service_type, preferred_date, preferred_time, description):
    """
    Create new quotation/appointment from portal
    """
    try:
        # Find customer by email
        customer = frappe.db.get_value("Customer", {"email_id": customer_email}, "name")
        
        if not customer:
            return {"success": False, "message": "Customer not found"}
        
        # Create quotation
        quotation = frappe.get_doc({
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": customer,
            "transaction_date": frappe.utils.today(),
            "custom_scheduled_date": preferred_date,
            "custom_scheduled_time": preferred_time,
            "custom_service_description": f"{service_type}\n\n{description}"
        })
        quotation.insert(ignore_permissions=True)
        
        return {
            "success": True,
            "quotation_id": quotation.name,
            "message": "Appointment scheduled successfully"
        }
    except Exception as e:
        frappe.log_error(f"Schedule appointment error: {str(e)}", "Portal API")
        return {"success": False, "message": str(e)}

@frappe.whitelist()
def sync_estimate_to_gcal(quotation_id):
    """
    Manually trigger GCal sync for a quotation
    """
    try:
        from integrity_flow_custom.events.quotation import _sync_quotation_to_gcal
        
        quotation = frappe.get_doc("Quotation", quotation_id)
        _sync_quotation_to_gcal(quotation)
        
        return {"success": True, "message": "Synced to Google Calendar"}
    except Exception as e:
        frappe.log_error(f"Manual GCal sync error: {str(e)}", "GCal API")
        return {"success": False, "message": str(e)}
