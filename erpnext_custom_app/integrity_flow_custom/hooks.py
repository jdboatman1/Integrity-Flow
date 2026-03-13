from . import __version__ as app_version

app_name = "integrity_flow_custom"
app_title = "Integrity Flow Custom"
app_publisher = "Boatman Systems"
app_description = "Custom ERPNext app for AAA Irrigation Service field service management"
app_icon = "octicon octicon-file-directory"
app_color = "#1b7abf"
app_email = "info@aaairrigationservice.com"
app_license = "Proprietary"

# Includes in <head>
app_include_css = "/assets/integrity_flow_custom/css/custom.css"
app_include_js = "/assets/integrity_flow_custom/js/custom.js"

# Document Events
doc_events = {
    "Communication": {
        "before_save": "integrity_flow_custom.events.communication.log_3cx_call"
    },
    "Customer": {
        "after_insert": "integrity_flow_custom.events.customer.send_portal_invite"
    },
    "Quotation": {
        "after_insert": "integrity_flow_custom.events.quotation.on_quotation_insert",
        "validate": "integrity_flow_custom.events.quotation.on_quotation_validate",
        "before_save": "integrity_flow_custom.events.quotation.send_schedule_portal_invite",
        "on_update": "integrity_flow_custom.events.quotation.sync_to_gcal",
        "on_submit": "integrity_flow_custom.events.quotation_approval.on_quotation_update"
    },
    "Sales Invoice": {
        "after_insert": "integrity_flow_custom.events.sales_invoice.sync_to_gcal",
        "on_update": "integrity_flow_custom.events.sales_invoice.sync_to_gcal"
    }
}

# Scheduled Tasks
scheduler_events = {
    "hourly": [
        "integrity_flow_custom.tasks.sync_pending_calendar_events"
    ]
}

# Website
website_route_rules = [
    {"from_route": "/portal/<path:app_path>", "to_route": "portal"},
]

# Whitelisted Methods
white_listed_methods = {
    "integrity_flow_custom.api.get_customer_portal_data",
    "integrity_flow_custom.api.sync_estimate_to_gcal",
    "integrity_flow_custom.api.schedule_appointment",
}

# Fixtures (Custom Fields, Workflows, etc.)
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Integrity Flow Custom"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Integrity Flow Custom"]]
    },
    {
        "dt": "Workflow",
        "filters": [["name", "in", ["Quotation Workflow", "Sales Invoice Workflow"]]]
    }
]

# Override standard ERPNext pages
override_doctype_class = {
    # "Quotation": "integrity_flow_custom.overrides.quotation.CustomQuotation"
}

# Brand
app_logo_url = "/assets/integrity_flow_custom/images/logo.png"
brand_html = '<div class="powered-by">Powered by Boatman Systems™</div>'
