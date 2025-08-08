# PersonaKit Quick Start

## Prerequisites
- Docker
- Node.js 18+ and pnpm
- Python 3.11+ and uv
- OpenAI API key (for the demo)
- Vector (optional, for centralized logging)

## Installation

```bash
# Install dependencies
pnpm install
pnpm run setup

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

## Running PersonaKit

### Start Everything
```bash
# Start database, PersonaKit API, and demo UI
pnpm start
```

This will:
1. Start PostgreSQL with pgvector on port 5436
2. Run database migrations
3. Start PersonaKit API on port 8042
4. Start the Agno coaching demo (backend on 8100, frontend on 5176)

### Individual Components

```bash
# Database only
pnpm run start:db

# PersonaKit API only (requires database)
pnpm run start:personakit

# Demo UI only (requires PersonaKit)
pnpm run start:demo
```

### Stop Everything
```bash
pnpm stop
```

### Reset Database
```bash
# Stop everything and wipe database
pnpm run reset
```

## Useful Commands

```bash
# Check PersonaKit health
pnpm run health

# View logs
pnpm run logs

# Start centralized logging (requires Vector)
cd tools/log-viewer && ./start.sh

# View aggregated logs from all services
./tools/log-viewer/view-logs.sh

# Run migrations
pnpm run migrate

# Seed demo data
pnpm run seed

# Run tests
pnpm test

# Lint and format
pnpm run check
```

## Ports
- 5436: PostgreSQL (pgvector)
- 8042: PersonaKit API
- 8100: Demo backend
- 5176: Demo frontend

## Troubleshooting

### PersonaKit won't start
```bash
# Check if port is in use
lsof -i :8042

# Kill any existing process
pkill -f "python -m src.main"
```

### Database issues
```bash
# Reset database completely
pnpm run clean
pnpm run start:db
pnpm run migrate
```

### Demo not loading personas
1. Ensure PersonaKit is running: `pnpm run health`
2. Check for personas: `curl http://localhost:8042/personas/active?person_id=e0f9a601-01be-4c24-b5a0-f70f7917248a`
3. If empty, run: `pnpm run seed`