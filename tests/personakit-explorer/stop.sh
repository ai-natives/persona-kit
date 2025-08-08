#!/usr/bin/env bash
# Stop PersonaKit Explorer

echo "Stopping PersonaKit Explorer..."

# Kill process on the specific port
if lsof -ti :5173 >/dev/null 2>&1; then
    kill $(lsof -ti :5173) 2>/dev/null
    echo "  ✓ Stopped PersonaKit Explorer (port 5173)"
else
    echo "  - PersonaKit Explorer not running (port 5173)"
fi

echo "PersonaKit Explorer stopped."