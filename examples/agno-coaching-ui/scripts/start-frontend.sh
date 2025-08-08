#!/bin/bash

# Check if frontend is already running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend already running on port 5173"
    exit 0
fi

# If not running, start it
echo "🚀 Starting frontend on port 5173..."
cd frontend && pnpm dev