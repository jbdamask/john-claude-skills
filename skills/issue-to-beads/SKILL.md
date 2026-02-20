---
name: issue-to-beads
description: Decomposes GitHub issues into structured Beads epics, tasks, and sub-tasks with objectively verifiable acceptance criteria. Use this skill whenever the user mentions converting GitHub issues to Beads, planning work from a GitHub issue, decomposing issues into tasks, breaking down a GitHub issue, or wants to take an issue and turn it into actionable Beads work items. Also trigger when the user says things like "plan this issue", "break down issue X", "convert this to beads", or references a GitHub issue URL and wants it turned into trackable work. Requires that the user's project uses Beads (bd) for issue tracking.
context: fork
---

# Issue-to-Beads

Converts a GitHub issue into a structured Beads work breakdown with epics, tasks, and sub-tasks - each with 3-5 objectively verifiable acceptance criteria. All beads must have relationships and dependecies mapped out.

## Prerequisites

- The user's project must have Beads initialized (`bd init` already run)
- The `bd` CLI must be available on PATH
- The `gh` CLI must be authenticated for the target GitHub repo
- The user should be in (or specify) the project directory containing `.beads/`
- The project should have an `AGENTS.md` file — read it first, as its acceptance criteria conventions and landing-the-plane workflow take precedence over this skill's defaults

## Workflow Overview

```
GitHub Issue → Fetch → Branch & Worktree → Interactive Planning (ask_user) → File Beads → Review & Refine (up to 5x) → Handoff
```

The skill operates in six phases:

1. **Fetch** — Pull the GitHub issue content and present a summary
2. **Branch** — Create a git branch and check out a worktree for the issue
3. **Plan** — Collaborate with the user to agree on the work breakdown
4. **File** — Create detailed Beads epics, tasks, sub-tasks, verifiable criteria, and beads relationships and dependencies
5. **Refine** — Review, proofread, polish, and iterate (up to 5 rounds)
6. **Handoff** — Show the tree, ready queue, and sync to git

## Phase 1: Fetch the GitHub Issue

Accept any of these input formats:
- Issue number: `#42` or `42`
- Full URL: `https://github.com/owner/repo/issues/42`
- Owner/repo + number: `myorg/myrepo#42`

Fetch the issue using `gh`:

```bash
gh issue view <number> --json title,body,labels,assignees,milestone,comments --repo <owner/repo>
```

If `--repo` is not specified, `gh` will use the current directory's git remote. If the fetch fails, ask the user for the correct repo.

Also fetch any linked issues or referenced PRs mentioned in the body to build context.

After fetching, present a brief summary to the user covering: the issue's goal, key requirements, constraints, and any open questions or ambiguities you noticed. This sets the stage for planning.

## Phase 2: Branch & Worktree

After fetching the issue, create a dedicated branch and worktree so all Beads work happens in isolation from the main branch.

### Branch Naming

Derive the branch name from the issue number and title:

```
<issue-number>-<slugified-title>
```

For example, issue #42 titled "Add user authentication" becomes `42-add-user-authentication`. Keep the slug short — truncate to ~50 characters if needed.

### Create Branch and Worktree

```bash
# Create the branch from the current HEAD
git branch <branch-name>

# Check out a worktree for the branch
git worktree add ../<branch-name> <branch-name>
```

The worktree is created as a sibling directory to the current repo. After creating it, **all subsequent work (planning, filing beads, syncing) must happen inside the worktree directory**.

If a branch or worktree with that name already exists, ask the user whether to reuse it or pick a different name.

## Phase 3: Interactive Planning

This is the most important phase. The goal is to reach full agreement on what work needs to happen **before any Beads issues are created**.

If the GitHub issue isn't clear or if you have any unresolved questions about requirements or approach, use the AskUserQuestion tool. Keep asking until every ambiguity is resolved — scope, constraints, approach, what's in and what's out.

Once you are satisfied that you have enough information, enter planning mode to develop a plan for execution. Only once you are confident that the plan is clear, comprehensive, and unambiguous should you move onto the next step.

### Step 2a: Propose the Work Breakdown

Present a draft work breakdown structured as:

```
Epic: [Title derived from issue]
  ├── Task 1: [Title]
  │   ├── Acceptance Criteria: [verifiable criteria]
  │   └── Blocked by: —
  ├── Task 2: [Title]
  │   ├── Acceptance Criteria: [verifiable criteria]
  │   └── Blocked by: Task 1
  └── Task 3: [Title]
      ├── Acceptance Criteria: [verifiable criteria]
      └── Blocked by: —  (can parallelize with Task 1)
```

Pay careful attention to:
- **Organization**: All tasks must belong to an Epic, which is effectively the top-level container for the GitHub issue. 
- **Dependencies**: Which tasks block which? Get this right — it determines what shows up in `bd ready`.
- **Parallelization**: Tasks that are independent of each other should have no blocking dependency between them, so multiple workers can pick them up simultaneously.
- **Granularity**: File a bead for any work that would take longer than about 2 minutes to finish. If something is trivially quick, it can be a bullet point inside a parent task's description rather than its own bead.
- **Detailed designs**: Each task description should give the implementing agent enough context to start working without needing to re-read the entire GitHub issue.

Solicit feedback on the breakdown:
- Are these the right tasks?
- Is the dependency ordering correct?
- Are any tasks missing?
- Should any tasks be split or merged?

### Step 2b: Refine Acceptance Criteria

Every task must have **acceptance criteria that are objectively verifiable** — meaning a different person (or an AI agent) could determine pass/fail without subjective judgment.

Follow the conventions from the project's `AGENTS.md`:

**Always include as the final criterion:**
- "Typecheck passes"

**For tasks with testable logic, also include:**
- "Tests pass"

**For tasks that change UI, also include:**
- "Verify in browser"

Good acceptance criteria examples:
- "Status column added to tasks table with default 'pending'"
- "Filter dropdown has options: All, Active, Completed"
- "Clicking delete shows confirmation dialog"
- "Running `npm test` produces 0 failures"
- "The endpoint `GET /api/users` returns HTTP 200 with a JSON array"
- "The file `src/auth/jwt.ts` exists and exports a `verifyToken` function"

Bad acceptance criteria (too vague — never use these):
- "Works correctly"
- "User can do X easily"
- "Good UX"
- "Handles edge cases"

If something is inherently subjective (like design quality), decompose it into measurable proxies:
- "The component renders without console errors"
- "Lighthouse accessibility score ≥ 90"
- "All text meets WCAG AA contrast ratio (4.5:1)"

Present the acceptance criteria to the user for approval.

### Step 2c: Final Confirmation

Show the complete plan one more time with all tasks, dependencies, priorities, and acceptance criteria. Ask the user to confirm before proceeding to filing.

## Phase 4: File Beads

Now grind through creating every issue in Beads. This is the execution-heavy phase — be thorough and methodical.

### Beads Hierarchy

Beads uses hierarchical IDs rooted on an epic:

```
bd-a3f8        Epic
bd-a3f8.1      Task (child of epic)
bd-a3f8.2      Task (child of epic)
bd-a3f8.2.1    Sub-task (child of task)
```

Use `--parent <id>` when creating to place items in the hierarchy. Beads auto-assigns the dotted ID.

| Plan Element | Beads Type | bd Flag |
|---|---|---|
| Top-level work item | `epic` | `-t epic` |
| Individual work unit (>2 min) | `task` | `-t task --parent <epic-id>` |
| Smaller piece within a task | `task` (sub-task) | `-t task --parent <task-id>` |
| Bug found during analysis | `bug` | `-t bug` |

### Priority Mapping

The following table is provided for completeness, only. All tasks created for GitHub issues are considered essential and, therefore, should be one of P0, P1, P2, P3. Do not use P4 as that priority level suggests the task is unnecessary.

| Priority | When to use |
|---|---|
| P0 | Blocking other teams or production |
| P1 | Core path — must be done for the issue to be considered complete |
| P2 | Important but not on the critical path |
| P3 | Nice-to-have, polish, optimization |
| P4 | Backlog / future consideration |

### Creation Order

1. Create the top-level epic first
2. Create tasks as children of the epic
3. Create sub-tasks as children of their respective tasks (if needed)
4. Add `blocks` dependencies between tasks
5. Add any `related` or `discovered-from` links

### Command Pattern

```bash
# 1. Create epic (returns an ID like bd-a3f8)
bd create "Epic Title" -t epic -p 1 \
  -d "Description including GitHub issue reference.

Acceptance Criteria:
- [Objective criterion 1]
- [Objective criterion 2]
- Typecheck passes" \
  --json

# 2. Create tasks under epic (auto-assigns bd-a3f8.1, bd-a3f8.2, etc.)
bd create "Task Title" -t task -p 1 \
  --parent <epic-id> \
  -d "Detailed description of what to implement and how.

Acceptance Criteria:
- [Objective criterion 1]
- [Objective criterion 2]
- Typecheck passes" \
  --json

# 3. Create sub-tasks under a task if needed (auto-assigns bd-a3f8.1.1, etc.)
bd create "Sub-task Title" -t task -p 1 \
  --parent <task-id> \
  -d "Focused piece of work within the parent task.

Acceptance Criteria:
- [Objective criterion 1]
- Typecheck passes" \
  --json

# 4. Add blocking dependencies
bd dep add <blocked-task-id> <blocker-task-id> --type blocks

# 5. Add discovered-from links (if applicable)
bd dep add <new-issue-id> <source-issue-id> --type discovered-from
```

### Description Format

Every Beads issue description must follow this structure:

```
[Detailed functional description of what needs to be done.
Include enough context that a worker agent can start implementing
without re-reading the full GitHub issue. Mention specific files,
functions, APIs, or patterns to use where relevant.]

Source: GitHub Issue <owner>/<repo>#<number>

Acceptance Criteria:
- [Objective criterion 1]
- [Objective criterion 2]
- Typecheck passes
```

### Dependency Best Practices

- Tasks that produce artifacts consumed by later tasks get `blocks` dependencies
- Tasks within the same phase that are independent get **no dependency** — this enables parallelization
- All child tasks get `parent-child` links to their epic automatically via `--parent`
- Use `discovered-from` for bugs or follow-up work found during analysis

## Phase 5: Review & Refine

This phase is critical for quality. After filing all the beads, step back and do a thorough review. The goal is to ensure that worker agents will have as smooth a time as possible when they pick up these tasks.

### Review Checklist

For each bead, check:
- **Clarity**: Could a worker agent understand what to do without asking questions?
- **Acceptance criteria**: Are they truly objectively verifiable? No vague language?
- **Standard criteria included**: Does every task end with "Typecheck passes"? Do testable tasks include "Tests pass"? Do UI tasks include "Verify in browser"?
- **Dependencies**: Are all blocking relationships correct? Are parallelizable tasks actually unblocked from each other?
- **Descriptions**: Do they include enough detail about files, functions, and approach?
- **Granularity**: Is every bead scoped to more than ~2 minutes of work? Are any too large and should be split?
- **Titles**: Are they clear and specific enough to understand at a glance in `bd ready` output?
- **Priorities**: Do they accurately reflect importance and critical path?

### Iteration Loop

After each review pass, make updates using `bd update`:

```bash
# Fix a description or acceptance criteria
bd update <id> -d "Improved description..." --json

# Fix priority
bd update <id> -p <new-priority> --json

# Add a missing dependency
bd dep add <blocked-id> <blocker-id> --type blocks

# Add a missing task discovered during review
bd create "Newly discovered task" -t task --parent <epic-id> -p 2 \
  -d "Description...

Acceptance Criteria:
- [criteria]
- Typecheck passes" --json
```

**Repeat this review-and-refine cycle up to 5 times.** Each pass should focus on progressively finer details:

1. **Pass 1**: Structural correctness — are the right tasks present with correct dependencies?
2. **Pass 2**: Description quality — are descriptions detailed enough for a cold-start worker?
3. **Pass 3**: Acceptance criteria rigor — are all criteria truly objective and verifiable?
4. **Pass 4**: Parallelization opportunities — can any blocking deps be removed to enable more concurrent work?
5. **Pass 5**: Final polish — titles, priorities, consistency, anything remaining

After each pass, briefly note what was changed. Stop early if a pass produces no meaningful improvements — say "I don't think we can do much better than this" and move on to handoff.

## Phase 6: Handoff

Once refinement is complete:

1. Run `bd dep tree <epic-id>` to show the user the full hierarchy
2. Run `bd ready --json` to show what's immediately actionable
3. Summarize what was created: epic count, task count, dependency count, how many tasks are parallelizable
4. Sync and push per the project's landing-the-plane workflow:

```bash
git pull --rebase
bd sync
git push
git status  # MUST show "up to date with origin"
```

Work is NOT complete until `git push` succeeds. Never stop before pushing — that leaves work stranded locally.

## Edge Cases

- **Tiny issues** (single task, no decomposition needed): Skip the epic, create one task directly. Still include acceptance criteria with "Typecheck passes" as the final criterion.
- **Enormous issues** (20+ tasks): Suggest breaking the GitHub issue into multiple Beads epics, each with its own task hierarchy. Ask the user how they'd like to group them.
- **Vague issues** (missing requirements): Use Phase 2 aggressively to fill gaps. Create "Research" or "Spike" tasks for unknowns with acceptance criteria like "A decision document exists at `docs/decisions/001-auth-approach.md` with Status, Context, Decision, and Consequences sections."
- **Issues with existing Beads work**: Run `bd list --json` to check for duplicates before creating. Alert the user if overlap is found.

## Reference

For detailed Beads CLI syntax and advanced patterns, read `references/beads-cli-reference.md`.
