#!/bin/bash
# Start PersonaKit Workbench CLI with logging enabled

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set environment variables for logging
export LOG_FILE="${LOG_FILE:-./app.log}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_FORMAT="${LOG_FORMAT:-text}"

# Ensure log directory exists
LOG_DIR=$(dirname "$LOG_FILE")
if [ "$LOG_DIR" != "." ] && [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

echo "Starting PersonaKit Workbench CLI..."
echo "Logs will be written to: $LOG_FILE"

# Pass all arguments to the CLI
exec uv run persona-kit-workbench "$@"