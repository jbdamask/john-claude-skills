---
name: git-push-and-tag
description: Final-phase skill that stages beads, commits, pushes to the remote branch, and labels the GitHub issue as "ready". Invoked by issue-to-beads as the last step after all beads have been filed, reviewed, and synced. Can also be used standalone when you have synced beads on an issue branch that need to be committed and pushed.
context: fork
---

# Git Push and Tag

Stages the `.beads/` directory, commits, pushes the branch, and labels the corresponding GitHub issue as "ready". This is the final step in the issue-to-beads workflow.

## Prerequisites

- Must be on an issue branch (pattern: `<issue-number>-<slug>`)
- Beads must already be synced (`bd sync` has been run or will be run here)
- The `gh` CLI must be authenticated for the target GitHub repo
- The `bd` CLI must be available on PATH
- The `.beads/` directory must exist with filed beads

## Workflow

### Step 1: Pull latest changes

```bash
git pull --rebase
```

If this fails due to conflicts, stop and ask the user how to resolve them.

### Step 2: Sync beads

```bash
bd sync
```

This ensures the JSONL index is up to date with the beads on disk.

### Step 3: Stage the beads directory

```bash
git add .beads/
git add .plan/
```

Stage `.beads/` (the filed beads) and `.plan/` (the approved plan artifact). Do not stage unrelated changes. If there are other files that should be committed, ask the user before staging them.

### Step 4: Commit

Infer the issue number and title from the current branch name. The branch follows the pattern `<issue-number>-<slug>` (e.g., `42-add-user-authentication`).

```bash
# Get branch name
git rev-parse --abbrev-ref HEAD

# Commit with descriptive message
git commit -m "Add beads for issue #<number>: <title-from-slug>"
```

Replace `<number>` with the issue number extracted from the branch name, and `<title-from-slug>` with the slug portion converted back to readable text (hyphens to spaces).

### Step 5: Push

```bash
git push -u origin <branch-name>
```

If the push fails (e.g., due to remote changes), try:

```bash
git pull --rebase
git push -u origin <branch-name>
```

If it still fails, stop and ask the user for help.

### Step 6: Label the GitHub issue

Confirm the issue number with the user before labeling:

> I inferred issue **#\<number\>** from branch `<branch-name>`. Should I add the "ready" label to this issue?

After confirmation:

```bash
gh issue edit <number> --add-label "ready"
```

If the label doesn't exist on the repo, show the error and suggest the user create it manually or pick a different label.

### Step 7: Verify

```bash
git status
```

This must show the branch is up to date with the remote. If it doesn't, diagnose and fix before declaring success.

## Error Handling

- **Push fails**: Suggest `git pull --rebase` and retry once. If still failing, ask the user.
- **Label fails**: Show the error message. Common causes: label doesn't exist, insufficient permissions, wrong issue number. Suggest manual labeling as a fallback.
- **Commit fails (nothing to commit)**: Run `git status` to diagnose. The beads may already be committed, or `bd sync` may not have produced changes. Ask the user how to proceed.
- **Branch name doesn't match pattern**: Ask the user to provide the issue number manually.
