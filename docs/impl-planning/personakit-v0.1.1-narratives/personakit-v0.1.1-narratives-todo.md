# PersonaKit v0.1.1 Narratives - Work Plan

## Goal
Extend PersonaKit's configuration-driven architecture with human narrative support, enabling semantic search and richer persona generation while maintaining the performance and simplicity of the trait system.

## Key Outcomes
- Narratives (self-observations and curations) stored with embeddings for semantic search
- Rule engine can evaluate narrative-based conditions
- Personas include narrative context in suggestions
- Workbench provides direct narrative input capabilities
- Explorer shows narrative influence on personas

## Success Criteria
- [ ] Narratives can be created, searched, and linked to traits
- [ ] Persona generation with narratives remains under 2 seconds
- [ ] Semantic search returns relevant narratives with >85% precision
- [ ] All narrative collection is user-initiated (no push notifications)
- [ ] Backward compatibility maintained for trait-only mappers

## Related Documentation
- **Primary Reference**: @docs/persona-kit-v0.1.1-unified-plan.md
- **Architecture Plan**: @docs/architecture/narrative-enhancement-plan.md
- **Current System**: @docs/persona-kit-v0.1-specification.md
- **Dependencies Identified**:
  - PostgreSQL with pgvector extension required
  - OpenAI API for embeddings (text-embedding-3-large)
  - Existing rule engine needs narrative condition support
  - Persona generator needs narrative context handling
- **Potential Conflicts**: None - narratives complement existing traits

## Phase 1: Database & Core Models
- [ ] Enable pgvector extension in PostgreSQL
- [ ] Create narratives table with embedding column
- [ ] Create trait_narrative_links table
- [ ] Create Narrative SQLAlchemy model
- [ ] Create Pydantic schemas for API requests/responses
- [ ] Add database migration scripts

### Phase 1 Verification
- [ ] **Run database migrations**
  - Execute migrations against test database
  - Verify tables created with correct columns and indexes
- [ ] **Test vector operations**
  - Insert sample narrative with embedding
  - Perform similarity search query
  - Verify HNSW index is used (check query plan)
- [ ] **Verify models**
  - Create Narrative instance and save to database
  - Query back and verify all fields preserved
  - Test JSONB fields for tags and context

### Phase 1 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY run the migrations?**
   - [ ] "I executed command: _____"
   - [ ] "Tables created: narratives, trait_narrative_links"

2. **Did you verify pgvector works?**
   - [ ] "I ran similarity search: _____"
   - [ ] "Query plan shows index usage: _____"

3. **Show your work:**
   - [ ] Sample embedding stored: [first 5 dimensions]
   - [ ] Similarity search returned: _____

## Phase 2: Embedding Service & API
- [ ] Create EmbeddingService class with OpenAI client
- [ ] Implement embed_text and embed_batch methods
- [ ] Create NarrativeService with CRUD operations
- [ ] Implement semantic_search method
- [ ] Add narrative API endpoints (self-observation, curate, search)
- [ ] Add request/response validation

### Phase 2 Verification
- [ ] **Test embedding generation**
  - Generate embedding for test text
  - Verify dimension is 1536
  - Measure latency (should be <200ms)
- [ ] **Test API endpoints**
  - Create self-observation via API
  - Create curation via API
  - Search narratives semantically
- [ ] **Verify service integration**
  - Check embeddings are stored correctly
  - Verify tags are extracted
  - Test error handling for OpenAI failures

### Phase 2 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY call the OpenAI API?**
   - [ ] "API key configured: [first 8 chars]"
   - [ ] "Embedding response received for text: _____"

2. **Did you test the full API flow?**
   - [ ] "Created narrative with ID: _____"
   - [ ] "Semantic search for 'morning productivity' returned: _____"

3. **Show your work:**
   - [ ] API endpoint tested: POST /narratives/self-observation
   - [ ] Response time: _____ms

## Phase 3: Rule Engine Integration
- [ ] Add narrative_check condition type to rule engine
- [ ] Implement _evaluate_narrative_check method
- [ ] Add narrative prefetching for performance
- [ ] Update suggestion generation to include narrative context
- [ ] Create example narrative-aware mapper configuration
- [ ] Add narrative context to suggestion output

### Phase 3 Verification
- [ ] **Test narrative conditions**
  - Create rule with narrative_check
  - Add matching narrative to database
  - Verify rule evaluates to true
- [ ] **Test semantic matching**
  - Use different phrasings for same concept
  - Verify similarity threshold works
  - Test negative cases (no match)
- [ ] **Performance check**
  - Measure rule evaluation time with narratives
  - Verify caching/prefetching works
  - Ensure <500ms for complex rules

### Phase 3 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY evaluate narrative rules?**
   - [ ] "Rule with semantic query: _____"
   - [ ] "Matched narrative text: _____"

2. **Did you verify the integration?**
   - [ ] "Mapper config used: _____"
   - [ ] "Suggestion included narrative excerpt: _____"

3. **Show your work:**
   - [ ] Similarity score for match: _____
   - [ ] Total evaluation time: _____ms

## Phase 4: Persona Generation Updates
- [ ] Update PersonaGenerator to accept person_id
- [ ] Add narrative fetching based on mapper config
- [ ] Track narrative usage in persona generation
- [ ] Store narrative_usage relationships
- [ ] Update PersonaResponse to include narrative context
- [ ] Add backwards compatibility for non-narrative mappers

### Phase 4 Verification
- [ ] **Test narrative-aware generation**
  - Generate persona with narrative-enabled mapper
  - Verify narratives are fetched
  - Check narrative context in output
- [ ] **Test backwards compatibility**
  - Use original daily_work_optimizer mapper
  - Verify it still works without narratives
  - Check performance unchanged
- [ ] **Verify tracking**
  - Check persona_narrative_usage recorded
  - Verify relevance scores stored
  - Test narrative influence tracing

### Phase 4 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you generate a real persona with narratives?**
   - [ ] "Persona ID generated: _____"
   - [ ] "Narratives used: [list IDs]"

2. **Did you verify the output?**
   - [ ] "Suggestion contained narrative: _____"
   - [ ] "Backward compatibility tested with mapper: _____"

3. **Show your work:**
   - [ ] Total generation time: _____ms
   - [ ] Narrative influence visible in: _____

## Phase 5: Workbench Integration
- [ ] Add narrative commands to CLI
- [ ] Implement add_observation command
- [ ] Implement curate_trait command
- [ ] Implement list_narratives command
- [ ] Update bootstrap wizard to collect narratives
- [ ] Add narrative prompts to mock data generator

### Phase 5 Verification
- [ ] **Test CLI commands**
  - Add observation via workbench
  - Curate a trait with correction
  - List recent narratives
- [ ] **Test bootstrap integration**
  - Run bootstrap wizard
  - Verify it collects narrative responses
  - Check narratives stored with embeddings
- [ ] **Test mock data**
  - Generate mock narratives
  - Verify realistic content
  - Check embeddings generated

### Phase 5 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY use the workbench?**
   - [ ] "Command executed: persona-kit-workbench add-observation '...'"
   - [ ] "Narrative created with ID: _____"

2. **Did bootstrap collect narratives?**
   - [ ] "Wizard prompt shown: _____"
   - [ ] "User response stored as: _____"

3. **Show your work:**
   - [ ] Number of mock narratives generated: _____
   - [ ] Sample narrative text: _____

## Phase 6: Explorer Integration
- [ ] Add Narratives tab to Explorer UI
- [ ] Implement narrative timeline component
- [ ] Add semantic search interface
- [ ] Create narrative-trait relationship viewer
- [ ] Add narrative influence tracing
- [ ] Implement curation interface

### Phase 6 Verification
- [ ] **Test UI components**
  - View narratives in timeline
  - Search narratives semantically
  - See trait-narrative links
- [ ] **Test influence tracing**
  - Generate persona
  - View which narratives influenced it
  - Check relevance scores displayed
- [ ] **Test curation flow**
  - Select trait to curate
  - Add curation note
  - Verify curation stored

### Phase 6 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY run the Explorer?**
   - [ ] "Explorer URL: http://localhost:5174"
   - [ ] "Narratives tab shows: _____ entries"

2. **Did you test the full flow?**
   - [ ] "Searched for: _____"
   - [ ] "Results included: _____"

3. **Show your work:**
   - [ ] Screenshot location: _____
   - [ ] Curation created for trait: _____

## Phase 7: Performance & Testing
- [ ] Create comprehensive test suite for narratives
- [ ] Add performance benchmarks
- [ ] Optimize database queries
- [ ] Add caching for embeddings
- [ ] Create integration tests
- [ ] Write documentation

### Phase 7 Verification
- [ ] **Run all tests**
  - Unit tests for services
  - Integration tests for API
  - End-to-end persona generation
- [ ] **Performance benchmarks**
  - Narrative creation: <200ms
  - Semantic search: <500ms
  - Persona generation: <2s
- [ ] **Load testing**
  - Test with 10k narratives
  - Verify search still performant
  - Check index usage

### Phase 7 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you run actual benchmarks?**
   - [ ] "Benchmark command: _____"
   - [ ] "Results: creation=___ms, search=___ms, generation=___ms"

2. **Did you test at scale?**
   - [ ] "Number of narratives in test: _____"
   - [ ] "Search performance at scale: _____ms"

3. **Show your work:**
   - [ ] Test coverage: _____%
   - [ ] Slowest operation: _____

## Key Principles
1. **Incremental Progress**: Each phase adds usable functionality
2. **Performance Focus**: Monitor latency at each step
3. **User Control**: All narrative input is user-initiated
4. **Backward Compatibility**: Existing mappers continue to work
5. **Semantic Power**: Leverage embeddings for rich search

## Success Metrics
- [ ] All narrative types implemented and tested
- [ ] Performance targets met (<2s generation)
- [ ] Explorer and Workbench fully integrated
- [ ] Documentation complete
- [ ] No breaking changes to v0.1 functionality