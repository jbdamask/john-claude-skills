# Beads CLI reference (bd 1.3.1)

Checked against `bd --help` and `bd <command> --help` on bd 1.3.1. When in doubt, run the help; it is the source, not this file. `bd prime` prints the project's own brief for agents.

## Creating a breakdown in one step
```bash
bd help create --all              # full --graph plan schema
bd create --graph plan.json --dry-run     # validate structure and cycles, create nothing
bd create --graph plan.json --json        # create every node and edge atomically; prints {"ids": {key: id}}
```
Plan file: `{"commit_message": "...", "nodes": [...], "edges": [...]}`.
- Node fields use the names `bd show --json` emits: `key` (plan-local, required), `title`, `type`, `priority` (0-4), `description`, `design`, `acceptance_criteria`, `notes`, `labels`, `assignee`, `estimated_minutes`, `external_ref`, `spec_id`, `metadata` (any JSON), `status`, `defer_until`/`due_at` (RFC3339), `id` (pin an explicit id).
- `parent_key` (a plan key) or `parent_id` (an existing issue) makes the parent-child link. Children created this way get flat ids and do not inherit the parent's labels.
- Edge: `{"from_key": "a", "to_key": "b", "type": "blocks"}` means a waits for b (b must close before a is ready). `from_id`/`to_id` point at existing issues. `type` defaults to `blocks`; do not repeat parent links as edges.
- Unknown fields are dropped with a warning, so read the dry-run output.
- The dry run does not check paths that run through dependencies already stored; the live create can still refuse. A refused create creates nothing.

## One issue at a time
```bash
bd create "Title" -t task -p 1 --parent <epic> -d "What and why" \
  --acceptance "- \`pytest -q\` exits 0" --external-ref gh-42 --spec-id docs/specs/42.md \
  --deps discovered-from:<id> -l label1,label2 --json
bd create "Title" --body-file desc.md --acceptance "..."   # long description from a file
```
`--parent` gives a dotted child id (`proj-a3f8.1`) and copies the parent's labels (`--no-inherit-labels` to stop it). `--deps` takes `type:id`; bare `id`, `blocked-by:id` and `depends-on:id` all make the new issue wait on `id`; `blocks:id` reverses it. Types: task, bug, feature, epic, chore, decision, spike, story, milestone.

## Fields after creation
```bash
bd update <id> --acceptance "..." --external-ref gh-42 --spec-id <path> -d "..." -p 1
bd update <id> --add-label x --remove-label y
bd note <id> "one line"               # append to notes (same as --append-notes)
bd note <id> --file note.txt          # longer note from a file
bd lint [ids...]                      # missing sections: tasks need acceptance (field counts), epics need acceptance or success criteria
```
`--notes` replaces all notes; use `bd note` to append.

## Dependencies
```bash
bd dep add <waiting-id> <blocker-id>            # waiting-id depends on blocker-id (type blocks)
bd dep add <a> --blocked-by <b>                 # same
bd dep add <a> <b> -t discovered-from           # types: blocks, tracks, related, parent-child, discovered-from, until, caused-by, validates, relates-to, supersedes
bd dep add --file deps.jsonl                    # bulk: {"from":"a","to":"b"} per line
bd dep remove <a> <b>
bd dep tree <id>
bd dep cycles
```
Only blocking types (blocks, waits-for, parent-child) affect `bd ready`. A blocked parent blocks its children.

## Finding work
```bash
bd ready [--parent <epic>] [--label x] [--json] [-n 0]   # unblocked open work
bd ready --explain                                       # why each issue is or is not ready
bd list --all --external-ref gh-42 --json                # everything linked to issue 42
bd list --spec docs/specs/42                             # by spec_id prefix
bd list --parent <epic>
bd show <id> [--children] [--json]
bd search "text"
```

## Claiming and leases
```bash
bd update <id> --claim          # atomic: assignee = you (BEADS_ACTOR), status in_progress, takes a lease
bd ready --claim [--label x]    # claim the first ready issue matching the filters
bd heartbeat <id>               # extend your lease while you work
bd unclaim <id>                 # give it back: assignee cleared, status open
bd reclaim [--older-than 10m]   # supervisor: return issues whose lease expired back to open
bd close <id> --reason "..."    # done
```
A claim fails if someone else holds a live lease. `--actor` or `BEADS_ACTOR` sets who you are.

## Sync and export
`bd sync` is one pull / conflict-check / push cycle against the project's Dolt remote. It does not write a JSONL file. `bd export -o .beads/issues.jsonl` writes the JSONL export when a project keeps one in git; `export.auto: true` in `.beads/config.yaml` writes it after each write command. Whether to export or commit is the project's choice (its `.beads/PLANNING.md`).

## Acceptance lines that settle themselves
- Code: `` `src/auth/jwt.ts` exports `verifyToken` ``
- Tests: `` `pytest tests/test_auth.py` exits 0 ``
- API: `` `curl -s -o /dev/null -w '%{http_code}' localhost:3000/api/admin` prints 401 without a token ``
- Build: `` `npm run build` exits 0 and writes `dist/` ``
- Data: `` `psql -c '\d users'` shows an index on `email` ``
- Docs: `` `docs/api/auth.md` has sections Overview, Endpoints, Examples ``
- UI: `` `npx playwright test login.spec.ts` exits 0 ``; `` axe reports 0 WCAG AA violations on /dashboard ``
