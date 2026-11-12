---
name: git-push-and-tag
description: Commits and pushes the record of a beads breakdown (the plan file and, when the project keeps one, its JSONL export) and optionally labels the GitHub issue. Runs only when a project's .beads/PLANNING.md asks for it or the user invokes it; issue-to-beads does not call it otherwise. Use when the user says "commit and push the beads for issue 42" or "push the plan and label the issue".
context: fork
---

# Git push and tag

## Goal
Put the breakdown for one issue into git and, if asked, mark the issue. Nothing else.

## Inputs
- The issue number (given; never inferred from a branch name).
- The project's `.beads/PLANNING.md`: whether to export, the export path, the plan file path, the branch, the label. With no such file and no instruction from the caller, stop and say so; there is no default commit.

## Steps
1. If the conventions keep a JSONL export in git, write it: `bd export -o <path>` (usually `.beads/issues.jsonl`). Do not run `bd sync` for this: it syncs the Dolt remote and writes no file.
2. Stage only named files: the plan file and the export path. Never `git add .beads/` or `git add -A`; `.beads/` holds the database, locks and backups.
3. Commit with a plain message: `beads for #<n>: <issue title>`.
4. Push the current branch: `git push` (or `git push -u origin <branch>` for a new branch). If it is rejected, pull with the project's merge style (the conventions say rebase or merge), resolve only conflicts in the files you staged, and push once more. If it fails again, stop and report.
5. If the conventions name a label, `gh issue edit <n> --add-label <label>`. If the label does not exist, report it; do not create it.
6. `git status -sb | head -1` must show the branch even with its remote.

## Report
The commit sha, the branch, the files committed, the label added (or why not).
