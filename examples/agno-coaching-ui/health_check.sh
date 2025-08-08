#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 Health Check for Agno Coaching UI Services"
echo "=============================================="
echo ""

# Check PersonaKit API
echo -n "1. PersonaKit API (http://localhost:8042): "
if curl -s http://localhost:8042/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    PERSONAKIT_RESPONSE=$(curl -s http://localhost:8042/health)
    echo "   Response: $PERSONAKIT_RESPONSE"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "   Start with: cd ../../.. && uv run python src/main.py"
fi
echo ""

# Check Backend API
echo -n "2. Backend API (http://localhost:8100): "
BACKEND_RESPONSE=$(curl -s http://localhost:8100/)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    echo "   Response: $BACKEND_RESPONSE"
    
    # Check if agent is available (real OpenAI or mock)
    AGENT_AVAILABLE=$(echo $BACKEND_RESPONSE | grep -o '"agent_available":[^,}]*' | cut -d: -f2)
    if [ "$AGENT_AVAILABLE" = "true" ]; then
        echo -e "   Agent: ${GREEN}Real OpenAI Agent Active${NC}"
    else
        echo -e "   Agent: ${YELLOW}Mock Mode (No OpenAI API Key)${NC}"
    fi
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "   Start with: cd backend && uv run python api_server.py"
fi
echo ""

# Check Frontend
echo -n "3. Frontend UI (http://localhost:5176): "
if curl -s http://localhost:5176/ | grep -q "<!doctype html>" 2>/dev/null; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    echo "   Vite dev server is running"
else
    # Try alternative ports
    for PORT in 5173 5174 5175 5177; do
        if curl -s http://localhost:$PORT/ | grep -q "<!doctype html>" 2>/dev/null; then
            echo -e "${GREEN}✅ HEALTHY${NC} (on port $PORT)"
            echo "   Vite dev server is running on alternative port"
            break
        fi
    done
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ NOT RUNNING${NC}"
        echo "   Start with: cd frontend && pnpm run dev"
    fi
fi
echo ""

# Test Backend endpoints
echo "4. Testing Backend Endpoints:"
echo -n "   - GET /api/profiles: "
PROFILES_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8100/api/profiles)
HTTP_CODE=$(echo "$PROFILES_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
    PROFILE_COUNT=$(echo "$PROFILES_RESPONSE" | head -n-1 | grep -o "\"id\"" | wc -l | tr -d ' ')
    echo "     Found $PROFILE_COUNT demo profiles"
else
    echo -e "${RED}❌ Failed (HTTP $HTTP_CODE)${NC}"
fi

echo -n "   - GET /api/memory: "
MEMORY_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8100/api/memory)
HTTP_CODE=$(echo "$MEMORY_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ Failed (HTTP $HTTP_CODE)${NC}"
fi
echo ""

# Check processes
echo "5. Running Processes:"
echo "   PersonaKit processes:"
ps aux | grep "src/main.py" | grep -v grep | head -2
echo ""
echo "   Backend processes:"
ps aux | grep "api_server.py" | grep -v grep | head -2
echo ""
echo "   Frontend processes:"
ps aux | grep "vite" | grep -v grep | head -2
echo ""

# Summary
echo "=============================================="
echo "Summary:"
ALL_HEALTHY=true

# Check each service
if ! curl -s http://localhost:8042/health > /dev/null 2>&1; then
    ALL_HEALTHY=false
    echo -e "${RED}⚠️  PersonaKit is not running${NC}"
fi

if ! curl -s http://localhost:8100/ > /dev/null 2>&1; then
    ALL_HEALTHY=false
    echo -e "${RED}⚠️  Backend API is not running${NC}"
fi

FRONTEND_RUNNING=false
for PORT in 5173 5174 5175 5176 5177; do
    if curl -s http://localhost:$PORT/ | grep -q "<!doctype html>" 2>/dev/null; then
        FRONTEND_RUNNING=true
        FRONTEND_PORT=$PORT
        break
    fi
done

if [ "$FRONTEND_RUNNING" = false ]; then
    ALL_HEALTHY=false
    echo -e "${RED}⚠️  Frontend is not running${NC}"
fi

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ All services are healthy!${NC}"
    echo ""
    echo "🎉 Ready to use the Agno Coaching UI!"
    echo "   Open http://localhost:${FRONTEND_PORT} in your browser"
else
    echo ""
    echo "To start all services, run:"
    echo "  ./start.sh"
fi