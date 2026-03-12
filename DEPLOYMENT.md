# Integrity Flow ERP/CRM - Deployment Guide

## 🏠 System Overview

This repository contains:
1. **ERPNext Automation Scripts** - Complete backend workflow automation
2. **Modern Customer Portal** - React frontend + FastAPI backend
3. **Mobile App** (Coming Soon) - React Native cross-platform app
4. **Marketing Site** - Static site in `setup_site/`

---

## 🛠 Phase 1: ERPNext Backend Setup

### Required Configuration

1. **Get ERPNext API Credentials**
   - Log in to ERPNext at `https://erp.aaairrigationservice.com`
   - Go to: **User Menu → API Access**
   - Click **Generate Keys**
   - Copy the **API Key** and **API Secret**

2. **Update Backend Environment**
   ```bash
   cd /app/backend
   nano .env
   ```
   
   Update these values:
   ```env
   ERPNEXT_API_KEY=your_api_key_here
   ERPNEXT_API_SECRET=your_api_secret_here
   ```

3. **Deploy ERPNext Server Scripts**

   The following scripts need to be added to your ERPNext instance:

   **A. 3CX Call Logging Script**
   - File: `/app/scripts/3cx_call_logging.py`
   - Location: ERPNext → Settings → Server Script → New
   - DocType: `Communication`
   - Event: `before_save`
   - Copy the content from the script file

   **B. Google Calendar Sync for Estimates**
   - File: `/app/scripts/tech_schedule_deploy/api_addition.py`
   - This adds the `sync_estimate_to_gcal` function
   - Already deployed (confirmed in docs)

   **C. Google Calendar Sync for Sales Invoice**
   - File: `/app/scripts/gcal_work_order_sync.py`
   - Location: ERPNext → Settings → Server Script → New
   - DocType: `Sales Invoice`
   - Events: `after_insert`, `on_update`
   - Copy the content from the script file

4. **Custom Fields Setup**
   
   Run this script on your ERPNext server:
   ```bash
   python /app/add_customer_fields.py
   ```

---

## 🌐 Phase 2: Customer Portal Deployment

### Prerequisites
- MongoDB (already running)
- Node.js & Yarn (installed)
- Python 3.8+ with pip

### Backend Setup

1. **Install Python Dependencies**
   ```bash
   cd /app/backend
   pip install -r requirements.txt
   ```

2. **Configure Email for Magic Links**
   
   Update `/app/backend/.env`:
   ```env
   SMTP_HOST=smtp.mail.yahoo.com
   SMTP_PORT=465
   SMTP_USER=aaairrigationservice@yahoo.com
   SMTP_PASSWORD=your_yahoo_password
   ```

3. **Start Backend**
   ```bash
   sudo supervisorctl restart backend
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd /app/frontend
   yarn install
   ```

2. **Start Frontend**
   ```bash
   sudo supervisorctl restart frontend
   ```

### Verify Portal is Running

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api/health

---

## 📧 Customer Invite System

### Automatic Invite on Customer Creation

Create a Server Script in ERPNext:
- DocType: `Customer`
- Event: `after_insert`

Script:
```python
import frappe
from frappe import _

def send_portal_invite(doc, method):
    """Send portal invite email to new customer"""
    if not doc.email_id:
        return
    
    # Your portal URL
    portal_url = "https://portal.aaairrigationservice.com"
    
    # Send email
    frappe.sendmail(
        recipients=[doc.email_id],
        subject="Welcome to AAA Irrigation Service Portal",
        message=f"""
        <h2>Welcome {doc.customer_name}!</h2>
        <p>You now have access to your AAA Irrigation Service customer portal.</p>
        <p>Access your portal here: <a href="{portal_url}">{portal_url}</a></p>
        <p>Use your email address ({doc.email_id}) to log in.</p>
        <br>
        <p>Powered by Boatman Systems™</p>
        """
    )
```

### Automatic Invite on Schedule from Website

When a customer schedules from the website, they receive an invite automatically through the lead creation process.

---

## 📱 Phase 3: Mobile App (React Native)

### Directory Structure
```
/app/mobile/
  ├── android/        # Android-specific code
  ├── ios/            # iOS-specific code
  ├── src/
  │   ├── screens/    # App screens
  │   ├── components/ # Reusable components
  │   ├── services/   # API services
  │   └── utils/      # Helper functions
  ├── App.js
  └── package.json
```

### Mobile App Features
1. ✅ Create estimates in the field
2. ✅ Capture customer signatures
3. ✅ Upload photos for line items
4. ✅ GPS tracking and routing
5. ✅ Convert estimate to invoice
6. ✅ View schedule
7. ✅ Offline capability

**Status:** Architecture ready, implementation in next phase

---

## 🎨 Phase 4: UI/UX Improvements

### Branding Standards (Boatman Systems™)

```css
:root {
  --primary-blue: #1b7abf;    /* Primary UI, headers, links */
  --trust-green: #059669;     /* TCEQ/licensed badges */
  --action-orange: #ea580c;   /* CTA buttons */
}
```

**Typography:** Inter font, weight 900, italic for headings, uppercase

### Customer Portal Design
- ✅ Modern glassmorphism effects
- ✅ Professional Boatman Systems™ branding
- ✅ Mobile-responsive design
- ✅ Intuitive navigation
- ✅ Real-time data from ERPNext

### Marketing Site Improvements
File: `/app/setup_site/`
- Current: Plain HTML/CSS/JS
- Improvements: Already has professional design with Boatman AI™ chatbot

---

## 🔒 Security Configuration

### Production Checklist

- [ ] Change `JWT_SECRET_KEY` in backend/.env
- [ ] Update CORS origins in backend/server.py
- [ ] Set strong ERPNext API credentials
- [ ] Enable HTTPS for all endpoints
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Enable rate limiting on APIs

---

## 📦 Deployment to Production

### Backend (Customer Portal API)

1. Update frontend URL in `.env`:
   ```env
   FRONTEND_URL=https://portal.aaairrigationservice.com
   ```

2. Start with Supervisor:
   ```bash
   sudo supervisorctl restart backend
   ```

### Frontend (Customer Portal)

1. Build for production:
   ```bash
   cd /app/frontend
   yarn build
   ```

2. Serve with Nginx:
   ```nginx
   server {
       listen 80;
       server_name portal.aaairrigationservice.com;
       
       root /app/frontend/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8001;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

---

## 📊 Monitoring & Logs

### Check Backend Logs
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log
```

### Check Frontend Logs
```bash
tail -f /var/log/supervisor/frontend.err.log
tail -f /var/log/supervisor/frontend.out.log
```

### Supervisor Control
```bash
sudo supervisorctl status
sudo supervisorctl restart all
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

---

## ❓ Troubleshooting

### Issue: Magic Link Not Sending
- Check SMTP credentials in `.env`
- Verify Yahoo App Password (not regular password)
- Check backend logs for email errors

### Issue: ERPNext API Not Working
- Verify API Key/Secret in `.env`
- Check ERPNext API Access is enabled
- Test with: `curl -H "Authorization: token KEY:SECRET" https://erp.aaairrigationservice.com/api/resource/Customer`

### Issue: Customer Not Found
- Ensure customer has `email_id` field populated in ERPNext
- Check customer record exists
- Verify ERPNext API permissions

---

## 📞 Support

For technical support:
- Email: info@aaairrigationservice.com
- Phone: 469-751-3567

**Powered by Boatman Systems™**