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

## Usage

### Bootstrap Wizard

Start the interactive wizard to set up your initial profile:

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

### Web Interface (Optional)

Run the web-based bootstrap wizard:

```bash
persona-kit-workbench serve
# Visit http://localhost:8043/bootstrap
```

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

## Requirements

- Python 3.11+
- PersonaKit API running (default: http://localhost:8042)
- Optional: Web framework dependencies for UI