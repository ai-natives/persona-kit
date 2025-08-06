# PersonaKit Implementation Guide

## Table of Contents
1. [Core Principle: Task-Driven Personas](#core-principle-task-driven-personas)
2. [Use Case Analysis](#use-case-analysis)
3. [The Pruning Process](#the-pruning-process)
4. [Mapper Specifications](#mapper-specifications)
5. [Implementation Plan](#implementation-plan)
6. [Testing Strategy](#testing-strategy)

## Core Principle: Task-Driven Personas

### Fundamental Constraint: Personas Exist Only in Task Context

**A Persona without a task is meaningless.** This isn't a design choice - it's a fundamental constraint. Here's why:

1. **Mindscapes are vast**: A complete model of a person contains thousands of traits, experiences, preferences, patterns, and relationships
2. **Tasks require focus**: Any specific task only needs a tiny subset of that information
3. **Wrong information is harmful**: Including irrelevant traits adds noise and degrades performance
4. **Context determines relevance**: The same trait might be critical for one task and irrelevant for another

### The Persona Mapper's True Role

The Persona Mapper is not just a "query engine" - it's a **task-aware pruning algorithm** that understands:
- What information is relevant for this specific task
- What level of detail is appropriate
- What contextual factors matter right now
- What can be safely ignored

## Use Case Analysis

### 1. English Learning Coaching App

**System Overview**: An app that helps users practice English for specific workplace scenarios by simulating conversations with realistic personas of actual colleagues, clients, or managers.

**PersonaKit Integration**:
- **Observations**: Email/chat samples, meeting recordings, communication style notes
- **Mappers**: Communication Partner Mapper, Meeting Communication Partner
- **Scale**: 20-50+ personas per user (entire professional network)
- **Update Frequency**: Weekly
- **Detail Level**: Deep Dive for accurate simulation

**Key Requirements**:
- Focus on stable communication patterns over volatile traits
- Need language patterns, formality levels, cultural context
- Feedback: "Did the simulated conversation feel authentic?"

### 2. Marketing Strategy Testing App

**System Overview**: An app that tests marketing campaigns against panels of synthetic target audience members based on real customer data.

**PersonaKit Integration**:
- **Observations**: CRM data, surveys, behavioral analytics (often aggregated)
- **Mappers**: Consumer Purchase Decision Maker, Marketing Message Evaluator
- **Scale**: 100s of personas for panel diversity
- **Update Frequency**: Monthly
- **Detail Level**: Balanced (cost-effective for large panels)

**Key Requirements**:
- Focus on consumer behavior and decision patterns
- Need buying motivations, brand perceptions, media preferences
- Privacy considerations for aggregated data
- Feedback: "Did panel predictions match real campaign results?"

### 3. Knowledge Work Assistant

**System Overview**: An AI assistant that helps knowledge workers by understanding their work style and modeling stakeholders for tasks like review preparation.

**PersonaKit Integration**:
- **Observations**: Work artifacts, communication logs, productivity metrics
- **Mappers**: Daily Work Optimizer (self), Stakeholder Review Simulator (others)
- **Scale**: 1 primary user + multiple stakeholder personas
- **Update Frequency**: Daily/Hourly for user, weekly for stakeholders
- **Detail Level**: Instant for user (frequent checks), Balanced for stakeholders

**Key Requirements**:
- Real-time overlay updates for current state
- High-frequency persona access throughout the day
- Feedback: "Did suggestions match your needs?" / "Was review prediction accurate?"

### Comparison Matrix

| Aspect | English Coaching | Marketing Testing | Work Assistant |
|--------|------------------|-------------------|----------------|
| **Persona Count** | Many (20-50+ people) | Many (100s) | Mixed (1 primary + stakeholders) |
| **Update Frequency** | Weekly | Monthly | Daily/Hourly |
| **Detail Level** | Deep Dive | Balanced | Instant (user) / Balanced (others) |
| **Data Sensitivity** | High (personal) | Medium (aggregated) | High (personal + work) |
| **Volatility Focus** | Low (stable patterns) | Medium | High (current state) |
| **Primary Traits** | Communication style | Consumer behavior | Work patterns & preferences |

## The Pruning Process

### The Scale Challenge

A complete Mindscape might contain:
- 500+ distinct traits
- 1000+ experiences and memories
- 100+ relationships
- 50+ skills and competencies
- 200+ preferences and opinions

For a single task, we need only 10-20 data points.

### The Pruning Pipeline

#### Step 1: Task Context Analysis
```python
def analyze_task_context(request):
    task_type = request.task_type  # "email_composition"
    scenario = request.scenario     # "request_deadline_extension"
    
    # Determine required trait categories
    required_categories = TASK_TRAIT_MAP[task_type]
    scenario_traits = SCENARIO_MODIFIERS[scenario]
    
    return TraitSelector(required_categories + scenario_traits)
```

#### Step 2: Multi-Level Filtering
```python
def prune_mindscape(mindscape, trait_selector, task_context):
    # Level 1: Category filtering (1000s → 100s)
    filtered = mindscape.filter_by_categories(relevant_categories)
    
    # Level 2: Relevance scoring (100s → 10s)
    scored_traits = apply_relevance_threshold(filtered, task_context)
    
    # Level 3: Dependency resolution
    final_traits = resolve_dependencies(scored_traits)
    
    return final_traits
```

#### Step 3: Contextual Overlay
Apply current state adjustments:
- High-volatility trait updates
- Temporal modifiers (time of day, day of week)
- Recent event impacts

### Concrete Example: Email to Sarah

**Before Pruning**: 500+ traits including hobbies, family info, technical skills, health data...

**Task Context**: "Write email requesting deadline extension"

**After Pruning**: 10-15 relevant traits:
- `communication.written.formality`: "high"
- `work.deadline_flexibility`: "low" (Critical!)
- `values.advance_notice`: "high" (Critical!)
- `values.data_driven`: "very_high"
- Plus derived email guidance

## Mapper Specifications

### English Coaching Mappers

#### Workplace Email Composer
```typescript
{
  mapperId: "workplace-email-composer-v1",
  taskContext: {
    scenarios: ["request_something", "provide_update", "share_bad_news"]
  },
  pruningRules: {
    mustInclude: [
      "communication.email.*",
      "values.punctuality",
      "relationship.power_dynamic"
    ],
    mustExclude: ["personal.*", "technical.*", "hobbies.*"],
    conditionalInclude: [
      {
        condition: "scenario == 'request_something'",
        include: ["values.reciprocity", "work.deadline_flexibility"]
      }
    ]
  }
}
```

### Marketing Testing Mappers

#### Consumer Purchase Decision Maker
```typescript
{
  mapperId: "consumer-purchase-decision-v1",
  taskContext: {
    productCategories: ["eco_friendly", "premium_luxury", "value_budget"]
  },
  pruningRules: {
    mustInclude: [
      "consumer.price_sensitivity",
      "consumer.purchase_triggers",
      "values.environmental"
    ],
    mustExclude: ["work.*", "communication.workplace.*"],
    conditionalInclude: [
      {
        condition: "category == 'eco_friendly'",
        include: ["consumer.greenwashing_sensitivity"]
      }
    ]
  },
  aggregationRules: {
    panelSize: { minimum: 10, optimal: 25, maximum: 50 }
  }
}
```

### Work Assistant Mappers

#### Daily Work Optimizer
```typescript
{
  mapperId: "daily-work-optimizer-v1",
  taskContext: {
    timeHorizon: "today",
    adaptiveTo: ["energy", "calendar", "priorities"]
  },
  pruningRules: {
    mustInclude: [
      "work.energy_patterns",
      "current_state.energy_level",
      "productivity.peak_hours"
    ],
    mustExclude: ["personal.family.*", "consumer.*"]
  },
  realTimeOverlay: {
    refreshInterval: "hourly",
    signals: ["calendar_density", "completion_momentum"]
  }
}
```

## Implementation Plan

### Phase 1: Foundation
**Goal**: Basic PersonaKit that can ingest observations and generate simple personas

**Storage Architecture Decision**:
Based on the analysis in `mindscape-persona-schema-options.md`, we recommend:
- **Start with Option B (PostgreSQL + JSONB)** for MVP
- Provides ACID guarantees and familiar SQL tooling
- Supports future migration to Option D (Polyglot) when scale demands it
- See architectural options document for full trade-off analysis

**Technology Stack**:
```yaml
Database: PostgreSQL 15+ with pgvector
API: REST (not GraphQL initially)
Background Jobs: Redis + BullMQ
Caching: Redis for Persona cores
Language: TypeScript/Node.js or Python/FastAPI
```

**Core Components**:
- Observation API (create, approve)
- Basic Mindscaper (simple trait extraction)
- Simple Persona Generator
- One general-purpose Mapper

### Phase 2: Use Case MVP
**Goal**: Support Work Assistant use case end-to-end

Starting with Work Assistant because:
- Most frequent API usage (surfaces issues quickly)
- Single user focus (simpler than panels)
- Clear feedback loop

**Deliverables**:
1. Work Style Mapper
2. Real-time overlay support
3. Feedback API
4. Simple CLI/SDK for testing

### Phase 3: Multi-Use Case Support

Add remaining use cases in parallel:
- **English Coaching**: Communication Partner Mapper, language pattern analysis
- **Marketing Testing**: Target Audience Mapper, bulk generation, panel aggregation

### Phase 4: Production Readiness

**Scalability**:
- Add caching layer
- Implement proper queuing
- Add vector search for traits

**Robustness**:
- Add sync protocol
- Implement versioning
- Add monitoring/observability

## Testing Strategy

### Synthetic Test Data Requirements

#### English Coaching
- 30-50 fake workplace contacts:
  - 5-10 immediate team members
  - 10-15 cross-functional colleagues
  - 5-10 senior managers
  - 5-10 external clients/partners
  - 5-10 international colleagues

#### Marketing Testing
- 100 fake customers
- 3 distinct segments
- Purchase history and survey data

#### Work Assistant
- 1 primary user with 30 days of work artifacts
- 3-5 stakeholder reviewers with feedback history

### Success Metrics
- Persona generation time: <2s (Instant), <10s (Balanced), <30s (Deep Dive)
- Feedback incorporation improves accuracy by >10%
- System handles 100 concurrent persona requests
- Storage grows linearly with observations

## Implementation Sequence

### Immediate Actions
1. Set up PostgreSQL with JSONB
2. Create REST API scaffold
3. Implement Observation ingestion
4. Build simple Mindscaper
5. Create Work Style Mapper
6. Implement Persona generation
7. Add feedback collection
8. Generate synthetic test data
9. Run end-to-end tests
10. Iterate based on results

### Parallel Workstreams
- **Stream 1**: Add remaining mappers
- **Stream 2**: Performance optimizations
- **Stream 3**: Build SDKs for each use case
- **Stream 4**: Monitoring and observability

## Critical Design Decisions

1. **Mappers Are Not Generic**: Each mapper is designed for specific task categories
2. **Task Context Is Mandatory**: Every persona request must include task context
3. **Caching Is Task-Aware**: Same person needs different personas for different tasks
4. **Success = Task Completion**: Not "accurate persona" but "effective task outcome"

## Migration Paths

As outlined in `mindscape-persona-schema-options.md`, starting with Option B (PostgreSQL + JSONB) provides flexibility:

- **To Option A (Document DB)**: If you need simpler operations and can sacrifice some query flexibility
- **To Option D (Polyglot)**: When scale demands specialized stores:
  - Vector DB (Pinecone, Weaviate) for embeddings
  - Document DB (MongoDB) for observations
  - Graph DB (Neo4j) for relationship analysis
  - Redis for caching

The architecture supports gradual evolution without major rewrites. Each option is designed to handle different scale and complexity requirements:
- **Option A**: Best for small teams, rapid iteration
- **Option B**: Best for regulated environments, strong consistency needs  
- **Option C**: Best for relationship-heavy analysis, explainability
- **Option D**: Best for large scale, specialized performance requirements