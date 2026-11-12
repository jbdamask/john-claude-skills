---
name: issue-to-beads
description: Turns a GitHub issue, and its spec file when the project has one, into a Beads epic with one bead per agent-sized task, created in a single `bd create --graph` call after a mechanical check and one cold read. Runs without asking questions. Use when the user says "break down issue 42", "plan this issue into beads", "convert this issue to beads", or passes an issue number or URL to /beads-planner. Needs a project that uses Beads (bd 1.3 or later) and an authenticated gh CLI.
context: fork
---

# Issue to beads

## Goal
Turn one GitHub issue into beads that one-shot agents can pick up from `bd ready` and finish without asking anyone anything. You run in the background and cannot ask the user questions: decide, and list every decision in the report.

## Inputs
- An issue: `42`, `#42`, `owner/repo#42` or its URL. Fetch it with `gh issue view <n> --json number,title,body,labels,comments,url` (add `--repo owner/repo` when given).
- A spec file, when the project has one: given as a second argument, or found where the conventions say specs live. With a spec, the spec is the requirement and the issue is context; skip any planning phase and go straight to the plan file.
- The project's conventions: `.beads/PLANNING.md` (below). Read it first. Also read whatever it, the spec or the issue points to that you need to name files correctly.
- Run `bd prime` once if the project's hooks have not already shown it to you; it is the project's Beads brief.

If there is no spec and the issue is too vague to say what done looks like for each piece, stop: create nothing, and report exactly which questions must be answered first. Do not interview.

## Project conventions: .beads/PLANNING.md
A short file the project owns. Follow it over any default here. It may say:
- **Spec files**: where they live and how they are named.
- **Description lines**: lines every bead description must carry (for example `Read:` files, a pin or lock line, which tree or worktree to work in).
- **Standard acceptance lines**: lines added to every bead, or to beads of a kind (code, UI, docs).
- **Labels**: labels every bead or certain beads carry. Graph-created children do not inherit the epic's labels, so put each label on each node.
- **Epic**: how the epic is titled and what its acceptance is (often the spec's own acceptance, word for word).
- **Links**: `external_ref` and `spec_id` format.
- **Where the plan file goes**.
- **Git**: branch and worktree per issue or trunk; whether beads are exported (`bd export -o <path>`) and committed, and by whom; whether to run the `git-push-and-tag` skill and with which label.
- **Report**: what the final report to the caller must contain beyond the defaults.

With no such file, use these defaults and say so in the report: the epic is titled `<issue title> (#<n>)`; every node gets `external_ref: gh-<n>` and, with a spec, `spec_id: <spec path>`; no standard acceptance lines; no labels; plan file at `.beads/plans/<n>.json`; no branch, no worktree, no export, no commit, no push, no issue label.

## What one bead is
One bead is one agent's worth of work: it fits in one agent's context, ends in one commit, can be checked on its own, and does not share a file with a bead that can run beside it. Smaller steps go as bullets inside a bead. If two beads must touch the same file, either add a `blocks` edge so they run one after the other, or merge them. A spike (a question to answer before building) is a bead whose acceptance is a file with the answer.

Each description gives the agent what it needs to start cold: what to build and why, the files and functions involved, decisions already made, and the convention lines. Do not paste the whole spec; point to its sections.

## Acceptance
Put acceptance in the node's `acceptance_criteria` field, never in the description. One line per criterion. Every bead needs at least one line a command or a direct observation settles. Add only the standard lines the conventions name; with none, add none.

Good:
- `` `pytest tests/test_auth.py` exits 0 ``
- `` `GET /api/users` returns 200 with a JSON array ``
- `` `src/auth/jwt.ts` exports `verifyToken` ``
- `` The filter menu lists All, Active, Completed ``

Bad: "Works correctly", "Handles edge cases", "Good UX". Turn a judgment into something measurable ("axe reports 0 WCAG AA violations on /dashboard").

## The plan file
One JSON file in the format `bd create --graph` reads (full schema: `bd help create --all`). It is the record of the breakdown; keep it where the conventions say. Shape:

```json
{
  "commit_message": "beads for #42",
  "nodes": [
    {"key": "epic", "type": "epic", "title": "Add login (#42)", "priority": 1,
     "description": "...", "acceptance_criteria": "...",
     "external_ref": "gh-42", "spec_id": "docs/specs/42-login.md", "labels": []},
    {"key": "api", "parent_key": "epic", "type": "task", "title": "...", "priority": 1,
     "description": "...", "acceptance_criteria": "- `pytest tests/test_login.py` exits 0",
     "external_ref": "gh-42", "spec_id": "docs/specs/42-login.md",
     "metadata": {"files": ["src/auth/login.py", "tests/test_login.py"], "new_files": ["tests/test_login.py"]}}
  ],
  "edges": [{"from_key": "ui", "to_key": "api", "type": "blocks"}]
}
```

- An edge `{"from_key": A, "to_key": B, "type": "blocks"}` means A waits for B. `parent_key` already makes the parent-child link; do not repeat it in `edges`.
- `metadata.files` lists every file the bead edits or creates; `metadata.new_files` the ones that do not exist yet. The check uses both.
- Priorities 0 to 3. Use `type` `task` unless the work is a `bug`, `spike`, `chore` or `feature`.
- Graph children get flat ids (`proj-x7k2`), not dotted ones; `bd ready --parent <epic>` and `bd show <epic> --children` still group them.

## Steps
1. Read the conventions, the issue, the spec and the files they name. Run `bd list --all --external-ref gh-<n> --json` to catch beads already filed for it; if some exist, add only what is missing and say so.
2. Write the plan file.
3. Check it: `python3 <this skill's directory>/scripts/check_plan.py <plan> --root <repo root> --issue <n>`. It fails loudly on: a bead with no acceptance line a command or an observation can settle, a vague acceptance line, a dependency cycle, a named file path that does not exist and is not in `new_files`, two beads that can run at the same time owning the same file, a missing parent or external_ref. Fix and rerun until it prints `OK`. Then `bd create --graph <plan> --dry-run`, which checks the graph against bd itself.
4. Cold read, once. Start a fresh subagent and give it only the plan file path, the spec path (or the issue URL) and the repo root; it may open the files the beads name, as the working agent would. Ask: "For each bead, could you start it without asking anything? List what you would have to ask, by bead key. Do not suggest new scope. Change no files." Fix what it finds in the plan file once, rerun step 3, and do not ask again. If you cannot start a subagent, skip this and say so in the report.
5. Create: `bd create --graph <plan> --json`. It is atomic: either every bead and edge exists or none does. Keep the returned key-to-id map.
6. Verify: `bd lint <epic id> <child ids...>` (acceptance present), `bd dep cycles`, `bd ready --parent <epic id>`.
7. Do what the conventions say about git, export and the issue label (the `git-push-and-tag` skill, if they name it). With no conventions, do none of it.

If `bd create --graph` fails, nothing was created: fix the plan and run it again. Never fall back to one `bd create` per bead.

## Report
Your last message, to the caller:
- The epic id and the plan file path.
- How many beads and how many dependencies were created.
- What is ready now (`bd ready --parent <epic>`), by id and title.
- Every judgment call: splits and merges, ordering you chose, anything in the spec or issue you could not turn into a checkable bead, and what the cold read changed.
- What you did not do: no commit, no export, no push, no label, no cold read, whichever apply; and whether `.beads/PLANNING.md` was found.
- Anything the conventions add.

## Edge cases
- **One-task issue**: still an epic with one child, so the issue has one place in `bd ready --parent`.
- **Very large issue** (more than about 25 beads): split into several epics under the issue, each with its own plan file, and say so in the report.
- **Unknowns**: a spike bead whose acceptance names the answer file and the question it answers; beads that depend on the answer wait on it with a `blocks` edge.
- **Issue already broken down**: add only the missing beads, with `parent_id` set to the existing epic.

## Reference
`references/beads-cli-reference.md` has the bd 1.3.1 commands this skill and the agents who work the beads use.
