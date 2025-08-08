#!/bin/bash
# Start Career Navigator Backend with logging

LOG_DIR="/tmp/personakit-logs"
mkdir -p "$LOG_DIR"

echo "Starting Career Navigator Backend with logging to $LOG_DIR/career-backend.log"
cd backend
uv run python main.py 2>&1 | tee "$LOG_DIR/career-backend.log"