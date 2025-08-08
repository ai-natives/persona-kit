#!/bin/bash
# Simple Vector setup - following Gemini's recommendation

echo "🚀 PersonaKit Unified Logging"
echo "============================"
echo ""

# Create log directory
LOG_DIR="/tmp/personakit-logs"
mkdir -p "$LOG_DIR"
echo "Log directory: $LOG_DIR"
echo ""

# Check Vector is installed
if ! command -v vector &> /dev/null; then
    if [ -f "$HOME/.vector/bin/vector" ]; then
        export PATH="$HOME/.vector/bin:$PATH"
    else
        echo "❌ Vector not found. Install with:"
        echo "   brew install vectordotdev/brew/vector"
        exit 1
    fi
fi

echo "📝 How to use:"
echo ""
echo "1. Start your services with output redirection:"
echo ""
echo "   # PersonaKit API"
echo "   uv run python -m src.main > $LOG_DIR/personakit.log 2>&1"
echo ""
echo "   # Agno Coaching Backend"
echo "   cd examples/agno-coaching-ui/backend"
echo "   uv run uvicorn api_server:app > $LOG_DIR/agno-backend.log 2>&1"
echo ""
echo "   # Admin Dashboard Backend"
echo "   cd tools/admin-dashboard/backend"
echo "   uv run python main.py > $LOG_DIR/admin-backend.log 2>&1"
echo ""
echo "   # Career Navigator Backend"
echo "   cd examples/career-navigator/backend"
echo "   uv run python main.py > $LOG_DIR/career-backend.log 2>&1"
echo ""
echo "2. For frontend apps, add to your HTML:"
echo "   <script src=\"http://localhost:8080/browser-logger.js\"></script>"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting Vector (logs will appear below)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start browser logger in background
python3 serve-browser-logger.py &
BROWSER_PID=$!

# Start Vector
vector --config vector-simple.yaml

# Cleanup
trap "kill $BROWSER_PID 2>/dev/null" EXIT