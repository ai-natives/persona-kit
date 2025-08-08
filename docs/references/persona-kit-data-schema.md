# PersonaKit Data Schema

This document describes the actual database schema as implemented in PersonaKit v0.2.0.

## Core Tables

### 1. Users
Authentication and API access management.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE
);
```

**Fields:**
- `id`: UUID primary key
- `email`: Unique email address
- `api_key_hash`: Bcrypt-hashed API key
- `is_active`: Whether the user can access the API
- `created_at`: When the user was created
- `last_used_at`: Last API access time

### 2. Observations
Raw input data about individuals from various sources.

```sql
CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL,
    observation_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);
```

**Fields:**
- `id`: UUID primary key
- `person_id`: The individual this observation is about
- `observation_type`: Type of observation (work_session, user_input, calendar_event)
- `content`: Flexible JSON content specific to the observation type
- `metadata`: Additional metadata (source, context, etc.)
- `created_at`: When the observation was recorded
- `created_by`: User who created the observation

**Example Content:**
```json
{
  "duration_minutes": 90,
  "focus_level": "deep",
  "task_type": "coding",
  "tools_used": ["vscode", "github"]
}
```

### 3. Mindscapes
Aggregated traits and patterns for an individual.

```sql
CREATE TABLE mindscapes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID UNIQUE NOT NULL,
    traits JSONB NOT NULL DEFAULT '{}',
    version INTEGER DEFAULT 1,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key
- `person_id`: One-to-one relationship with the individual
- `traits`: Hierarchical trait structure as JSON
- `version`: Optimistic locking version
- `updated_at`: Last modification time

**Trait Structure Example:**
```json
{
  "work": {
    "chronotype": "morning",
    "focus_patterns": {
      "deep_work_duration": 90,
      "peak_hours": ["09:00", "11:00"]
    }
  },
  "communication": {
    "style": "direct",
    "preferred_medium": "written"
  }
}
```

### 4. Narratives
Human-written observations and trait curations with semantic search capabilities.

```sql
CREATE TABLE narratives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL,
    narrative_type VARCHAR(20) NOT NULL CHECK (narrative_type IN ('self_observation', 'curation')),
    raw_text TEXT NOT NULL,
    curated_text TEXT,
    tags TEXT[],
    context JSONB,
    trait_path TEXT,
    curation_action JSONB,
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    embedding vector(1536)
);

CREATE INDEX idx_narratives_embedding ON narratives 
USING hnsw (embedding vector_cosine_ops);
```

**Fields:**
- `id`: UUID primary key
- `person_id`: The individual this narrative is about
- `narrative_type`: Either 'self_observation' or 'curation'
- `raw_text`: Original text input
- `curated_text`: Processed/refined version
- `tags`: Array of descriptive tags
- `context`: Additional context as JSON
- `trait_path`: For curations, which trait is being curated
- `curation_action`: For curations, the specific action taken
- `source`: Where this narrative came from
- `embedding`: 1536-dimensional vector for semantic search

### 5. Trait-Narrative Links
Relationships between narratives and traits.

```sql
CREATE TABLE trait_narrative_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narrative_id UUID NOT NULL REFERENCES narratives(id) ON DELETE CASCADE,
    trait_path TEXT NOT NULL,
    link_type VARCHAR(20) NOT NULL CHECK (link_type IN ('extracted_from', 'curates', 'supports', 'contradicts')),
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key
- `narrative_id`: Which narrative this link is from
- `trait_path`: Dot-notation path to the trait (e.g., "work.chronotype")
- `link_type`: Type of relationship
- `confidence`: How confident we are in this link (0-1)
- `metadata`: Additional link information

### 6. Mapper Configurations
Versioned configuration files that define how to generate personas.

```sql
CREATE TABLE mapper_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL,
    configuration JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'deprecated')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    usage_count INTEGER DEFAULT 0,
    metadata JSONB,
    UNIQUE(config_id, version)
);
```

**Fields:**
- `id`: UUID primary key
- `config_id`: Human-readable configuration identifier
- `version`: Version number (auto-incremented)
- `configuration`: Full mapper configuration as JSON
- `status`: Lifecycle status
- `usage_count`: How many times this mapper has been used
- `metadata`: Additional metadata

**Configuration Structure:**
```json
{
  "metadata": {
    "id": "productivity-optimizer",
    "name": "Productivity Pattern Optimizer",
    "description": "Optimizes work patterns",
    "author": "user@example.com"
  },
  "rules": [
    {
      "id": "morning-person-deep-work",
      "conditions": {
        "all": [
          {
            "type": "trait_check",
            "trait": "work.chronotype",
            "operator": "equals",
            "value": "morning"
          }
        ]
      },
      "actions": [
        {
          "type": "suggestion",
          "template": "Schedule deep work in morning",
          "priority": "high"
        }
      ]
    }
  ]
}
```

### 7. Personas
Generated personas with time-to-live support.

```sql
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID NOT NULL,
    mapper_id UUID REFERENCES mapper_configs(id),
    mapper_config_id VARCHAR(255),
    mapper_version INTEGER,
    core JSONB NOT NULL,
    overlay JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_personas_person ON personas(person_id);
CREATE INDEX idx_personas_expires ON personas(expires_at);
```

**Fields:**
- `id`: UUID primary key
- `person_id`: The individual this persona represents
- `mapper_id`: Which mapper configuration was used
- `mapper_config_id`: Human-readable mapper ID
- `mapper_version`: Version of the mapper used
- `core`: Core persona data (low-volatility traits)
- `overlay`: Contextual overlay (high-volatility state)
- `metadata`: Generation metadata (tokens used, duration, etc.)
- `expires_at`: When this persona expires (TTL)

### 8. Persona-Narrative Usage
Tracks which narratives influenced persona generation.

```sql
CREATE TABLE persona_narrative_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    narrative_id UUID NOT NULL REFERENCES narratives(id),
    usage_type VARCHAR(50) NOT NULL,
    relevance_score FLOAT,
    usage_context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key
- `persona_id`: Which persona used this narrative
- `narrative_id`: Which narrative was used
- `usage_type`: How the narrative was used
- `relevance_score`: How relevant it was (0-1)
- `usage_context`: Additional context

### 9. Feedback
User feedback on generated personas and suggestions.

```sql
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID REFERENCES personas(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    helpful BOOLEAN,
    context JSONB,
    rule_id VARCHAR(255),
    mapper_version INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);
```

**Fields:**
- `id`: UUID primary key
- `persona_id`: Which persona this feedback is about
- `rating`: 1-5 star rating
- `helpful`: Whether the persona was helpful
- `context`: Task context and additional feedback
- `rule_id`: Which rule generated the suggestion
- `mapper_version`: Version of the mapper used

### 10. Outbox Tasks
Reliable asynchronous task processing.

```sql
CREATE TABLE outbox_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'done', 'failed')),
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    run_after TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_outbox_status_runafter ON outbox_tasks(status, run_after);
```

**Fields:**
- `id`: UUID primary key
- `task_type`: Type of task (process_observation, generate_embeddings, etc.)
- `payload`: Task-specific data as JSON
- `status`: Current task status
- `attempts`: Number of processing attempts
- `last_error`: Error message from last failed attempt
- `run_after`: When to process this task
- `completed_at`: When the task was completed

## Indexes

Key indexes for performance:

```sql
-- Observations
CREATE INDEX idx_observations_person_created ON observations(person_id, created_at DESC);

-- Mindscapes
CREATE UNIQUE INDEX idx_mindscapes_person ON mindscapes(person_id);

-- Narratives
CREATE INDEX idx_narratives_person ON narratives(person_id);
CREATE INDEX idx_narratives_type ON narratives(narrative_type);
CREATE INDEX idx_narratives_tags ON narratives USING GIN(tags);

-- Trait-Narrative Links
CREATE INDEX idx_trait_links_narrative ON trait_narrative_links(narrative_id);
CREATE INDEX idx_trait_links_trait ON trait_narrative_links(trait_path);

-- Mapper Configs
CREATE INDEX idx_mapper_configs_status ON mapper_configs(status);
CREATE UNIQUE INDEX idx_mapper_configs_active ON mapper_configs(config_id) WHERE status = 'active';

-- Feedback
CREATE INDEX idx_feedback_persona ON feedback(persona_id);
CREATE INDEX idx_feedback_created ON feedback(created_at DESC);
```

## Data Types and Constraints

### JSON Structure Guidelines

1. **Observation Content**: Flexible based on observation_type
2. **Mindscape Traits**: Hierarchical dot-notation paths
3. **Mapper Configuration**: Must follow the mapper schema with metadata, rules, and templates
4. **Persona Core/Overlay**: Structured according to mapper output

### Embedding Dimensions

- All narrative embeddings are 1536-dimensional vectors
- Generated using sentence-transformers locally (no external APIs)
- Indexed with HNSW for fast similarity search

### Time-to-Live (TTL)

- Personas have an `expires_at` field for automatic expiration
- Default TTL is 24 hours but can be configured per mapper
- Expired personas are retained for analytics but marked as expired

## Migration Notes

When upgrading from previous versions:

1. **v0.1 → v0.2**: Added narratives, mapper_configs, users tables
2. **Embedding Support**: Requires PostgreSQL with pgvector extension
3. **Authentication**: API keys are now required for all operations

## Performance Considerations

1. **JSONB vs JSON**: Use JSONB for better indexing and query performance
2. **Vector Search**: HNSW index provides O(log n) similarity search
3. **Partitioning**: Consider partitioning large tables (observations, narratives) by person_id or date
4. **Connection Pooling**: Use async connection pooling for high-concurrency scenarios