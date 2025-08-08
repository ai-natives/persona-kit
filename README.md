# PersonaKit

PersonaKit is a service for building AI systems that **understand and collaborate with specific individuals**—going beyond generic roles to capture personal preferences, communication styles, motivations, and work patterns.

**Current Version**: 0.2.0 (Stable)

## ✨ Implemented Features

### Core Functionality
- **Observation System** - Track behaviors and patterns over time with immutable, timestamped records
- **Mindscape Storage** - Flexible trait hierarchies stored as JSONB with confidence scores
- **Persona Generation** - Context-aware persona creation based on traits and observations
- **Mapper Configurations** - YAML/JSON-based configuration system with versioning
  - Upload configurations via API
  - Version tracking with draft/active/deprecated states
  - Usage analytics

### Narratives System
- **Self-Observations** - Human-written insights about personal patterns
- **Trait Curations** - Direct refinements to trait values with explanations
- **Semantic Search** - Find relevant narratives using embeddings
  - Local embedding generation (privacy-first, no external APIs)
  - PostgreSQL pgvector with HNSW indexing
  - Sub-500ms search performance

### API & Infrastructure
- **RESTful API** - Comprehensive endpoints for all operations
- **API Key Authentication** - Secure bcrypt-hashed keys with user management
- **Async Architecture** - Full async/await support with SQLAlchemy 2.0
- **Background Tasks** - Outbox pattern for reliable async processing

### Developer Tools
- **Workbench CLI** - Interactive tools for development and testing
- **Explorer Web UI** - Visual interface for exploring mindscapes and personas
- **PersonaKit CLI** - Command-line interface for users

## 🚧 Roadmap

- **Advanced Rule Engine** - Complex rule evaluation beyond current validation
- **Feedback Learning** - Automatic mapper weight adjustment from feedback
- **Multi-layer Mindscape** - Hot/warm/cold knowledge storage layers
- **Graph Relationships** - Entity and concept relationship modeling

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) for Python package management
- [pnpm](https://pnpm.io/) for JavaScript package management (for Explorer UI)
- [Vector](https://vector.dev/) for centralized logging (optional but recommended)

### 1. Clone and Setup
```bash
git clone https://github.com/ai-natives/persona-kit.git
cd persona-kit

# Install Python dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Start the Database
```bash
# Start PostgreSQL with pgvector extension
docker-compose up -d postgres

# Run database migrations
uv run alembic upgrade head
```

### 3. Create a User and Get API Key
```bash
# Create your first user
uv run python -m src.cli.main user create your-email@example.com

# This will output an API key like:
# Created user: your-email@example.com
# API Key: pk_abcdef1234567890... (save this!)
```

### 4. Start the API Server
```bash
# Using the start script (recommended)
./scripts/start.sh

# Or manually
uv run python -m src.main
```

The API will be available at http://localhost:8042

### 5. Test the API
```bash
# Set your API key
export PERSONAKIT_API_KEY="pk_your_api_key_here"

# Check health
curl http://localhost:8042/api/health

# Create an observation
curl -X POST http://localhost:8042/api/observations \
  -H "Authorization: Bearer $PERSONAKIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "550e8400-e29b-41d4-a716-446655440000",
    "observation_type": "work_session",
    "content": {
      "duration_minutes": 90,
      "focus_level": "deep",
      "task_type": "coding"
    }
  }'
```

## 🛠️ API Endpoints

### Authentication
All endpoints require API key authentication:
```
Authorization: Bearer pk_your_api_key_here
```

### Core Endpoints

#### User Management
- `POST /api/users` - Create a new user (returns API key)
- `GET /api/users` - List all users
- `POST /api/users/{id}/regenerate-key` - Generate new API key

#### Observations
- `POST /api/observations` - Create an observation
- `GET /api/observations?person_id={id}` - List observations for a person

#### Mindscapes
- `GET /api/mindscapes/{person_id}` - Get current mindscape
- `PUT /api/mindscapes/{person_id}` - Update mindscape traits

#### Personas
- `POST /api/personas` - Generate a persona
- `GET /api/personas/{id}` - Get specific persona
- `GET /api/personas?person_id={id}` - List personas for a person

#### Narratives
- `POST /api/narratives/self-observation` - Add a self-observation
- `POST /api/narratives/curation` - Curate a trait value
- `POST /api/narratives/search` - Semantic search narratives
- `GET /api/narratives?person_id={id}` - List narratives

#### Mapper Configurations
- `GET /api/mappers` - List available mappers
- `GET /api/mappers/{id}` - Get mapper details
- `POST /api/mappers` - Create new mapper
- `PUT /api/mappers/{id}` - Update mapper (creates new version)
- `POST /api/mappers/upload` - Upload YAML/JSON config file
- `GET /api/mappers/{id}/versions` - Get version history

#### Feedback
- `POST /api/feedback` - Submit feedback on suggestions

#### System
- `GET /api/health` - Health check endpoint

## 📦 Components

### 1. Workbench CLI
Interactive command-line tools for development and testing.

**Install:**
```bash
cd persona-kit-workbench
uv pip install -e .
```

**Available Commands:**
```bash
# Interactive setup wizard - creates user and configures API
persona-kit-workbench bootstrap

# Generate mock data for testing
persona-kit-workbench mock-data generate --days 7

# Start mock API server (for development)
persona-kit-workbench mock-api

# Show current configuration
persona-kit-workbench config
```

### 2. Explorer Web Interface
Visual tools for exploring and testing PersonaKit.

**Setup:**
```bash
cd tests/personakit-explorer
pnpm install
pnpm run dev
```

Open http://localhost:5173 to access:
- **Mindscapes Explorer** - Visualize trait hierarchies and observations
- **Narratives Explorer** - Browse and search self-observations

### 3. PersonaKit CLI
Command-line interface for user management.

**Commands:**
```bash
# User management
uv run python -m src.cli.main user create email@example.com
uv run python -m src.cli.main user list
```

### 4. Centralized Logging for Debugging (Recommended for AI Assistants)

PersonaKit uses a simple, consistent logging pattern across all services. Each service writes to its own `app.log` file in its directory, and Vector can aggregate these for centralized monitoring.

**How Logging Works:**
- Each service writes to `./app.log` in its own directory
- The `LOG_FILE` environment variable is automatically set by startup scripts
- Vector can aggregate all logs for unified monitoring (optional)

**Starting Services with Logging:**
```bash
# Each service has its own start script that enables logging
cd examples/career-navigator/backend && ./start.sh
cd examples/agno-coaching-ui/backend && ./start.sh
cd tools/admin-dashboard/backend && ./start.sh

# Or start PersonaKit API with logging
./scripts/start.sh  # Logs to ./app.log
```

**What Gets Logged:**
- ✅ **PersonaKit API** - All API requests, errors, and system events
- ✅ **Backend Services** - Full logging with proper log levels
  - Agno Coaching Backend → `examples/agno-coaching-ui/backend/app.log`
  - Career Navigator Backend → `examples/career-navigator/backend/app.log`
  - Admin Dashboard Backend → `tools/admin-dashboard/backend/app.log`
- ✅ **Frontend Apps** - Browser console logs (development mode)

**Using Vector for Log Aggregation (Optional):**
```bash
# Install Vector
brew install vectordotdev/brew/vector  # macOS
# Or see https://vector.dev/docs/setup/installation/ for other platforms

# Run Vector with PersonaKit config
vector --config vector.toml

# View aggregated logs
tail -f logs/all-services.log
```

**Direct Log Access:**
```bash
# View individual service logs
tail -f app.log                                      # PersonaKit API
tail -f examples/career-navigator/backend/app.log   # Career Navigator
tail -f examples/agno-coaching-ui/backend/app.log   # Agno Coaching
tail -f tools/admin-dashboard/backend/app.log       # Admin Dashboard
```

**For AI Assistants - How to Use Logs for Troubleshooting:**

1. **View Real-time Logs**: The Vector terminal shows ALL logs from ALL services
2. **Search for Errors**: Look for patterns like:
   - `"Failed to record observation: 400"` - API validation errors
   - `"Error loading profile"` - Missing PersonaKit connection
   - `"Network Error"` - Service connectivity issues

3. **Trace Request Flow**: Follow a request across services by timestamp:
   ```
   10:15:23 [AGNO-COACH] Recording observation for person e0f9a601...
   10:15:23 [PERSONAKIT] POST /api/observations 
   10:15:23 [PERSONAKIT] Error: Observation timestamp in future
   10:15:24 [AGNO-COACH] Failed to record observation: 400
   ```

4. **Access Aggregated Logs** (if using Vector): 
   ```bash
   # View all services together
   tail -f logs/all-services.log | jq .
   
   # Search for specific errors
   grep -i "failed" logs/all-services.log | jq .
   ```

**Important Notes for AI Assistants:**
- Logs are the PRIMARY way to debug issues across PersonaKit's distributed architecture
- Always check logs when users report issues with observations, personas, or API errors
- Frontend browser logs are automatically captured if the page includes browser-logger.js
- Backend services need manual configuration to write to monitored log files

## 🧪 Examples

### Working with Narratives

```python
import httpx
import asyncio

async def add_narrative():
    # Create a self-observation
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8042/api/narratives/self-observation",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "person_id": "550e8400-e29b-41d4-a716-446655440000",
                "raw_text": "I find myself most focused in the early morning hours",
                "tags": ["productivity", "morning", "focus"],
                "source": "daily reflection"
            }
        )
        print(response.json())

asyncio.run(add_narrative())
```

### Complete Example Applications

#### 1. Agno Coaching UI (Web Interface)
A full-stack application with React frontend showing real-time persona adaptation:

```bash
cd examples/agno-coaching-ui
./start.sh  # Starts both backend and frontend
```

Features:
- Visual profile switching between learners (Sato-san, Alex, Jordan)
- Real-time adaptation indicators
- Memory state visualization
- Clean, sparse UI focused on conversation

#### 2. Senior Developer Mentor (CLI)
Sophisticated mentoring system with dual memory architecture:

```bash
cd examples/agno-senior-mentor
python setup_sato_san.py  # Create learner profile
python senior_mentor.py   # Run the mentor
```

Features:
- Agno framework integration for conversation memory
- PersonaKit for long-term learner modeling
- Adaptive teaching strategies based on learner traits

#### 3. Simple Coaching Agent
Basic implementation without external dependencies:

```bash
cd examples/coaching-agent
python setup-sato-san.py     # Create learner profile
python dx-testing-coach.py   # Run the coach
```

See [`examples/README.md`](examples/README.md) for more example applications.

### Mapper Configuration

```yaml
# mapper-config.yaml
metadata:
  id: "productivity-optimizer"
  version: "1.0.0"
  name: "Productivity Pattern Optimizer"
  description: "Optimizes work patterns based on energy and focus traits"

rules:
  - id: "morning-person-deep-work"
    conditions:
      all:
        - type: "trait_check"
          trait: "work.chronotype"
          operator: "equals"
          value: "morning"
        - type: "trait_check"
          trait: "work.energy_patterns.morning"
          operator: "equals"
          value: "high"
    actions:
      - type: "suggestion"
        template: "Schedule your most important work between 6-10 AM"
        priority: "high"

templates:
  productivity_tips:
    morning: "Your peak hours are in the morning"
    evening: "Save creative work for evening hours"
```

Upload the mapper:
```bash
curl -X POST http://localhost:8042/api/mappers/upload \
  -H "Authorization: Bearer $PERSONAKIT_API_KEY" \
  -F "file=@mapper-config.yaml" \
  -F "status=active"
```

## 📊 Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   Web Apps      │────▶│  PersonaKit  │────▶│  PostgreSQL │
│   CLI Tools     │     │   API Server │     │  + pgvector │
│   AI Agents     │     │   (Port 8042)│     │  (Port 5436)│
└─────────────────┘     └──────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Background  │
                        │   Workers    │
                        └──────────────┘
```

### Core Components

1. **API Server** - FastAPI async REST API with authentication
2. **PostgreSQL Database** - Main storage with pgvector extension for embeddings
3. **Background Workers** - Async task processing via outbox pattern
4. **Narrative System** - Semantic search over human observations
5. **Mapper Engine** - Configuration-driven persona generation

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```bash
DATABASE_URL=postgresql+asyncpg://personakit:personakit_dev@localhost:5436/personakit
API_HOST=0.0.0.0
API_PORT=8042
```

### Workbench Configuration
The workbench stores config in `~/.personakit/config.json`:
```json
{
  "api_url": "http://localhost:8042",
  "person_id": "your-uuid-here",
  "auth_token": "your-token-here"
}
```

## 📚 Documentation

- **Architecture Decision Records**: [`docs/adr/`](docs/adr/) - Key architectural decisions
- **Data Schema**: [`docs/persona-kit-data-schema.md`](docs/persona-kit-data-schema.md) - Database models and structure
- **Conceptual Overview**: [`docs/persona-kit-overview.md`](docs/persona-kit-overview.md) - Philosophy and concepts
- **API Documentation**: See [API Endpoints](#-api-endpoints) section above
- **Example Integrations**: [`docs/architecture-notes/example-app-integrations.md`](docs/architecture-notes/example-app-integrations.md) - Building applications
- **Bootstrap Guide**: [`docs/persona-kit-bootstrapping-guide.md`](docs/persona-kit-bootstrapping-guide.md) - User onboarding patterns
- **Migration Guide**: [`docs/migration-guide.md`](docs/migration-guide.md) - Upgrading between versions

## 🧑‍💻 Development

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_feedback.py -v
```

### Database Management

#### PostgreSQL with pgvector
PersonaKit requires PostgreSQL 15+ with the pgvector extension for semantic search:

```bash
# The docker-compose.yml includes pgvector-enabled PostgreSQL
docker-compose up -d postgres

# Verify pgvector is installed
docker exec -it personakit-postgres psql -U personakit -d personakit -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

#### Migrations
```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

### Code Quality
```bash
# Run linter
uv run ruff check src/

# Run type checker
uv run mypy src/

# Format code
uv run ruff format src/
```

## 📁 Project Structure

```
persona-kit/
├── src/                      # Main application code
│   ├── api/                  # REST API endpoints
│   ├── models/               # SQLAlchemy database models
│   ├── schemas/              # Pydantic schemas for validation
│   ├── services/             # Business logic services
│   ├── repositories/         # Data access layer
│   └── cli/                  # Command-line interface
├── tests/                    # Test suite
│   └── personakit-explorer/  # Web UI for testing
├── persona-kit-workbench/    # Developer tools CLI
├── alembic/                  # Database migrations
├── docs/                     # Documentation
│   └── adr/                  # Architecture Decision Records
├── examples/                 # Example configurations
└── scripts/                  # Utility scripts
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass (`uv run pytest`)
- Code is formatted (`uv run ruff format`)
- Type hints are correct (`uv run mypy src/`)
- Documentation is updated

## 📄 License

Licensed under the Apache License 2.0. See [LICENSE](LICENSE) for full details.

## 🔗 Links

- [GitHub Repository](https://github.com/ai-natives/persona-kit)
- [Issue Tracker](https://github.com/ai-natives/persona-kit/issues)
- [Discussions](https://github.com/ai-natives/persona-kit/discussions)