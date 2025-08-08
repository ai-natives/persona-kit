#!/bin/bash
# Setup script for Vector log aggregation

echo "Setting up Vector for PersonaKit log aggregation..."

# Detect OS
OS=$(uname -s)
ARCH=$(uname -m)

# Install Vector based on OS
if [[ "$OS" == "Darwin" ]]; then
    echo "Installing Vector on macOS..."
    if command -v brew &> /dev/null; then
        brew tap vectordotdev/brew
        brew install vector
    else
        echo "Homebrew not found. Installing Vector manually..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.vector.dev | bash
    fi
elif [[ "$OS" == "Linux" ]]; then
    echo "Installing Vector on Linux..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.vector.dev | bash
else
    echo "Unsupported OS: $OS"
    echo "Please install Vector manually from: https://vector.dev/docs/setup/installation/"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo ""
echo "Vector installed! To start collecting logs:"
echo ""
echo "  vector --config vector.toml"
echo ""
echo "Then visit http://localhost:8686 for the GraphQL playground"
echo ""
echo "To send browser logs, add this to your frontend apps:"
echo ""
cat << 'EOF'
// Send console logs to Vector
const vectorEndpoint = 'http://localhost:8105/log';
['log', 'error', 'warn', 'info'].forEach(level => {
    const original = console[level];
    console[level] = (...args) => {
        original(...args);
        fetch(vectorEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level,
                message: args.join(' '),
                timestamp: new Date().toISOString(),
                source: window.location.pathname
            })
        }).catch(() => {});
    };
});
EOF