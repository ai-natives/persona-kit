# PersonaKit v0.1 Context

## Problem Statement
Knowledge workers struggle to optimize their daily productivity because they lack awareness of their own work patterns, energy cycles, and task-switching costs. Existing productivity tools focus on task management but ignore the human factors that determine when and how work gets done most effectively.

## Goals
- Create a minimal viable PersonaKit that demonstrates value through a single use case
- Help individual knowledge workers optimize their daily work patterns
- Validate the core PersonaKit architecture (Observations → Mindscape → Persona → Feedback)
- Build foundation for future expansion to other use cases

## Non-Goals
- NOT building a full task management system
- NOT implementing multiple personas or use cases
- NOT creating a polished UI (API/CLI only)
- NOT supporting teams or organizations
- NOT implementing advanced ML/AI features

## Target Audience
Individual knowledge workers (developers, designers, analysts) who:
- Work primarily on a computer
- Have flexibility in how they structure their day
- Want to optimize their productivity without invasive monitoring
- Are comfortable with CLI/API tools

## Success Criteria
- Users can bootstrap their work patterns in < 10 minutes
- System generates helpful daily work suggestions (>70% "helpful" ratings)
- Suggestions improve over time based on feedback
- Persona generation takes < 2 seconds
- Single command to run entire system locally

## Constraints
- Single user only (no multi-tenancy)
- PostgreSQL + JSONB for storage (no complex infrastructure)
- Must work completely offline/locally
- Privacy-first: no cloud dependencies
- Must be developer-friendly and hackable

## Key Decisions
- **Storage**: PostgreSQL with JSONB (Option B) - provides good balance of flexibility and queryability
- **Single Mapper**: Daily Work Optimizer only - focused on immediate value
- **Bootstrapping**: Quick wizard + passive observation - minimal user effort
- **Feedback**: Simple helpful/not helpful - reduces friction
- **Architecture**: Monolithic service first - can decompose later
- **Language**: Python/FastAPI - good ecosystem for data processing and APIs