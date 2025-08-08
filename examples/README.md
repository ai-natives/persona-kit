# PersonaKit Examples

This directory contains working examples demonstrating how to integrate PersonaKit into applications.

## 🚀 Quick Start

To see PersonaKit in action with the Career Navigator demo:

```bash
# From the PersonaKit root directory
cd examples/career-navigator
./start.sh
```

This starts:
1. PersonaKit API (port 8042)
2. Career Navigator Backend (port 8111)
3. Career Navigator Frontend (port 5175)

## 📁 Available Examples

### 1. Career Navigator (`career-navigator/`)
A personalized career transition guidance app that demonstrates:
- Creating personas on-demand based on user traits
- Recording observations for every user action
- Adapting recommendations based on mindscape data
- Full-stack React + FastAPI implementation

**Key Features:**
- Onboarding flow to capture initial traits
- Journey map visualization
- Task recommendations based on persona
- Real-time trait updates from user actions

### 2. Agno Coaching UI (`agno-coaching-ui/`)
An AI mentor that adapts teaching style based on learner profiles:
- Integration with OpenAI GPT models
- Real-time adaptation indicators
- Profile switching to see different teaching styles
- Visual feedback on personalization

**Key Features:**
- Multiple pre-configured learner profiles
- Adaptive conversation UI
- OpenAI integration example
- React + Python backend


## 🛠️ Building Your Own Integration

### 1. Setup PersonaKit Client
```python
from personakit import PersonaKitClient

client = PersonaKitClient(
    base_url="http://localhost:8042",
    api_key="your-api-key"
)
```

### 2. Record Observations
```python
await client.create_observation(
    person_id="user-123",
    observation_type="user_action",
    content={
        "action": "completed_onboarding",
        "preferences": ["visual_learning", "hands_on"]
    }
)
```

### 3. Generate Personas
```python
persona = await client.create_persona(
    person_id="user-123",
    mapper_id="career-guidance-mapper"
)
```

### 4. Use Personas in Your App
```python
if persona.core.get("learning_style") == "visual":
    # Show diagrams and charts
else:
    # Show text-based content
```

## 🎯 Best Practices

1. **Record Meaningful Observations**: Every significant user action should create an observation
2. **Use Real Data**: Don't hardcode personas - let PersonaKit generate them
3. **Respect Privacy**: Only collect what's needed for personalization
4. **Provide Value**: Make personalization benefits clear to users

## 🤝 Contributing Examples

When adding a new example:
1. Create a clear README with setup instructions
2. Include start/stop scripts
3. Document which traits and mappers you use
4. Keep examples focused on a specific use case
5. Use consistent ports (8100-8199 range)