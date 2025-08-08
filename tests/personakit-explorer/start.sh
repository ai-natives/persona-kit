#!/usr/bin/env bash
# Start PersonaKit Explorer

echo "Starting PersonaKit Explorer..."

# Start the development server
pnpm run dev &
EXPLORER_PID=$!

echo "PersonaKit Explorer started!"
echo "  URL: http://localhost:5176 (PID: $EXPLORER_PID)"
echo ""
echo "Press Ctrl+C to stop"

# Handle shutdown
cleanup() {
    echo "Stopping PersonaKit Explorer..."
    kill $EXPLORER_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for the process
wait