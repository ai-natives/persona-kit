# ADR-002: PostgreSQL with JSONB for Data Storage

## Status
Accepted

## Context
PersonaKit needs to store complex, hierarchical trait data that evolves over time. The schema needs to be flexible enough to accommodate new trait types without database migrations, while still providing good query performance and consistency guarantees.

## Decision
Use PostgreSQL 15+ with JSONB columns for storing mindscape traits, observations, and persona data.

## Alternatives Considered
1. **MongoDB** (document store)
   - Pros: Native document model, flexible schema
   - Cons: 
     - Weaker consistency guarantees
     - Separate database technology to operate and monitor
     - Complex backup/restore when running alongside PostgreSQL
     - Team needs to learn two query languages
     - Difficult to join with relational data
     - Transaction support limitations across collections

2. **Pure relational schema**
   - Pros: Strong typing, referential integrity
   - Cons: 
     - Rigid schema requires migrations for every trait addition
     - Complex joins for nested trait hierarchies
     - ALTER TABLE locks can cause downtime
     - Difficult to store varying structures per persona
     - Schema evolution requires coordinated deployments

3. **Graph database** (Neo4j)
   - Pros: Natural for trait relationships
   - Cons: 
     - Complex queries require Cypher expertise
     - Limited cloud hosting options increase costs
     - Poor performance for non-graph queries
     - Difficult integration with existing PostgreSQL data
     - Specialized backup/restore procedures
     - Smaller talent pool for maintenance

4. **Vector database only** (Pinecone, Weaviate)
   - Pros: Optimized for embeddings
   - Cons: 
     - Not suitable for primary data storage
     - Lack of ACID transactions
     - Expensive at scale ($0.096/GB/month for Pinecone)
     - Vendor lock-in with proprietary APIs
     - No support for complex queries beyond similarity
     - Requires separate database for non-vector data

## Consequences
### Positive
- Single database technology to learn and maintain
- JSONB provides schema flexibility with indexing capabilities
- Strong ACID guarantees for consistency
- Can add pgvector extension for embeddings later
- Mature ecosystem and tooling
- Efficient storage with automatic compression

### Negative
- JSONB queries can be more complex than pure relational
- Need to carefully design indexes for JSON paths
- Not optimized for graph traversals
- May need additional extensions for specialized features

### Implementation Notes
- Use JSONB for traits, context, and metadata fields
- Create GIN indexes on frequently queried paths
- Validate JSON schema at application layer
- Plan for pgvector extension in v0.1.1

## References
- PersonaKit v0.1 Specification
- Database Design section