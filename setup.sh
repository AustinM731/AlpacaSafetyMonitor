#!/bin/bash

ALPACA_APP_DIR="/opt/ASCOM/AlpacaSafetyMonitor"
WEATHER_APP_DIR="/opt/ASCOM/Weather"
ALPACA_SERVICE_NAME="AlpacaSafetyMonitor"
WEATHER_SERVICE_NAME="Weather"
PYTHON_SCRIPT="app.py"
REQUIREMENTS_FILE="requirements.txt"
GITHUB_REPO="https://github.com/AustinM731/AlpacaFlats.git"
ALPACA_VENV_DIR="$ALPACA_APP_DIR/venv"
WEATHER_VENV_DIR="$WEATHER_APP_DIR/venv"

# Extract Git directory name
# GIT_DIR_NAME=$(basename -s .git "$GITHUB_REPO")
# GIT_CLONE_DIR="$ALPACA_APP_DIR/$GIT_DIR_NAME"
# VENV_DIR="$GIT_CLONE_DIR/venv"


# Installation of Python and virtualenv
apt-get update
apt-get install -y python3 python3-venv git

# Create application directory and clone the repo
mkdir -p $ALPACA_APP_DIR

# Move contents of repo to application directory
mv Alpaca $ALPACA_APP_DIR

# Set up Python virtual environment
if [ ! -d "$ALPACA_VENV_DIR" ]; then
    python3 -m venv $ALPACA_VENV_DIR
fi
$ALPACA_VENV_DIR/bin/pip install -r $ALPACA_APP_DIR/Alpaca/$REQUIREMENTS_FILE

# Create a systemd service file
ALPACA_SERVICE_FILE="/etc/systemd/system/$ALPACA_SERVICE_NAME.service"
echo "[Unit]
Description=ASCOM Alpaca driver for Flat Panel Calibrator Device
After=network.target

[Service]
Type=simple
ExecStart=$ALPACA_VENV_DIR/bin/python $ALPACA_APP_DIR/Alpaca/$PYTHON_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee $ALPACA_SERVICE_FILE

# Reload systemd to include new service, then start and enable it
systemctl daemon-reload
systemctl start $ALPACA_SERVICE_NAME
systemctl enable $ALPACA_SERVICE_NAME

echo "Installation complete. Service $ALPACA_SERVICE_NAME started."

