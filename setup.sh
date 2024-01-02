#!/bin/bash

ALPACA_APP_DIR="/opt/ASCOM/AlpacaSafetyMonitor"
WEATHER_APP_DIR="/opt/ASCOM/Weather"
ALPACA_SERVICE_NAME="AlpacaSafetyMonitor"
WEATHER_SERVICE_NAME="Weather"
ALPACA_PYTHON_SCRIPT="app.py"
WEATHER_PYTHON_SCRIPT="weather.py"
REQUIREMENTS_FILE="requirements.txt"
ALPACA_VENV_DIR="$ALPACA_APP_DIR/venv"
WEATHER_VENV_DIR="$WEATHER_APP_DIR/venv"
APP_USER="austin"

# Installation of Python and virtualenv
apt-get update
apt-get install -y python3 python3-venv git

# Create application directory and clone the repo
mkdir -p $ALPACA_APP_DIR
mkdir -p $WEATHER_APP_DIR

# Move contents of Alpaca repo to application directory
cp -r Alpaca/* $ALPACA_APP_DIR/

# Move contents of WeatherStation repo to application directory
cp -r WeatherStation/* $WEATHER_APP_DIR/

# Set up Python virtual environment for Alpaca
if [ ! -d "$ALPACA_VENV_DIR" ]; then
    python3 -m venv $ALPACA_VENV_DIR
fi
$ALPACA_VENV_DIR/bin/pip install -r $ALPACA_APP_DIR/$REQUIREMENTS_FILE

# Set up Python virtual environment for Weather
if [ ! -d "$WEATHER_VENV_DIR" ]; then
    python3 -m venv $WEATHER_VENV_DIR
fi
$WEATHER_VENV_DIR/bin/pip install -r $WEATHER_APP_DIR/$REQUIREMENTS_FILE

# Change ownership of application directory to user
chown -R $APP_USER:$APP_USER $ALPACA_APP_DIR
chown -R $APP_USER:$APP_USER $WEATHER_APP_DIR

# Create a systemd service file for Alpaca
ALPACA_SERVICE_FILE="/etc/systemd/system/$ALPACA_SERVICE_NAME.service"
echo "[Unit]
Description=ASCOM Alpaca driver for Flat Panel Calibrator Device
After=network.target

[Service]
Type=simple
ExecStart=$ALPACA_VENV_DIR/bin/python $ALPACA_APP_DIR/$ALPACA_PYTHON_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee $ALPACA_SERVICE_FILE

# Create a systemd service file for Weather
WEATHER_SERVICE_FILE="/etc/systemd/system/$WEATHER_SERVICE_NAME.service"
echo "[Unit]
Description=ASCOM Weather Station Service
After=network.target

[Service]
Type=simple
ExecStart=$WEATHER_VENV_DIR/bin/python $WEATHER_APP_DIR/$WEATHER_PYTHON_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target" | sudo tee $WEATHER_SERVICE_FILE

# Reload systemd to include new services, then start and enable them
systemctl daemon-reload
systemctl start $ALPACA_SERVICE_NAME
systemctl enable $ALPACA_SERVICE_NAME
systemctl restart $ALPACA_SERVICE_NAME
systemctl start $WEATHER_SERVICE_NAME
systemctl enable $WEATHER_SERVICE_NAME
systemctl restart $WEATHER_SERVICE_NAME

echo "Installation complete. Services $ALPACA_SERVICE_NAME and $WEATHER_SERVICE_NAME started."
