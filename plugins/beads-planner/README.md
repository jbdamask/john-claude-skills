# beads-planner

A Claude Code plugin that turns a GitHub issue, and its spec when the project has one, into a [Beads](https://github.com/steveyegge/beads) epic with one bead per agent-sized task. Built for bd 1.3.1.

## Quick start

```
/beads-planner 42
/beads-planner https://github.com/owner/repo/issues/42 docs/specs/42-login.md
```

## Prerequisites

- Beads initialized in the project (`bd init`), bd 1.3 or later on PATH
- GitHub CLI (`gh`) authenticated for the repo
- `python3` (the plan check uses the standard library only)

## What it does

issue-to-beads runs in the background and asks no questions:

1. Reads the project's `.beads/PLANNING.md` (if any), the issue and the spec.
2. Writes one plan file in the format `bd create --graph` reads: an epic, one bead per agent-sized task, acceptance in the acceptance field, `external_ref` gh-&lt;n&gt; and `spec_id` on each bead, and the files each bead owns.
3. Checks it mechanically (`scripts/check_plan.py`): checkable acceptance, no cycles, named files exist, no two beads that can run together own the same file. Then `bd create --graph --dry-run`.
4. Has a fresh subagent cold-read the plan once and fixes what it finds.
5. Creates every bead and dependency in one atomic `bd create --graph` call.
6. Reports the epic id, counts, what is ready now, every judgment call, and what it did not do.

If there is no spec and the issue is too vague to break down, it creates nothing and says what is missing.

By default it does not branch, export, commit, push or label anything. A project turns those on in `.beads/PLANNING.md`.

## Project conventions: .beads/PLANNING.md

A short file the project owns. It can set: where specs live, lines every bead description carries, standard acceptance lines, labels, the epic's title and acceptance, the plan file's location, branch or trunk, export and commit (and who does it), whether to run git-push-and-tag and with which label, and what the report must contain. See the skill for details.

## Skills

- **issue-to-beads**: the breakdown above. Invoked by `/beads-planner`.
- **git-push-and-tag**: commits the plan file and the JSONL export (when the project keeps one), pushes, and adds the label the conventions name. Runs only when the conventions or the user ask.
- **plan-only**: a separate, interactive planning mode that writes a plan and stops after the user approves it. issue-to-beads no longer uses it.

## Changes in 0.2.0

- One `bd create --graph` call replaces a `bd create` and a `bd dep add` per bead.
- No user-approval stops; no five review rounds. A mechanical check and one cold read instead.
- No `bd sync` (in bd 1.3 it syncs the Dolt remote; it does not write the JSONL file).
- Acceptance goes in `--acceptance`; links in `--external-ref` and `--spec-id`.
- No hard-coded acceptance lines, no mandatory branch and worktree, no default commit or "Ready" label: all come from the project's conventions.
- CLI reference rewritten from bd 1.3.1's own help.

## Structure

```
beads-planner/
├── commands/beads-planner.md
├── skills/
│   ├── issue-to-beads/
│   │   ├── SKILL.md
│   │   ├── scripts/check_plan.py
│   │   └── references/beads-cli-reference.md
│   ├── git-push-and-tag/SKILL.md
│   └── plan-only/SKILL.md
└── .claude-plugin/plugin.json
```
