# Work Plan Quality Guidelines

## Purpose
These guidelines ensure work plans are practical, testable, and resilient. Every work plan should be reviewed against these characteristics before execution.

## Essential Characteristics

### 0. Documentation-Driven Planning
Every work plan must start with a thorough review of existing documentation:

**Good Example:**
```markdown
## Related Documentation
- **Primary ADR**: @docs/adr/delegated_outputs.md - Core design decisions
- **Related ADRs**:
  - @docs/adr/operations_controller_adr.md - How operations are managed
  - @docs/adr/workflow_state_mutations.md - State change patterns
- **Schema Files**:
  - @domain/delegated_output_schema.json - Message format we must follow
  - @domain/workflow_definition_schema.json - How delegateTo field works
  - @domain/workflow_run_state_mutations_schema.json - Mutation log format
- **Dependencies Identified**:
  - Operation controller must detect delegateTo field
  - State manager must handle output bindings
  - Pub/sub system must support broadcast pattern
- **Potential Conflicts**: None identified
```

**Bad Example:**
```markdown
## Phase 1: Build the thing
- [ ] Read some docs maybe
- [ ] Start coding
```

**Key Points:**
- List all relevant ADRs and understand their decisions
- Identify all schemas that constrain your implementation
- Map dependencies on other components
- Check for conflicts with existing patterns
- Reference specific fields/sections that affect your work

### 1. Progressive Testing Strategy
Each phase must include appropriate testing that matches the scope:

**Good Example:**
```markdown
## Phase 2: Implement Core Logic
- [ ] Create business logic functions
- [ ] Write unit tests for pure functions (no dependencies)
- [ ] Create focused integration test for database layer only
- [ ] Verify: Unit tests pass in < 2 seconds
- [ ] Verify: Integration test works with in-memory database
```

**Bad Example:**
```markdown
## Phase 2: Implement Core Logic
- [ ] Create all the code
- [ ] Test everything
```

**Key Points:**
- Unit tests for pure logic (no external dependencies)
- Focused integration tests (one boundary at a time)
- Contract tests for interfaces
- Full end-to-end tests only when necessary
- Each test type has different setup requirements

### 2. Incremental Validation
Every phase must produce something demonstrable:

**Good Example:**
```markdown
## Phase 1: Create Message Queue Abstraction
- [ ] Define interface
- [ ] Implement in-memory version
- [ ] Create simple demo script
- [ ] Verify: Demo script shows messages being sent/received
```

**Key Points:**
- Not just "does it compile" but "can I see it work"
- Each phase has a mini-demo or verification script
- Stakeholders can see progress without full system setup

### 3. Dependency Minimization
Each phase should work with minimal setup:

**Good Example:**
```markdown
## Phase 2: Add Authentication
- [ ] Create auth module with interface
- [ ] Implement in-memory token store for development
- [ ] Add Redis token store for production
- [ ] Verify: Can run in development mode without external dependencies
```

**Bad Example:**
```markdown
## Phase 2: Add Authentication
- [ ] Install Redis, PostgreSQL, LDAP server
- [ ] Configure all services
- [ ] Implement authentication
```

**Key Points:**
- Development mode with zero infrastructure
- Production features added progressively
- Document exactly what's needed for each mode
- "Works on my machine" → "Works in clean environment"

### 4. Built-in Observability
Debugging support added during development, not after:

**Good Example:**
```markdown
## Phase 3: Implement Workflow Engine
- [ ] Add debug logging for state transitions
- [ ] Include trace IDs in all operations
- [ ] Create diagnostic endpoint (/debug/workflow/{id})
- [ ] Add meaningful error messages with context
- [ ] Verify: Can trace a request through logs
```

**Key Points:**
- Logging/tracing from the start
- Error messages that help diagnose issues
- Debug endpoints or tools
- Performance metrics where relevant

### 5. Context Preservation
Each phase preserves knowledge for future sessions:

**Good Example:**
```markdown
## Phase 4: Optimize Performance
- [ ] Document baseline metrics (current: 100 req/s)
- [ ] Apply optimization X
- [ ] Measure again, document results
- [ ] Update decision log with what worked/didn't work
```

**Key Points:**
- Document decisions and rationale
- Record metrics and measurements
- Update context documents as you learn
- Leave breadcrumbs for future work

### 6. Deep Verification (Not Fooling Yourself)
Verification must test actual behavior, not just surface appearances:

**Bad Example (Shallow Verification):**
```markdown
## Phase 3: Implement Workflow Engine
- [ ] Create workflow executor
- [ ] Write example workflow
- [ ] Verify: Script runs without crashing
- [ ] Verify: Output contains "Workflow started"
```

**Good Example (Deep Verification):**
```markdown
## Phase 3: Implement Workflow Engine
- [ ] Create workflow executor
- [ ] Write example workflow
- [ ] Create verification script that checks:
  - Workflow progresses through all expected states
  - Final state matches expected outcome
  - Side effects (files created, data saved) are correct
- [ ] Verify mock interfaces match real ones:
  - Run contract test between mock and real implementation
  - Ensure same method signatures and behavior
- [ ] Keep verification scripts in repo for future use
- [ ] Verify: Verification script shows all checks pass
```

**Real Failure Case:**
A recent refactoring passed all "verifications" but failed immediately when run because:
- Verification only checked for string output, not actual functionality
- Mock objects had different signatures than real implementations
- Verification scripts were deleted, hiding what was actually tested

**Key Points:**
- Test behavior and outcomes, not just execution
- Verify mocks match real implementations exactly
- Keep verification scripts as permanent test artifacts
- Include semantic checks (did it do the right thing?)
- Test failure cases (does it fail correctly?)
- Don't delete verification code - it's documentation

### 7. Reality Check Questions (Mandatory)
Each phase MUST include a "Reality Check" section that forces concrete verification:

**Example Reality Check Section:**
```markdown
### Phase 3 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**

1. **Did you ACTUALLY run the main code path?**
   - [ ] "I executed command: `pnpm orchestrator:start --workflow=test.json`"
   - [ ] "Output was: [paste actual output showing workflow execution]"

2. **Did you verify your database changes work?**
   - [ ] "I ran migration: `pnpm prisma migrate dev`"
   - [ ] "I queried table: `SELECT * FROM operation_executions` and saw: [results]"

3. **Did you check what actually happens at runtime?**
   - [ ] "Console output showed: [paste relevant logs]"
   - [ ] "No unexpected errors or warnings in logs"

4. **Show your work:**
   - [ ] Exact commands used: `[list them]`
   - [ ] Key output received: `[paste relevant parts]`
```

**Why This Works:**
- Forces implementers to run actual code, not just tests
- Requires pasting real output as proof
- Catches issues that tests miss (serialization, logging, integration)
- Creates accountability through specific evidence

## Review Checklist

Before finalizing any work plan, verify:

- [ ] **Documentation Review**: Have you reviewed all relevant ADRs and domain schemas?
- [ ] **Consistency Check**: Does the plan align with existing architectural decisions?
- [ ] **Schema Compliance**: Will implementations follow the defined schemas exactly?
- [ ] **Dependency Mapping**: Are all dependencies on other components identified?
- [ ] **Testing**: Does each phase have appropriate tests?
- [ ] **Demos**: Can progress be demonstrated after each phase?
- [ ] **Dependencies**: Can development start with minimal setup?
- [ ] **Debugging**: Will we be able to diagnose issues?
- [ ] **Context**: Will future sessions understand what was done?
- [ ] **Isolation**: Are phases independent enough to be interrupted?
- [ ] **Verification**: Are success criteria objective and measurable?
- [ ] **Deep Verification**: Do verifications test actual behavior, not just surface execution?
- [ ] **Mock Fidelity**: Do any mocks match real implementations exactly?
- [ ] **Reality Checks**: Does EVERY phase include a Reality Check section with specific questions?
- [ ] **Proof Requirements**: Do Reality Checks require pasting actual commands and outputs?
- [ ] **Integration Clarity**: Are integration points explicitly planned, not hand-waved?
- [ ] **Scope Sanity**: Can each phase be understood within a context window?
- [ ] **Design Protection**: Are critical design decisions documented to prevent corruption?

## Common Anti-patterns to Avoid

### Implementation Anti-patterns
1. **"Test everything at the end"** - Testing should be incremental
2. **"Requires full production setup"** - Development should be lightweight
3. **"We'll add logging later"** - Observability is harder to retrofit
4. **"Just follow the code"** - Document decisions and context
5. **"Big bang migration"** - Prefer incremental transitions
6. **"Trust me, it works"** - Provide objective verification
7. **"It printed success"** - Verify actual behavior, not just output
8. **"The mock is close enough"** - Ensure mocks match real interfaces exactly
9. **"Make the test pass"** - Never corrupt implementation to match flawed tests

### Planning Self-Deceptions (Common LLM Pitfalls)

**1. "It's Just Like X" Syndrome**
- Assuming similarity means equivalence
- Plan explicitly for differences, not just similarities
- Bad: "Copy auth from project Y and adapt"
- Good: "Study project Y auth, identify gaps, design for our constraints"

**2. Integration Hand-waving**
- Hiding complexity in "connect them together" tasks
- Bad: "Implement A, implement B, connect them"
- Good: "Define interface, test contract, implement A, verify contract, implement B"

**3. Context Window Illusion**
- Planning changes that require understanding too much at once
- Bad: "Refactor entire module and update all 47 callers"
- Good: "Create adapter interface, migrate 5 callers, verify pattern, then continue"

**4. Library Magic Thinking**
- Assuming libraries solve more than they do
- Bad: "Install WorkflowEngine library, configure it, done!"
- Good: "Evaluate library capabilities, identify gaps, plan custom code"

**5. Clean Slate Fantasy**
- Ignoring legacy constraints and existing users
- Bad: "Redesign API with beautiful REST endpoints"
- Good: "Survey existing clients, plan migration path, support both versions"

**6. Test Retrofitting Optimism**
- Assuming untestable code can be easily tested later
- Bad: "Build everything, then add tests in Phase 5"
- Good: "Design for testability, add tests with each component"

**7. Naming Confidence**
- Using buzzwords without understanding implications
- Bad: "Implement saga pattern and event sourcing"
- Good: "Research saga pattern trade-offs, prototype small example, then decide"

**8. Context Amnesia Corruption**
- Changing carefully designed code to make tests pass, forgetting why it was written that way
- This happens when an LLM writes tests after implementation, they fail, and instead of fixing the tests, it "fixes" the implementation
- Critical design decisions (ordering, error handling, distributed consistency) get destroyed

**Example of this disaster:**
```python
# Original (careful design for distributed consistency)
def process_mutations(self, mutations):
    # CRITICAL: Sort by transaction order for consistency
    sorted_mutations = self._sort_by_transaction_order(mutations)
    return self._apply_with_savepoints(sorted_mutations)

# Test expects different order, fails

# Corrupted "fix" to make test pass
def process_mutations(self, mutations):
    # Just apply in given order
    return [self._apply(m) for m in mutations]
```

**The cure:** When tests fail, first understand WHY the implementation works as it does. Document critical design decisions inline. Fix tests to match requirements, not implementation to match tests.

### How to Guard Against These

**Include Reality Check Phases:**
```markdown
## Phase 0: Validate Assumptions
- [ ] Research how existing system actually works
- [ ] Build minimal proof of concept
- [ ] Test with real dependencies
- [ ] Document what we learned
- [ ] Go/no-go decision
```

**Plan for Discovery:**
```markdown
## Phase 1: Understand Current State
- [ ] Document actual behavior (not assumed)
- [ ] Find all consumers/dependencies
- [ ] Identify hidden coupling
- [ ] Only then: Design new approach
```

**Add Integration Checkpoints:**
```markdown
## Phase 2: Component Integration
- [ ] Define explicit contracts
- [ ] Create contract tests
- [ ] Build component A against contract
- [ ] Verify contract independently
- [ ] Build component B against contract
- [ ] Only then: Connect with confidence
```

**Protect Critical Design Decisions:**
```markdown
## Phase 3: Implement State Management
- [ ] Document WHY: State mutations must be ordered for distributed consistency
- [ ] Implement with inline comments explaining critical invariants
- [ ] Write tests that verify requirements, not implementation details
- [ ] If tests fail, understand design before changing code
- [ ] Add "DO NOT CHANGE" comments on critical logic
```

## Design Principles for Developer-Friendly Architecture

### Why This Matters

Any future developer (human or LLM) working on your code needs to understand it quickly and modify it safely. LLMs in particular face unique challenges that highlight the importance of good design.

### Anti-Patterns That Hinder Understanding

Several coding anti-patterns can make it harder for an LLM to effectively understand, analyze, and modify a system. These often increase cognitive load and obscure the code's intent or structure:

**1. Lack of Clear Abstractions or Leaky Abstractions**

When low-level implementation details are not well-encapsulated or "leak" into higher-level logic, it's harder for an LLM to grasp the overall architecture and the purpose of different components. The LLM might get bogged down in details rather than understanding the "what" and "why."

Example: Business logic directly manipulating database connection objects or raw SQL strings instead of going through a data access layer.

**2. Inconsistent Naming and Conventions**

If functions, variables, classes, and modules are named inconsistently or obscurely, the LLM will struggle to infer their purpose and relationships.

Example: Using `process_data`, `handle_info`, and `manage_records` for similar operations in different parts of the codebase.

**3. Poor or Missing Documentation and Comments**

LLMs rely heavily on textual cues. A lack of comments explaining complex logic, non-obvious decisions, or the purpose of modules/functions forces the LLM to infer more, increasing the chance of misinterpretation.

Example: A complex algorithm with no comments explaining its steps or the rationale behind its design.

**4. Overly Complex Control Flow**

Deeply nested conditional statements (if/else if/else), complex loops with multiple exit points, or excessive use of flags to control flow make it difficult for an LLM (and humans) to trace execution paths and understand the state at any given point.

Example: A single function with 5 levels of nested if statements.

**5. Global State and Excessive Side Effects**

When functions modify global variables or have many non-obvious side effects, it's hard for an LLM to reason about the state of the system and the impact of a particular piece of code in isolation.

Example: Multiple functions reading from and writing to the same global dictionary without clear synchronization or ownership.

**6. Large, Monolithic Functions or Classes (God Objects/Methods)**

Functions or classes that do too many unrelated things violate the Single Responsibility Principle. This makes it hard for an LLM to understand the specific role of the component and increases the surface area for potential misunderstandings.

Example: A `UserManager` class that also handles payment processing and email notifications.

### Design Guidelines for Better Comprehension

**Good Example:**
```markdown
## Phase 3: Create Authentication Module
- [ ] Define IAuthProvider interface with clear contracts
- [ ] Implement InMemoryAuthProvider for testing
- [ ] Create consistent naming: authenticate_user, validate_token, refresh_session
- [ ] Document auth flow at top of auth_module.py
- [ ] Keep auth logic separate from user management
- [ ] Verify: Can understand auth module without reading other files
```

**Key Design Principles:**
1. **Bounded Contexts**: Each module has a clear, limited scope
2. **Consistent Patterns**: Same problems solved the same way throughout
3. **Explicit Dependencies**: All imports and dependencies at the top
4. **Local Documentation**: Purpose and contracts documented in each file
5. **Simple Control Flow**: Avoid deep nesting and complex state machines
6. **Pure Functions**: Minimize side effects and global state

## Integration with Work Plan Template

When using the work plan template, ensure:
1. Each phase incorporates relevant testing
2. Verification steps check these characteristics
3. The plan supports incremental development
4. Context preservation is built into the workflow
5. Design decisions support future comprehension

A well-designed work plan makes complex projects manageable, testable, and resilient to interruptions.
