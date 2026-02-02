#!/bin/bash
cd "$(dirname "$0")/backend"
source .venv/bin/activate
echo "Starting Backend Server on 0.0.0.0..."
uvicorn jdcrawler.main:app --reload --host 0.0.0.0
