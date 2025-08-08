# ADR-008: Optimistic Locking for Mindscape Updates

## Status
Accepted

## Context
Multiple processes may attempt to update a mindscape simultaneously:
- Background workers processing observations
- API endpoints handling direct updates
- Batch processing jobs

We need a concurrency control mechanism that doesn't harm read performance while preventing lost updates.

## Decision
Use optimistic locking with version fields on mindscape documents rather than pessimistic locking or last-write-wins approaches.

## Alternatives Considered
1. **Pessimistic locking** (SELECT FOR UPDATE)
   - Pros: Prevents all conflicts
   - Cons: Blocks readers, reduces throughput

2. **Last-write-wins**
   - Pros: Simple, no retries needed
   - Cons: Silent data loss, unpredictable results

3. **Event sourcing with CQRS**
   - Pros: No conflicts possible, full history
   - Cons: Complex implementation, eventual consistency

4. **Database-level MVCC only**
   - Pros: No application logic needed
   - Cons: Doesn't prevent lost updates at document level

## Consequences
### Positive
- No blocking on reads (high read throughput)
- Conflicts detected reliably
- No silent data loss
- Works well with document-oriented updates
- Simple to understand and implement
- Standard pattern with good library support

### Negative
- Requires retry logic in application
- May have multiple retries under high contention
- Version field must be maintained carefully
- Slightly more complex than last-write-wins

### Implementation Details
```python
async def update_mindscape(db, person_id, updates):
    while True:
        # Read current version
        mindscape = await db.get_mindscape(person_id)
        current_version = mindscape.version
        
        # Apply updates
        new_traits = merge_traits(mindscape.traits, updates)
        
        # Try to save with version check
        result = await db.execute("""
            UPDATE mindscapes 
            SET traits = %s, version = version + 1
            WHERE person_id = %s AND version = %s
        """, [new_traits, person_id, current_version])
        
        if result.rowcount == 1:
            break  # Success
        
        # Retry with backoff
        await asyncio.sleep(random.uniform(0.1, 0.5))
```

### Monitoring
- Track retry rates to identify contention
- Alert on excessive retries
- Log version conflicts for debugging

## References
- Technical Specification: Concurrency Control
- Data Merge & Concurrency section