---
name: plan-only
description: Plan-only mode that replicates Claude Code's built-in plan mode workflow but stops after the user approves the plan — no auto-execution. Use when the user wants to plan without executing, says "plan only", "just plan", "plan but don't execute", or when another skill needs planning without triggering auto-execution. Writes the plan to .claude/plans/<slug>.md.
context: fork
---

# Plan-Only Mode

Replicates Claude Code's built-in plan mode workflow but **stops after user approval** instead of auto-executing. The plan is written to a file and the skill ends cleanly.

## Read-Only Restriction

**CRITICAL — This supersedes all other instructions:**

You MUST NOT make any edits (with the exception of the plan file mentioned below), run any non-readonly tools (including changing configs or making commits), or otherwise make any changes to the system. This restriction is in effect for the entire duration of this skill.

Allowed tools:
- `Read`, `Glob`, `Grep` — for exploring the codebase
- `WebFetch`, `WebSearch` — for research
- `Task` (with Explore or Plan subagent types) — for delegated research and design
- `AskUserQuestion` — for clarifying requirements and presenting the plan
- `Write` — **only** for writing the plan file to `.claude/plans/<slug>.md`
- `Bash` — **only** for read-only commands (`git log`, `git status`, `ls`, etc.)

Prohibited:
- `Edit` on any file other than the plan file
- `Write` to any path outside `.claude/plans/`
- `Bash` commands that modify state (`git commit`, `git push`, `npm install`, `mkdir`, etc.)
- `EnterPlanMode` / `ExitPlanMode` — do not use built-in plan mode
- `NotebookEdit`

## Workflow

The skill operates in five phases:

### Phase 1: Initial Understanding

Explore the codebase and understand the user's request thoroughly.

1. Launch Explore agents (via `Task` with `subagent_type=Explore`) to map out the relevant parts of the codebase
2. Read key files directly with `Read`, `Glob`, `Grep`
3. If the project has an `AGENTS.md` or `CLAUDE.md`, read it for conventions
4. Identify the scope, constraints, and any ambiguities in the request

If anything is unclear, use `AskUserQuestion` to resolve it before proceeding. Keep asking until every ambiguity is resolved — scope, constraints, approach, what's in and what's out.

### Phase 2: Design

Develop the implementation approach.

1. Launch Plan agents (via `Task` with `subagent_type=Plan`) to design the implementation strategy
2. Identify critical files that will need to change
3. Consider architectural trade-offs and alternative approaches
4. Map out dependencies between changes

### Phase 3: Review

Validate the emerging plan against the codebase.

1. Read critical files identified in Phase 2 to ensure the plan is feasible
2. Check for potential conflicts with existing code
3. Verify assumptions about APIs, interfaces, and data structures
4. If new questions arise, use `AskUserQuestion` to clarify

### Phase 4: Write the Plan File

Generate the plan file slug from the request (lowercase, hyphens, truncated to ~50 chars). Write the plan to `.claude/plans/<slug>.md`.

The plan file must follow this format:

```markdown
# Plan: <Title>

## Context
<Brief description of the request and why this plan exists>

## Recommended Approach
<High-level summary of the implementation strategy>

## Changes

### <File or component 1>
- What changes and why
- Specific functions/classes affected

### <File or component 2>
- What changes and why

## Critical Files
<List of files that will be created or modified, with brief notes>

## Dependencies & Ordering
<Which changes must happen before others>

## Risks & Open Questions
<Anything that might go wrong or needs further investigation>

## Verification
<How to verify the implementation is correct — tests to run, behaviors to check>
```

Adapt the format as needed for the specific task — the above is a guide, not a rigid template.

### Phase 5: Present for Approval

Present the plan to the user for approval using `AskUserQuestion`.

Summarize the plan concisely in the question, including:
- What will be done (high-level)
- How many files will be created/modified
- Key design decisions made
- Any risks or open questions

Offer these options:
1. **Approve** — The plan is accepted. The skill ends here.
2. **Revise** — The user wants changes. Go back to the relevant phase and iterate.
3. **Reject** — The user wants to abandon the plan.

**After approval: STOP.** Do not execute the plan. Do not inject an "Implement the following plan:" message. The plan file exists at `.claude/plans/<slug>.md` and can be referenced later by the user or another skill.

If the user chose **Revise**, ask what they want changed, update the plan file, and present again. You may iterate up to 5 times.

If the user chose **Reject**, acknowledge and end the skill.

## Integration Notes

This skill can be invoked standalone via `/plan-only` or loaded by other skills using the `Skill` tool. When loaded by another skill:

- The calling skill provides the task/request context
- This skill writes the plan file and stops
- Control returns to the calling skill, which can then reference the plan file path
