# CLAUDE.md - Important Project Conventions

## ⚠️ CRITICAL: AVOID HANGING AND TIMEOUTS
**This is a top priority:** Never create systems or write code that can hang for 30 seconds, 2 minutes, or any extended period.

### During Development:
- **Set explicit timeouts** on all operations (max 5-10 seconds)
- **Use `timeout` parameter** in Bash commands when testing
- **Kill hanging processes immediately** - don't wait
- **Test with small timeouts first** (5s) before longer operations

### In Production Code:
- **All HTTP clients must have timeouts**: `httpx.AsyncClient(timeout=5.0)`
- **All subprocess calls must have timeouts**: `subprocess.run(cmd, timeout=10)`
- **All async operations should be cancellable**
- **Implement health checks** that respond quickly (< 1s)

### Server Management:
- **Always create server management scripts** (start/stop/restart)
- **Track PIDs** to kill orphaned processes
- **Clean shutdown handlers** (SIGINT, SIGTERM)
- **Never leave stray processes** running

## Package Managers - ALWAYS USE THESE

### JavaScript/TypeScript
**ALWAYS use `pnpm`** - Never use npm or yarn
- Install packages: `pnpm add <package>`
- Install dev dependencies: `pnpm add -D <package>`
- Install all: `pnpm install`
- Run scripts: `pnpm run <script>`

### Python
**ALWAYS use `uv`** - Never use pip directly
- Install packages: `uv pip install <package>`
- Run Python scripts: `uv run python <script>`
- Create venv: `uv venv`
- Add to pyproject.toml: `uv add <package>`

## Project Structure

### Typing Coach Components
- **VS Code Extension**: `/typing-coach-extension/` (pnpm)
- **MCP Server**: `/typing-coach-mcp-server/` (pnpm for TypeScript)
- **Web Backend**: `/typing-coach-web/backend/` (uv for Python)
- **Web Frontend**: `/typing-coach-web/frontend/` (pnpm for React)

## Port Allocations
- **3000**: MCP WebSocket server (VS Code → MCP)
- **3001**: MCP SSE endpoint (for Python client)
- **5173**: React frontend (Vite default)
- **5436**: PersonaKit PostgreSQL (custom port to avoid conflicts)
- **8000**: Real FastAPI backend (production)
- **8001**: Mock FastAPI backend (development)
- **8042**: PersonaKit API (custom port to avoid conflicts)

## Key Commands to Remember

### Running the Extension
```bash
cd typing-coach-extension
pnpm run compile
# Then F5 in VS Code
```

### Running MCP Server
```bash
cd typing-coach-mcp-server
pnpm run build
pnpm run start
```

### Running Python Backend
```bash
cd typing-coach-web/backend
uv run python src/main.py
```

### Running React Frontend
```bash
cd typing-coach-web/frontend
pnpm run dev
```

### Running Mock Demo
```bash
cd typing-coach-web/mock-backend
uv run python mock_server.py
```

## Testing Commands

### TypeScript/JavaScript
```bash
pnpm run lint
pnpm run test
pnpm run build
```

### Python
```bash
uv run pytest
uv run ruff check
uv run mypy src/
```

## NEVER DO THESE
- ❌ Don't use `npm install`
- ❌ Don't use `pip install` directly
- ❌ Don't use `python` command directly (use `uv run python`)
- ❌ Don't commit without checking lint/tests
- ❌ Don't use port 3000/3001 for new services

## Git Commit Style
- Concise, descriptive messages
- No emojis in commit messages
- Focus on what changed, not why
- Never run `git add` or `git commit` automatically

## When Resuming Work
1. Check what other Claude instances are doing
2. Read this file first
3. Use the correct package managers
4. Check port allocations before starting services
5. Update context checkpoints in plan files