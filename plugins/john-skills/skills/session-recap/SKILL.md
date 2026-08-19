---
name: session-recap
description: Reconstruct where a coding session left off by reading the latest .handoff document if one exists, then gathering context from git history, planning docs, task trackers, and past Claude Code chat logs, then summarizing it as recent activity, current state, active tasks, and likely next steps. Use when the user asks "where were we?", "what were we working on?", "recap the session", "catch me up", "what did I do yesterday", or otherwise returns to a project and needs to resume. Also use when a new conversation looks like a continuation of earlier work.
---

# Session Recap

Reconstruct the state of a project so the user can get back to work fast. Gather from several sources, then summarize. Do not guess — report only what you actually find.

## 1. Check for a handoff first

If the previous session wrote one, it beats every other source — it carries intent, not just artifacts.

```bash
ls .handoff/*-HANDOFF.md 2>/dev/null | sort | tail -1
```

Filenames sort chronologically, so the last one is the newest. Read it in full. Then find out what changed *after* it was written, using the `HEAD_SHA` in its frontmatter:

```bash
git log --oneline <HEAD_SHA>..HEAD
git status --short
```

If that range is empty and the tree is clean, the handoff is still accurate — report it as described under "Surfacing a handoff" below, and stop. Skip the rest of this skill; you're done.

If work landed after the handoff, the handoff is your baseline and the sources below fill the gap. Say plainly which parts of your recap came from the handoff and which you reconstructed, since the reconstructed parts are the less reliable half.

Older handoffs form a chain via their `PREDECESSOR` field. Follow it back only when the newest one leaves a real gap — don't read the whole folder by default.

### Surfacing a handoff

You are reporting to whoever directs the next session — the user, or an orchestrating agent. Your job is to put the previous session's findings in front of them as **input to a decision they own**, not to act on those findings yourself.

- **Open loops** (`OPEN_LOOPS`, the "Open threads" section): report all of them. Mark which were in scope for that session and went unfinished, versus discoveries and deferred extras.
- **`RECOMMENDED_NEXT` and "Recommended next"**: surface it, always, and attribute it — "the previous session recommended X, because Y." Carry the reasoning and any stated consequence of skipping it; that's the part the orchestrator can't reconstruct. Never restate it as your own conclusion or as a settled plan, and never start executing it. If `SCOPE_COMPLETE: false`, say so — unfinished in-scope work is the case where that recommendation carries the most weight.
- **`## Stated direction`**: if the user said something about what comes next, that outranks the recommendation. Lead with it, and name the conflict if there is one.
- **"May have moved since I stopped"**: turn each item into a concrete thing to verify now. Where you can check cheaply (a PR's status, a CI run), check it and report the current answer rather than the stale worry.

Then stop and let them choose. A recap that quietly adopts the previous session's plan defeats the point of writing it down.

## 2. Gather Context

Only if there's no handoff, or it's stale. Run the cheap checks in parallel; stop early once you have a clear picture. Not every source exists in every project.

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

Past sessions for this project live under `~/.claude/projects/<project-path-with-slashes-as-hyphens>/` — e.g. `/Users/barry/project1` maps to `-Users-barry-project1`. Each session is a JSONL file named by its session id. If a handoff gave you a `SESSION_ID`, read that file directly instead of guessing; a project directory often holds several concurrent logs.

```bash
ls -lt ~/.claude/projects/$(pwd | tr '/' '-')/ | head
```

Files are chronological, so tail the most recent one or two rather than reading them whole:

```bash
tail -c 20000 ~/.claude/projects/$(pwd | tr '/' '-')/<session>.jsonl
```

These files get large. Read the tail, grep for specifics, and never dump a whole session into context.

## 3. Report

Four sections, tight:

1. **Recent Activity** — what the last few commits and sessions accomplished
2. **Current State** — branch, uncommitted changes, work in progress
3. **Active Tasks** — open TODOs, beads, issues, unfinished plans
4. **Open threads** — what's unfinished, unranked. If a handoff supplied a recommendation, present it here as the previous session's view with its reasoning, clearly attributed and clearly still open. Without a handoff, offer what the work seems to have been heading toward, labeled as your inference. Either way it's a suggestion for the orchestrator to accept or redirect — don't act on it unprompted.

Keep it short and actionable. The user wants to resume work, not read a report. If the project is new or has no history, say so plainly in a sentence.

If no handoff existed and the session had real substance worth preserving, mention that the `handoff` skill can write one at the end of this session so the next recap is a single file read instead of an excavation.
