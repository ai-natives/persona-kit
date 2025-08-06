# PersonaKit Narrative Enhancement Plan

## Overview

This plan extends PersonaKit's configuration-driven architecture (Phase 6.5) to support human narratives alongside traits. The goal is to preserve the messy, valuable human input that makes personas feel real while maintaining the performance and queryability of the trait system.

## Core Concept

Two types of human narratives as first-class data:
1. **Self-observations**: Raw brain dumps about own patterns
2. **Curations**: User refinements and corrections to their mindscape

All narratives are stored with embeddings for semantic search from day one.

## Key Architectural Principles

1. **PersonaKit remains a service**: Agents call PersonaKit, not the other way around
2. **Pull-based interaction**: Users choose when to view/edit via Workbench/Explorer
3. **Agent-driven collection**: Agents decide when/how to collect observations
4. **No push notifications**: PersonaKit never prompts users directly

## Role Separation

### PersonaKit Core (Service)
- Stores narratives with embeddings
- Evaluates rules using narratives
- Provides API for CRUD operations
- Never initiates user contact

### Agents (Collectors)
- Decide when to collect observations
- Ask users for narrative context
- Create observations based on behavior
- Control the timing and manner of collection

### Workbench (User Control)
- Direct narrative input when user chooses
- Curation and correction capabilities  
- Privacy controls (consent, deletion)
- Bootstrap wizard (user-initiated only)

### Explorer (Visibility)
- Browse all narratives and their relationships
- Trace narrative influence on personas
- Audit social perspectives and consent
- Search and filter capabilities

## Implementation Plan

### Phase 1: Database & Core Models (Week 1)

#### 1.1 Database Schema
```sql
-- Enable vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Unified narratives table with embeddings
CREATE TABLE narratives (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL,
    narrative_type TEXT NOT NULL, -- 'self_observation', 'curation'
    raw_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL, -- OpenAI ada-3 or similar
    
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
    extraction_method TEXT, -- 'manual', 'auto', 'validated'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track which narratives influenced persona generation
CREATE TABLE persona_narrative_usage (
    persona_id UUID REFERENCES personas(id),
    narrative_id UUID REFERENCES narratives(id),
    relevance_score FLOAT,
    usage_type TEXT, -- 'context', 'validation', 'generation'
    PRIMARY KEY (persona_id, narrative_id)
);
```

#### 1.2 Data Models
```python
# models/narrative.py
from sqlalchemy import Column, String, Text, TIMESTAMP, UUID, Float
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

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

### Phase 2: Services & API (Week 2)

#### 2.1 Embedding Service
```python
# services/embedding_service.py
from openai import AsyncOpenAI

class EmbeddingService:
    def __init__(self):
        self.client = AsyncOpenAI()
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        response = await self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts efficiently."""
        response = await self.client.embeddings.create(
            model="text-embedding-3-large", 
            input=texts
        )
        return [d.embedding for d in response.data]
```

#### 2.2 Narrative Service
```python
# services/narrative_service.py
class NarrativeService:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        
    async def create_self_observation(
        self,
        person_id: UUID,
        raw_text: str,
        tags: List[str] = None
    ) -> Narrative:
        # Generate embedding
        embedding = await self.embedding_service.embed_text(raw_text)
        
        narrative = Narrative(
            person_id=person_id,
            narrative_type='self_observation',
            raw_text=raw_text,
            embedding=embedding,
            tags=tags or self._extract_tags(raw_text)
        )
        
        await self.session.add(narrative)
        await self.session.commit()
        
        return narrative
    
    async def semantic_search(
        self,
        person_id: UUID,
        query: str,
        narrative_types: List[str] = None,
        similarity_threshold: float = 0.7,
        limit: int = 5
    ) -> List[Tuple[Narrative, float]]:
        """Find narratives semantically similar to query."""
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Build query
        sql = """
        SELECT n.*, 1 - (n.embedding <=> %s::vector) as similarity
        FROM narratives n
        WHERE n.person_id = %s
          AND 1 - (n.embedding <=> %s::vector) > %s
        """
        params = [query_embedding, person_id, query_embedding, similarity_threshold]
        
        if narrative_types:
            sql += " AND n.narrative_type = ANY(%s)"
            params.append(narrative_types)
            
        sql += " ORDER BY similarity DESC LIMIT %s"
        params.append(limit)
        
        result = await self.session.execute(sql, params)
        return [(Narrative(**row), row['similarity']) for row in result]
```

#### 2.3 API Endpoints
```python
# api/narratives.py
@router.post("/narratives/self-observation")
async def create_self_observation(
    request: CreateNarrativeRequest,
    narrative_service: NarrativeService = Depends(get_narrative_service)
):
    """Add a self-observation narrative."""
    narrative = await narrative_service.create_self_observation(
        person_id=request.person_id,
        raw_text=request.raw_text,
        tags=request.tags
    )
    return {"narrative_id": narrative.id}

@router.post("/narratives/curate")
async def curate_mindscape(
    request: CurationRequest,
    narrative_service: NarrativeService = Depends(get_narrative_service)
):
    """Add a curation to refine/correct mindscape."""
    narrative = await narrative_service.create_curation(
        person_id=request.person_id,
        action=request.action,  # 'refine', 'correct', 'add_context'
        target_type=request.target_type,
        target_id=request.target_id,
        note=request.note
    )
    return {"curation_id": narrative.id}

@router.post("/narratives/social-perspective")
async def add_social_perspective(
    request: SocialPerspectiveRequest,
    consent_service: ConsentService = Depends(get_consent_service),
    narrative_service: NarrativeService = Depends(get_narrative_service)
):
    """Add perspective about someone (requires consent)."""
    # Verify consent
    consent = await consent_service.verify_consent(
        subject_id=request.about_person_id,
        observer_id=request.source_person_id,
        type='social_observation'
    )
    
    if not consent:
        raise HTTPException(403, "No valid consent for social perspective")
    
    narrative = await narrative_service.create_social_perspective(
        about_person_id=request.about_person_id,
        source_person_id=request.source_person_id,
        source_relationship=request.relationship,
        raw_text=request.raw_text,
        consent_id=consent.id
    )
    
    return {"perspective_id": narrative.id}
```

### Phase 3: Rule Engine Integration (Week 3)

#### 3.1 Enhanced Rule Engine
```python
# services/rule_engine.py (updates)
class RuleEngine:
    def __init__(self, embedding_service: EmbeddingService, session: AsyncSession):
        self.embedding_service = embedding_service
        self.session = session
        
    async def evaluate_rules(
        self,
        config: Dict[str, Any],
        mindscape: Mindscape,
        person_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Evaluate rules with narrative support."""
        suggestions = []
        context = context or {}
        
        # Pre-fetch narratives if config uses them
        narratives = None
        if config.get("narrative_config", {}).get("enabled", False):
            narratives = await self._prefetch_narratives(person_id, config)
        
        for rule in config.get("rules", []):
            try:
                # Evaluate conditions including narrative checks
                matched, narrative_context = await self._evaluate_conditions(
                    rule["conditions"], 
                    mindscape.traits, 
                    person_id,
                    narratives,
                    context
                )
                
                if matched:
                    weight = rule.get("weight", 1.0)
                    if weight > 0:
                        for action in rule.get("actions", []):
                            suggestion = self._generate_suggestion(
                                action["generate_suggestion"],
                                config.get("templates", {}),
                                mindscape.traits,
                                context,
                                narrative_context  # Pass matching narratives
                            )
                            suggestions.append(suggestion)
                            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.get('id')}: {e}")
                
        return suggestions
    
    async def _evaluate_narrative_check(
        self,
        check: Dict[str, Any],
        person_id: UUID,
        cached_narratives: Optional[Dict] = None
    ) -> Tuple[bool, List[Narrative]]:
        """
        Evaluate narrative condition using semantic search.
        Returns (matched, matching_narratives)
        """
        semantic_query = check.get('semantic_query')
        if not semantic_query:
            return False, []
            
        # Use cached narratives if available
        if cached_narratives and semantic_query in cached_narratives:
            narratives = cached_narratives[semantic_query]
        else:
            # Perform semantic search
            narrative_service = NarrativeService(self.embedding_service)
            narratives = await narrative_service.semantic_search(
                person_id=person_id,
                query=semantic_query,
                narrative_types=check.get('narrative_types'),
                similarity_threshold=check.get('similarity_threshold', 0.7),
                limit=check.get('limit', 5)
            )
        
        return len(narratives) > 0, narratives
```

#### 3.2 Configuration Schema Updates
```yaml
# Enhanced mapper configuration
metadata:
  id: daily_work_optimizer_narrative
  version: 2.0.0
  description: "Work optimization with narrative awareness"
  
narrative_config:
  enabled: true
  search_patterns:
    - id: energy_patterns
      queries:
        - "when I feel most productive and energized"
        - "my energy levels throughout the day"
        - "times when I do my best work"
      similarity_threshold: 0.75
      
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
          type: task_recommendation
          template: deep_work_window
          include_narrative_context: true
          narrative_excerpt_length: 200
          
templates:
  deep_work_window:
    title: "Deep Work Window"
    description: "Block the next {duration} minutes for challenging work"
    with_narrative: |
      Based on your observation: "{narrative_excerpt}"
```

### Phase 4: Persona Generation Updates (Week 4)

#### 4.1 Enhanced Persona Generator
```python
# services/persona_generator.py (updates)
class PersonaGenerator:
    async def generate_persona(
        self,
        person_id: UUID,
        mapper_id: str,
        mindscape: Mindscape,
        context: Optional[Dict[str, Any]] = None,
        include_narratives: bool = True
    ) -> Persona:
        """Generate persona with optional narrative enrichment."""
        # Load mapper configuration
        mapper_config = await self._get_mapper_config(mapper_id)
        
        # Evaluate rules (with narrative support if enabled)
        suggestions = await self.rule_engine.evaluate_rules(
            config=mapper_config,
            mindscape=mindscape,
            person_id=person_id,
            context=context
        )
        
        # Track narrative usage
        narrative_usage = []
        for suggestion in suggestions:
            if narratives := suggestion.get('narrative_context'):
                for narrative, score in narratives:
                    narrative_usage.append({
                        'narrative_id': narrative.id,
                        'relevance_score': score,
                        'usage_type': 'generation'
                    })
        
        # Create persona
        persona = Persona(
            person_id=person_id,
            mapper_id=mapper_id,
            mapper_config_id=mapper_config.id,
            core=self._build_core(suggestions),
            overlay=self._build_overlay(suggestions, context),
            metadata={'narrative_aware': mapper_config.get('narrative_config', {}).get('enabled', False)}
        )
        
        # Record narrative usage
        if narrative_usage:
            await self._record_narrative_usage(persona.id, narrative_usage)
            
        return persona
```

### Phase 5: Workbench & Explorer Integration (Week 5)

#### 5.1 PersonaKit Explorer Updates
```typescript
// New Narratives tab in Explorer
interface NarrativeExplorer {
  // Browse all narratives with filtering
  narrativeBrowser: {
    view: 'timeline' | 'grouped' | 'search'
    filters: {
      type: NarrativeType[]
      dateRange: DateRange
      hasTraitLinks: boolean
    }
  }
  
  // Trace narrative influence on personas
  narrativeTracing: {
    showUsedInPersona: PersonaId[]
    showExtractedTraits: TraitPath[]
    showSimilarNarratives: number
  }
  
}

// NO push notifications or prompts
// Users navigate here when THEY choose to explore
```

#### 5.2 PersonaKit Workbench Updates
```python
# workbench/cli/narratives.py
class NarrativeCommands:
    """User-initiated narrative management"""
    
    @command
    def add_observation(self, text: str, tags: List[str] = None):
        """Add a self-observation directly"""
        narrative = self.client.create_narrative(
            type="self_observation",
            raw_text=text,
            tags=tags,
            source="workbench_direct"  # Track that user added this
        )
        print(f"Added observation: {narrative.id}")
    
    @command
    def curate_trait(self, trait_path: str, note: str):
        """Correct or refine a trait interpretation"""
        curation = self.client.create_curation(
            target_type="trait",
            target_path=trait_path,
            note=note
        )
        print(f"Curation recorded: {curation.id}")
    
    @command
    def list_narratives(self, limit: int = 10):
        """View your recent narratives"""
        # Shows what's stored, doesn't collect new ones
    

# NO periodic prompts or check-ins
# Workbench is used when user chooses to use it
```

#### 5.3 Agent Integration Pattern
```python
# Example: How agents should collect narratives
class WorkAssistantAgent:
    """Example of agent-driven narrative collection"""
    
    async def handle_user_message(self, message: str):
        # Agent decides if this contains valuable insight
        if self._seems_like_self_reflection(message):
            # Agent asks permission
            if await self.ask_user(
                "That's an interesting insight about your work style. "
                "Would you like me to remember this for PersonaKit?"
            ):
                await self.personakit.create_narrative(
                    type="self_observation",
                    raw_text=message,
                    collected_by=self.agent_id,
                    context={"conversation_topic": "work_patterns"}
                )
        
    async def notice_behavioral_pattern(self):
        # Agent observes pattern
        pattern = self.analyze_recent_actions()
        
        # Agent creates observation (not narrative)
        await self.personakit.create_observation({
            "type": "behavioral_pattern",
            "content": pattern,
            "observed_by": self.agent_id
        })
        
        # Agent might ask for narrative context
        response = await self.ask_user(
            f"I noticed you {pattern.description}. "
            "Want to share any context about this?"
        )
        
        if response:
            # Store user's explanation as narrative
            await self.personakit.create_narrative(
                type="self_observation",
                raw_text=response,
                linked_observation_id=pattern.id
            )

# Key: AGENT decides when to collect, not PersonaKit
```

### Phase 6: Testing & Performance (Week 6)

#### 5.1 Test Suite
```python
# tests/test_narratives.py
async def test_semantic_search():
    """Test that semantic search finds related narratives."""
    # Create narratives with similar meaning but different words
    await create_narrative(
        person_id=test_person_id,
        raw_text="I'm incredibly productive in the early morning hours"
    )
    await create_narrative(
        person_id=test_person_id,
        raw_text="My best work happens before 10am"
    )
    
    # Search should find both
    results = await narrative_service.semantic_search(
        person_id=test_person_id,
        query="morning productivity",
        similarity_threshold=0.7
    )
    
    assert len(results) == 2
    assert all(score > 0.7 for _, score in results)

async def test_consent_required_for_social():
    """Test that social perspectives require consent."""
    # Attempt without consent
    with pytest.raises(HTTPException) as exc:
        await add_social_perspective(
            about_person_id=subject_id,
            source_person_id=observer_id,
            raw_text="Sarah is great at architecture design"
        )
    assert exc.value.status_code == 403
```

#### 5.2 Performance Optimizations
```python
# services/narrative_cache.py
class NarrativeCache:
    """Cache embeddings and search results for performance."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1 hour
        
    async def get_or_search(
        self,
        cache_key: str,
        search_func,
        *args,
        **kwargs
    ):
        # Check cache
        cached = await self.redis.get(cache_key)
        if cached:
            return pickle.loads(cached)
            
        # Execute search
        results = await search_func(*args, **kwargs)
        
        # Cache results
        await self.redis.setex(
            cache_key,
            self.ttl,
            pickle.dumps(results)
        )
        
        return results
```

## Success Metrics

1. **Performance**: Persona generation remains <2s with narrative search
2. **Relevance**: Semantic search precision >85% for finding related narratives  
3. **Privacy**: 100% of social perspectives have valid consent
4. **Transparency**: Users can see which narratives influenced suggestions
5. **User Control**: 100% of narratives are user-initiated (via agents or workbench)
6. **No Interruptions**: Zero push notifications or unsolicited prompts from PersonaKit

## Next Steps

1. **Immediate**: Implement database schema and core models
2. **Week 1-2**: Build embedding service and narrative APIs
3. **Week 3**: Integrate with rule engine
4. **Week 4**: Update persona generation
5. **Week 5**: Testing and optimization

This plan treats narratives as first-class data with modern semantic search, proper consent management, and seamless integration with the existing configuration-driven architecture.