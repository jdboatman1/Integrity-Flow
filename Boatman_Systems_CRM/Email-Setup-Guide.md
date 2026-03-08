# Integrity Flow Powered by Boatman Systems™
## Email Configuration Guide (Outgoing/SMTP)

To enable Integrity Flow to send emails (Estimates, Invoices, and System Alerts) via your Yahoo/Cloudflare setup, follow these steps within the **Integrity Flow** desk.

### 1. Generate a Yahoo App Password
Since you are using a Yahoo-backed system, you **must** use an "App Password" rather than your standard login password.
1. Log in to your Yahoo account settings.
2. Go to **Account Security** > **Generate App Password**.
3. Select "Other App" and name it "Integrity Flow - Boatman Systems".
4. Copy the 16-character code provided.

### 2. Configure the Email Domain
In Integrity Flow, search for **Email Domain** and create a new record:
- **Domain Name:** `aaairrigationservice.com`
- **Outgoing Server:** `smtp.mail.yahoo.com`
- **Port:** `465` (SSL)
- **Use TLS:** Enabled
- **Attachment Limit:** 10 MB

### 3. Configure the Email Account
Search for **Email Account** and create a new record for `info@aaairrigationservice.com`:
- **Email Address:** `info@aaairrigationservice.com`
- **Email ID:** `info@aaairrigationservice.com`
- **Enable Outgoing:** Checked
- **Service:** Yahoo Mail (or leave blank and use custom)
- **SMTP Server:** `smtp.mail.yahoo.com`
- **Username:** `aaairrigationservice@yahoo.com` (Your actual Yahoo account)
- **Password:** `[PASTE_YOUR_16_CHAR_APP_PASSWORD_HERE]`
- **Always use this for Outgoing:** Checked

### 4. Verification (Cloudflare SPF/DKIM)
To ensure your emails don't hit the "Spam" folder, ensure your **Cloudflare DNS** includes these records:
- **SPF:** `v=spf1 include:_spf.mx.cloudflare.net include:mail.yahoo.com ~all`
- **DKIM:** Ensure Yahoo's DKIM records are mirrored if available.

---
**Boatman Systems™ Status:** Once these settings are saved in Integrity Flow, the system will automatically begin using the "Artificial Rain™" quality standard for all customer communications.
