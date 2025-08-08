#!/bin/bash

# Check if frontend is already running
if curl -s http://localhost:5175 > /dev/null 2>&1; then
    echo "✅ Frontend already running on port 5175"
    exit 0
fi

# If not running, start it
echo "🚀 Starting frontend on port 5175..."
cd frontend && pnpm dev