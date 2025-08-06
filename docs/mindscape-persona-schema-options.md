# Mindscape & Persona Schema Options

Below are four viable data-modeling approaches for the core PersonaKit objects—**Mindscape** and **Persona**—plus supporting entities.

---
## Option A – Single-Document (Document DB)

Mindscape and Persona each live in their own document collections (e.g., MongoDB or Firestore).

```jsonc
// mindscapes
{
  _id: "<userId>",
  version: 42,
  lastUpdated: "2024-06-30T18:22:00Z",
  traits: [
    {
      id: "comm_style/assertive",
      category: "communication",
      value: "assertive",
      volatility: "low",
      confidence: 0.86,
      embedding: [0.12, 0.07, …],
      sources: [{ obsId: "...", weight: 0.7 }]
    }
  ],
  highVolatileCache: {
    mood: "focused",
    availability: "UTC+1 09:00-17:00"
  }
}
```

```jsonc
// personas
{
  _id: "<mapperId>:<userId>:<detail>",
  userId: "<userId>",
  mapperId: "<mapperId>",
  detailLevel: "Instant",
  generatedAt: "2024-06-30T18:25:00Z",
  isStale: false,
  expiresAt: "2024-07-01T18:25:00Z",      // Matches TTL rules in logical schema
  coreSnapshot: { /* low-volatility traits */ },
  overlaySlice: { /* high-volatility slice */ }
}
```

**Best for:** small teams, rapid iteration, minimal ops overhead.

_Alignment with logical schema:_ Includes `version`, `isStale`, and now `expiresAt` to satisfy TTL requirement.

---
## Option B – Relational + JSONB (PostgreSQL)

Traits are first-class rows; embeddings use `pgvector`; Persona Core is a materialized view.

```sql
CREATE TABLE humans (
  id UUID PRIMARY KEY,
  created_at TIMESTAMP
);

CREATE TABLE traits (
  human_id UUID REFERENCES humans(id),
  category TEXT,
  name TEXT,
  value TEXT,
  volatility SMALLINT,      -- 0 = low, 2 = high
  confidence NUMERIC,
  embedding VECTOR(768),    -- pgvector
  sources JSONB,
  PRIMARY KEY (human_id, category, name)
);

CREATE MATERIALIZED VIEW persona_core AS
SELECT human_id,
       jsonb_agg(jsonb_build_object(
         'category', category,
         'name',     name,
         'value',    value,
         'confidence', confidence
       )) AS traits
FROM traits
WHERE volatility = 0
GROUP BY human_id;

CREATE TABLE personas (
  id UUID PRIMARY KEY,
  human_id UUID,
  mapper_id UUID,
  detail_level SMALLINT,
  generated_at TIMESTAMP,
  core   JSONB,
  overlay JSONB,
  is_stale BOOLEAN,
  expires_at TIMESTAMP
);
```

**Best for:** regulated environments, strong SQL familiarity, ACID guarantees.

_Alignment with logical schema:_ Adds `expires_at` column; other logical rules (unique Mindscape per person, FK constraints) enforced via SQL.

---
## Option C – Graph-Native (Neo4j / Neptune)

Model provenance and relationships explicitly with nodes and edges.

```
(:Human {id})
(:Observation {id, ts})
(:Trait {category, name, value, volatility, confidence})
(:Mapper {id, version})
(:Persona {id, detail, generatedAt, isStale})

(:Human)-[:HAS_OBSERVATION]->(:Observation)
(:Observation)-[:YIELDED]->(:Trait)
(:Human)-[:HAS_TRAIT]->(:Trait)

(:Human)-[:GENERATED_WITH {detail}]->(:Persona)
(:Persona)-[:INCLUDES]->(:Trait)
(:Persona)-[:USING_MAPPER]->(:Mapper)
```

**Best for:** rich provenance queries, recommendation graphs, explainability-heavy domains.

_Alignment with logical schema:_ Add `expiresAt` / `ttlHours` properties on `:Persona` nodes to respect TTL; maintain `version` as node prop on `:Mindscape`.

---
## Option D – Polyglot (Vector + Document + Relational)

Split storage by concern.

1. **Vector DB** (e.g., Pinecone) — `Trait.id`, embedding, volatility tag.  
2. **Document DB** (e.g., Mongo) — Observations & full trait JSON.  
3. **Relational** (e.g., Postgres) — canonical Humans, Personas, Mappers; joins & access control.

Persona build flow:
1. Fetch low-volatility trait IDs from Postgres; bulk-read JSON bodies from Mongo.  
2. Run real-time overlay query on Vector DB filtered by `humanId AND volatility=high`.  
3. Assemble & cache Persona in Postgres or Redis.

**Best for:** very large-scale embeddings, specialized infra teams willing to manage multiple datastores.

_Alignment with logical schema:_ Use Redis TTL or Postgres `expires_at` column for Persona caching; store `version` and `is_stale` flags in relational layer. 