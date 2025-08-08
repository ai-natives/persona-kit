#!/usr/bin/env bash
# Start Admin Dashboard Backend with logging

# Set log file location
export LOG_FILE="./app.log"

# Start the service
exec uv run python main.py