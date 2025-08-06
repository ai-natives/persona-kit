# PersonaKit v0.1.1 Unified Build Plan

## Overview

PersonaKit v0.1.1 extends the configuration-driven architecture (completed in Phase 6.5) with human narrative support. This preserves the messy, valuable human input that makes personas feel real while maintaining the performance of the trait system.

## What's Already Built (v0.1)

1. **Core Infrastructure**: FastAPI, PostgreSQL, observation processing
2. **Configuration-Driven Mappers**: YAML/JSON rule definitions uploaded via API
3. **Rule Engine**: Evaluates conditions and generates suggestions
4. **Feedback Loop**: Adjusts rule weights based on accuracy
5. **PersonaKit Workbench**: Bootstrap wizard and developer tools
6. **PersonaKit Explorer**: Visibility into personas and mindscapes

## What v0.1.1 Adds

### Core Enhancement: Human Narratives

Two types of first-class narrative data:
1. **Self-observations**: Raw brain dumps about own patterns
2. **Curations**: User refinements and corrections to their mindscape

All narratives stored with embeddings for semantic search from day one.

### Key Principles

1. **PersonaKit remains a service**: Agents call PersonaKit, not the other way around
2. **Pull-based interaction**: Users choose when to view/edit via Workbench/Explorer
3. **Agent-driven collection**: Agents decide when/how to collect observations
4. **No push notifications**: PersonaKit never prompts users directly

## Implementation Phases

### Phase 1: Database & Core Models

#### Database Extensions
```sql
-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Unified narratives table with embeddings
CREATE TABLE narratives (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL,
    narrative_type TEXT NOT NULL, -- 'self_observation', 'curation'
    raw_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    
    -- Metadata
    tags TEXT[],
    context JSONB,
    
    -- For curations
    target_type TEXT, -- 'trait', 'narrative', 'rule'
    target_id UUID,
    
    -- Tracking
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fast semantic search
CREATE INDEX idx_narratives_embedding ON narratives 
USING hnsw (embedding vector_cosine_ops);

-- Link narratives to extracted traits
CREATE TABLE trait_narrative_links (
    id UUID PRIMARY KEY,
    trait_path TEXT NOT NULL,
    narrative_id UUID REFERENCES narratives(id),
    extraction_confidence FLOAT,
    extraction_method TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Data Models
```python
class Narrative(Base):
    __tablename__ = "narratives"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    person_id = Column(UUID, nullable=False)
    narrative_type = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    tags = Column(JSONB)
    context = Column(JSONB)
    
    # For curations
    target_type = Column(String)
    target_id = Column(UUID)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
```

### Phase 2: Services & API

#### Embedding Service
```python
class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI()
        
    async def embed_text(self, text: str) -> List[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
```

#### Narrative API Endpoints
```python
@router.post("/narratives/self-observation")
async def create_self_observation(request: CreateNarrativeRequest):
    """Add a self-observation narrative."""
    narrative = await narrative_service.create_self_observation(
        person_id=request.person_id,
        raw_text=request.raw_text,
        tags=request.tags
    )
    return {"narrative_id": narrative.id}

@router.post("/narratives/curate")
async def curate_mindscape(request: CurationRequest):
    """Add a curation to refine/correct mindscape."""
    narrative = await narrative_service.create_curation(
        person_id=request.person_id,
        action=request.action,
        target_type=request.target_type,
        target_id=request.target_id,
        note=request.note
    )
    return {"curation_id": narrative.id}

@router.get("/narratives/search")
async def semantic_search(
    person_id: UUID,
    query: str,
    limit: int = 5
):
    """Find narratives semantically similar to query."""
    results = await narrative_service.semantic_search(
        person_id=person_id,
        query=query,
        limit=limit
    )
    return {"narratives": results}
```

### Phase 3: Rule Engine Integration

#### Enhanced Rule Engine
```python
class RuleEngine:
    async def evaluate_rules(
        self,
        config: Dict[str, Any],
        mindscape: Mindscape,
        person_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Evaluate rules with narrative support."""
        # Pre-fetch narratives if config uses them
        narratives = None
        if config.get("narrative_config", {}).get("enabled", False):
            narratives = await self._prefetch_narratives(person_id, config)
        
        # Evaluate conditions including narrative checks
        for rule in config.get("rules", []):
            matched, narrative_context = await self._evaluate_conditions(
                rule["conditions"], 
                mindscape.traits, 
                person_id,
                narratives
            )
            
            if matched:
                # Generate suggestions with narrative context
                suggestion = self._generate_suggestion(
                    action,
                    templates,
                    mindscape.traits,
                    context,
                    narrative_context
                )
```

#### Enhanced Mapper Configuration
```yaml
metadata:
  id: daily_work_optimizer_narrative
  version: 2.0.0
  
narrative_config:
  enabled: true
  
rules:
  - id: morning_energy_with_narratives
    conditions:
      any:
        # Traditional trait check
        - trait_check:
            path: work.energy_patterns.morning
            value: high
            
        # Semantic narrative search
        - narrative_check:
            semantic_query: "I'm most productive in the morning"
            narrative_types: ["self_observation"]
            similarity_threshold: 0.8
            
    actions:
      - generate_suggestion:
          template: deep_work_window
          include_narrative_context: true
```

### Phase 4: Persona Generation Updates

Update persona generation to track narrative usage:
```python
class PersonaGenerator:
    async def generate_persona(
        self,
        person_id: UUID,
        mapper_id: str,
        mindscape: Mindscape,
        context: Optional[Dict[str, Any]] = None,
        include_narratives: bool = True
    ) -> Persona:
        # Evaluate rules with narrative support
        suggestions = await self.rule_engine.evaluate_rules(
            config=mapper_config,
            mindscape=mindscape,
            person_id=person_id,
            context=context
        )
        
        # Track which narratives influenced the persona
        narrative_usage = []
        for suggestion in suggestions:
            if narratives := suggestion.get('narrative_context'):
                for narrative, score in narratives:
                    narrative_usage.append({
                        'narrative_id': narrative.id,
                        'relevance_score': score,
                        'usage_type': 'generation'
                    })
```

### Phase 5: Workbench & Explorer Updates

#### PersonaKit Explorer
- New Narratives tab for browsing all narratives
- Trace narrative influence on personas
- Search and filter capabilities

#### PersonaKit Workbench
```python
class NarrativeCommands:
    @command
    def add_observation(self, text: str, tags: List[str] = None):
        """Add a self-observation directly"""
        
    @command
    def curate_trait(self, trait_path: str, note: str):
        """Correct or refine a trait interpretation"""
        
    @command
    def list_narratives(self, limit: int = 10):
        """View your recent narratives"""
```

### Phase 6: Testing & Performance

#### Performance Targets
- Persona generation with narratives: < 2s
- Semantic search: < 500ms for 10k narratives
- Embedding generation: < 200ms

#### Test Coverage
- Semantic search accuracy tests
- Narrative influence tracing
- Performance benchmarks with embeddings
- Integration tests for narrative flow

## Success Metrics

1. **Performance**: Persona generation remains <2s with narrative search
2. **Relevance**: Semantic search precision >85% for finding related narratives  
3. **Privacy**: Users have full control over their narratives
4. **Transparency**: Users can see which narratives influenced suggestions
5. **Adoption**: >50% of generated personas use narrative context

## Key Deliverables

1. **Database Migration**: Add narrative tables with pgvector
2. **Embedding Service**: OpenAI integration for semantic search
3. **Enhanced Rule Engine**: Support for narrative conditions
4. **API Extensions**: Narrative CRUD and search endpoints
5. **Workbench Updates**: Direct narrative input commands
6. **Explorer Updates**: Narrative browsing and influence tracing
7. **Documentation**: How narratives enhance personas
8. **Test Suite**: Comprehensive tests for narrative features

## Development Approach

With multiple coding agents working in parallel:

1. **Agent A**: Database schema, models, embedding service
2. **Agent B**: API endpoints, narrative service
3. **Agent C**: Rule engine integration, mapper updates
4. **Agent D**: Workbench/Explorer UI updates
5. **Agent E**: Testing, performance optimization

All work happens on feature branches, merged via PR when complete.

## Next Steps After v0.1.1

- v0.2.0: Full role-playing support (agents embodying other people)
- v0.2.1: Social perspectives with consent management
- v0.3.0: Advanced behavioral modeling (state machines, temporal patterns)