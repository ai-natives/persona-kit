# PersonaKit Explorer - Work Plan

## v0.1.1 Update: Narrative Support
PersonaKit v0.1.1 adds human narratives (self-observations and curations) with semantic search. The Explorer needs to support:
- Browsing and searching narratives
- Creating self-observations and curations through the UI
- Visualizing narrative → trait relationships
- Debugging narrative-enhanced persona generation
- Analyzing narrative influence on personas

## Goal
Build a comprehensive web-based explorer that enables developers, operators, and data scientists to explore PersonaKit's data structures, experiment with persona generation, and debug system behavior through visual interfaces.

## Key Outcomes
- Visual exploration interface for mindscapes, traits, observations, and narratives
- Interactive persona laboratory with context simulation and narrative influence
- Agent framework integration templates for LangChain, AutoGen, and CrewAI
- Real-time system monitoring and analytics dashboard with narrative insights
- Developer debugging tools with performance profiling and semantic search
- Narrative management interface for self-observations and curations

## Success Criteria
- [ ] Can browse any mindscape and understand trait relationships visually
- [ ] Can generate personas interactively without writing code
- [ ] Can export personas to agent frameworks in < 30 seconds
- [ ] System bottlenecks and errors are immediately visible
- [ ] Works with both mock data and real PersonaKit API
- [ ] Loads initial view in < 2 seconds
- [ ] **v0.1.1**: Can search narratives semantically and see their influence on personas
- [ ] **v0.1.1**: Can add self-observations and curations through the UI
- [ ] **v0.1.1**: Can debug narrative-enhanced rule conditions

## Related Documentation
- **Design Document**: @docs/persona-kit-explorer-design.md
- **PersonaKit API Spec**: @docs/persona-kit-v0.1-specification.md
- **Main Build Plan**: @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md
- **Dependencies Identified**:
  - Must integrate with PersonaKit API endpoints
  - Should not require modifications to core PersonaKit
  - Complements but doesn't overlap with Companion App (Phase 5)
- **Potential Conflicts**: None - explorer is a separate client application

## Phase 1: Foundation with Mock Integration (COMPLETE)
- [x] Create React/TypeScript project with Vite
- [x] Set up core dependencies (TanStack Query, Radix UI, Lucide icons)
- [x] Implement mock API service with realistic delays
- [x] Create comprehensive mock data (mindscape, observations, personas)
- [x] Build tab-based main navigation structure
- [x] Set up CSS architecture with consistent styling

### Phase 1 Verification
- [x] **Run the development server**
  - [x] Execute `pnpm run dev` and access http://localhost:5174
  - [x] All tabs render without console errors
- [x] **Verify mock data loads**
  - [x] Mindscape data appears in first tab
  - [x] Mock API delays simulate real network calls
- [x] **Check responsive layout**
  - [x] UI adapts to different screen sizes
  - [x] No horizontal scrolling on mobile widths

### Phase 1 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY run the explorer?**
   - [x] "I executed command: `cd tests/admin-tool && pnpm run dev`"
   - [x] "Browser opened showing PersonaKit Explorer with 4 tabs"

2. **Did you verify the mock API works?**
   - [x] "Network tab shows mock API calls with 150-600ms delays"
   - [x] "Mock mindscape has 6 traits including work.focus_duration"

3. **Show your work:**
   - [x] Dev server URL: http://localhost:5174
   - [x] Initial load shows: Mindscape v42 with trait browser

## Phase 2: Core Exploration Features (COMPLETE)
- [x] Implement MindscapeExplorer with hierarchical trait browser
- [x] Create trait timeline visualization component
- [x] Build PersonaLab with context simulation controls
- [x] Develop AgentPlayground with framework templates
- [x] Add observation history panel
- [x] Implement copy/download functionality for agent code

### Phase 2 Verification
- [x] **Test trait exploration**
  - [x] Click traits to see details and timeline
  - [x] Confidence badges show percentages
  - [x] Sample size indicators display correctly
- [x] **Verify persona generation**
  - [x] Change context controls and generate new persona
  - [x] Suggestions update based on context
- [x] **Test agent export**
  - [x] Switch between framework tabs
  - [x] Copy button puts code in clipboard
  - [x] Download creates .py file

### Phase 2 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY test persona generation?**
   - [x] "Changed time to 'afternoon' and energy to 'low'"
   - [x] "Generated persona showed different suggestions"

2. **Did you verify all three main features work?**
   - [x] "Mindscape Explorer: Clicked work.focus_duration, saw timeline"
   - [x] "Persona Lab: Generated 3 different personas"
   - [x] "Agent Playground: Exported to LangChain format"

3. **Show your work:**
   - [x] Timeline shows 4 data points from Jan 1-15
   - [x] LangChain export includes actual persona data

## Phase 3: Real API Integration with Narratives
- [ ] Add environment configuration (VITE_API_MODE=mock|real)
- [ ] Create real PersonaKit API client with proper error handling
- [ ] Implement API/mock toggle in UI header
- [ ] Add authentication support if required by API
- [ ] Create person selector for multi-profile support
- [ ] Handle loading states with skeletons/spinners
- [ ] **v0.1.1: Add narrative API endpoints**
  - [ ] Implement `/narratives/self-observation` client
  - [ ] Implement `/narratives/curate` client
  - [ ] Implement `/narratives/search` client with semantic query support

### Phase 3 Verification
- [ ] **Test with real PersonaKit API**
  - [ ] Start PersonaKit API on port 8042
  - [ ] Toggle to "real" mode in admin tool
  - [ ] Verify data loads from actual database
- [ ] **Test error scenarios**
  - [ ] Stop API and verify error handling
  - [ ] Test with invalid person ID
  - [ ] Verify timeout handling
- [ ] **Performance check**
  - [ ] Initial load < 2 seconds
  - [ ] Smooth transitions between views

### Phase 3 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY connect to the real API?**
   - [ ] "API running at: _____"
   - [ ] "Real mindscape version: _____"

2. **Did you test error handling?**
   - [ ] "Stopped API, saw error: _____"
   - [ ] "Recovery worked by: _____"

3. **Show your work:**
   - [ ] Network requests go to: _____
   - [ ] Response times: _____

## Phase 4: Observation & Narrative Management
- [ ] Create observation creation form with type selector
- [ ] Implement observation timeline with filtering
- [ ] Build bulk import for CSV/JSON files
- [ ] Add observation edit/delete functionality
- [ ] Show real-time trait recalculation preview
- [ ] Create observation templates for common patterns
- [ ] **v0.1.1: Add Narratives Tab**
  - [ ] Create narrative browser with timeline view
  - [ ] Add self-observation input form with rich text editor
  - [ ] Build curation interface for refining traits
  - [ ] Show narrative → trait extraction links
  - [ ] Implement semantic search interface
  - [ ] Display embedding similarity scores

### Phase 4 Verification
- [ ] **Test observation CRUD**
  - [ ] Create work_session observation
  - [ ] Edit observation content
  - [ ] Delete observation
- [ ] **Verify bulk import**
  - [ ] Import 50 observations from CSV
  - [ ] Check all observations appear in timeline
- [ ] **Test trait updates**
  - [ ] Create observation
  - [ ] Verify mindscape version increments
  - [ ] See trait changes highlighted
- [ ] **v0.1.1: Test narrative features**
  - [ ] Add self-observation and see it appear in timeline
  - [ ] Create curation to refine a trait
  - [ ] Search narratives with semantic query
  - [ ] Verify trait-narrative links display correctly

### Phase 4 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY create observations?**
   - [ ] "Created observation type: _____"
   - [ ] "Trait that changed: _____"

2. **Did bulk import work correctly?**
   - [ ] "Imported file: _____"
   - [ ] "Number of records: _____"

3. **v0.1.1: Did narratives work?**
   - [ ] "Self-observation added: _____"
   - [ ] "Semantic search query: _____"
   - [ ] "Similar narratives found: _____"

4. **Show your work:**
   - [ ] New mindscape version: _____
   - [ ] Trait value before/after: _____
   - [ ] Narrative → trait link example: _____

## Phase 5: Analytics Dashboard with Narrative Insights
- [ ] Create trait coverage heatmap component
- [ ] Build observation frequency chart (daily/weekly)
- [ ] Implement mapper success rate metrics
- [ ] Add system performance gauges (queue depth, processing time)
- [ ] Create error log viewer with filtering
- [ ] Build correlation matrix for trait relationships
- [ ] **v0.1.1: Add Narrative Analytics**
  - [ ] Create narrative frequency timeline
  - [ ] Build semantic cluster visualization
  - [ ] Show narrative → persona influence metrics
  - [ ] Display embedding similarity heatmap
  - [ ] Track curation activity over time
  - [ ] Analyze narrative sentiment patterns

### Phase 5 Verification
- [ ] **Test visualizations with data**
  - [ ] Heatmap shows trait population percentages
  - [ ] Frequency chart displays actual counts
  - [ ] Performance metrics update live
- [ ] **Verify error tracking**
  - [ ] Trigger errors and see in log
  - [ ] Filter by error type works
- [ ] **Check dashboard performance**
  - [ ] All charts render < 1 second
  - [ ] No lag with 1000+ data points
- [ ] **v0.1.1: Verify narrative analytics**
  - [ ] Semantic clusters group similar narratives
  - [ ] Influence metrics show which narratives affect personas
  - [ ] Embedding similarity makes sense for related content

### Phase 5 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you test with realistic data volumes?**
   - [ ] "Number of observations: _____"
   - [ ] "Chart render time: _____"

2. **Do the metrics make sense?**
   - [ ] "Trait coverage range: _____"
   - [ ] "Common error pattern: _____"

3. **Show your work:**
   - [ ] Screenshot of dashboard: _____
   - [ ] Key insight discovered: _____

## Phase 6: Developer Tools with Narrative Support
- [ ] Create API request builder with method/endpoint selector
- [ ] Implement response inspector with JSON highlighting
- [ ] Build mapper development kit with live preview
- [ ] Add trait calculation step-through debugger
- [ ] Create performance profiler for slow operations
- [ ] Implement scenario recorder/player for testing
- [ ] **v0.1.1: Add Narrative Development Tools**
  - [ ] Create narrative → trait extraction debugger
  - [ ] Build embedding visualization tool
  - [ ] Add semantic search query builder
  - [ ] Implement narrative rule condition tester
  - [ ] Create mapper configuration with narrative_check support
  - [ ] Build narrative performance profiler (embedding time, search latency)

### Phase 6 Verification
- [ ] **Test API request builder**
  - [ ] Build GET /mindscapes request
  - [ ] Execute and see formatted response
  - [ ] Save request as template
- [ ] **Verify mapper development**
  - [ ] Create custom mapper
  - [ ] Test with different mindscapes
  - [ ] See preview update live
- [ ] **Test performance profiler**
  - [ ] Profile persona generation
  - [ ] Identify slowest operation
  - [ ] Export performance report
- [ ] **v0.1.1: Test narrative tools**
  - [ ] Debug narrative → trait extraction flow
  - [ ] Test semantic search with different queries
  - [ ] Create mapper with narrative_check conditions
  - [ ] Profile embedding generation time

### Phase 6 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you build and execute real API requests?**
   - [ ] "Request sent: _____"
   - [ ] "Response status: _____"

2. **Did the mapper preview work?**
   - [ ] "Mapper tested: _____"
   - [ ] "Preview showed: _____"

3. **Show your work:**
   - [ ] Slowest operation found: _____
   - [ ] Time taken: _____

## Phase 7: Advanced Features
- [ ] Implement side-by-side persona comparison
- [ ] Create trait correlation matrix visualization
- [ ] Build feedback simulation with impact preview
- [ ] Add A/B testing framework for personas
- [ ] Implement comprehensive export system (JSON/CSV/PDF)
- [ ] Create annotation system for collaborative notes

### Phase 7 Verification
- [ ] **Test persona comparison**
  - [ ] Generate 2 personas with different contexts
  - [ ] Compare side-by-side
  - [ ] Highlight differences
- [ ] **Verify correlation analysis**
  - [ ] See trait relationships
  - [ ] Correlation values make sense
- [ ] **Test export functionality**
  - [ ] Export mindscape as JSON
  - [ ] Export analytics as CSV
  - [ ] Generate PDF report

### Phase 7 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did comparison reveal insights?**
   - [ ] "Key difference found: _____"
   - [ ] "Correlation discovered: _____"

2. **Did exports contain complete data?**
   - [ ] "JSON export size: _____"
   - [ ] "CSV row count: _____"

3. **Show your work:**
   - [ ] Strong correlation example: _____
   - [ ] Export file location: _____

## Phase 8: Polish & Production Readiness
- [ ] Add comprehensive error boundaries
- [ ] Implement keyboard shortcuts for common actions
- [ ] Create contextual help system with tooltips
- [ ] Optimize bundle size and lazy loading
- [ ] Add accessibility features (ARIA labels, keyboard nav)
- [ ] Write user guide and API documentation

### Phase 8 Verification
- [ ] **Test error recovery**
  - [ ] Trigger component error
  - [ ] Verify graceful degradation
  - [ ] Check error boundary message
- [ ] **Verify accessibility**
  - [ ] Navigate with keyboard only
  - [ ] Run axe accessibility audit
  - [ ] Test with screen reader
- [ ] **Performance audit**
  - [ ] Run Lighthouse audit
  - [ ] Bundle size < 500KB
  - [ ] First paint < 1 second

### Phase 8 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Is it actually production-ready?**
   - [ ] "Lighthouse score: _____"
   - [ ] "Bundle size: _____"

2. **Can users navigate without mouse?**
   - [ ] "Keyboard shortcuts tested: _____"
   - [ ] "Tab order correct: _____"

3. **Show your work:**
   - [ ] Accessibility score: _____
   - [ ] Performance metrics: _____

## Key Principles
1. **Progressive Enhancement**: Each phase adds value independently
2. **Mock-First Development**: Can develop without PersonaKit running
3. **Real Integration**: Seamlessly switches to real API
4. **Developer Focus**: Debugging and exploration over prettiness
5. **Performance Conscious**: Fast load times and smooth interactions

## Timeline Summary
- **Phase 1-2**: Foundation & Features (COMPLETE)
- **Phase 3**: Real API Integration with Narratives
- **Phase 4**: Observation & Narrative Management
- **Phase 5**: Analytics Dashboard with Narrative Insights
- **Phase 6**: Developer Tools
- **Phase 7**: Advanced Features
- **Phase 8**: Polish & Production