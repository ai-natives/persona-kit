# PersonaKit Workbench

A workbench application for PersonaKit that provides developer tools, bootstrapping utilities, mock data generation, and interactive testing features.

## Overview

While PersonaKit Core focuses on being a robust API for persona generation, the Workbench app handles:

- **Bootstrap Wizard**: Interactive onboarding for new users
- **Mock Data Generator**: Create realistic test data
- **Interactive CLI**: User-friendly commands beyond basic API calls
- **Example Integrations**: Demonstrates how to integrate with PersonaKit API

## Architecture

```
persona-kit-workbench/
├── src/
│   ├── bootstrap/          # Wizard and onboarding
│   │   ├── wizard.py      # Interactive questionnaire
│   │   └── mock_data.py   # Generate test observations
│   ├── cli/               # Enhanced CLI commands
│   └── api/               # PersonaKit API client
├── tests/
├── pyproject.toml
└── README.md
```

## Why a Separate Workbench?

1. **Clean Separation**: Keeps PersonaKit Core focused on the API
2. **Flexibility**: Users can build their own tools
3. **Examples**: Shows best practices for PersonaKit integration
4. **Optional**: Core PersonaKit works without it

## Installation

```bash
cd persona-kit-workbench
uv pip install -e .
```

## Quick Start

1. **Make sure PersonaKit API is running** (in another terminal):
   ```bash
   cd .. && ./scripts/start.sh
   ```

2. **Run the interactive bootstrap wizard**:
   ```bash
   ./start-cli.sh bootstrap
   ```

3. **Or use the mock server for standalone testing**:
   ```bash
   # Terminal 1: Start mock server
   ./start-mock-server.sh
   
   # Terminal 2: Run bootstrap against mock
   ./start-cli.sh bootstrap --api-url http://localhost:8043
   ```

## Usage

### Available Commands

Check what's available:
```bash
./start-cli.sh --help
```

Commands:
- `bootstrap` - Interactive wizard to create your PersonaKit profile
- `config` - Show current configuration
- `generate-mock-data` - Create test observations
- `add-observation` - Add a self-observation narrative
- `curate-trait` - Curate a specific trait value
- `list-narratives` - View recent narratives

### Using the Startup Scripts (Recommended)

The workbench includes startup scripts that enable logging for debugging:

```bash
# Run any CLI command with logging
./start-cli.sh <command> [options]

# Examples:
./start-cli.sh bootstrap
./start-cli.sh generate-mock-data --days 7
./start-cli.sh config

# Start mock server with logging (port 8043)
./start-mock-server.sh
```

Logs are written to `./app.log` by default. This integrates with PersonaKit's Vector observability.

### Direct Usage

You can also run commands directly:

```bash
persona-kit-workbench bootstrap
```

This will:
1. Ask a few questions about your work patterns
2. Create initial observations in PersonaKit
3. Generate your first persona

### Generate Mock Data

For testing or demos, generate realistic work patterns:

```bash
persona-kit-workbench generate-mock-data --days 7
```

This creates:
- Work sessions with varying productivity
- Calendar events (meetings, focus blocks)
- User preference observations

### Mock API Server

For testing without the full PersonaKit API:

```bash
# Start mock server on port 8043
./start-mock-server.sh

# Or manually:
python mock_api_server.py
```

The mock server provides simplified endpoints for testing workbench commands.

## Integration with PersonaKit

The workbench app is a client of the PersonaKit API:

```python
from personakit_workbench import PersonaKitClient

client = PersonaKitClient(base_url="http://localhost:8042")

# Create observations
await client.create_observation({
    "person_id": person_id,
    "type": "user_input",
    "content": wizard_responses
})

# Generate persona
persona = await client.generate_persona(
    person_id=person_id,
    mapper_id="daily_work_optimizer"
)
```

## Development

This workbench app demonstrates how to build applications on top of PersonaKit. Feel free to:

- Fork and customize for your needs
- Extract patterns for your own integration
- Contribute improvements back

## Logging and Debugging

The workbench participates in PersonaKit's centralized logging:

1. **Log Files**: All components write to `./app.log`
2. **Log Levels**: Set via `LOG_LEVEL` environment variable (default: INFO)
3. **Log Format**: Text or JSON via `LOG_FORMAT` environment variable

### Environment Variables

```bash
export LOG_FILE="./logs/workbench.log"  # Custom log location
export LOG_LEVEL="DEBUG"                # More verbose logging
export LOG_FORMAT="json"                # JSON formatted logs
export MOCK_SERVER_PORT="8044"          # Custom mock server port
```

## Requirements

- Python 3.11+
- PersonaKit API running (default: http://localhost:8042)
- Optional: Mock server for testing (default: http://localhost:8043)