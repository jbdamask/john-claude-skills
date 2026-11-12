# Planning conventions for beads-planner

The lead runs `/beads-planner:issue-to-beads <issue number>` on an issue labelled `approved_spec` (hive/BUILD.md step 4). This file says what is particular to this team; the rules it points to win.

## Inputs
- Spec: `hive/specs/<issue number>-<short name>.md`. {{owner}}'s words and its `DECIDED:` lines are settled; do not reopen them. Every bead also follows the agent brief; descriptions never repeat it.

## Epic
- Title carries `#<issue number>`; acceptance is the spec's acceptance, word for word.

## Every bead
- `external_ref`: `gh-<issue number>`; `spec_id`: the spec path. One bead is one one-shot task ending in one commit.
- The description ends with `Read:` (the files the agent reads first; every path exists) and `Tree:` (`worktree` when the diff changes code, else `shared`).
- No file that every bead must edit: two beads that can run at the same time never own the same file. Give each bead its own file, or generate the shared one.
- A file built from another file gets a row in hive/GENERATED.json in the same bead that creates it.
- Acceptance on any bead that changes code: `hive/tools/land.py landed it (fast tests passed on the merge)`.

## Check beads
- `role:red-team` on the feature's evidence, blocked by the build beads. `role:blind-checker` for each part that makes a judgment. `role:product-reviewer` when the feature changes what the user sees. A plain bead shows the feature on a case it was not built on.

## Git
- Trunk: no issue branch. Plan file: `.beads/plans/<issue number>.json`. The skill commits, pushes and labels nothing; the lead swaps the issue's labels (hive/BUILD.md).

## Report to the lead
The default report, plus the beads labelled `role:*` and every spec item with no bead and why.
