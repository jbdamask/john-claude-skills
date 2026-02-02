---
name: memory-checkpoint
description: Save and restore session state for continuity across context compressions. Invoke with "/memory-checkpoint" to save current session state, or "/memory-checkpoint your search query" to search past checkpoints by semantic similarity.
---

# Memory Checkpoint

## Workflow

**If user provides a query** (e.g., `/memory-checkpoint authentication bug`):
→ Search checkpoints using `scripts/search.py "<query>" --full --project-dir "$PWD"`

**If no query** (e.g., `/memory-checkpoint`):
→ Create checkpoint using format from `references/checkpoint-format.md`, pipe to `scripts/checkpoint.py --project-dir "$PWD"`

## Creating a Checkpoint

Generate content with these sections, then pipe to script:
- **Status**: IN_PROGRESS, BLOCKED, DECISION_NEEDED, COMPLETED
- **Current Task**: What is actively being worked on
- **Why (Context)**: Reasoning behind current approach, what was tried
- **Decisions Made**: Key choices with rationale
- **Pending Items**: Uncompleted work
- **Blockers**: Things waiting on external input
- **Next Steps**: Immediate actions to take
- **Key Files**: Important files for resuming context

```bash
echo "CHECKPOINT_CONTENT" | python3 scripts/checkpoint.py --project-dir "$PWD"
```

## Searching Checkpoints

```bash
python3 scripts/search.py "query" --full --project-dir "$PWD"
```

Returns checkpoints ranked by semantic similarity. `--full` includes content of top result.

## Setup (one-time)

```bash
./scripts/setup.sh
```

Creates `.venv` and installs `fastembed`. Scripts auto-detect the venv when present.
