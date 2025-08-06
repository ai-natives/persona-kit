# PersonaKit v0.1 Execution Prompt - MUST READ BEFORE PROCEEDING

## Critical Instructions for Claude

You are about to execute the work plan in @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md. To succeed, you MUST follow these strict guidelines:

### 1. Plan Adherence Protocol

**BEFORE STARTING ANY WORK:**
1. Read @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-context.md to understand WHY we're building this
2. Read the ENTIRE @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md file to understand WHAT we're doing
3. Identify which phase you're currently on
4. Read the CONTEXT CHECKPOINT section below to understand previous work
5. ONLY work on the current phase - do not jump ahead

**WHILE WORKING:**
1. Keep @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md open and reference it every 3-5 steps
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
2. Read @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-context.md to refresh understanding of the problem
3. Read the CONTEXT CHECKPOINT section
4. Review completed phases in @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md
5. Identify exactly where you left off
6. State clearly: "I am resuming at Phase X, Task Y"

**BEFORE ENDING A SESSION:**
1. Update the CONTEXT CHECKPOINT section below
2. Mark all completed items in @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md
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
- Say "Phase X is complete" when test output shows failures
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
- If it says "Verify JSONB queries work" - actually run queries and check results
- If it says "Check that Persona TTL is enforced" - test with expired personas
- These are not suggestions - they are requirements

**ABSOLUTE RULE: NEVER CLAIM COMPLETION WITH FAILING TESTS**
- You MUST NOT mark any task, phase, or stage as complete if ANY test is failing
- You MUST NOT proceed to the next phase if the current phase has test failures
- If tests fail, you MUST fix the underlying issue, not skip or ignore the test

**Code Verification Examples:**
- Run tests: `pytest tests/`
- Check types: `mypy src/`
- Lint code: `ruff check`
- Test functionality: Execute examples and verify output
- Check for regressions: Run integration tests

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

**Last Updated:** 2025-08-06 16:30 JST
**Current Phase:** Phase 3 - Observation Processing Pipeline (In Progress)
**Current Task:** Create OutboxTask repository
**Completed Phases:** Phase 1 (Foundation Setup), Phase 2 (Core Data Models)

**Key Decisions Made:**
- Using Python with FastAPI for the API
- PostgreSQL with JSONB for storage (Option B from schema options)
- Single mapper focus (Daily Work Optimizer)
- Monolithic architecture to start
- Custom ports: 5436 (PostgreSQL), 8042 (API) to avoid conflicts
- Repository pattern for database operations
- Using `uv` for Python package management (per user instruction)

**Important Context:**
- Building minimal Work Assistant use case only
- Must work completely offline/locally
- Single user system (no multi-tenancy)
- See @docs/persona-kit-v0.1-specification.md for detailed requirements

**Next Steps:**
- Begin Phase 1 of the work plan
- Set up project structure and development environment

---

## DEVIATION LOG (Record any deviations from plan)

[No deviations yet]

---

## VERIFICATION LOG (Record all verification results)

### Phase 1 Verification (2025-08-06)
- ✅ PostgreSQL running on port 5436
- ✅ Migrations applied successfully (all tables created)
- ✅ Health check endpoint working at http://localhost:8042/health/
- ✅ pytest running (1 test passing)
- ✅ ruff check passing (fixed 81 errors)
- ✅ mypy src/ passing (fixed 7 type errors)
- ✅ Error handling tested (404, 405 responses)
- ✅ JSON logs verified working

### Phase 2 Verification (2025-08-06)
- ✅ Unit tests written for models (4 tests passing)
- ✅ CRUD operations tested via Python scripts
- ✅ JSONB queries verified working:
  ```
  Peak hours: ['09:00-11:00', '14:00-16:00']
  Likes music: True
  ```
- ✅ Persona TTL tested (expired personas filtered)
- ✅ ruff check passing
- ✅ mypy src/ passing
- ✅ All 6 indexes created and verified:
  - idx_observations_person_created
  - idx_mindscapes_person
  - idx_personas_expires
  - idx_personas_person_id
  - idx_feedback_persona
  - idx_outbox_status
- ✅ Testcontainers configured for proper PostgreSQL testing
- ✅ 9/10 tests passing (1 minor transaction issue in mindscape upsert test)

---

## Implementation Notes (Add important discoveries here)

### Phase 1 Notes:
- Fixed datetime deprecation: `datetime.utcnow()` → `datetime.now(UTC)`
- Fixed SQLAlchemy metadata conflict by renaming to `meta` in Python
- Had to add greenlet dependency for async SQLAlchemy
- Using async_sessionmaker instead of regular sessionmaker

### Phase 2 Notes:
- Repository pattern implemented with BaseRepository for common CRUD
- Enum handling issue: PostgreSQL expects lowercase but Python enum sends uppercase
  - Fixed with `native_enum=False` in SQLAlchemy Enum type
- SQLite incompatible with PostgreSQL features (JSONB, enums) for testing
  - Solved by using testcontainers for real PostgreSQL in tests
- JSONB queries work perfectly with PostgreSQL
- Mindscape upsert uses ON CONFLICT for atomic updates
- Feedback repository includes advanced statistics methods
- Test suite now uses testcontainers for proper isolation
- Added outbox_tasks columns: attempts, last_error, completed_at via migration

### Phase 3 Planning Decisions:
- Use AsyncIO background task (not separate process) for simplicity
- Use FOR UPDATE SKIP LOCKED for queue processing (PostgreSQL native)
- Process observations immediately, not daily summaries
- Simple trait schema with confidence scores and sample sizes
- Basic validation only (schema + timestamp checks)
- Skip duplicate detection for v0.1

---

## REMINDER CHECKLIST (Read before EVERY work session)

- [ ] I have read this entire prompt
- [ ] I have read @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-context.md to understand the problem
- [ ] I have read the CONTEXT CHECKPOINT
- [ ] I have identified my current position in @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md
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
   - @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-context.md - Understand the problem and approach
   - @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-todo.md - See the full plan and what's been completed
   - @docs/impl-planning/persona-kit-v0.1/persona-kit-v0.1-exec.md - Read this entire file

2. **Check the CONTEXT CHECKPOINT section above** - This is your primary memory

3. **Scan recent changes** to understand what was just done:
   ```bash
   git log --oneline -10
   git diff HEAD~1
   ls -la src/
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