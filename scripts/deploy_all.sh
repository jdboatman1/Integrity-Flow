#!/bin/bash
# Deploy all Integrity Flow components to Linode B
# AAA Irrigation Service — Powered by Boatman Systems™

set -e

SSH_KEY="$HOME/.ssh/id_gemini_cli"
SSH_HOST="deploy@100.106.12.60"
ERP_CONTAINER="frappe_docker-backend-1"
SITE="erp.aaairrigationservice.com"
ERP_APPS_BASE="/home/frappe/frappe-bench/apps"
WEBSITE_PATH="/opt/aaa-website"
SETUP_SITE_PATH="/var/www/setup.aaairrigationservice.com"

echo "---------------------------------------------------------"
echo "Boatman Systems™ - Initiating Master Deployment Pipeline"
echo "Target: erp.aaairrigationservice.com (Linode B)"
echo "---------------------------------------------------------"

# 1. Sync ERP Apps (to /tmp then into container)
echo "[1/4] Syncing ERP Custom Apps..."

# Sync erpnext_3cx
echo "  -> Syncing erpnext_3cx..."
rsync -avz --progress -e "ssh -i $SSH_KEY" --exclude '.git' erpnext_3cx/ "$SSH_HOST:/tmp/erpnext_3cx/"
ssh -i "$SSH_KEY" "$SSH_HOST" "sudo docker cp /tmp/erpnext_3cx/. $ERP_CONTAINER:$ERP_APPS_BASE/erpnext_3cx/"

# Sync integrity_flow_custom
echo "  -> Syncing integrity_flow_custom..."
rsync -avz --progress -e "ssh -i $SSH_KEY" --exclude '.git' erpnext_custom_app/ "$SSH_HOST:/tmp/integrity_flow_custom/"
ssh -i "$SSH_KEY" "$SSH_HOST" "sudo docker cp /tmp/integrity_flow_custom/. $ERP_CONTAINER:$ERP_APPS_BASE/integrity_flow_custom/"

# 2. Sync Website Stack (Frontend/Backend)
echo "[2/4] Syncing Website Stack (Frontend/Backend)..."
rsync -avz --progress -e "ssh -i $SSH_KEY" --exclude '.git' --exclude 'node_modules' frontend/ "$SSH_HOST:/tmp/frontend/"
rsync -avz --progress -e "ssh -i $SSH_KEY" --exclude '.git' --exclude '__pycache__' backend/ "$SSH_HOST:/tmp/backend/"
ssh -i "$SSH_KEY" "$SSH_HOST" "sudo cp -r /tmp/frontend/* $WEBSITE_PATH/frontend/ && sudo cp -r /tmp/backend/* $WEBSITE_PATH/backend/"

# 3. Sync Setup Site
echo "[3/4] Syncing Setup Site (setup.aaairrigationservice.com)..."
rsync -avz --progress -e "ssh -i $SSH_KEY" --exclude '.git' setup_site/ "$SSH_HOST:/tmp/setup_site/"
ssh -i "$SSH_KEY" "$SSH_HOST" "sudo cp -r /tmp/setup_site/* $SETUP_SITE_PATH/"

# 4. Finalize & Restart
echo "[4/4] Finalizing & Restarting Services..."

# ERP: Clear cache and migrate
echo "  -> ERP: bench clear-cache, migrate..."
ssh -i "$SSH_KEY" "$SSH_HOST" "
sudo docker exec $ERP_CONTAINER bench --site $SITE clear-cache
sudo docker exec $ERP_CONTAINER bench --site $SITE migrate
"

# Website: Restart containers
echo "  -> Website: Restarting containers..."
ssh -i "$SSH_KEY" "$SSH_HOST" "cd $WEBSITE_PATH && sudo docker compose restart"

echo "---------------------------------------------------------"
echo "Integrity Flow Full Deployment Complete!"
echo "ERP: https://$SITE"
echo "Setup Site: http://setup.aaairrigationservice.com"
echo "---------------------------------------------------------"
