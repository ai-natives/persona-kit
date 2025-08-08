#!/bin/bash

# Export environment variables from shell
export OPENAI_API_KEY="${OPENAI_API_KEY}"

# Check if backend is already running
if lsof -ti:8103 > /dev/null 2>&1; then
    echo "✅ Backend already running on port 8103"
    exit 0
fi

# If not running, start it
echo "🚀 Starting backend on port 8103..."
cd backend && uv run python main.py