# Artifact Generation Meta-Prompt

## Purpose
This meta-prompt guides you through creating a complete artifact generation system for any substantial project. Use this when starting a new multi-phase project that requires systematic execution, context preservation, and resilience to interruptions.

---

## Instructions for Creating an Artifact Generation System

You are about to help create a systematic approach for building [describe what you're building]. This meta-prompt will guide you through creating all necessary artifacts for reliable, interruption-resilient execution.

### Step 1: Understand the Project

First, gather information about what needs to be built:

1. **Ask these questions:**
   - What is the main goal of this project?
   - What type of artifact(s) will be created? (code, documentation, or both)
   - Who is the target audience/user, or other subsystems that will need to integrate closely with what we build here?
   - Are there any existing materials to work with? (in particular, an ADR that you've already fine-tuned, would be ideal)

2. **Determine the artifact type:**
   - CODE: Software, scripts, configurations
   - DOCUMENTATION: Guides, references, explanations

### Step 2: Create Project Directory

Create a dedicated directory for the project's planning artifacts:

```bash
mkdir -p docs/impl-planning/[project-name]
cd docs/impl-planning/[project-name]
```

This keeps implementation plans organized and prevents clutter in the main impl-planning directory.

### Step 3: Create the Context Document

Based on the answers from Step 1, create `[project-name]-context.md` within the project directory:

```markdown
# [Project Name] Context

## Problem Statement
[What problem are we solving?]

## Goals
- [Primary goal]
- [Secondary goals]

## Non-Goals
- [What we're explicitly NOT doing]

## Target Audience
[Who will use/read this?]

## Success Criteria
- [How we know we've succeeded]
- [Measurable outcomes]

## Constraints
- [Technical constraints]
- [Time/resource constraints]
- [Compatibility requirements]

## Key Decisions
- [Important choices already made]
- [Rationale for those choices]
```

### Step 4: Create the Work Plan

Using the work plan template, create `[project-name]-todo.md` in the same project directory:

1. **Read the template:** `wiki/DELETE-ME-doc-fragments/work-plan-template.md`
2. **Read the quality guidelines:** `wiki/DELETE-ME-doc-fragments/work-plan-quality-guidelines.md`
3. **Structure the project into 4-8 phases**
4. **For each phase:**
   - 4-8 specific, actionable tasks
   - Clear verification criteria
   - Dependencies noted
   - Appropriate testing strategy
   - Rollback plan if needed

**Key principles:**
- Each phase should produce something usable
- Tasks should be 5-30 minutes each
- Verifications must be objective pass/fail

5. **Quality Review:** After drafting the plan, review it against the quality guidelines checklist
6. **Revise:** Update the plan to address any gaps found during review

### Step 5: Generate the Execution Prompt

Using the execution prompt template, create `[project-name]-exec.md` in the same project directory:

1. **Read the template:** `wiki/DELETE-ME-doc-fragments/execution-prompt-template.md`
2. **Fill in all placeholders:**
   - PROJECT_NAME (human-readable with spaces)
   - WORK_PLAN_FILE (path from project root, e.g., `docs/impl-planning/[project-name]/[project-name]-todo.md`)
   - CONTEXT_FILE (path from project root, e.g., `docs/impl-planning/[project-name]/[project-name]-context.md`)
   - THIS_EXECUTION_PROMPT_FILE (path from project root, e.g., `docs/impl-planning/[project-name]/[project-name]-exec.md`)
   - ARTIFACT_TYPE (CODE, DOCUMENTATION)
   - Other project-specific values
3. **Note on file paths**: The template uses `@[PLACEHOLDER]` notation. When you fill in the placeholder with a path, the @ will be prepended to create Claude's file reference (e.g., `@docs/impl-planning/project/file.md`)
4. **Customize verification examples** for your artifact type
5. **Remove sections** that don't apply

### Step 6: Prepare for Execution

Create the initial directory structure for the actual implementation:

```bash
# For code projects
mkdir -p src tests docs examples

# For documentation projects
mkdir -p wiki/[output-directory]
```

### Step 7: Begin Execution

Present the three documents to the executing Claude instance:

```
"I have a [artifact type] project to execute. Here are the guiding documents:

1. Context: [project-name]-context.md - explains why we're doing this
2. Work Plan: [project-name]-todo.md - the detailed plan to follow
3. Execution Prompt: [project-name]-exec.md - how to execute the plan

Please read all three documents in order, then follow the execution prompt exactly. Start by reading the Context document."
```

### Step 8: Maintain Progress

During execution:
- The CONTEXT CHECKPOINT in the execution prompt is the persistent memory
- Update it before ending each session
- Use it to recover from interruptions
- Check completed items in the work plan

## Quick Reference

**Directory structure:**
```
docs/impl-planning/
├── [project-name]/
│   ├── [project-name]-context.md    # Why we're doing this
│   ├── [project-name]-todo.md       # What we're doing (the plan)
│   └── [project-name]-exec.md       # How to do it
├── START-HERE-artifact-generation-meta-prompt.md
└── [templates and other docs...]
```

**Naming guidelines:**
- Use kebab-case for project names (e.g., `workflow-inspector`, `state-manager-docs`)
- Keep project names concise but descriptive
- Create a dedicated directory for each project's planning files
- If redoing a project, archive the old directory first

**Available templates and guides:**
- `wiki/DELETE-ME-doc-fragments/work-plan-template.md` - Structure for work plans
- `wiki/DELETE-ME-doc-fragments/work-plan-quality-guidelines.md` - Quality characteristics
- `wiki/DELETE-ME-doc-fragments/execution-prompt-template.md` - Execution prompt structure
- `wiki/DELETE-ME-doc-fragments/artifact-generation-workflow.md` - Overall workflow

## Remember

This systematic approach ensures:
- **Consistency**: Same process every time
- **Resilience**: Can recover from any interruption
- **Quality**: Verification at each step
- **Clarity**: Always know what's next
- **Memory**: Context preserved in files, not just in Claude's context window

The artifacts you create become the "peripheral brain" that augments the LLM's ephemeral memory, enabling complex multi-session projects to succeed reliably.

---

## Next Steps

1. Start with Step 1 above
2. Create the three documents
3. Begin systematic execution
4. Trust the process - it works!

When in doubt, refer back to this meta-prompt and the templates provided.
