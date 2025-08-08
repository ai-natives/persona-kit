#!/usr/bin/env bash
# Stop Agno Coaching UI (backend + frontend)

echo "Stopping Agno Coaching UI..."

# Kill processes on the specific ports
if lsof -ti :8100 >/dev/null 2>&1; then
    kill $(lsof -ti :8100) 2>/dev/null
    echo "  ✓ Stopped backend (port 8100)"
else
    echo "  - Backend not running (port 8100)"
fi

if lsof -ti :5174 >/dev/null 2>&1; then
    kill $(lsof -ti :5174) 2>/dev/null
    echo "  ✓ Stopped frontend (port 5174)"
else
    echo "  - Frontend not running (port 5174)"
fi

echo "Agno Coaching UI stopped."