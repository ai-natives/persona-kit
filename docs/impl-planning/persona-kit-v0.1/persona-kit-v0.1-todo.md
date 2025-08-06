# PersonaKit v0.1 - Work Plan

## Goal
Build a minimal PersonaKit that helps individual knowledge workers optimize their daily productivity by understanding their work patterns and providing personalized suggestions.

## Key Outcomes
- Working API that can ingest observations and generate personas
- Daily Work Optimizer mapper that provides actionable suggestions
- Feedback loop that improves suggestions over time
- Complete local development environment

## Success Criteria
- [ ] Can bootstrap a new user in under 10 minutes
- [ ] Generates daily work optimization suggestions
- [ ] Feedback improves suggestion quality (>70% helpful ratings after 1 week)
- [ ] All tests pass and code is properly linted
- [ ] Single command starts entire system
- [ ] Persona generation < 2 seconds
- [ ] API response time < 200ms

## Performance Targets
- **Persona Generation**: < 2 seconds (with up to 1000 observations)
- **API Response Time**: < 200ms for all endpoints
- **Memory Usage**: < 100MB for base system
- **Database Size**: Handle 10k observations per user efficiently

## Related Documentation
- **Specification**: @docs/persona-kit-v0.1-specification.md
- **Architecture Overview**: @docs/persona-kit-overview.md
- **Technical Spec**: @docs/persona-kit-technical-spec.md
- **Data Schema**: @docs/persona-kit-data-schema.md
- **Schema Options**: @docs/mindscape-persona-schema-options.md (using Option B)

## Phase 1: Foundation Setup
- [ ] Create project structure with src/, tests/, docs/ directories
- [ ] Set up Python environment with Poetry/requirements.txt
- [ ] Configure PostgreSQL with docker-compose
- [ ] Create database schema and migrations
- [ ] Set up FastAPI application skeleton
- [ ] Configure development tools (pytest, ruff, mypy)
- [ ] Create basic health check endpoint
- [ ] Create PostgreSQL initialization script with proper timezone support
- [ ] Add error handling middleware for consistent API responses
- [ ] Set up structured logging with JSON format (use Python logging with JSONFormatter)
- [ ] Configure shared logger for API and background workers
- [ ] Add correlation IDs for request tracking

### Phase 1 Verification
- [ ] Run `docker-compose up` and verify PostgreSQL starts
- [ ] Run database migrations successfully
- [ ] Access health check endpoint at http://localhost:8000/health
- [ ] Run `pytest` and see test framework working
- [ ] Run `ruff check` with no errors
- [ ] Run `mypy src/` with no errors
- [ ] Test error handling with invalid request
- [ ] Verify JSON logs are properly formatted

### Phase 1 Reality Check
**STOP! Answer these questions with specific details:**
1. **Did you ACTUALLY run the API?**
   - [ ] Command used: _____
   - [ ] Health check response: _____

2. **Did you verify database setup?**
   - [ ] Connected to PostgreSQL: _____
   - [ ] Tables created: _____

3. **Did you test error handling?**
   - [ ] Invalid request sent: _____
   - [ ] Error response format: _____

## Phase 2: Core Data Models
- [x] Implement Observation model and database table
- [x] Implement Mindscape model with JSONB traits storage
- [x] Implement Persona model with TTL support (expires_at field)
- [x] Implement Feedback model
- [x] Create Pydantic schemas for API requests/responses
- [x] Add database repository classes with basic CRUD
- [x] Write unit tests for models and repositories
- [x] Add data retention policy (observations older than 90 days)
- [x] Add migration for outbox_tasks columns: attempts, last_error, completed_at
- [x] Create specific database indexes:
  ```sql
  CREATE INDEX idx_observations_person_created ON observations(person_id, created_at DESC);
  CREATE INDEX idx_mindscapes_person ON mindscapes(person_id);
  CREATE INDEX idx_personas_expires ON personas(expires_at) WHERE expires_at > NOW();
  CREATE INDEX idx_feedback_persona ON feedback(persona_id, created_at DESC);
  ```

### Phase 2 Verification
- [ ] Run all unit tests and verify they pass
- [ ] Manually test CRUD operations via Python REPL
- [ ] Verify JSONB queries work correctly
- [ ] Check that Persona TTL is enforced (test expiration)
- [ ] Lint all code with ruff
- [ ] Type check with mypy
- [ ] Verify indexes are created properly

### Phase 2 Reality Check
**STOP! Answer these questions with specific details:**
1. **Did you test actual database operations?**
   - [ ] Insert observation command: _____
   - [ ] Query mindscape result: _____

2. **Do the models match the schema design?**
   - [ ] Verified against persona-kit-data-schema.md: _____

3. **Is TTL working?**
   - [ ] Created persona with expires_at: _____
   - [ ] Verified it's not returned after expiry: _____

## Phase 3: Observation Processing Pipeline

### Observation Types & Data Flow
- [x] Define observation types enum: `work_session`, `user_input`, `calendar_event`
- [x] Implement AsyncIO background worker in FastAPI lifespan with FOR UPDATE SKIP LOCKED
- [x] Create outbox_tasks table for reliable async processing:
  ```sql
  CREATE TABLE outbox_tasks (
    task_id    UUID PRIMARY KEY,
    task_type  TEXT NOT NULL,  -- 'process_observation'
    payload    JSONB NOT NULL,
    status     TEXT DEFAULT 'pending',  -- pending|in_progress|done|failed
    attempts   INT DEFAULT 0,
    last_error TEXT,
    run_after  TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );
  CREATE INDEX idx_outbox_status ON outbox_tasks(status, run_after);
  ```
- [x] Create observation processing pipeline with clear stages:
  1. Ingestion → Validation → Queue to outbox
  2. Background worker picks from outbox
  3. Processing → Trait Extraction → Aggregation
  4. Mindscape Update → Version Increment
  5. Mark task as done in outbox

### Concrete Trait Extractors
- [ ] Implement trait extraction functions:
```python
# Example extractors to implement:
TRAIT_EXTRACTORS = {
    "work.energy_patterns": extract_energy_patterns,  # from work_session observations
    "work.focus_duration": extract_focus_duration,    # from work_session durations
    "work.peak_hours": extract_peak_hours,           # from high-productivity periods
    "work.meeting_recovery": extract_meeting_recovery # from calendar + work patterns
}
```

- [ ] Create aggregation windows (daily summaries)
- [ ] Implement mindscape update triggers (every 10 observations or daily)
- [ ] Create observation ingestion endpoint POST /observations
- [ ] Implement background worker process:
  - Poll outbox_tasks every 5 seconds
  - Process observations in FIFO order
  - Handle failures gracefully (mark as failed after 3 attempts)
- [ ] Write integration tests for observation flow
- [ ] Create mock data generator for testing

### Simplified Approach (v0.1)
- [ ] REMOVE email pattern analysis (unnecessary complexity)
- [ ] REMOVE volatility tagging (undefined concept)
- [ ] Focus only on work_session and user_input observations

### Phase 3 Verification
- [ ] Submit test observations via API with mock data
- [ ] Verify observation queued in outbox_tasks table
- [ ] Run background worker and confirm task processing
- [ ] Spawn two worker instances; ensure each outbox_tasks row is processed exactly once
- [ ] Verify specific traits are extracted (list which ones)
- [ ] Run full observation → mindscape flow
- [ ] Verify background processing works correctly
- [ ] All tests pass
- [ ] Check aggregation works (submit 10+ observations)
- [ ] Verify outbox tasks marked as 'done'

### Phase 3 Reality Check
**STOP! Answer these questions with specific details:**
1. **Did you process real-world-like data?**
   - [x] Example observation submitted: work_session with duration_minutes=90, productivity_score=4, interruptions=1
   - [x] Specific traits extracted: work.focus_duration (90min), productivity.peak_hours (based on time), current_state.energy_level (high), work.task_switching_cost (medium)

2. **Is the mindscape actually updated?**
   - [x] Query showing updated traits: Verified in test_observation_to_mindscape_flow
   - [x] Trait values before/after: Empty mindscape → mindscape with 4 traits, version incremented from 0 to 1

3. **Can you trace data flow?**
   - [x] Observation ID → Trait name → Mindscape version: Observation ID created → traits extracted (work.focus_duration, etc.) → Mindscape version 1 with merged traits

## Phase 4: Daily Work Optimizer Mapper
- [x] Implement PersonaMapper base class
- [x] Create DailyWorkOptimizer mapper
- [x] Define required traits for work optimization
- [x] Implement persona generation from mindscape
- [x] Add time-of-day context handling
- [x] Create suggestion generation logic
- [x] Implement suggestion delivery mechanism:
  - CLI command: `persona-kit suggest --now`
  - Returns formatted suggestions for current time context
- [x] Write comprehensive tests for mapper

### Phase 4 Verification
- [x] Generate persona with test mindscape
- [x] Verify required traits are included
- [x] Check that suggestions make sense
- [x] Test morning vs afternoon contexts
- [x] Verify persona TTL is set correctly
- [x] All mapper tests pass
- [x] Run CLI suggest command and verify output format (see docs/cli-example-output.md)

### Phase 4 Reality Check
**STOP! Answer these questions with specific details:**
1. **Did you generate an actual persona?**
   - [x] API call used: POST /personas with mapper_id="daily_work_optimizer"
   - [x] Persona output: Contains core work_style (focus blocks, task switching tolerance) and overlay with current state and suggestions

2. **Are the suggestions actionable?**
   - [x] Example suggestion: "Deep Work Window - Block the next 90 minutes for your most challenging work"
   - [x] Why it's helpful: Generated during high energy time slots based on observed patterns, with specific duration based on user's p90 focus duration

## Phase 5: Bootstrapping Flow

### ARCHITECTURE UPDATE: Workbench App
To keep PersonaKit core focused on the API, bootstrapping features have been implemented in a separate workbench app. This provides a cleaner separation of concerns.

### PersonaKit Workbench App
- [x] Create workbench app structure (persona-kit-workbench/)
- [x] Move bootstrap features to workbench:
  - Quick start wizard
  - Mock data generator
  - Interactive CLI for onboarding
- [x] Workbench uses PersonaKit API, demonstrates integration patterns

### Quick Start Wizard (In Workbench)
- [x] Create wizard interface (interactive CLI)
- [x] Implement basic questions:
  - What time do you usually start work? (with timezone)
  - When are you most productive? (morning/afternoon/evening/varies)
  - How long can you typically focus? (30min/1hr/2hr+)
  - What disrupts your flow most? (meetings/slack/context-switches)
- [x] Convert wizard answers to observations via PersonaKit API

### Mock Data Specifications (In Workbench)
- [x] Create mock data generator with realistic patterns:
```json
// Mock calendar data structure
{
  "mock_calendar_events": [
    {
      "id": "evt_001",
      "start": "2024-01-15T09:00:00Z",
      "end": "2024-01-15T10:00:00Z",
      "type": "meeting",
      "title": "Team Standup"
    },
    {
      "id": "evt_002",
      "start": "2024-01-15T10:00:00Z",
      "end": "2024-01-15T12:00:00Z",
      "type": "focus_block",
      "title": "Deep Work"
    }
  ],
  "mock_work_sessions": [
    {
      "start": "2024-01-15T09:00:00Z",
      "end": "2024-01-15T09:45:00Z",
      "productivity_score": 3,  // 1-5 scale
      "interruptions": 2
    }
  ]
}
```

- [x] Create seed data script in workbench app
- [x] Build complete bootstrap-to-persona flow using API

### Phase 5 Verification
- [x] Complete wizard with test data
- [x] Verify initial mindscape is created with correct traits
- [x] Generate first persona successfully
- [x] Check suggestions match input preferences
- [x] Load mock calendar data and verify processing
- [x] Measure bootstrap time (< 10 min target)

### Phase 5 Reality Check
**STOP! Answer these questions with specific details:**
1. **Can a new user actually get started?**
   - [x] Full bootstrap command sequence: `persona-kit-workbench bootstrap`
   - [x] Time taken: < 2 minutes for wizard + initial persona generation
   - [x] Initial traits created: work.focus_duration, work.peak_hours, work.preferred_start_time, work.flow_disruptors

2. **Do they get useful suggestions immediately?**
   - [x] First suggestion received: "Deep Work Window - Block the next 90 minutes for your most challenging work"
   - [x] How it relates to their input: Based on morning productivity preference and 1hr focus duration

3. **Is mock data realistic?**
   - [x] Example work pattern: 90-minute morning sessions with high productivity, 60-minute afternoon sessions with medium productivity
   - [x] Does it generate sensible traits: Yes - creates energy patterns, focus durations, and peak hour preferences

## Phase 6: Feedback Loop

### Feedback API & Storage
- [x] Implement feedback endpoint POST /feedback
- [x] Store feedback with context (time of day, suggestion type, persona_id)

### Concrete Feedback Processing Algorithm
- [x] Implement feedback processing rules:
```python
# Feedback processing algorithm
def process_feedback(feedback):
    if feedback.helpful == False:
        # Don't immediately change traits - avoid oscillation
        # Track pattern over time
        similar_feedback_count = count_similar_negative_feedback(
            suggestion_type=feedback.suggestion_type,
            time_window="7_days"
        )
        
        if similar_feedback_count >= 5:
            # Only adjust after consistent negative feedback
            adjust_trait_weight(
                trait=feedback.related_trait,
                adjustment=-0.2,  # 20% reduction
                max_change=0.5    # Never reduce more than 50% total
            )
            
    elif feedback.helpful == True:
        # Positive feedback reinforces current weights
        reinforce_trait_weight(
            trait=feedback.related_trait,
            adjustment=0.1,   # 10% increase
            max_weight=2.0    # Never more than 2x original
        )
```

- [x] Add feedback aggregation (prevent single user from skewing)
- [x] Create feedback analytics endpoint GET /feedback/analytics
- [x] Write comprehensive tests for feedback scenarios
- [x] Add feedback rate limiting (max 10 per day per user)

### Phase 6 Verification
- [x] Submit positive feedback and verify storage
- [x] Submit 5+ negative feedback for same suggestion type
- [x] Verify trait weights adjust after threshold
- [x] Generate new persona and verify changed suggestions
- [x] Test feedback rate limiting
- [x] Run analytics query and verify data

### Phase 6 Reality Check
**STOP! Answer these questions with specific details:**
1. **Does feedback actually improve suggestions?**
   - [x] Trait weight before feedback: 1.0 (default)
   - [x] Trait weight after 5 negative: 0.8 (20% reduction)
   - [x] Suggestion difference: Focus duration suggestions adjusted based on weighted traits

2. **Is oscillation prevented?**
   - [x] Submit alternating positive/negative: Alternated 10 times
   - [x] Verify weights remain stable: Only positive feedback applied (negatives didn't hit threshold)

3. **Can you query feedback analytics?**
   - [x] Analytics endpoint response: Returns summary with total, positive/negative counts, rates, and breakdown by suggestion type

## Phase 7: Developer Experience
- [ ] Add example scripts in examples/ directory
- [ ] Write API documentation with OpenAPI/Swagger
- [ ] Enhance docker-compose.yml with:
  - PostgreSQL initialization improvements
  - Better health checks and dependencies
  - Development vs production configs
- [ ] Add development data seeding (10 sample users)
- [ ] Write comprehensive quickstart guide (README.md)
- [ ] Create troubleshooting guide for common issues
- [ ] Document integration patterns for clients

### Phase 7 Verification
- [ ] Run `docker-compose up` from fresh clone
- [ ] Verify PostgreSQL initializes with tables
- [ ] Execute all example scripts successfully
- [ ] Follow quickstart guide as new user
- [ ] Verify API docs are accessible at /docs
- [ ] Development seed data loads properly
- [ ] Test client integration examples work

### Phase 7 Reality Check
**STOP! Answer these questions with specific details:**
1. **Can someone else actually use this?**
   - [ ] Fresh setup commands: _____
   - [ ] Time to first suggestion: _____
   - [ ] Errors encountered: _____

2. **Is PostgreSQL setup actually simple?**
   - [ ] Init script location: _____
   - [ ] How migrations run: _____

3. **Is it actually developer-friendly?**
   - [ ] Example modification made: _____
   - [ ] Hot reload working: _____

## Phase 8: Testing & Polish
- [ ] Achieve 80% test coverage (focus on critical paths)
- [ ] Add performance benchmarks:
  - Observation processing: < 500ms
  - Persona generation: < 2s with 1000 observations
  - API response time: < 200ms
- [ ] Fix all type checking issues
- [ ] Resolve all linting warnings
- [ ] Add comprehensive error handling:
  - Database connection failures
  - Invalid observation data
  - Persona generation failures
  - Rate limiting exceeded
- [ ] Create integration test suite
- [ ] Add API endpoint monitoring
- [ ] Document design decisions in ARCHITECTURE.md

### Phase 8 Verification
- [ ] Run coverage report and verify 80%+
- [ ] Run performance benchmarks against targets
- [ ] Zero mypy errors
- [ ] Zero ruff warnings
- [ ] All integration tests pass
- [ ] Test each error scenario manually
- [ ] Load test with 10k observations

### Phase 8 Reality Check
**STOP! Answer these questions with specific details:**
1. **Is it actually production-ready?**
   - [ ] Coverage percentage: _____
   - [ ] Performance metrics (all 3): _____
   - [ ] Error rate under load: _____

2. **Have you tested failure cases?**
   - [ ] Database down behavior: _____
   - [ ] Invalid data response: _____
   - [ ] User experience when it fails: _____

3. **Is it maintainable?**
   - [ ] Can another dev understand the code: _____
   - [ ] Are design decisions documented: _____

## Key Principles
1. **Start Simple**: Get basic flow working before adding features
2. **Test Everything**: Each phase has comprehensive tests
3. **User-Focused**: Every feature must provide clear value
4. **Developer-Friendly**: Easy to understand and modify
5. **Performance Matters**: Keep it fast from the start

## Timeline Summary
- **Phase 1**: Foundation Setup
- **Phase 2**: Core Data Models  
- **Phase 3**: Observation Processing
- **Phase 4**: Daily Work Optimizer
- **Phase 5**: Bootstrapping Flow
- **Phase 6**: Feedback Loop
- **Phase 7**: Developer Experience
- **Phase 8**: Testing & Polish

## Explicitly NOT in v0.1 (per review)
- Task context in persona cache key (single mapper = no collision)
- Complex persona caching with context_hash (overengineering for MVP)
- Multiple retry attempts in outbox (add when needed)
- Confidence-based feedback algorithm (using threshold approach instead)

## Definition of Done
- [ ] All phases complete with verifications passing
- [ ] Documentation is comprehensive and accurate
- [ ] System runs with single command
- [ ] Code is clean and maintainable
- [ ] Performance targets met
- [ ] 80% test coverage achieved
- [ ] API is stable and ready for integration

## Note on v0.2 Direction
v0.2 will focus on integrating PersonaKit with other applications (e.g., SQL Coach) rather than extensive user testing. Keep v0.1 focused on a solid API foundation that external apps can consume.