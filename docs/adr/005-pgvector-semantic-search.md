# ADR-005: pgvector for Semantic Search

## Status
Accepted

## Context
PersonaKit v0.1.1 introduces narratives - human-written observations that need semantic search capabilities. We need to search these narratives by meaning, not just keywords, while maintaining system simplicity.

## Decision
Use PostgreSQL's pgvector extension for storing and searching embeddings, keeping all data in a single database.

## Alternatives Considered
1. **Dedicated vector database** (Pinecone, Weaviate)
   - Pros: Purpose-built for vectors, advanced features
   - Cons: 
     - Additional infrastructure to deploy and monitor
     - Data synchronization complexity and lag
     - Vendor lock-in with proprietary query languages
     - Significant cost at scale (Pinecone: ~$70/million vectors/month)
     - Network latency for every search operation
     - Complex backup/restore across two systems
     - Difficult local development setup

2. **Elasticsearch with vector plugin**
   - Pros: Powerful search features, mature
   - Cons: 
     - Complex cluster management (sharding, replicas)
     - High memory requirements (heap sizing issues)
     - Version upgrade complexity with downtime
     - Additional infrastructure team expertise needed
     - JVM tuning and garbage collection issues
     - Expensive at scale (3x memory of data size)

3. **No semantic search** (keyword only)
   - Pros: Simple implementation
   - Cons: 
     - Poor search quality for natural language
     - Users frustrated by exact match requirements
     - Missed insights from conceptually related content
     - Competitive disadvantage vs semantic-aware systems
     - Requires manual tagging for discovery

4. **In-memory vector search** (FAISS, Annoy)
   - Pros: Very fast
   - Cons: 
     - Doesn't scale beyond single machine memory
     - Not persistent (cold start penalties)
     - Requires distributed coordination for HA
     - Memory costs prohibitive for large datasets
     - Complex index rebuild on startup
     - No transactional consistency with main data

## Consequences
### Positive
- Single database maintains architectural simplicity
- No data synchronization between systems
- Leverages existing PostgreSQL knowledge
- Good enough performance for current scale (<500ms target)
- Native SQL integration with other queries
- Cost-effective (no additional services)

### Negative
- Requires PostgreSQL extension installation
- May hit scaling limits with millions of vectors
- Less sophisticated than dedicated vector databases
- Limited to distance metrics supported by pgvector
- Requires PostgreSQL 11+ with extension support

### Implementation Details
- Use pgvector's vector type for embeddings
- Create indexes using IVFFlat or HNSW (when available)
- Cosine distance for similarity (1 - cosine similarity)
- Embedding dimension: 1536 (compatible with OpenAI)
- Index parameters tuned for <500ms search on 10k vectors

### Migration Path
If scaling limits are reached:
1. Can migrate to dedicated vector DB later
2. Use PostgreSQL for metadata, vector DB for embeddings
3. Implement caching layer for common queries

## References
- PersonaKit v0.1.1 Narratives Specification
- Technical Implementation Notes