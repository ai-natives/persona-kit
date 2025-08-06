# Work Plan Template

**Before using this template:**
1. Read `work-plan-quality-guidelines.md` for essential characteristics of well-designed work plans.
2. Review relevant ADRs in @docs/adr/ to understand architectural decisions
3. Review relevant schemas in @domain/ to understand data structures and constraints
4. Check for dependencies, omissions, or discrepancies between your plan and existing documentation

## Header Section
```markdown
# [Project Name] - Work Plan

## Goal
[1-2 sentences describing the end goal and why it matters]

## Key Outcomes
- [Outcome 1: Specific, measurable result]
- [Outcome 2: Specific, measurable result]
- [Outcome 3: Specific, measurable result]

## Success Criteria
- [ ] [Criterion 1: How we know we're done]
- [ ] [Criterion 2: Observable/testable outcome]
- [ ] [Criterion 3: User-facing benefit]

## Related Documentation
- **Primary ADR**: @docs/adr/[relevant-adr].md
- **Related ADRs**: [List any other relevant ADRs]
- **Schema Files**:
  - @domain/[schema1].json - [Why it's relevant]
  - @domain/[schema2].json - [Why it's relevant]
- **Dependencies Identified**: [Any dependencies found during review]
- **Potential Conflicts**: [Any conflicts with existing decisions]
```

## Phase Structure
```markdown
## Phase [Number]: [Descriptive Name]
- [ ] [Task 1: Specific, atomic action]
- [ ] [Task 2: Specific, atomic action]
- [ ] [Task 3: Specific, atomic action]
- [ ] [Task 4: Specific, atomic action]

### Phase [Number] Verification
- [ ] **Run linter on ALL changed files**
  - Fix ALL issues reported by linter before proceeding
  - Re-run linter to confirm zero issues
- [ ] **Run tests for this phase's functionality**
  - READ the actual test output, don't just check exit code
  - If any test fails, fix the code (not the test) unless test is wrong
  - Document what each failing test was checking before fixing
  - **ABSOLUTE REQUIREMENT: ALL TESTS MUST PASS - NO EXCEPTIONS**
  - **You CANNOT mark this phase complete while ANY test is failing**
- [ ] **Verify tests aren't fooling us**:
  - Open each test file and read what it's actually testing
  - Confirm tests check behavior, not just "doesn't crash"
  - Add a deliberate bug to code and confirm tests catch it
  - Remove the bug after confirming tests work
- [ ] **Check for missing test cases**:
  - List all error paths in the code - is each one tested?
  - List all edge cases (empty input, None, etc.) - are they tested?
  - If mock objects are used, do they match real interfaces exactly?
- [ ] **Manual verification of actual functionality**:
  - Run the actual feature/component (not just tests)
  - Verify it produces expected output/behavior
  - Try to break it with unexpected inputs

### Phase [Number] Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Before proceeding, answer these questions. If ANY answer is "No", you have more work to do:**

1. **Did you ACTUALLY run the main code path?**
   - [ ] "I executed the actual feature with real inputs and saw real outputs" (Not just tests!)
   - [ ] "I can paste the exact command I ran and its output here: _____"

2. **Did you verify your SQL/migrations work?**
   - [ ] "I ran every CREATE INDEX, ALTER TABLE, etc. against a real database"
   - [ ] "I queried the tables/indexes afterward to confirm they exist"

3. **Did you check what actually happens at runtime?**
   - [ ] "I examined the actual logs/console output during execution"
   - [ ] "I verified the system handles all data types and edge cases properly"

4. **Did you test the integration points?**
   - [ ] "I ran the full workflow from entry point to completion"
   - [ ] "I verified data flows correctly between components"

5. **Did you verify error paths?**
   - [ ] "I triggered actual errors and saw proper error messages"
   - [ ] "I confirmed the system fails gracefully, not with cryptic errors"

6. **Show your work:**
   - [ ] Key output that proves it works: _____
   - [ ] Commands used for manual testing: _____

**If you cannot fill in ALL these checkboxes with specific details, return to verification.**


```

## Phase Design Guidelines

### For Code Projects:
- Each phase should produce a working subset of functionality
- Tasks should be ordered by dependencies
- Include both implementation and test tasks
- Verifications should include:
  - Compilation/syntax checks
  - Unit test passage (use `pnpm test` with Vitest for TypeScript)
  - Linting checks (use `pnpm run biome:check` for TypeScript)
  - Integration verification
  - Performance benchmarks (if relevant)

**Note for TypeScript Projects**: We use pnpm (not npm), Vitest (not Jest), and Biome (not ESLint) for TypeScript development.

### For Documentation Projects:
- Each phase should produce a complete section/chapter
- Tasks should build on previous knowledge
- Include review and revision tasks
- Verifications should include:
  - Completeness checks
  - Accuracy verification
  - Readability assessment (target audience perspective)
  - Cross-reference consistency

### For Mixed Projects:
- Alternate between implementation and documentation phases
- Ensure artifacts stay synchronized
- Include cross-verification between code and docs
- Verifications should validate both technical correctness and explanation clarity

## Task Writing Guidelines

### Good Tasks:
- Start with action verb: "Create", "Extract", "Define", "Write", "Update"
- Have clear deliverable: file, function, section, diagram
- Are independently verifiable
- Take 5-30 minutes to complete

### Bad Tasks:
- Too vague: "Improve the system"
- Too large: "Rewrite the entire module"
- Not verifiable: "Think about the design"
- Dependencies unclear: "Fix the thing we discussed"

## Verification Writing Guidelines

### Good Verifications:
- Have binary pass/fail outcome
- Can be executed by someone unfamiliar with the project
- Test the actual requirement, not just existence
- Describe what to verify, not prescribe exact commands
- Force you to actually look at outputs, not just run commands

**Note on Commands**: Avoid prescribing specific commands (like `pytest tests/test_foo.py`) in work plans. Instead, describe the verification goal (like "Run tests for the foo module"). The implementing Claude should determine the appropriate commands for the actual project environment.

### Examples:
```markdown
# Code verification
- [ ] Run linter on changed modules and fix ALL issues until it shows 0 errors
- [ ] Run relevant tests and READ output to confirm what passed
- [ ] Open test file and verify it tests real behavior, not just "runs without error"
- [ ] Add intentional bug to verify tests catch failures
  - Example: change a return value or skip a critical step
  - Confirm appropriate test fails with meaningful error
  - Revert the bug after confirming test catches it
- [ ] Execute example/demo code and verify output matches expected behavior
- [ ] Try edge cases manually: empty input, None, very large input
- [ ] **Alert human if verification fails**: Use `osascript -e 'beep'` on macOS

# Documentation verification
- [ ] Copy each code example to a new file and run it - must work without modification
- [ ] Search for every cross-reference link (e.g., "see X") and verify target exists
- [ ] Have someone else (or fresh context) read it - can they follow without questions?
- [ ] **Alert human if verification fails**: Use `osascript -e 'beep'` on macOS
```

## Template Structure

```markdown
# [Project Name] - Work Plan

## Goal
[Clear statement of what we're building and why]

## Phase 1: [Foundation/Setup/Initial Structure]
- [ ] [Create directory structure]
- [ ] [Set up initial files]
- [ ] [Define core interfaces/outlines]
- [ ] [Create validation framework]

### Phase 1 Verification
- [ ] [All files created and accessible]
- [ ] [Structure follows conventions]
- [ ] [No circular dependencies]
- [ ] [Validation tools run successfully]

### Phase 1 Reality Check (MANDATORY BEFORE MARKING COMPLETE)
**STOP! Answer these questions with specific details:**
1. **Did you ACTUALLY run the code?**
   - [ ] Command used: _____
   - [ ] Key output observed: _____

## Phase 2: [Core Implementation/Content]
- [ ] [Implement primary functionality]
- [ ] [Write main content sections]
- [ ] [Create essential tests/examples]
- [ ] [Add error handling]

### Phase 2 Verification
- [ ] [Core features work as specified]
- [ ] [Content covers all required topics]
- [ ] [Tests provide adequate coverage]
- [ ] [Errors are handled gracefully]

## Phase 3: [Integration/Connections]
- [ ] [Connect components together]
- [ ] [Link related sections]
- [ ] [Add cross-cutting concerns]
- [ ] [Ensure consistency]

### Phase 3 Verification
- [ ] [End-to-end workflows function]
- [ ] [All references resolve correctly]
- [ ] [No orphaned components]
- [ ] [Consistent style throughout]

## Phase 4: [Polish/Optimization]
- [ ] [Optimize performance]
- [ ] [Improve clarity/readability]
- [ ] [Add helpful extras]
- [ ] [Final cleanup]

### Phase 4 Verification
- [ ] [Meets performance targets]
- [ ] [User feedback incorporated]
- [ ] [Documentation complete]
- [ ] [Ready for release]

## Key Principles
1. **Incremental Progress**: Each phase builds on the previous
2. **Verifiable Outcomes**: Every task has a clear completion criteria
3. **Dependency Awareness**: Tasks ordered by prerequisites
4. **Quality Gates**: Can't proceed until verifications pass
5. **Context Preservation**: Enough detail to resume after interruption
6. **TEST INTEGRITY**: No phase/stage/task is complete while tests fail

## Success Criteria
- [ ] [Primary goal achieved]
- [ ] [Quality standards met]
- [ ] [Stakeholder needs satisfied]
- [ ] [Maintenance path clear]
```

## Usage Notes

1. **Customize phases** based on project type and size
2. **Add more phases** for larger projects (typically 4-8 phases total)
3. **Time estimates** can be added to tasks if helpful
4. **Dependencies** between phases should be explicit

## Quality Review Process

After creating your work plan:
1. Review against the checklist in `work-plan-quality-guidelines.md`
2. Ensure each phase has:
   - Appropriate testing strategy
   - Demonstrable output
   - Minimal dependencies
   - Built-in observability
3. Revise the plan to address any gaps

## Remember

This template ensures work plans are:
- Compatible with the artifact generation protocol
- Clear enough to execute without additional context
- Verifiable at each step
- Recoverable after interruption
- Testable at appropriate levels
- Debuggable when things go wrong
