#!/bin/bash
# Deploy Tech Schedule page to ERPNext on Linode B
# AAA Irrigation Service — Powered by Boatman Systems™

set -e

SSH_KEY="$HOME/.ssh/id_gemini_cli"
SSH_HOST="deploy@100.106.12.60"
CONTAINER="frappe_docker-backend-1"
SITE="erp.aaairrigationservice.com"
APP_PATH="/home/frappe/frappe-bench/apps/erpnext_3cx/erpnext_3cx"
DEPLOY_DIR="$(dirname "$0")/tech_schedule_deploy"

echo "=== Tech Schedule Page Deployment ==="
echo ""

# Step 1: Create page directory in container
echo "[1/6] Creating page directory structure..."
ssh -i "$SSH_KEY" "$SSH_HOST" "sudo docker exec $CONTAINER mkdir -p $APP_PATH/erpnext_3cx/page/tech_schedule"

# Step 2: Copy page files to remote host, then into container
echo "[2/6] Uploading page files..."
scp -i "$SSH_KEY" "$DEPLOY_DIR/tech_schedule.json" "$SSH_HOST:/tmp/ts_page.json"
scp -i "$SSH_KEY" "$DEPLOY_DIR/tech_schedule.js" "$SSH_HOST:/tmp/ts_page.js"
scp -i "$SSH_KEY" "$DEPLOY_DIR/tech_schedule.css" "$SSH_HOST:/tmp/ts_page.css"
scp -i "$SSH_KEY" "$DEPLOY_DIR/tech_schedule.py" "$SSH_HOST:/tmp/ts_page.py"
scp -i "$SSH_KEY" "$DEPLOY_DIR/__init__.py" "$SSH_HOST:/tmp/ts_init.py"
scp -i "$SSH_KEY" "$DEPLOY_DIR/api_addition.py" "$SSH_HOST:/tmp/ts_api_addition.py"

echo "[3/6] Copying files into container..."
ssh -i "$SSH_KEY" "$SSH_HOST" "
sudo docker cp /tmp/ts_page.json $CONTAINER:$APP_PATH/erpnext_3cx/page/tech_schedule/tech_schedule.json
sudo docker cp /tmp/ts_page.js $CONTAINER:$APP_PATH/erpnext_3cx/page/tech_schedule/tech_schedule.js
sudo docker cp /tmp/ts_page.css $CONTAINER:$APP_PATH/erpnext_3cx/page/tech_schedule/tech_schedule.css
sudo docker cp /tmp/ts_page.py $CONTAINER:$APP_PATH/erpnext_3cx/page/tech_schedule/tech_schedule.py
sudo docker cp /tmp/ts_init.py $CONTAINER:$APP_PATH/erpnext_3cx/page/tech_schedule/__init__.py
"

# Step 4: Append API function to api.py
echo "[4/6] Adding get_schedule_data API endpoint..."
ssh -i "$SSH_KEY" "$SSH_HOST" "
# Read current api.py and check if function already exists
if sudo docker exec $CONTAINER grep -q 'def get_schedule_data' $APP_PATH/api.py; then
    echo '  -> get_schedule_data already exists in api.py, skipping'
else
    # Append the new function
    sudo docker cp /tmp/ts_api_addition.py $CONTAINER:/tmp/ts_api_addition.py
    sudo docker exec $CONTAINER bash -c 'cat /tmp/ts_api_addition.py >> $APP_PATH/api.py'
    echo '  -> Added get_schedule_data to api.py'
fi
" 2>&1 || {
    # Fallback: use direct approach
    echo "  -> Using direct append method..."
    ssh -i "$SSH_KEY" "$SSH_HOST" "
    sudo docker cp /tmp/ts_api_addition.py $CONTAINER:/tmp/ts_api_addition.py
    sudo docker exec $CONTAINER bash -c 'cat /tmp/ts_api_addition.py >> ${APP_PATH}/api.py'
    "
}

# Step 5: Fix ownership
echo "[5/6] Fixing file ownership..."
ssh -i "$SSH_KEY" "$SSH_HOST" "
sudo docker exec $CONTAINER chown -R frappe:frappe $APP_PATH/erpnext_3cx/page/tech_schedule/
sudo docker exec $CONTAINER chown frappe:frappe $APP_PATH/api.py
"

# Step 6: Clear cache and build
echo "[6/6] Clearing cache and building assets..."
ssh -i "$SSH_KEY" "$SSH_HOST" "
sudo docker exec $CONTAINER bench --site $SITE clear-cache
sudo docker exec $CONTAINER bench build --app erpnext_3cx
sudo docker exec $CONTAINER bench --site $SITE migrate
"

echo ""
echo "=== Deployment Complete ==="
echo "Access: https://$SITE/app/tech-schedule"
echo ""
