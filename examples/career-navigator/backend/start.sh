#!/usr/bin/env bash
# Start Career Navigator Backend with logging

# Set log file location
export LOG_FILE="./app.log"

# Start the service
exec uv run python main.py