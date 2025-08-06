# PersonaKit Explorer Context

## Problem Statement
Developers and operators working with PersonaKit need visibility into the system's data structures and behaviors. Currently, there's no easy way to explore mindscapes, test persona generation, or debug trait extraction without writing custom scripts or querying the database directly. This creates friction in development, makes debugging difficult, and prevents data scientists from discovering patterns in the data.

## Goals
- Provide visual exploration of mindscapes, traits, and observations
- Enable interactive persona generation with context simulation
- Offer ready-to-use agent framework integrations
- Create a debugging environment for developers
- Build monitoring tools for operators
- Support data analysis and pattern discovery

## Non-Goals
- NOT an end-user application (that's the Companion App's role)
- NOT a production management interface (no user management, etc.)
- NOT a replacement for the API (it's a client of the API)
- NOT required for PersonaKit to function (it's a development tool)

## Target Audience
1. **Developers** building PersonaKit integrations who need to understand the data model
2. **Operators** monitoring system health and debugging issues
3. **Data Scientists** analyzing behavioral patterns and optimizing mappers
4. **QA Engineers** testing edge cases and validating system behavior

## Success Criteria
- Developers can explore any mindscape and understand trait relationships
- Persona generation can be tested with different contexts without writing code
- Agent integrations can be prototyped in minutes, not hours
- System bottlenecks and errors are immediately visible
- Trait extraction logic can be debugged step-by-step
- Performance issues can be identified and analyzed

## Constraints
- Must work with both mock data (for development) and real API
- Should not require modifications to core PersonaKit
- Must be performant with large datasets (10k+ observations)
- Should follow PersonaKit's security model (when connected to real API)
- Must be maintainable alongside PersonaKit core

## Key Decisions
- **React/TypeScript**: Modern web stack for rich interactivity
- **Standalone deployment**: Separate from PersonaKit API
- **Mock-first development**: Can work without running PersonaKit
- **Progressive disclosure**: Simple by default, powerful when needed
- **Developer-focused**: Prioritize debugging over prettiness
- **Three core modules**: Exploration, Experimentation, Integration