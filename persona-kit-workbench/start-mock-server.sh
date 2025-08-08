#!/bin/bash
# Start PersonaKit Workbench Mock API Server with logging enabled

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set environment variables for logging
export LOG_FILE="${LOG_FILE:-./app.log}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_FORMAT="${LOG_FORMAT:-text}"

# Mock server specific settings
export MOCK_SERVER_PORT="${MOCK_SERVER_PORT:-8043}"  # Different from PersonaKit API

# Ensure log directory exists
LOG_DIR=$(dirname "$LOG_FILE")
if [ "$LOG_DIR" != "." ] && [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

echo "Starting PersonaKit Workbench Mock Server..."
echo "Server will run on port: $MOCK_SERVER_PORT"
echo "Logs will be written to: $LOG_FILE"

# Start the mock server
exec uv run python mock_api_server.py