# Beads CLI Reference

Quick reference for `bd` commands used by the issue-to-beads skill.
For foundational information about Beads, see the AGENTS.md file in the project's root directory.

## Table of Contents
1. [Issue Creation](#issue-creation)
2. [Dependencies](#dependencies)
3. [Querying](#querying)
4. [Status Management](#status-management)
5. [Verification Criteria Patterns](#verification-criteria-patterns)

---

## Issue Creation

```bash
# Create an epic
bd create "Title" -t epic -p <0-4> -d "Description" --json

# Create a task under an epic
bd create "Title" -t task -p <0-4> --parent <epic-id> -d "Description" --json

# Create with blocking dependency in one command
bd create "Title" -t task -p <0-4> --deps "blocks:<blocker-id>" --json

# Create with discovered-from provenance
bd create "Title" -t bug -p <0-4> --deps "discovered-from:<source-id>" --json

# Quick create (less output)
bd create "Title" -q --json
```

### Issue Types
| Type | Flag | When to Use |
|------|------|-------------|
| `epic` | `-t epic` | Large multi-task work items; the root of a hierarchy |
| `task` | `-t task` | Individual actionable work units (children of epics or other tasks) |
| `feature` | `-t feature` | New functionality (alternative to task) |
| `bug` | `-t bug` | Defects discovered during analysis |
| `chore` | `-t chore` | Maintenance, cleanup, infrastructure |

### Hierarchical IDs

Beads auto-assigns dotted IDs based on parent-child relationships:

```
bd-a3f8        Epic
bd-a3f8.1      Task (child of epic)
bd-a3f8.2      Task (child of epic)
bd-a3f8.2.1    Sub-task (child of bd-a3f8.2)
bd-a3f8.2.2    Sub-task (child of bd-a3f8.2)
```

Create children using `--parent`:
```bash
bd create "Design login UI" -t task --parent bd-a3f8 --json   # → bd-a3f8.1
bd create "Backend validation" -t task --parent bd-a3f8 --json # → bd-a3f8.2
bd create "Validate email format" -t task --parent bd-a3f8.2 --json # → bd-a3f8.2.1
```

### Priority Levels
| Level | Flag | Meaning |
|-------|------|---------|
| P0 | `-p 0` | Critical — blocking production or other teams |
| P1 | `-p 1` | High — core path, must complete |
| P2 | `-p 2` | Normal — important but not blocking |
| P3 | `-p 3` | Low — polish, optimization |
| P4 | `-p 4` | Backlog — future consideration |

## Dependencies

```bash
# Add a blocks dependency (task-A is blocked BY task-B)
bd dep add <blocked-id> <blocker-id> --type blocks

# Parent-child relationship (child OF parent)
bd dep add <child-id> <parent-id> --type parent-child

# Related (soft connection, no blocking)
bd dep add <issue-a> <issue-b> --type related

# Discovered-from (provenance tracking)
bd dep add <discovered-id> <source-id> --type discovered-from

# View dependency tree
bd dep tree <issue-id>
```

### Dependency Types
| Type | Effect on `bd ready` | When to Use |
|------|---------------------|-------------|
| `blocks` | Blocked task hidden from ready queue | Task B cannot start until Task A completes |
| `parent-child` | Child inherits parent's blocked status | Organizing tasks under epics |
| `related` | No effect on ready queue | Soft connections for context |
| `discovered-from` | No effect on ready queue | Tracking where work was discovered |

**Important:** Blocking propagates through parent-child hierarchies. When a parent epic is blocked, ALL children are automatically blocked.

## Querying

```bash
# Find ready work (unblocked tasks)
bd ready --json

# List all issues
bd list --json

# Show details of a specific issue
bd show <issue-id> --json

# Show epic status with children
bd epic status <epic-id>

# View dependency tree
bd dep tree <issue-id>

# Check for duplicates before creating
bd duplicates --dry-run

# Project statistics
bd stats
```

## Status Management

```bash
# Start working on a task
bd update <issue-id> -s in_progress --json

# Add progress notes
bd update <issue-id> --notes "Progress update" --json

# Close a completed task
bd close <issue-id> -r "Completed: [brief reason]" --json

# Add labels
bd update <issue-id> --add-label "github-issue-42" --json
```

## Verification Criteria Patterns

These patterns help write objectively verifiable acceptance criteria.

### Code Existence
```
- File `src/auth/middleware.ts` exists and exports `authenticateRequest`
- Module `@app/utils/validator` is importable without errors
```

### Test Results
```
- `npm test -- --grep "auth"` exits with code 0
- `pytest tests/test_auth.py` reports 0 failures
- Test coverage for `src/auth/` is ≥ 80% (via `npm run coverage`)
```

### API Behavior
```
- `curl -s localhost:3000/api/health` returns HTTP 200 with `{"status":"ok"}`
- `curl -X POST localhost:3000/api/login -d '{"user":"test","pass":"test"}' returns HTTP 200 with a JSON body containing `token` field
- `curl -s -o /dev/null -w "%{http_code}" localhost:3000/api/admin` returns 401 without auth header
```

### Build / CI
```
- `npm run build` exits with code 0 and produces `dist/` directory
- `docker build -t app .` completes without errors
- GitHub Actions CI workflow passes on the PR branch
```

### Database / Migration
```
- Migration `004_add_users_index.sql` exists in `migrations/`
- Running `psql -c "\d users"` shows an index on the `email` column
- `bd show <id>` confirms status=closed
```

### Documentation
```
- `docs/api/authentication.md` exists and contains sections: Overview, Endpoints, Examples
- `README.md` contains a "Getting Started" section with install instructions
- Decision record `docs/decisions/001-auth-approach.md` exists with Status, Context, Decision, Consequences sections
```

### Performance / Quality
```
- Lighthouse performance score ≥ 85 for `/dashboard` route
- `npx eslint src/ --max-warnings 0` exits with code 0
- Response time for `GET /api/users` is < 200ms with 1000 seeded records (measured via `time curl`)
```

### UI / Accessibility
```
- Component renders without React console errors in development mode
- All interactive elements are reachable via Tab key navigation
- `npx axe-core /dashboard` reports 0 violations at WCAG AA level
- Screenshot comparison: `npx playwright test --update-snapshots` produces no diff
```
