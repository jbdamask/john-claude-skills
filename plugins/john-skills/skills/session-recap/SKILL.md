---
name: session-recap
description: Reconstruct where a coding session left off by gathering context from git history, planning docs, task trackers, and past Claude Code chat logs, then summarizing it as recent activity, current state, active tasks, and likely next steps. Use when the user asks "where were we?", "what were we working on?", "recap the session", "catch me up", "what did I do yesterday", or otherwise returns to a project and needs to resume. Also use when a new conversation looks like a continuation of earlier work.
---

# Session Recap

Reconstruct the state of a project so the user can get back to work fast. Gather from several sources, then summarize. Do not guess — report only what you actually find.

## 1. Gather Context

Run the cheap checks in parallel. Stop early once you have a clear picture; not every source exists in every project.

### Git

```bash
git log --oneline -10
git status
git diff --stat HEAD~5
git branch -a
```

Recently changed files (`git diff --name-only HEAD~5`) point at what was being worked on. Read the two or three most relevant ones if the commit messages aren't enough.

### Planning and documentation files

Check for whichever of these exist: `DEVLOG.md`, `CHANGELOG.md`, `PLAN.md`, `.claude/plan.md`, `.claude/plans/`, `CLAUDE.md`, `README.md`. The devlog and plan files usually carry the most signal about intent.

### Task trackers

- `TODO.md`
- `.beads/` or `beads.db` — run `bd list` to see current tasks
- `.github/` — issue and PR templates, workflow context
- `.linear/` or `linear.json`
- Issue references in recent commit messages (`#123`, `JIRA-456`)

### Claude Code chat history

Past sessions for this project live under `~/.claude/projects/<project-path-with-slashes-as-hyphens>/` — e.g. `/Users/barry/project1` maps to `-Users-barry-project1`. Each session is a timestamped JSONL file.

```bash
ls -lt ~/.claude/projects/$(pwd | tr '/' '-')/ | head
```

Files are chronological, so tail the most recent one or two rather than reading them whole:

```bash
tail -c 20000 ~/.claude/projects/$(pwd | tr '/' '-')/<session>.jsonl
```

These files get large. Read the tail, grep for specifics, and never dump a whole session into context.

## 2. Report

Four sections, tight:

1. **Recent Activity** — what the last few commits and sessions accomplished
2. **Current State** — branch, uncommitted changes, work in progress
3. **Active Tasks** — open TODOs, beads, issues, unfinished plans
4. **Likely Next Steps** — what the user was probably about to do

Keep it short and actionable. The user wants to resume work, not read a report. If the project is new or has no history, say so plainly in a sentence.
