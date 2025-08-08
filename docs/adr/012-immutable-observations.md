# ADR-012: Immutable Observations

## Status
Accepted

## Context
Observations are records of actual events or behaviors at specific points in time. There's debate about whether these should be editable after creation or remain immutable as historical facts.

## Decision
Observations are immutable once created - they cannot be modified or updated, only soft-deleted if necessary.

## Alternatives Considered
1. **Fully editable observations**
   - Pros: Can correct mistakes, update metadata
   - Cons: 
     - Loses historical accuracy and trust
     - Complex versioning and audit requirements
     - Race conditions with concurrent updates
     - Compliance issues (SOX, HIPAA require audit trails)
     - "Who changed what when" tracking overhead
     - Cache invalidation complexity
     - Difficult to debug trait calculations

2. **Versioned observations**
   - Pros: History preserved, can update
   - Cons: 
     - Complex queries (which version to use?)
     - Storage overhead (full copies or deltas?)
     - Cascading version impacts on derived traits
     - Point-in-time queries become complex
     - Migration complexity when schema changes
     - Confusing API (return all versions or latest?)

3. **Edit window** (e.g., 5 minutes)
   - Pros: Allows quick corrections
   - Cons: 
     - Arbitrary time limit frustrates users
     - Complex distributed timer logic
     - Timezone and clock sync issues
     - "Just missed the window" support tickets
     - Background job complexity for enforcement
     - Inconsistent state during window

4. **Append-only corrections**
   - Pros: Preserves history, allows corrections
   - Cons: 
     - Complex to interpret correction chains
     - Query performance (following pointers)
     - UI complexity showing corrections
     - Storage grows even faster
     - Circular correction possibility
     - Mental model harder to explain

## Consequences
### Positive
- Simpler concurrency model (no update conflicts)
- Clear audit trail of all observations
- Database writes are append-only (fast)
- No versioning complexity
- Historical accuracy preserved
- Cache-friendly (never changes)

### Negative
- Cannot correct data entry errors
- Storage grows monotonically
- May accumulate incorrect data
- Need good validation on input

### Implementation Details
```sql
CREATE TABLE observations (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL,
    observed_at TIMESTAMP NOT NULL,
    observation_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP  -- Soft delete only
);

-- No UPDATE permissions granted
REVOKE UPDATE ON observations FROM api_user;
```

### Mitigation Strategies
1. **Strong validation** on input to prevent errors
2. **Soft deletes** to remove incorrect observations
3. **New observations** to "correct" previous ones
4. **UI previews** before submission
5. **Bulk delete tools** for cleanup if needed

### Design Philosophy
- Observations are facts about what happened
- The system's interpretation may change
- But the historical record remains constant
- Trust is built on unchangeable history

## References
- Technical Specification: Data Immutability
- Observation Processing Pipeline