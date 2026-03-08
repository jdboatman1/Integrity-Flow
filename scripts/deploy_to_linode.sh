#!/bin/bash
# Integrity Flow Powered by Boatman Systems™
# Deployment Automation: Setup Prototype to Linode B

# Configuration
SOURCE_DIR="/home/john/boatman-systems/setup_site/"
REMOTE_HOST="96.126.117.73"
REMOTE_USER="deploy"
REMOTE_PATH="/var/www/setup.aaairrigationservice.com/"

echo "---------------------------------------------------------"
echo "Boatman Systems™ - Initiating Elite Deployment Pipeline"
echo "Target: setup.aaairrigationservice.com (Linode B)"
echo "---------------------------------------------------------"

# 1. Verify Local Files
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory $SOURCE_DIR not found."
    exit 1
fi

# 2. Sync Files (RSYNC)
echo "Syncing local prototype to Linode B..."
rsync -avz --progress -e "ssh -i /home/john/.ssh/id_gemini_cli" --rsync-path="sudo rsync" "$SOURCE_DIR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

# 3. Fix Permissions on Remote Server
echo "Applying Boatman Standard permissions..."
ssh -i /home/john/.ssh/id_gemini_cli "$REMOTE_USER@$REMOTE_HOST" "sudo chown -R www-data:www-data $REMOTE_PATH && sudo chmod -R 755 $REMOTE_PATH"

echo "---------------------------------------------------------"
echo "Integrity Flow Deployment Complete!"
echo "Check your site at: http://setup.aaairrigationservice.com"
echo "---------------------------------------------------------"
