#!/usr/bin/env bash
# Stop Admin Dashboard (backend + frontend)

echo "Stopping Admin Dashboard..."

# Kill processes on the specific ports
if lsof -ti :8104 >/dev/null 2>&1; then
    kill $(lsof -ti :8104) 2>/dev/null
    echo "  ✓ Stopped backend (port 8104)"
else
    echo "  - Backend not running (port 8104)"
fi

if lsof -ti :5175 >/dev/null 2>&1; then
    kill $(lsof -ti :5175) 2>/dev/null
    echo "  ✓ Stopped frontend (port 5175)"
else
    echo "  - Frontend not running (port 5175)"
fi

echo "Admin Dashboard stopped."