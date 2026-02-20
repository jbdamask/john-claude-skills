# beads-planner

A Claude Code plugin that converts GitHub issues into structured [Beads](https://github.com/beads-project/beads) work breakdowns — epics, tasks, and sub-tasks with objectively verifiable acceptance criteria.

## Quick Start

```
/beads-planner #42
/beads-planner https://github.com/owner/repo/issues/42
```

## Prerequisites

- **Beads** initialized in your project (`bd init`)
- **GitHub CLI** (`gh`) authenticated for the target repo
- **Beads CLI** (`bd`) on your PATH

## What It Does

Given a GitHub issue, the plugin:

1. **Fetches** the issue content and linked references
2. **Creates a branch and worktree** for isolated work (`42-add-user-auth`)
3. **Plans** the implementation (codebase exploration, no auto-execution)
4. **Breaks down** the work into epics/tasks/sub-tasks with the user
5. **Files beads** with descriptions, priorities, dependencies, and acceptance criteria
6. **Reviews and refines** the breakdown (up to 5 passes)
7. **Pushes** the branch and labels the GitHub issue as "ready"

## Plugin Structure

```
beads-planner/
├── commands/
│   └── beads-planner.md       # /beads-planner slash command
├── skills/
│   ├── issue-to-beads/        # Core workflow (7 phases)
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── beads-cli-reference.md
│   ├── plan-only/             # Codebase planning without auto-execution
│   │   └── SKILL.md
│   └── git-push-and-tag/      # Commit, push, and label the issue
│       └── SKILL.md
└── .claude-plugin/
    └── plugin.json
```

## Skills

### issue-to-beads

The main workflow. Fetches a GitHub issue, creates a branch, plans the implementation, collaborates with the user on a work breakdown, files everything as beads, then pushes. Invoked by the `/beads-planner` command.

### plan-only

Read-only planning mode. Explores the codebase, writes a plan to `.claude/plans/<slug>.md`, presents it for approval, then stops. No code is executed. Used internally by issue-to-beads (Phase 3) but can also be triggered directly when another skill needs a plan.

### git-push-and-tag

Final-phase skill that syncs beads, commits, pushes the branch, and adds a "ready" label to the GitHub issue. Used internally by issue-to-beads (Phase 7) but works standalone on any issue branch with synced beads.

## Acceptance Criteria Conventions

Every task gets 3-5 objectively verifiable criteria. Standard criteria always included:

- **"Typecheck passes"** — on every task
- **"Tests pass"** — on tasks with testable logic
- **"Verify in browser"** — on tasks that change UI

## Priority Levels

| Level | Meaning |
|-------|---------|
| P0 | Critical — blocking production or other teams |
| P1 | Core path — must complete for the issue to close |
| P2 | Important but not on the critical path |
| P3 | Nice-to-have, polish, optimization |
