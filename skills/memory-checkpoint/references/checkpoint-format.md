# Checkpoint Format Template

Use this structured format for all checkpoints.

```markdown
# Checkpoint: {ISO_TIMESTAMP}

## Status: {IN_PROGRESS | BLOCKED | DECISION_NEEDED | COMPLETED}

## Current Task
{Brief description of what is actively being worked on}

## Why (Context)
{Working on X **because** Y was failing. Tried Z which didn't work.
Currently exploring A approach.}

## Decisions Made
- {Decision 1 with brief rationale}
- {Decision 2 with brief rationale}

## Pending Items
- [ ] {Uncompleted item 1}
- [ ] {Uncompleted item 2}

## Blockers
{Any blockers or things waiting on user input}

## Next Steps
1. {Immediate next action}
2. {Following action}

## Key Files
- {path/to/important/file.py}
- {path/to/config.json}
```

## Field Guidelines

**Status values:**
- `IN_PROGRESS` - Work is ongoing
- `BLOCKED` - Waiting on external input/resource
- `DECISION_NEEDED` - Requires user decision to proceed
- `COMPLETED` - Task finished (rare for checkpoints)

**Why section:** Capture reasoning, not just state. Include:
- What problem prompted this work
- What approaches were tried
- What's currently being explored

**Decisions Made:** Include the "why" for each decision, not just what was decided.

**Key Files:** List files that would need to be re-read to resume context.
