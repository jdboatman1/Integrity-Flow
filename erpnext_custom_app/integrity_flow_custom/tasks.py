# Scheduled tasks
import frappe

def sync_pending_calendar_events():
    """Hourly task to sync any pending calendar events"""
    # Get quotations with scheduled date but no GCal event ID
    quotations = frappe.get_all(
        "Quotation",
        filters={
            "custom_scheduled_date": ["is", "set"],
            "custom_gcal_event_id": ["", "is", "not set"]
        },
        limit=10
    )
    
    for quot in quotations:
        try:
            from integrity_flow_custom.events.quotation import _sync_quotation_to_gcal
            doc = frappe.get_doc("Quotation", quot.name)
            _sync_quotation_to_gcal(doc)
        except Exception as e:
            frappe.log_error(f"Scheduled GCal sync failed for {quot.name}: {str(e)}", "GCal Sync")
