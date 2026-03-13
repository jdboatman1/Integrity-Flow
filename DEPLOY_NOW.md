# DEPLOY NOW - MANUAL STEPS

## You need to deploy the files to your ERPNext server!

The files are ready here: `/app/erpnext_custom_app/`

---

## 🚀 **QUICK DEPLOY (Option 1 - Automatic):**

Run this ONE command on your local machine:

```bash
/app/deploy_to_erpnext.sh
```

This will automatically:
1. Copy files to your server
2. Deploy them
3. Restart ERPNext

**Done in 30 seconds!**

---

## 📋 **MANUAL DEPLOY (Option 2 - Step by Step):**

### From YOUR machine (not the server):

```bash
# 1. Copy the archive to your server
scp -i ~/.ssh/id_gemini_cli /app/erpnext_custom_app_fixed.tar.gz deploy@100.106.12.60:~/

# 2. SSH to your server
ssh -i ~/.ssh/id_gemini_cli deploy@100.106.12.60
```

### Now on YOUR ERPNext server:

```bash
# 3. Extract files
cd ~
tar -xzf erpnext_custom_app_fixed.tar.gz

# 4. Backup existing (if any)
cd ~/frappe-bench/apps/
mv integrity_flow_custom integrity_flow_custom.backup.$(date +%Y%m%d)

# 5. Copy new version
cp -r ~/erpnext_custom_app/integrity_flow_custom .

# 6. Restart bench
cd ~/frappe-bench
bench restart

# 7. Done!
```

---

## ✅ **VERIFY IT WORKED:**

1. Open ERPNext: https://erp.aaairrigationservice.com
2. Create New Quotation
3. Select a Customer/Lead
4. **Check:** Do the address fields populate? ✅
5. **Check:** Is a line item added? ✅
6. Click Save
7. **Check:** Does it save successfully? ✅

---

## 🔍 **If It Still Doesn't Work:**

Check the bench logs:

```bash
# On your ERPNext server:
cd ~/frappe-bench
tail -100 logs/erp.aaairrigationservice.com.log
```

Look for errors related to "quotation" or "integrity_flow_custom"

---

## 📁 **What's Being Deployed:**

- `/app/erpnext_custom_app/integrity_flow_custom/events/quotation.py` - Fixed address population
- `/app/erpnext_custom_app/integrity_flow_custom/hooks.py` - Fixed function names
- `/app/erpnext_custom_app/integrity_flow_custom/fixtures/custom_fields.json` - Address fields

---

## ⚠️ **Important:**

The files in `/app/erpnext_custom_app/` are the FIXED versions.

Your ERPNext server at `erp.aaairrigationservice.com` is currently running the OLD broken version.

**You MUST deploy to see the changes!**

---

**Choose Option 1 (automatic script) or Option 2 (manual steps) and deploy now!**
