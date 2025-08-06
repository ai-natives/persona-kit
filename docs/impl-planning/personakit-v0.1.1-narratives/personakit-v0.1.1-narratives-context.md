# PersonaKit v0.1.1 Narratives Context

## Problem Statement
PersonaKit v0.1 successfully implements configuration-driven personas based on traits, but it loses the raw human insight that makes personas feel real. When users provide observations or feedback, the system distills them into traits, losing the messy, context-rich narratives that contain exactly what we're trying to extract - the hidden "in-brain stuff" that makes personas authentic.

## Goals
- **Primary goal**: Add human narrative support as first-class data alongside traits
- **Enable semantic search**: Store narratives with embeddings for rich querying
- **Preserve human voice**: Keep the messiness and context of human input
- **Maintain performance**: Keep persona generation under 2 seconds
- **Support two narrative types**: Self-observations and curations

## Non-Goals
- NOT implementing social perspectives (deferred to v0.2.1)
- NOT building push notifications or prompts (pull-based only)
- NOT replacing traits (narratives complement traits)
- NOT requiring narrative input (optional enhancement)
- NOT building complex consent management (no social perspectives yet)

## Target Audience
- **Agents**: Will collect narratives and use them in persona generation
- **Users**: Will view/edit narratives via Workbench and Explorer
- **PersonaKit System**: Rule engine and persona generator that will integrate narratives
- **Developers**: Will use the enhanced API to build narrative-aware applications

## Success Criteria
- Narratives can be created, stored, and searched semantically
- Rule engine can evaluate conditions based on narrative content
- Personas can include narrative context in suggestions
- Performance remains under 2s for persona generation
- Workbench allows direct narrative input
- Explorer shows narrative influence on personas
- All narrative collection is user-initiated (via agents or direct input)

## Constraints
- Must integrate with existing v0.1 architecture
- Must use PostgreSQL with pgvector extension
- Must maintain backward compatibility with trait-only mappers
- OpenAI API required for embeddings (text-embedding-3-large)
- No push notifications - purely pull-based interaction

## Key Decisions
- **Two narrative types only**: Self-observations and curations (no social perspectives)
- **Embeddings from day one**: All narratives stored with 1536-dim vectors
- **Semantic search primary**: Use pgvector with HNSW indexing
- **Pull-based architecture**: Users/agents initiate all interactions
- **Unified narratives table**: Single table with type discriminator
- **Agent-driven collection**: Agents decide when/how to collect narratives
- **No consent complexity**: Since no social perspectives in v0.1.1