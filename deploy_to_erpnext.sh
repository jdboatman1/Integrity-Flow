#!/bin/bash
# DEPLOY TO ERPNEXT SERVER

echo "================================================"
echo "Integrity Flow Custom App - Quick Deploy"
echo "================================================"

# 1. Copy the fixed files to your ERPNext server
echo "Step 1: Copying files to ERPNext server..."
scp -i ~/.ssh/id_gemini_cli /app/erpnext_custom_app_fixed.tar.gz deploy@100.106.12.60:~/

# 2. SSH and deploy
echo "Step 2: Deploying on ERPNext server..."
ssh -i ~/.ssh/id_gemini_cli deploy@100.106.12.60 << 'ENDSSH'
    # Extract files
    cd ~
    tar -xzf erpnext_custom_app_fixed.tar.gz
    
    # Backup existing app
    cd ~/frappe-bench/apps/
    if [ -d "integrity_flow_custom" ]; then
        mv integrity_flow_custom integrity_flow_custom.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Copy new version
    cp -r ~/erpnext_custom_app/integrity_flow_custom .
    
    # Restart bench
    cd ~/frappe-bench
    bench restart
    
    echo "✅ Deployment complete!"
ENDSSH

echo "================================================"
echo "✅ DONE! Test your estimate form now!"
echo "================================================"
