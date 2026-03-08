# AAA Irrigation Service Powered by Boatman Systems™
## Master Infrastructure & CRM Blueprint

### 1. Project Overview & Identity
**Goal:** Transform Integrity Flow Powered by Boatman Systems™ into a specialized Field Service Management (FSM) & CRM platform for AAA Irrigation Service.
**Core Branding:**
- **System Name:** AAA Irrigation Service Powered by Boatman Systems™
- **Module Branding:** "Powered by Boatman Systems™" visible on every module.
- **Visual Identity:**
    - **Primary Color:** Deep Sky Blue (`#1b7abf`) - Synced with Live Site.
    - **Trust Accent:** Emerald Green (`#059669`) - For TCEQ and Licensed status.
    - **Action Color:** High-Vis Orange (`#ea580c`) - Optimized for CTA buttons.
- **Typography:** Black-weight Sans-Serif (Inter/Black), heavy italics for brand flair.
- **Structure:** Massive centered logo backdrop for high-impact brand recognition.

### 2. Infrastructure Stack
| Component | Hardware/Host | Role | Status |
| :--- | :--- | :--- | :--- |
| **AI Stack** | Linode A (4GB) | Ollama, OpenClaw (LLM Backend) | Active |
| **Business Stack** | Linode B (4GB) | Integrity Flow Powered by Boatman Systems™, Portal, Live Website (Setup) | **Active & Optimized** |
| **Edge Cluster** | 3x RPi4 | Testing (Kali), Local Dev, Staging | Available |
| **Local AI** | Ubuntu (Local) | Ollama (DeepSeek-Coder:6.7b & 16b) | **Installed & Functional** |
| **The Vault** | Synology NAS | Database Backups, Secure File Storage | **Next Priority** |
| **Telephony** | 3CX System | VoIP, Caller ID Lookup, CRM Pop-ups | Active |

---

### 3. Progress Log (March 2026)
**Completed Actions:**
1. **Server Stabilization:** Fixed Integrity Flow scheduler, reclaimed 7.4GB space, optimized Nginx routing.
2. **Website Professionalization (setup.aaairrigationservice.com):**
    - **Market Segmentation:** Created distinct "Residential Repair" and "Commercial Management" service silos.
    - **Branding Update:** Transitioned system name to **Integrity Flow Powered by Boatman Systems™**.
    - **UI/UX:** Implemented full-width stretched logo header and glassmorphism interactive elements.
    - **Gallery:** Integrated high-resolution project photos (`Broken Head.jpg`, `Backflow RPZ.jpg`, etc.).
3. **AI Portal Bot Integration:**
    - **Boatman AI™:** Deployed interactive chat widget with specialized technical persona.
    - **Ollama Backend:** Successfully linked frontend bot to Server A (`qwen2.5-coder`) via backend proxy.
4. **Email & Communication:**
    - **SMTP Configuration:** Created comprehensive guide for Yahoo/Cloudflare outgoing mail setup.
    - **3CX Integration:** Drafted server-side Python script for automated call metadata capturing.
5. **Infrastructure:**
    - **Docker Deployment:** Established robust pipeline to push prototype updates directly into `aaa_frontend` containers.
    - **Tailscale Security:** Configured secure workstation-to-server deployment via Tailscale IP `100.106.12.60`.

---

### 4. CRM & Sales Pipeline Workflow
The system follows an automated linear progression from initial contact to paid invoice.

1. **Lead Generation & Telephony (3CX Integrated):**
    - **Incoming Call:** Intercepts caller ID.
    - **New Caller:** Auto-opens "Lead" page.
    - **Known Contact:** Opens "Customer Dashboard" with history and equipment list.
    - **Enhancement:** Custom script to log `Call Start Time`, `Duration`, and `Date` directly into the "Communication" log.
2. **Estimation & Sales:**
    - **Lead -> Estimate:** Convert Lead to Opportunity/Quotation.
    - **On-Site Estimation:** Techs use mobile view to add line items.
    - **Approval & E-Sign:** Estimate is emailed to customer and available in the Portal for digital signature.
3. **Invoicing & Conversion:**
    - Signed Estimate converts to **Sales Order** and **Invoice**.
    - Real-time updates in the Customer Portal showing "Paid" vs "Outstanding".
4. **Scheduling & Dispatch:**
    - 2-Way Sync with **Google Calendar**.
    - Jobs booked via AI/Portal are pushed to the technician's calendar and the Integrity Flow "Work Order" list.

---

### 5. AI & Customer Portal Features
A self-service hub "Powered by Boatman Systems™" for clients to manage their irrigation needs.

- **Portal AI (Boatman AI):**
    - Connected to Server A (Ollama) with access to AAA Irrigation's service manual and customer history.
    - Helps with technical questions (e.g., "How do I reset my controller?") and scheduling.
- **Documents:** View & Sign Estimates; View & Pay Invoices (Stripe/PayPal integration).

---

### 6. Next Steps for "Boatman Systems™"
1. **3CX Call Logging Script:** Write a Server Script in Integrity Flow Powered by Boatman Systems™ to automatically log call metadata from the 3CX pop-up event.
2. **The Vault (Synology Backup):** Configure a secure, automated backup pipeline from Linode B to the local Synology NAS via Tailscale.
3. **AI Portal Bot Integration:** Fully integrate Server A (Ollama) into the new website's frontend.
4. **RPi4 AI Cluster:** Install Ollama on the 3x RPi4 nodes with small models (Qwen2.5-Coder:1.5b) for low-power coding tasks.

---

### 7. Contact & System Details
- **Business Name:** AAA Irrigation Service LLC
- **Phone:** 469-751-3567
- **Web:** aaairrigationservice.com
- **Portal Email:** info@aaairrigationservice.com
- **System Email (Yahoo):** aaairrigationservice@yahoo.com
- **Mailing/Billing:** Managed via the Boatman Systems™ Portal
