# PersonaKit Explorer Context

## v0.1.1 Update: Narrative Support
PersonaKit v0.1.1 introduces human narratives with semantic search capabilities:
- **Self-observations**: Raw brain dumps about patterns
- **Curations**: User refinements to their mindscape
- **Embeddings**: All narratives stored with vector embeddings
- **Semantic Search**: Query narratives by meaning, not just keywords
- **Enhanced Rules**: Mappers can now use narrative_check conditions

## Problem Statement
Developers and operators working with PersonaKit need visibility into the system's data structures and behaviors. Currently, there's no easy way to explore mindscapes, test persona generation, or debug trait extraction without writing custom scripts or querying the database directly. This creates friction in development, makes debugging difficult, and prevents data scientists from discovering patterns in the data.

With v0.1.1's narrative features, there's an additional need to:
- Browse and search narratives semantically
- Understand how narratives influence persona generation
- Debug narrative → trait extraction flows
- Analyze narrative patterns and clusters

## Goals
- Provide visual exploration of mindscapes, traits, observations, and narratives
- Enable interactive persona generation with context simulation and narrative influence
- Offer ready-to-use agent framework integrations
- Create a debugging environment for developers with narrative tools
- Build monitoring tools for operators including narrative analytics
- Support data analysis and pattern discovery in both traits and narratives
- **v0.1.1**: Enable semantic search and narrative management through the UI

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
- **v0.1.1**: Narratives can be searched semantically with <500ms response time
- **v0.1.1**: Narrative → trait relationships are clearly visualized
- **v0.1.1**: Developers can test narrative_check conditions interactively

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

## Key Documentation for Implementation

### Essential Documents
1. **`/docs/persona-kit-v0.1.1-unified-plan.md`** - Complete v0.1.1 implementation plan
2. **`/docs/architecture/narrative-enhancement-plan.md`** - Detailed narrative architecture
3. **`/docs/persona-kit-data-schema.md`** - Existing database structure to extend
4. **`/src/services/rule_engine.py`** - Current rule engine implementation

### API Endpoints (v0.1.1)
- `POST /narratives/self-observation` - Add self-observations
- `POST /narratives/curate` - Create curations
- `GET /narratives/search` - Semantic search
- Existing endpoints remain unchanged

### Technical Stack
- **Frontend**: React, TypeScript, Vite, TanStack Query
- **Backend**: PersonaKit API (FastAPI)
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: OpenAI text-embedding-3-large (1536 dimensions)

### Mock Data Requirements
Mock data must include:
- Sample narratives with embeddings
- Narrative → trait links
- Semantic search results
- Curation history