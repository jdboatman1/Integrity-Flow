# Integrity Flow Custom App for ERPNext

## Overview

Complete Frappe custom app that transforms ERPNext into a specialized Field Service Management (FSM) platform for AAA Irrigation Service.

## Features

### 🎨 UI/UX Improvements
- Custom Boatman Systems™ theme
- Professional color scheme (Primary Blue #1b7abf, Trust Green #059669, Action Orange #ea580c)
- Clean, modern interface
- Mobile-responsive design

### 🔄 Workflow Automation
- 3CX call logging with automatic Lead/Customer linking
- Google Calendar sync for estimates and invoices
- Auto-send customer portal invites
- Signed quotation → Sales Order → Invoice automation

### 📋 Custom Fields
- **Customer**: Controller info, TCEQ license, property details
- **Quotation**: Scheduling fields, technician assignment, service description
- **Sales Invoice**: Tax exemption, parent customer, GCal event ID
- **Lead**: Address fields, service description

### 🌐 API Endpoints
- Customer portal integration
- Mobile app support
- Third-party integrations

## Installation

### Prerequisites
- ERPNext v14 or v15
- Frappe Framework
- Python 3.8+

### Install Steps

```bash
# Navigate to your Frappe bench
cd ~/frappe-bench

# Get the app
bench get-app https://github.com/jdboatman1/integrity_flow_custom

# Install on your site
bench --site erp.aaairrigationservice.com install-app integrity_flow_custom

# Migrate database
bench --site erp.aaairrigationservice.com migrate

# Restart bench
bench restart
```

## Configuration

### 1. Google Calendar Setup

1. Place your `gcal_credentials.json` in `/home/frappe/`
2. Update calendar ID in the app settings

### 2. Customer Portal

1. Update portal URL in settings
2. Configure SMTP for email invites

### 3. 3CX Integration

1. Configure 3CX webhook to trigger Communication doctype
2. Server script will auto-process calls

## Features Breakdown

### Custom Doctypes

#### Tech Schedule
- Visual calendar for technician scheduling
- Drag-and-drop appointment management
- Integration with Quotations

### Server Scripts

1. **3CX Call Logging** (`before_save` on Communication)
   - Auto-match phone numbers to Customers/Leads
   - Create new Lead if no match found
   - Use CNAM for caller name

2. **Google Calendar Sync** (`after_insert`, `on_update` on Sales Invoice)
   - Push appointments to Google Calendar
   - Include customer info, phone, navigation links
   - Store event ID for updates

3. **Customer Portal Invite** (`after_insert` on Customer)
   - Send branded welcome email with portal link
   - Include login instructions

4. **Schedule Portal Invite** (`after_insert` on Quotation)
   - Send confirmation email with portal access
   - Include appointment details

### Custom API Methods

```python
# Get customer portal data
@frappe.whitelist()
def get_customer_portal_data(customer_id):
    # Returns estimates, invoices, equipment info
    pass

# Sync estimate to Google Calendar
@frappe.whitelist()
def sync_estimate_to_gcal(quotation_id):
    # Creates/updates GCal event
    pass
```

## Customization Guide

### Adding Custom Fields

```python
# In hooks.py
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Integrity Flow Custom"]]
    }
]
```

### Modifying Workflows

Edit workflow JSON files in `integrity_flow_custom/fixtures/`

### Updating Branding

Modify CSS in `integrity_flow_custom/public/css/custom.css`

## Development

```bash
# Enable developer mode
bench --site erp.aaairrigationservice.com set-config developer_mode 1

# Watch for changes
bench watch
```

## Troubleshooting

### Issue: Scripts Not Running
- Check server script is enabled in ERPNext settings
- Verify event triggers are correct
- Check error logs: `bench --site erp.aaairrigationservice.com console`

### Issue: GCal Sync Failing
- Verify credentials file exists and is readable
- Check calendar ID is correct
- Ensure service account has calendar access

### Issue: Portal Invites Not Sending
- Verify SMTP settings in ERPNext
- Check email queue: Email Queue list in ERPNext
- Test email with: `bench --site erp.aaairrigationservice.com send-test-email`

## Support

- Email: info@aaairrigationservice.com
- Phone: 469-751-3567

## License

Proprietary - AAA Irrigation Service LLC

**Powered by Boatman Systems™**