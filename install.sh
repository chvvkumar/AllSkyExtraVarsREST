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

echo "==> Done! API is running on port 8080"
echo "    Try: curl http://localhost:8080/"
echo "    Docs: http://localhost:8080/docs"
