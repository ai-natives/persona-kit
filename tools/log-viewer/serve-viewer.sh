#!/bin/bash

echo "PersonaKit Log Viewer"
echo "===================="
echo ""
echo "Starting web server for log viewer..."
echo ""

# Change to the log-viewer directory
cd "$(dirname "$0")"

# Start a simple HTTP server
echo "Open your browser to: http://localhost:8080/log-viewer.html"
echo ""
echo "Make sure Vector is running in another terminal:"
echo "  ./start.sh"
echo ""
echo "Press Ctrl+C to stop"

# Try Python 3 first, fall back to Python 2
if command -v python3 &> /dev/null; then
    python3 -m http.server 8080 --bind localhost
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer 8080
else
    echo "Error: Python not found. Please install Python to run the web server."
    exit 1
fi