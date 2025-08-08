#!/usr/bin/env bash
# Stop Career Navigator (backend + frontend)

echo "Stopping Career Navigator..."

# Kill processes on the specific ports
if lsof -ti :8103 >/dev/null 2>&1; then
    kill $(lsof -ti :8103) 2>/dev/null
    echo "  ✓ Stopped backend (port 8103)"
else
    echo "  - Backend not running (port 8103)"
fi

if lsof -ti :5176 >/dev/null 2>&1; then
    kill $(lsof -ti :5176) 2>/dev/null
    echo "  ✓ Stopped frontend (port 5176)"
else
    echo "  - Frontend not running (port 5176)"
fi

echo "Career Navigator stopped."