# Execution Prompt Template

## Purpose
This template helps create specialized execution prompts for different types of artifact generation (code or documentation). The generated prompt will guide systematic creation through multi-stage work plans while maintaining quality, context, and progress across potentially interrupted sessions.

## How to Use This Template
1. Choose the artifact type: CODE or DOCUMENTATION
2. Fill in the [PLACEHOLDERS] with project-specific information
3. Select the appropriate verification examples for your artifact type
4. The result will be your project's execution prompt

---

# [PROJECT_NAME] Execution Prompt - MUST READ BEFORE PROCEEDING

## Critical Instructions for Claude

You are about to execute the work plan in @[WORK_PLAN_FILE]. To succeed, you MUST follow these strict guidelines:

### 1. Plan Adherence Protocol

**BEFORE STARTING ANY WORK:**
1. Read @[CONTEXT_FILE] to understand WHY we're doing this [ARTIFACT_TYPE]
2. Read the ENTIRE @[WORK_PLAN_FILE] file to understand WHAT we're doing
3. Identify which phase you're currently on
4. Read the CONTEXT CHECKPOINT section below to understand previous work
5. ONLY work on the current phase - do not jump ahead

**WHILE WORKING:**
1. Keep @[WORK_PLAN_FILE] open and reference it every 3-5 steps
2. For each task item:
   - Copy the exact task description before implementing
   - Implement ONLY what the task describes
   - Check off the item immediately after completion
   - Run the verification steps before moving to next item
3. **CHECKPOINT AFTER EACH TASK:**
   - After completing implementation: Update CONTEXT CHECKPOINT with what you implemented
   - After passing verification: Update CONTEXT CHECKPOINT with verification results
   - This creates a recoverable state after every successful step

**DEVIATION PROTOCOL:**
If you discover something that makes you want to deviate from the plan:
1. STOP immediately
2. Document the issue in the DEVIATION LOG section below
3. Ask the human: "I've encountered [issue]. Should I: A) Proceed as planned, B) Modify the plan, or C) Pause for discussion?"
4. Wait for human response before proceeding

### 2. Context Management Protocol

**AT THE START OF EACH SESSION:**
1. Read this entire prompt
2. Read @[CONTEXT_FILE] to refresh understanding of the problem
3. Read the CONTEXT CHECKPOINT section
4. Review completed phases in @[WORK_PLAN_FILE]
5. Identify exactly where you left off
6. State clearly: "I am resuming at Phase X, Task Y"

**BEFORE ENDING A SESSION:**
1. Update the CONTEXT CHECKPOINT section below
2. Mark all completed items in @[WORK_PLAN_FILE]
3. **CRITICAL: NEVER run git add or git commit commands**:
   - DO NOT run `git add` or `git commit` under any circumstances
   - DO NOT stage files or create commits automatically
   - Read-only git commands (status, diff, log, show) are allowed
   - ONLY prepare commit messages as text for human review
4. **Prepare commit message** (as text only, don't execute):
   - Create concise, neutral commit title (50 chars max)
   - Write multi-line description explaining what changed and why
   - Describe actual contents of the change, not test counts or outcomes
   - Avoid self-congratulatory or forward-looking statements
   - Never use emojis in commit messages
   - Don't mention stage/phase numbers (e.g., "Stage 2") - focus on what was actually implemented
   - Present the commit message to human for approval before they commit
5. Leave a note about what should be done next

### 3. Verification Enforcement

**YOU MUST NOT:**
- Skip verification steps
- Mark items complete without verification
- Proceed to next phase if ANY verification fails
- Assume tests pass without reading output
- Trust that linting is clean without running it
- Mark verifications done without doing them
- Claim completion of any task/phase/stage while tests are failing
- Say "Stage X is complete" when test output shows failures
- Run `git add` or `git commit` commands (read-only git commands are allowed)

**FOR EACH VERIFICATION:**
1. Run the EXACT command specified
2. READ the output carefully - don't just check exit code
3. If it says "print X" or "verify Y", actually DO that
4. Document the actual result in VERIFICATION LOG below
5. If it fails, fix the CODE (not the test) unless test is provably wrong
6. Only mark phase complete when ALL verifications show actual success
7. **CHECKPOINT AFTER VERIFICATION SUCCESS:**
   - Update CONTEXT CHECKPOINT immediately when verification passes
   - Include: Task completed, verification results, any learnings
   - This ensures progress is never lost if session ends

**CRITICAL: BE LITERAL ABOUT VERIFICATIONS**
- If it says "Run ruff and fix ALL issues" - run it repeatedly until 0 errors
- If it says "Print the message JSON" - actually print it and look at it
- If it says "Add intentional bug to confirm test works" - actually do this
- If it says "Manually verify output matches" - compare character by character
- These are not suggestions - they are requirements

**ABSOLUTE RULE: NEVER CLAIM COMPLETION WITH FAILING TESTS**
- You MUST NOT mark any task, phase, or stage as complete if ANY test is failing
- You MUST NOT proceed to the next phase if the current phase has test failures
- You MUST NOT claim "Stage X is complete" while tests show failures
- If tests fail, you MUST fix the underlying issue, not skip or ignore the test
- A failing test means the implementation is broken - fix the code, don't move on

**CRITICAL: COMPREHENSIVE VERIFICATION PROTOCOL**
For ANY verification (tests, linting, type checking, etc.), you MUST:

1. **Run Verifications Multiple Ways**
   - Run individually first (catches immediate errors)
   - Run again immediately (catches state pollution)
   - Run as part of full suite (catches interaction effects)
   - A verification isn't complete until it passes both individually AND as part of the full suite

2. **Never Trust Isolation**
   - What works alone may fail when run with others
   - What works in one order may fail in another
   - Race conditions and shared state issues only appear in full suite runs
   - If you claim "all tests pass", you must have run the ENTIRE suite, not just the tests you wrote

3. **Verify Clean State**
   - Run the full suite twice in a row
   - Second run proves proper cleanup and isolation
   - If second run fails, you have state pollution

4. **Reality Check Questions**
   - Each phase has a "Reality Check" section with specific questions
   - You MUST answer every question with concrete details
   - If you cannot provide specific commands and outputs, you haven't verified
   - Empty checkboxes mean incomplete work

**PROOF OF VERIFICATION REQUIRED**
You MUST NOT claim completion without showing actual verification output:
- Copy and paste the ACTUAL test output showing all tests passing
- Show the command you ran and its full output
- If you claim "all tests pass", show the output of running the full suite
- No exceptions: "seems to work" or "should pass" means NOT VERIFIED
- If tests are failing, you are NOT done - fix them or report the failures

**LOGIC IS NOT VERIFICATION**
The most dangerous trap: thinking "this code looks correct" and moving on:
- "The logic seems right" - NOT VERIFIED until you run it
- "This should work because..." - NOT VERIFIED until you see it work
- "The test looks correct" - NOT VERIFIED until it actually passes
- "I fixed the issue" - NOT VERIFIED until tests prove it
- Code can be perfectly logical and still fail due to typos, wrong assumptions, environment differences
- ALWAYS run the code, NEVER trust visual inspection alone

[ARTIFACT_TYPE: CODE]
**Code Verification Examples:**
- Run tests: `pytest tests/` or `pnpm test` (using Vitest)
- Check types: `mypy src/` or `tsc --noEmit`
- Lint code: `ruff check` or `pnpm run biome:check` (using Biome)
- Test functionality: Execute examples and verify output
- Check for regressions: Run integration tests
- Verify performance: Run benchmarks if provided

[ARTIFACT_TYPE: DOCUMENTATION]
**Documentation Verification Examples:**
- Read as [TARGET_PERSONA]: Does it make sense without prior knowledge?
- Test all code examples: Do they run without errors?
- Check cross-references: Do all links resolve?
- Verify completeness: Are all promised topics covered?
- Review flow: Does the narrative build logically?
- Check consistency: Are terms used uniformly?
- Code matches documentation: Do examples in docs work with actual code?
- API documentation accurate: Do described methods exist and work as documented?
- Tutorial progression: Can a user follow the tutorial with the current code?
- Conceptual alignment: Do code abstractions match documented concepts?

### 4. Communication Protocol

**ATTENTION ALERTS:**
When you need the human's attention (errors, completion, questions, verification failures):
- Use `osascript -e 'beep'` on macOS to make an audible alert
- This helps ensure important notifications aren't missed

**REGULAR UPDATES:**
Every 10-15 minutes, provide a status update:
- "Completed: [what you just did]"
- "Current: [what you're working on]"
- "Next: [what comes next in the plan]"
- "Blockers: [any issues encountered]"

**ASKING FOR HELP:**
If you're unsure about anything:
- DO ask for clarification
- DON'T make assumptions
- DON'T implement what you think might be right
- Use the beep command to get attention for important questions

### 5. Checkpoint Writing Protocol

**MANDATORY CHECKPOINT MOMENTS:**
1. **After Each Task Implementation** - Before running verification
   - What files were created/modified
   - Key decisions made during implementation
   - Any deviations from expected approach
   
2. **After Each Successful Verification** - Before moving to next task
   - Verification commands run and results
   - Performance metrics if measured
   - Confirmation that task is truly complete
   
3. **After Each Phase Reality Check** - Before moving to next phase
   - All Reality Check questions answered with specifics
   - Phase-level learnings and discoveries
   - Any technical debt or follow-up items identified

**CHECKPOINT FORMAT:**
```
**Task: [Task name from todo list]**
- Implementation: [What was actually built/changed]
- Files affected: [List of files created/modified]
- Verification: [Commands run and key results]
- Status: COMPLETE ✓
- Notes: [Any important discoveries or decisions]
```

**EXAMPLE CHECKPOINT:**
```
**Task: Create database schema and migrations**
- Implementation: Created PostgreSQL schema with 4 tables (observations, mindscapes, personas, feedback)
- Files affected: src/db/schema.sql, src/db/migrations/001_initial.sql
- Verification: 
  - Ran migrations: `docker-compose exec db psql -U postgres -d personakit < migrations/001_initial.sql`
  - Verified tables: All 4 tables created with correct columns and indexes
  - Tested JSONB: INSERT and SELECT on mindscapes.traits works correctly
- Status: COMPLETE ✓
- Notes: Added timezone support to all timestamp columns for consistency
```

---

## CONTEXT CHECKPOINT (Update this as you work)

**Last Updated:** [To be filled]
**Current Phase:** Phase 1 - [First phase name from work plan]
**Current Task:** Ready to start Phase 1
**Completed Phases:** None yet

**Key Decisions Made:**
- [To be updated as work progresses]

**Important Context:**
- [PROJECT_SPECIFIC_CONTEXT]
- See `[CONTEXT_FILE]` for full problem analysis and approach

**Next Steps:**
- Begin Phase 1 of `[WORK_PLAN_FILE]`

---

## DEVIATION LOG (Record any deviations from plan)

[No deviations yet]

---

## VERIFICATION LOG (Record all verification results)

### Phase 1 Verification ([Date])
- [ ] [To be filled with actual results]

---

## Implementation Notes (Add important discoveries here)

[No notes yet]

---

## REMINDER CHECKLIST (Read before EVERY work session)

- [ ] I have read this entire prompt
- [ ] I have read @[CONTEXT_FILE] to understand the problem
- [ ] I have read the CONTEXT CHECKPOINT
- [ ] I have identified my current position in @[WORK_PLAN_FILE]
- [ ] I understand I must follow the plan exactly
- [ ] I will ask for help if I need to deviate
- [ ] I will update this document before ending my session
- [ ] I will verify each phase before proceeding to the next

---

## THE GOLDEN RULE

**"The plan is the law. Deviations require permission. Verification is mandatory."**

When in doubt, stop and ask. It's better to pause for clarification than to implement the wrong thing and cause rework.

---

## AUTO-COMPACTION RECOVERY PROTOCOL

If you have been auto-compacted or are starting fresh:

1. **Read these files IN ORDER:**
   - @[CONTEXT_FILE] - Understand the problem and approach
   - @[WORK_PLAN_FILE] - See the full plan and what's been completed
   - @[THIS_EXECUTION_PROMPT_FILE] - Read this entire file

2. **Check the CONTEXT CHECKPOINT section above** - This is your primary memory

3. **Scan recent changes** to understand what was just done:
   [CODE]
   ```bash
   git log --oneline -10
   git diff HEAD~1
   ```
   [DOCUMENTATION]
   ```bash
   ls -la [OUTPUT_DIRECTORY]
   head -20 [RECENT_FILES]
   ```

4. **State your understanding:**
   "Based on the context files, I understand we are [current phase] because [evidence from files]. The last completed task was [task] and next is [task]."

5. **Ask for confirmation:**
   "Is this understanding correct? Should I proceed with [next task]?"

**IMPORTANT:** The CONTEXT CHECKPOINT section above is your persistent memory. Always update it before ending a session with:
- What you just completed
- Any decisions or discoveries
- Exact next task to tackle
- Any blocking issues

This way, even after auto-compaction, you can resume exactly where you left off.

---

## Template Placeholders Reference

**Required placeholders to fill:**
- `[PROJECT_NAME]` - The name of your project (human-readable with spaces)
- `[WORK_PLAN_FILE]` - Path from project root (e.g., "docs/impl-planning/workflow-inspector/workflow-inspector-todo.md")
- `[CONTEXT_FILE]` - Path from project root (e.g., "docs/impl-planning/workflow-inspector/workflow-inspector-context.md")
- `[ARTIFACT_TYPE]` - Choose: CODE or DOCUMENTATION
- `[TARGET_PERSONA]` - For docs: who is the intended reader?
- `[OUTPUT_DIRECTORY]` - Where artifacts are being created
- `[PROJECT_SPECIFIC_CONTEXT]` - 1-2 lines about the specific project
- `[THIS_EXECUTION_PROMPT_FILE]` - Path from project root (e.g., "docs/impl-planning/workflow-inspector/workflow-inspector-exec.md")
- `[RECENT_FILES]` - Pattern for recently created files

**Note**: When filling these placeholders, use paths relative to the project root and the @ symbol will be prepended automatically in the template.

**Artifact-specific sections:**
- Keep the verification examples that match your artifact type
- Remove the ones that don't apply
- Add project-specific verifications as needed
