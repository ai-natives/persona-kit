#!/bin/bash
# Start Vector log collection

echo "PersonaKit Log Viewer"
echo "===================="
echo ""

# Check if Vector is installed
if ! command -v vector &> /dev/null; then
    # Try the installed path
    if [ -f "$HOME/.vector/bin/vector" ]; then
        export PATH="$HOME/.vector/bin:$PATH"
    else
        echo "Vector not found. Please install it first:"
        echo "  curl --proto '=https' --tlsv1.2 -sSfL https://sh.vector.dev | bash"
        exit 1
    fi
fi

# Create logs directory
mkdir -p logs

# Start browser logger server in background
echo "Starting browser logger server..."
python3 serve-browser-logger.py &
BROWSER_LOGGER_PID=$!
echo "Browser logger running on http://localhost:8080"

# Give it a moment to start
sleep 1

echo ""
echo "Starting Vector..."
echo ""
echo "To add browser logging to your app, add this to your HTML:"
echo "  <script>"
echo "    window.PERSONAKIT_APP_NAME = 'your-app-name';"
echo "  </script>"
echo "  <script src=\"http://localhost:8080/browser-logger.js\"></script>"
echo ""
echo "Logs will appear below:"
echo "======================"
echo ""

# Start Vector (this will run in foreground)
vector --config vector.toml

# Cleanup on exit
trap "kill $BROWSER_LOGGER_PID" EXIT