#!/usr/bin/env bash
# Show status of all PersonaKit services

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 PersonaKit Services Status${NC}"
echo "================================"

# Function to check if a service is running
check_service() {
    local name=$1
    local port=$2
    local type=$3
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name ($type) - ${GREEN}Running${NC} on port $port"
        # Try to get PID
        local pid=$(lsof -t -i :$port | head -1)
        if [ ! -z "$pid" ]; then
            echo "  └─ PID: $pid"
        fi
    else
        echo -e "${RED}✗${NC} $name ($type) - ${RED}Not running${NC} (port $port)"
    fi
}

# Function to check if PostgreSQL is running via Docker
check_postgres() {
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "personakit-postgres.*Up"; then
        echo -e "${GREEN}✓${NC} PostgreSQL (Database) - ${GREEN}Running${NC} in Docker"
        local status=$(docker ps --format "{{.Status}}" --filter "name=personakit-postgres")
        echo "  └─ Status: $status"
    else
        echo -e "${RED}✗${NC} PostgreSQL (Database) - ${RED}Not running${NC}"
    fi
}

# Check core services
echo -e "\n${YELLOW}Core Services:${NC}"
check_postgres
check_service "PersonaKit API" 8042 "API"

# Check example applications
echo -e "\n${YELLOW}Example Applications:${NC}"
check_service "Career Navigator Backend" 8103 "API"
check_service "Career Navigator Frontend" 5176 "Web"
check_service "Agno Coaching Backend" 8100 "API"
check_service "Agno Coaching Frontend" 5174 "Web"

# Check tools
echo -e "\n${YELLOW}Tools & Development:${NC}"
check_service "Admin Dashboard Backend" 8104 "API"
check_service "Admin Dashboard Frontend" 5175 "Web"
check_service "PersonaKit Explorer" 5173 "Web"
echo -e "${BLUE}ℹ${NC} PersonaKit Workbench - CLI tool (run with: cd persona-kit-workbench && uv run pkw)"

# Check for log files
echo -e "\n${YELLOW}Active Log Files:${NC}"
if [ -f "app.log" ] && [ -s "app.log" ]; then
    echo -e "${GREEN}✓${NC} PersonaKit API log: app.log ($(wc -l < app.log) lines)"
fi
if [ -f "examples/career-navigator/backend/app.log" ] && [ -s "examples/career-navigator/backend/app.log" ]; then
    echo -e "${GREEN}✓${NC} Career Navigator log: examples/career-navigator/backend/app.log"
fi
if [ -f "examples/agno-coaching-ui/backend/app.log" ] && [ -s "examples/agno-coaching-ui/backend/app.log" ]; then
    echo -e "${GREEN}✓${NC} Agno Coaching log: examples/agno-coaching-ui/backend/app.log"
fi
if [ -f "tools/admin-dashboard/backend/app.log" ] && [ -s "tools/admin-dashboard/backend/app.log" ]; then
    echo -e "${GREEN}✓${NC} Admin Dashboard log: tools/admin-dashboard/backend/app.log"
fi

# Check Vector status
echo -e "\n${YELLOW}Log Aggregation:${NC}"
if pgrep -f "vector.*vector.toml" >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Vector - ${GREEN}Running${NC}"
    vector_pid=$(pgrep -f "vector.*vector.toml")
    echo "  └─ PID: $vector_pid"
else
    echo -e "${RED}✗${NC} Vector - ${RED}Not running${NC}"
fi

# Summary
echo -e "\n${BLUE}Summary:${NC}"
running_count=$(lsof -i :8042,8100,8103,8104,5173,5174,5175,5176 2>/dev/null | grep LISTEN | wc -l | tr -d ' ')
echo "Services running: $running_count"

# Quick start hint
if [ "$running_count" -eq 0 ]; then
    echo -e "\n${YELLOW}💡 Quick Start:${NC}"
    echo "  1. Start PersonaKit API: ./scripts/start.sh"
    echo "  2. Start an example app: cd examples/career-navigator/backend && ./start.sh"
fi