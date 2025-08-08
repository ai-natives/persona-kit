#!/bin/bash

# Check if backend is already running
if curl -s http://localhost:8100/health > /dev/null 2>&1; then
    echo "✅ Backend already running on port 8100"
    exit 0
fi

# If not running, start it
echo "🚀 Starting backend on port 8100..."
cd backend && uv run uvicorn api_server:app --host 0.0.0.0 --port 8100 --reload