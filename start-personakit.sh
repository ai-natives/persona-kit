#!/bin/bash
# Start PersonaKit infrastructure only (no demos)

echo "🚀 Starting PersonaKit infrastructure..."
echo ""

# 1. Start database if needed
echo "1. Checking PostgreSQL database..."
if ! docker ps | grep personakit-postgres > /dev/null 2>&1; then
    echo "   Starting PostgreSQL..."
    docker-compose -f docker-compose.pgvector.yml up -d
    echo "   Waiting for database..."
    until docker-compose -f docker-compose.pgvector.yml exec -T postgres pg_isready > /dev/null 2>&1; do
        sleep 1
    done
    echo "   ✅ Database ready"
    
    # Run migrations
    echo "   Running migrations..."
    uv run alembic upgrade head
else
    echo "   ✅ Database already running"
fi

# 2. Check if PersonaKit is already running
echo ""
echo "2. Checking PersonaKit API (port 8042)..."
if curl -s http://localhost:8042/health > /dev/null 2>&1; then
    echo "   ✅ PersonaKit is already running"
    exit 0
fi

echo "   Starting PersonaKit..."
nohup uv run python -m src.main > personakit.log 2>&1 &
PK_PID=$!
echo "   Started with PID: $PK_PID"

# Wait for PersonaKit to be ready
echo "   Waiting for PersonaKit to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8042/health > /dev/null 2>&1; then
        echo "   ✅ PersonaKit is now running"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ PersonaKit failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done

# 3. Seed demo data if needed
echo ""
echo "3. Checking demo data..."
uv run python seed_demo_data.py

echo ""
echo "✅ PersonaKit infrastructure is ready!"
echo "   API endpoint: http://localhost:8042"