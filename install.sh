#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"

echo "==> Installing dependencies..."
"$SCRIPT_DIR/venv/bin/pip" install --upgrade pip
"$SCRIPT_DIR/venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo "==> Installing systemd service..."
sudo cp "$SCRIPT_DIR/allsky-api.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable allsky-api.service
sudo systemctl restart allsky-api.service

echo "==> Done! API is running on port 8080"
echo "    Try: curl http://localhost:8080/"
echo "    Docs: http://localhost:8080/docs"
