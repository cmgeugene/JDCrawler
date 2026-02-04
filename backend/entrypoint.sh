#!/bin/bash
set -e

echo "Starting Xvfb..."
# Start Xvfb in the background on display :99
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

echo "Waiting for Xvfb to be ready..."
sleep 1

echo "Starting Backend Server..."
# Execute uvicorn as the main process
exec uvicorn jdcrawler.main:app --host 0.0.0.0 --port 8000
