#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Pulling latest changes..."
git -C "$SCRIPT_DIR" pull

echo "==> Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"

echo "==> Installing dependencies..."
"$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
"$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo "==> Installing systemd service..."
CURRENT_USER="$(whoami)"
sed -e "s|/home/pi/scripts/allskyAPI|${SCRIPT_DIR}|g" \
    -e "s|User=pi|User=${CURRENT_USER}|g" \
    "$SCRIPT_DIR/allsky-api.service" | sudo tee /etc/systemd/system/allsky-api.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable allsky-api.service
sudo systemctl restart allsky-api.service

echo "==> Checking service status..."
sudo systemctl status allsky-api.service --no-pager

echo ""
echo "==> Done! API is running on port 8080"
echo "    Try: curl http://localhost:8080/"
echo "    Docs: http://localhost:8080/docs"
echo ""
echo "    Useful commands:"
echo "      sudo systemctl status allsky-api    # Check status"
echo "      sudo systemctl stop allsky-api      # Stop service"
echo "      sudo systemctl start allsky-api     # Start service"
echo "      sudo systemctl restart allsky-api   # Restart service"
echo "      sudo journalctl -u allsky-api -f    # Follow logs"
