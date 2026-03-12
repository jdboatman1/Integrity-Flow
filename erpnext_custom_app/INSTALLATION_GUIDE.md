# Integrity Flow Custom App - Complete Installation Guide

## 🎯 What This App Does

This Frappe custom app transforms your ERPNext instance into a professional Field Service Management (FSM) platform with:

✅ **Boatman Systems™ Professional Branding**  
✅ **Complete Workflow Automation** (3CX, GCal, Portal Invites)  
✅ **Custom Fields** for irrigation service business  
✅ **Clean, Modern UI** (removes ERPNext "junk")  
✅ **Customer Portal API Integration**  
✅ **Mobile App Support**

---

## 📦 Installation Steps

### Step 1: Access Your ERPNext Server

```bash
# SSH into your Linode server (using Tailscale)
ssh -i ~/.ssh/id_gemini_cli deploy@100.106.12.60

# Navigate to Frappe bench directory
cd ~/frappe-bench
```

### Step 2: Get the App

```bash
# Copy the app folder from this repository to your server
# On your local machine:
scp -r /app/erpnext_custom_app deploy@100.106.12.60:~/

# On the server, move it to apps directory:
cd ~/frappe-bench
mv ~/erpnext_custom_app apps/integrity_flow_custom
```

### Step 3: Install the App

```bash
# Install on your ERPNext site
bench --site erp.aaairrigationservice.com install-app integrity_flow_custom

# You should see:
# Installing integrity_flow_custom...
# Integrity Flow Custom App - Installation Complete!
# Powered by Boatman Systems™
```

### Step 4: Migrate Database

```bash
# Apply all custom fields and configurations
bench --site erp.aaairrigationservice.com migrate

# Clear cache
bench --site erp.aaairrigationservice.com clear-cache

# Restart bench
bench restart
```

---

## ⚙️ Configuration

### 1. Access Integrity Flow Settings

1. Log in to ERPNext: https://erp.aaairrigationservice.com
2. Search for: **Integrity Flow Settings**
3. Configure:
   - **Customer Portal URL**: `https://portal.aaairrigationservice.com`
   - **Google Calendar ID**: `svkl6l87fddpvfubg96g3iklg8@group.calendar.google.com`
   - **Enable 3CX Call Logging**: ✓
   - **Enable Auto Portal Invites**: ✓
   - **Enable Google Calendar Sync**: ✓

### 2. Setup Google Calendar

```bash
# Place your Google Calendar credentials on the server
scp gcal_credentials.json deploy@100.106.12.60:/home/frappe/

# Set permissions
sudo chown frappe:frappe /home/frappe/gcal_credentials.json
sudo chmod 600 /home/frappe/gcal_credentials.json
```

### 3. Configure SMTP (for Portal Invites)

In ERPNext:
1. Go to **Email Domain**
2. Click **New**
3. Configure Yahoo SMTP:
   - Email Server: `smtp.mail.yahoo.com`
   - Port: `465`
   - Use SSL: ✓
   - Email ID: `aaairrigationservice@yahoo.com`
   - Password: [Your Yahoo app password]

---

## ✨ Features Enabled

### 1. Automatic 3CX Call Logging

**When**: Any call comes through 3CX  
**What Happens**:
- Looks up phone number in Customers
- If not found, looks up in Leads
- If still not found, creates new Lead automatically
- Links call to the record
- Shows customer/lead popup in 3CX

**No additional setup required** - works automatically!

### 2. Customer Portal Auto-Invites

**When**: New customer created OR customer schedules appointment  
**What Happens**:
- Sends beautiful branded email with portal link
- Includes login instructions
- Customer can access portal with magic link

**Email Example**:
```
Subject: Welcome to AAA Irrigation Service Customer Portal

Welcome, [Customer Name]!

Your customer portal account has been created...
[Access Your Portal Button]
```

### 3. Google Calendar Sync

**When**: Quotation with scheduled date OR Sales Invoice created/updated  
**What Happens**:
- Creates event in Google Calendar
- Includes customer phone, address, Google Maps/Waze links
- Shows technician assignment
- Updates event if date/time changes

**Manual Sync**: Click "Actions → Sync to Google Calendar" on any Quotation

### 4. Custom Fields Added

**Customer:**
- Controller Brand & Model
- Zone Count
- Backflow Preventer Type
- TCEQ License Number
- Property Size

**Quotation:**
- Scheduled Date & Time
- Assigned Technician
- Service Description
- Google Calendar Event ID (hidden)

**Sales Invoice:**
- Tax Exemption Flag
- Google Calendar Event ID (hidden)

**Lead:**
- Address fields (Line 1, City, State, ZIP)
- Service Description

### 5. UI/UX Improvements

✅ **Boatman Systems™ Colors**:
- Primary Blue: #1b7abf
- Trust Green: #059669
- Action Orange: #ea580c

✅ **Typography**: Bold, italic, uppercase headings (900 weight)

✅ **Clean Interface**: Removes unnecessary ERPNext buttons and clutter

✅ **"Powered by Boatman Systems™"** footer on all pages

---

## 🔧 Troubleshooting

### Issue: Custom fields not showing

```bash
# Re-run migration
bench --site erp.aaairrigationservice.com migrate
bench --site erp.aaairrigationservice.com clear-cache
```

### Issue: Portal invites not sending

1. Check SMTP settings in ERPNext
2. Test email: `bench --site erp.aaairrigationservice.com send-test-email`
3. Check email queue: Go to **Email Queue** in ERPNext
4. View logs: `bench --site erp.aaairrigationservice.com console`

### Issue: GCal sync not working

```bash
# Check credentials file exists
ls -la /home/frappe/gcal_credentials.json

# Check permissions
sudo chown frappe:frappe /home/frappe/gcal_credentials.json

# View logs
tail -f ~/frappe-bench/logs/erp.aaairrigationservice.com.log
```

### Issue: 3CX calls not linking

1. Verify Communication doctype is being created by 3CX
2. Check server script is enabled
3. View error log in ERPNext: **Error Log** list

---

## 📱 API Endpoints (For Customer Portal & Mobile App)

### Get Customer Portal Data
```python
GET /api/method/integrity_flow_custom.api.get_customer_portal_data
?customer_id=CUST-00001
```

Returns: Customer info, quotations, invoices, equipment details

### Schedule Appointment
```python
POST /api/method/integrity_flow_custom.api.schedule_appointment
{
  \"customer_email\": \"customer@email.com\",
  \"service_type\": \"Residential Repair\",
  \"preferred_date\": \"2026-04-15\",
  \"preferred_time\": \"9AM-11AM\",
  \"description\": \"Broken sprinkler head in zone 3\"
}
```

### Sync Estimate to GCal
```python
POST /api/method/integrity_flow_custom.api.sync_estimate_to_gcal
{
  \"quotation_id\": \"QTN-00001\"
}
```

---

## 🔄 Automated Tasks

The app runs these tasks automatically:

**Hourly:**
- Sync pending calendar events (quotations with scheduled date but no GCal event)

**On Event:**
- Communication save → 3CX call logging
- Customer insert → Portal invite email
- Quotation insert → Schedule confirmation + portal invite
- Quotation update → GCal event update
- Sales Invoice insert/update → GCal sync

---

## 🎨 Customization

### Change Branding Colors

Edit: `integrity_flow_custom/public/css/custom.css`

```css
:root {
  --boatman-primary-blue: #YOUR_COLOR;
  --boatman-trust-green: #YOUR_COLOR;
  --boatman-action-orange: #YOUR_COLOR;
}
```

### Add Custom API Endpoint

Edit: `integrity_flow_custom/api/__init__.py`

```python
@frappe.whitelist()
def your_custom_function():
    # Your code here
    return {\"success\": True}
```

### Modify Email Templates

Edit event files in: `integrity_flow_custom/events/`

---

## 📊 What's Next

With this app installed, your ERPNext now:

✅ Looks professional (Boatman Systems™ branding)  
✅ Works seamlessly with 3CX phone system  
✅ Auto-invites customers to portal  
✅ Syncs everything to Google Calendar  
✅ Has clean, modern interface  
✅ Supports customer portal integration  
✅ Ready for mobile app integration

**Next Phase**: Build the React Native mobile app for technicians!

---

## 🆘 Support

**Technical Issues:**
- Check logs: `tail -f ~/frappe-bench/logs/erp.aaairrigationservice.com.log`
- View error log in ERPNext: **Error Log** list
- Contact: info@aaairrigationservice.com

**Phone:** 469-751-3567

---

**Powered by Boatman Systems™**
