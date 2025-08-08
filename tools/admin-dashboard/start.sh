#!/usr/bin/env bash
# Start Admin Dashboard (backend + frontend)

echo "Starting Admin Dashboard..."

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

echo "Admin Dashboard started!"
echo "  Backend: http://localhost:8104 (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:5175 (PID: $FRONTEND_PID)"
echo ""
echo "Press Ctrl+C to stop both services"

# Handle shutdown
cleanup() {
    echo "Stopping Admin Dashboard..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait