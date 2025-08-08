# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the PersonaKit project. ADRs document significant architectural decisions made during the development of the system.

## Index

| ADR | Title | Status | Summary |
|-----|-------|--------|---------|
| [001](001-service-architecture.md) | Service Architecture over Framework/Library | Accepted | PersonaKit is implemented as a centralized service with REST API rather than an embedded framework |
| [002](002-postgresql-jsonb-storage.md) | PostgreSQL with JSONB for Data Storage | Accepted | Use PostgreSQL with JSONB columns for flexible schema and strong consistency |
| [003](003-configuration-driven-mappers.md) | Configuration-Driven Mapper Architecture | Accepted | Mappers are YAML/JSON configurations evaluated by a rule engine, not compiled code |
| [004](004-api-key-authentication.md) | API Key Authentication | Accepted | Use simple API keys for service-to-service auth instead of JWT/OAuth2 |
| [005](005-pgvector-semantic-search.md) | pgvector for Semantic Search | Accepted | Use PostgreSQL pgvector extension for embedding storage and semantic search |
| [006](006-local-embedding-generation.md) | Local Embedding Generation for Privacy | Accepted | Generate embeddings locally using sentence-transformers to protect privacy |
| [007](007-two-phase-data-architecture.md) | Two-Phase Data Architecture | Accepted | Separate persistent Mindscapes from ephemeral Personas with different lifecycles |
| [008](008-optimistic-locking.md) | Optimistic Locking for Mindscape Updates | Accepted | Use version-based optimistic locking for concurrent mindscape updates |
| [009](009-pull-based-interaction.md) | Pull-Based User Interaction Model | Accepted | Users must initiate all interactions; PersonaKit never pushes notifications |
| [010](010-feedback-driven-weights.md) | Feedback-Driven Weight Adjustment | Accepted | Automatically adjust mapper rule weights based on user feedback |
| [011](011-rest-api-design.md) | REST API over GraphQL/gRPC | Accepted | Use REST API with JSON for universal compatibility and simplicity |
| [012](012-immutable-observations.md) | Immutable Observations | Accepted | Observations cannot be modified after creation, only soft-deleted |

## ADR Template

When creating new ADRs, use this template:

```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
[Describe the issue motivating this decision]

## Decision
[Describe the decision and rationale]

## Alternatives Considered
[List alternatives with pros/cons]

## Consequences
### Positive
[List positive consequences]

### Negative
[List negative consequences]

## References
[Links to relevant documentation]
```

## Process

1. ADRs are numbered sequentially (001, 002, etc.)
2. New ADRs start with status "Proposed"
3. After review and agreement, status changes to "Accepted"
4. If an ADR is replaced, mark it "Superseded by ADR-XXX"
5. Keep ADRs concise but complete

## References

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) by Michael Nygard
- [Architecture Decision Records](https://adr.github.io/)