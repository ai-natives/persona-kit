#!/usr/bin/env bash
# Start Agno Coaching UI (backend + frontend)

echo "Starting Agno Coaching UI..."

# Start backend
echo "Starting backend..."
(cd backend && ./start.sh) &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend..."
(cd frontend && pnpm run dev) &
FRONTEND_PID=$!

echo "Agno Coaching UI started!"
echo "  Backend: http://localhost:8100 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:5174 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both services"

# Handle shutdown
cleanup() {
    echo "Stopping Agno Coaching UI..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait