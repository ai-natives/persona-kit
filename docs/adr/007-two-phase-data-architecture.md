# ADR-007: Two-Phase Data Architecture (Mindscape/Persona Separation)

## Status
Accepted

## Context
PersonaKit needs to handle two different types of data with vastly different characteristics:
1. Slowly-changing trait data that accumulates over time (Mindscape)
2. Context-specific, ephemeral personas generated on-demand (Persona)

Mixing these would lead to complex caching, confusing APIs, and performance issues.

## Decision
Implement a two-phase architecture with clear separation:
- **Mindscapes**: Persistent storage of traits, observations, and patterns
- **Personas**: Ephemeral, context-specific projections with TTL

## Alternatives Considered
1. **Single entity model**
   - Pros: Simpler concept, one thing to manage
   - Cons: 
     - Unclear caching strategy (volatile mixed with stable)
     - Query performance degradation over time
     - Index bloat from mixed access patterns
     - Difficult to reason about data freshness
     - No clear TTL strategy for context-specific data
     - Database contention between reads and writes

2. **Three-phase model** (Observations → Traits → Personas)
   - Pros: More granular separation
   - Cons: 
     - Over-engineered for current needs
     - Complex data flow increases bugs
     - Additional caching layer to manage
     - Cascade update complexity
     - Mental model too complex for developers
     - Triple the API surface area
     - Difficult to maintain consistency

3. **Event sourcing**
   - Pros: Complete history, eventual consistency
   - Cons: 
     - Complex implementation requiring CQRS
     - Unfamiliar pattern increases onboarding time
     - Event store size grows unbounded
     - Snapshot management overhead
     - Complex event replay for debugging
     - Requires specialized event store infrastructure
     - Difficult to query current state efficiently
     - Tooling ecosystem less mature

## Consequences
### Positive
- Clear separation of volatile and non-volatile data
- Mindscapes can be cached aggressively (change slowly)
- Personas can expire naturally (TTL-based)
- Different consistency requirements handled appropriately
- Easy to understand conceptual model
- Independent scaling strategies

### Negative
- Two entities to manage instead of one
- Potential for confusion about which to use when
- Need to manage cache invalidation between layers
- Additional API endpoints

### Implementation Details
```python
# Mindscape - Persistent traits
{
  "id": "uuid",
  "person_id": "uuid", 
  "traits": {
    "work.energy_patterns": {...},
    "work.focus_duration": {...}
  },
  "version": 1,
  "updated_at": "2024-01-20T10:00:00Z"
}

# Persona - Ephemeral projection
{
  "id": "uuid",
  "person_id": "uuid",
  "mapper_id": "daily_work_optimizer",
  "core": {...},        # Essential traits
  "overlay": {...},     # Context-specific
  "expires_at": "2024-01-20T22:00:00Z",
  "mindscape_version": 1
}
```

### Design Principles
- Mindscapes are the source of truth
- Personas are disposable views
- Changes flow one direction: Observations → Mindscape → Persona
- Personas never modify mindscapes

## References
- PersonaKit Technical Specification
- Data Flow Architecture