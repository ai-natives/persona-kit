# PersonaKit v0.1 Specification

## Overview

PersonaKit v0.1 is a focused MVP implementation of the Work Assistant use case, designed to validate core concepts while providing immediate value to individual knowledge workers.

## Why Work Assistant First?

1. **Most frequent API usage** - Hourly/daily persona requests will surface system issues quickly
2. **Simpler scope** - Single primary user + a few stakeholders (vs. 50+ personas for other use cases)
3. **Clear feedback loop** - "Did the suggestions match your needs?" is immediately verifiable
4. **Highest value** - Directly improves daily productivity
5. **Fast iteration** - Single-user focus enables rapid testing and refinement

## v0.1 Architecture

PersonaKit v0.1 is designed as a persona generation service with configuration-driven mappers:

1. **PersonaKit Service (API)** - The persona generation service
   - REST API for observations, mindscapes, personas
   - Background processing of observations
   - Rule engine for evaluating mapper configurations
   - Configuration management and versioning
   - Automatic weight adjustment from feedback
   - Minimal CLI for API interaction (e.g., `persona-kit suggest`)

2. **PersonaKit Workbench** - Developer tools
   - Bootstrap wizard for new users
   - Mock data generator for testing
   - Example mapper configurations
   - Configuration testing tools

3. **Mapper Configurations** - Domain logic as YAML/JSON
   - Not code - declarative rule definitions
   - Uploaded via API, not compiled in
   - Automatically versioned and adjusted by feedback

This architecture makes PersonaKit a domain-agnostic service that any application can use via API calls.

## v0.1 Scope

### Core Features (PersonaKit API)

#### 1. Foundation Components
- **Storage**: PostgreSQL 15+ with JSONB (Option B from architectural options)
  - Observations table
  - Mindscapes table (traits stored as JSONB)
  - Personas table (with TTL/expiration)
  - Feedback table
- **API**: REST endpoints for core operations
  - `POST /observations` - Ingest work patterns
  - `POST /personas` - Generate work optimization persona
  - `POST /feedback` - Collect accuracy feedback
  - `GET /suggestions` - Get current work suggestions
- **Processing**: Basic Mindscaper for trait extraction
  - Simple pattern recognition from work artifacts
  - Incremental mindscape updates

#### 2. Example Mapper Configuration: Daily Work Optimizer
```yaml
metadata:
  id: daily-work-optimizer-v1
  name: "Daily Work Optimizer"
  description: "Optimize daily work patterns and productivity"
  version: 1.0

required_traits:
  - work.energy_patterns
  - work.focus_duration
  - work.task_switching_cost
  - productivity.peak_hours

rules:
  - id: high_energy_deep_work
    conditions:
      all:
        - trait: work.energy_patterns.current
          equals: high
    actions:
      - generate_suggestion:
          type: task_recommendation
          template: deep_work_window
    weight: 1.0  # Adjustable by feedback

templates:
  deep_work_window:
    title: "Deep Work Window"
    description: "Your energy is high - ideal for challenging tasks"
    duration: "{work.focus_duration.p90}"
```

#### 3. Minimal Bootstrapping System

**Quick Start Flow** (< 10 minutes) - Provided by Companion App:
1. **Initial Setup Wizard** (in companion)
   ```
   Welcome! Let's learn your work patterns in 5 minutes.
   
   When do you typically start work? [9:00 AM]
   When are you most focused? [Morning/Afternoon/Evening/Varies]
   How long can you typically focus? [30min/1hr/2hr+]
   What disrupts your flow most? [Meetings/Slack/Email/Context switches]
   ```

2. **Mock Data Option** (in companion)
   - Generate realistic work patterns for testing
   - Immediate persona generation without waiting

3. **API Integration**
   - Companion sends observations to PersonaKit API
   - PersonaKit processes and builds mindscape
   - Personas available immediately via API

#### 4. Daily Workflow

**Morning Check-in** (< 30 seconds):
```
Good morning! How's your energy today?
[Low] [Medium] [High] [Skip]

Based on your calendar, you have 3 focus blocks available.
Suggested order: [Deep work] → [Meeting prep] → [Email batch]
```

**Throughout the Day**:
- Track completion momentum (did they follow suggestions?)
- Minimal interruptions (max 2-3 micro-moments)
- Passive observation continues

**Evening Wrap-up** (optional):
```
How well did today's suggestions match your needs?
[Not helpful] [Somewhat] [Very helpful]

Any specific feedback? [optional text]
```

### What v0.1 Does NOT Include

1. **Deferred Complexity**
   - No stakeholder personas (just self)
   - No vector database (JSONB queries only)
   - No graph layer
   - No sync protocol (single device)
   - No mobile SDK
   - No other use cases (English coaching, marketing)

2. **Deferred Features**
   - Multiple mappers
   - Persona composition from multiple mappers
   - Advanced trait extraction
   - Machine learning improvements
   - Team/organizational features

## Technical Implementation

### Database Schema (Simplified)

```sql
-- Core tables only
CREATE TABLE observations (
  id UUID PRIMARY KEY,
  person_id UUID NOT NULL,
  type VARCHAR(50),
  content JSONB,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE mindscapes (
  person_id UUID PRIMARY KEY,
  traits JSONB NOT NULL,  -- Simple trait storage
  version INTEGER DEFAULT 1,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE personas (
  id UUID PRIMARY KEY,
  person_id UUID NOT NULL,
  mapper_id VARCHAR(100),
  core JSONB,          -- Low-volatility traits
  overlay JSONB,       -- High-volatility state
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feedback (
  id UUID PRIMARY KEY,
  persona_id UUID NOT NULL,
  rating INTEGER,
  helpful BOOLEAN,
  context JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### API Examples

**Generate Daily Persona**:
```bash
POST /personas
{
  "userId": "current-user",
  "mapperId": "daily-work-optimizer-v1",
  "taskContext": {
    "timeOfDay": "morning",
    "dayOfWeek": "monday"
  }
}

Response:
{
  "personaId": "...",
  "suggestions": [
    {
      "time": "9:00-11:00",
      "activity": "deep-work",
      "reason": "Peak focus hours based on your patterns"
    },
    {
      "time": "11:00-11:30", 
      "activity": "email-batch",
      "reason": "Energy dip, good for routine tasks"
    }
  ],
  "currentState": {
    "energyLevel": "high",
    "focusBlocks": 3,
    "meetingLoad": "medium"
  }
}
```

### Success Metrics

1. **Performance**
   - Persona generation: < 2 seconds
   - Observation processing: < 500ms
   - API response time: < 200ms

2. **User Experience**
   - Bootstrap time: < 10 minutes
   - Daily interaction time: < 2 minutes total
   - Suggestion accuracy: > 70% "helpful" ratings after 1 week

3. **System Health**
   - Zero infrastructure dependencies for development
   - Single `docker-compose up` for full system
   - < 100MB memory footprint

## Development Approach

### Phase 1: Core Infrastructure (Week 1)
- PostgreSQL setup with JSONB
- Basic REST API (FastAPI or Express)
- Observation ingestion
- Simple Mindscaper

### Phase 2: Work Optimizer (Week 2)
- Daily Work Optimizer mapper
- Quick start wizard
- Basic trait extraction
- Persona generation

### Phase 3: Daily Workflow (Week 3)
- Morning check-in UI
- Suggestion generation
- Feedback collection
- Basic analytics

### Phase 4: Polish & Testing (Week 4)
- Performance optimization
- Error handling
- Documentation
- Deployment setup

## Migration Path to v0.2

v0.1 is designed to evolve:
1. **Add Stakeholder Mappers** - Review simulation
2. **Enhance Bootstrapping** - More extraction strategies
3. **Add Vector Search** - Better trait matching
4. **Multi-device Sync** - Work across devices
5. **Team Features** - Aggregate patterns

## Constraints & Assumptions

1. **Single User** - No multi-tenancy in v0.1
2. **Desktop Focus** - Optimize for where work happens
3. **Privacy First** - All data local, no cloud dependency
4. **Developer-Friendly** - Easy to hack on and extend

## Definition of Done for v0.1

- [ ] Can bootstrap new user in < 10 minutes
- [ ] Generates personalized daily work suggestions
- [ ] Suggestions improve based on feedback
- [ ] Complete development environment in one command
- [ ] Basic documentation and examples
- [ ] All core APIs have integration tests
- [ ] Performance meets targets
- [ ] API is stable and ready for integration

## Out of Scope (Explicitly)

- Authentication/authorization (assume single user)
- Data export/import
- Sophisticated ML/AI improvements
- Web UI (CLI/API only)
- Cloud deployment
- Other use cases beyond work optimization

## Note on v0.2 Direction

v0.2 will focus on integrating PersonaKit with other applications (e.g., SQL Coach) rather than expanding to additional use cases. v0.1 should prioritize a stable API foundation that external applications can consume.

This specification provides a clear, achievable target for v0.1 that proves PersonaKit's value while maintaining flexibility for future expansion.