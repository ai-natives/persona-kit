#!/usr/bin/env bash
# Start the PersonaKit API server

set -e

echo "Starting PersonaKit API..."

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    uv venv
fi

# Install dependencies if needed
uv pip install -e ".[dev]"

# Check if PostgreSQL is running
if ! docker-compose ps | grep -q "personakit-postgres.*healthy"; then
    echo "Starting PostgreSQL..."
    docker-compose up -d postgres
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi

# Run migrations
echo "Running database migrations..."
uv run alembic upgrade head

# Set log file location (always set, app decides whether to use it)
export LOG_FILE="${LOG_FILE:-./app.log}"

# Start the server
echo "Starting API server on port ${API_PORT:-8042}..."
exec uv run python -m src.main