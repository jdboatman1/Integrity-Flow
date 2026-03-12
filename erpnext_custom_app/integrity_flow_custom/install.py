# Setup script
import frappe

def after_install():
    """Run after app installation"""
    print("\n" + "="*60)
    print("Integrity Flow Custom App - Installation Complete!")
    print("Powered by Boatman Systems™")
    print("="*60)
    
    # Create Settings DocType if not exists
    create_settings_doctype()
    
    # Set default values
    set_default_settings()
    
    print("\nNext Steps:")
    print("1. Upload gcal_credentials.json to /home/frappe/")
    print("2. Configure portal URL in Integrity Flow Settings")
    print("3. Setup SMTP for email notifications")
    print("4. Test 3CX call logging integration")
    print("\n" + "="*60 + "\n")

def create_settings_doctype():
    """Create Integrity Flow Settings doctype"""
    if not frappe.db.exists("DocType", "Integrity Flow Settings"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Integrity Flow Settings",
            "module": "Integrity Flow Custom",
            "issingle": 1,
            "fields": [
                {
                    "fieldname": "portal_url",
                    "fieldtype": "Data",
                    "label": "Customer Portal URL",
                    "default": "https://portal.aaairrigationservice.com"
                },
                {
                    "fieldname": "gcal_calendar_id",
                    "fieldtype": "Data",
                    "label": "Google Calendar ID",
                    "default": "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
                },
                {
                    "fieldname": "enable_3cx_logging",
                    "fieldtype": "Check",
                    "label": "Enable 3CX Call Logging",
                    "default": 1
                },
                {
                    "fieldname": "enable_portal_invites",
                    "fieldtype": "Check",
                    "label": "Enable Auto Portal Invites",
                    "default": 1
                },
                {
                    "fieldname": "enable_gcal_sync",
                    "fieldtype": "Check",
                    "label": "Enable Google Calendar Sync",
                    "default": 1
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1
                }
            ]
        })
        doc.insert()
        frappe.db.commit()

def set_default_settings():
    """Set default settings"""
    if frappe.db.exists("DocType", "Integrity Flow Settings"):
        settings = frappe.get_single("Integrity Flow Settings")
        if not settings.portal_url:
            settings.portal_url = "https://portal.aaairrigationservice.com"
        if not settings.gcal_calendar_id:
            settings.gcal_calendar_id = "svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com"
        settings.save()
        frappe.db.commit()
