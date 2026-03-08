#!/bin/bash
# Integrity Flow Powered by Boatman Systems™
# Deployment: Boatman AI™ Proxy → Linode B

REMOTE_HOST="96.126.117.73"
REMOTE_USER="deploy"
SSH="ssh -i /home/john/.ssh/id_gemini_cli"
SCP="scp -i /home/john/.ssh/id_gemini_cli"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "---------------------------------------------------------"
echo "Boatman Systems™ - Deploying Boatman AI™ Proxy"
echo "Target: Linode B ($REMOTE_HOST)"
echo "---------------------------------------------------------"

# 1. Create destination directory
$SSH "$REMOTE_USER@$REMOTE_HOST" "sudo mkdir -p /opt/boatman && sudo chown $REMOTE_USER /opt/boatman"

# 2. Upload proxy script
echo "Uploading ai_proxy.py..."
$SCP "$SCRIPT_DIR/ai_proxy.py" "$REMOTE_USER@$REMOTE_HOST:/opt/boatman/ai_proxy.py"
$SSH "$REMOTE_USER@$REMOTE_HOST" "sudo chown www-data:www-data /opt/boatman/ai_proxy.py && sudo chmod 755 /opt/boatman/ai_proxy.py"

# 3. Install systemd service
echo "Installing systemd service..."
$SCP "$SCRIPT_DIR/ai_proxy.service" "$REMOTE_USER@$REMOTE_HOST:/tmp/boatman-ai-proxy.service"
$SSH "$REMOTE_USER@$REMOTE_HOST" "sudo mv /tmp/boatman-ai-proxy.service /etc/systemd/system/boatman-ai-proxy.service && sudo systemctl daemon-reload && sudo systemctl enable boatman-ai-proxy && sudo systemctl restart boatman-ai-proxy"

# 4. Verify service is running
echo "Verifying service status..."
$SSH "$REMOTE_USER@$REMOTE_HOST" "sudo systemctl is-active boatman-ai-proxy && echo 'Proxy is RUNNING' || echo 'ERROR: Proxy failed to start — check: journalctl -u boatman-ai-proxy'"

# 5. Print required Nginx config
echo ""
echo "---------------------------------------------------------"
echo "ACTION REQUIRED: Add this location block to the Nginx"
echo "server config for setup.aaairrigationservice.com"
echo "(typically /etc/nginx/sites-available/setup.aaairrigationservice.com)"
echo "---------------------------------------------------------"
cat << 'EOF'

    location /api/ai/chat {
        proxy_pass         http://127.0.0.1:11436;
        proxy_http_version 1.1;
        proxy_set_header   Host $host;
        proxy_read_timeout 90s;
    }

EOF
echo "Then run: sudo nginx -t && sudo systemctl reload nginx"
echo "---------------------------------------------------------"
echo "Boatman AI™ Proxy deployment complete."
