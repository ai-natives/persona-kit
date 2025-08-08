#!/usr/bin/env bash
# Start Agno Coaching Backend with logging

# Set log file location
export LOG_FILE="./app.log"

# Start the service
exec uv run python api_server.py