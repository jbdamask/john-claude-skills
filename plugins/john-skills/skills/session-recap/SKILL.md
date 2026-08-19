---
name: session-recap
description: Reconstruct where a coding session left off by reading the latest .handoff document if one exists, then gathering context from git history, planning docs, task trackers, and past agent chat logs from any supported harness (Claude Code, Codex CLI, Amp, opencode, Grok CLI), then summarizing it as recent activity, current state, active tasks, and likely next steps. Use when the user asks "where were we?", "what were we working on?", "recap the session", "catch me up", "what did I do yesterday", or otherwise returns to a project and needs to resume. Also use when a new conversation looks like a continuation of earlier work.
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

### Agent chat history

**Do not assume the last session was Claude Code.** Five harnesses keep local transcripts, and a
repo can have several of them in its history. If a handoff is present, its `HARNESS` and
`SESSION_ID` name the exact one — read that and skip the search.

Fastest way to find what exists: the companion `handoff` skill's gather script, which is
read-only and already resolves all five.

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/handoff/scripts/gather.sh"   # outside Claude Code, use the path relative to that SKILL.md
```

Its `SESSION` and `OTHER_AGENT_SESSIONS` blocks print a `transcript:` path per harness. Two
bounds to know: it reports only the **newest** session per harness, and its codex scan stops at
the 600 newest rollout files. For anything older, search by hand with the table below.

| Harness | Where this repo's sessions live | Format |
|---|---|---|
| Claude Code | `~/.claude/projects/<cwd with / as ->/<id>.jsonl` | JSONL, one record per line |
| Codex CLI | `${CODEX_HOME:-~/.codex}/sessions/YYYY/MM/DD/rollout-*-<id>.jsonl` | JSONL; **not keyed by cwd** — match on the `session_meta` line |
| Amp | `~/.local/share/amp/threads/T-*.json` (synced), else `~/.cache/amp/logs/threads/<id>.log` (live) | single JSON doc; repo is in `env.initial.trees[].uri` |
| opencode | `~/.local/share/opencode/storage/` — `session/*/ses_*.json` carries `directory` | one JSON file per message, **text in a separate tree** |
| Grok CLI | `~/.grok/sessions/<percent-encoded cwd>/<id>/chat_history.jsonl` | JSONL; dir name is the `unquote`d cwd |

Only two of the five are tail-able. Read the tail, grep for specifics, and never dump a whole
session into context.

```bash
# Claude Code — newest transcript for this directory
ls -t ~/.claude/projects/$(pwd | tr '/' '-')/*.jsonl | head
tail -n 60 <file> | python3 -c '
import sys, json
for l in sys.stdin:
    try: d = json.loads(l)
    except: continue
    if d.get("type") not in ("user", "assistant"): continue
    c = (d.get("message") or {}).get("content")
    if isinstance(c, list): c = " ".join(b.get("text","") for b in c if isinstance(b, dict) and b.get("type") == "text")
    if c and str(c).strip(): print(d["type"].upper(), ":", str(c).replace("\n", " ")[:200])'

# Codex — find this repo's rollouts, then read one
grep -l "\"cwd\":\"$(pwd)\"" $(ls -t ${CODEX_HOME:-~/.codex}/sessions/*/*/*/rollout-*.jsonl | head -200) 2>/dev/null | head
tail -n 80 <rollout> | python3 -c '
import sys, json
for l in sys.stdin:
    try: d = json.loads(l)
    except: continue
    p = d.get("payload") or {}
    if p.get("type") != "message": continue
    t = " ".join(c.get("text","") for c in (p.get("content") or []) if isinstance(c, dict))
    if t.strip(): print(str(p.get("role","?")).upper(), ":", t.replace("\n", " ")[:200])'

# Grok — records key on "type", NOT "role"; "reasoning" and "tool_result" are noise
python3 -c '
import json, sys
rows = []
for l in open(sys.argv[1], errors="replace"):
    try: d = json.loads(l)
    except: continue
    if d.get("type") not in ("user", "assistant"): continue
    c = d.get("content")
    if isinstance(c, list): c = " ".join(b.get("text","") for b in c if isinstance(b, dict))
    if c and str(c).strip(): rows.append(d["type"].upper() + ": " + str(c).replace("\n", " ")[:200])
print("\n".join(rows[-30:]))' <chat_history.jsonl>

# Amp — one JSON doc; user and assistant text are both content[].text
python3 -c '
import json, sys
d = json.load(open(sys.argv[1], errors="replace"))
print("title:", d.get("title"))
for m in (d.get("messages") or [])[-20:]:
    c = m.get("content")
    if isinstance(c, list): c = " ".join(b.get("text","") for b in c if isinstance(b, dict) and b.get("type") == "text")
    if c and str(c).strip(): print(str(m.get("role","?")).upper(), ":", str(c).replace("\n", " ")[:200])' <T-*.json>

# opencode — message metadata and message text are in two different trees
python3 -c '
import json, glob, os, sys
ses = sys.argv[1]  # ses_...
st = os.path.expanduser("~/.local/share/opencode/storage")
for f in sorted(glob.glob(os.path.join(st, "message", ses, "msg_*.json")), key=os.path.getmtime)[-20:]:
    m = json.load(open(f, errors="replace"))
    txt = []
    for pf in sorted(glob.glob(os.path.join(st, "part", m["id"], "prt_*.json"))):
        p = json.load(open(pf, errors="replace"))
        if p.get("type") == "text" and p.get("text"): txt.append(p["text"])
    if txt: print(str(m.get("role","?")).upper(), ":", " ".join(txt).replace("\n", " ")[:200])' ses_XXXX
```

Traps, all hit for real:

- **`msg_*.json` holds no text.** opencode stores the message record and its text separately —
  the words live in `storage/part/<msg_id>/prt_*.json`. Reading only the message tree returns
  metadata and looks like an empty session.
- **Grok has no `role` field.** Filter on `type`; `reasoning` records carry `encrypted_content`
  and are unreadable, so skip them rather than treating the session as opaque.
- **Amp's synced thread store lags a live session badly** — the newest `threads/T-*.json` can be
  months old while a thread is running. A live thread exists only as
  `~/.cache/amp/logs/threads/<id>.log`, which has the title and agent mode but no model.
- **Codex rollouts are date-partitioned, not cwd-partitioned.** Every match requires opening
  files, so bound the scan and say so if you do.
- **`$CLAUDE_CODE_SESSION_ID` is inherited by subshells.** If you shell out to inspect another
  harness, it is still set — do not read it as evidence about that harness.

## 3. Report

Four sections, tight:

1. **Recent Activity** — what the last few commits and sessions accomplished
2. **Current State** — branch, uncommitted changes, work in progress
3. **Active Tasks** — open TODOs, beads, issues, unfinished plans
4. **Open threads** — what's unfinished, unranked. If a handoff supplied a recommendation, present it here as the previous session's view with its reasoning, clearly attributed and clearly still open. Without a handoff, offer what the work seems to have been heading toward, labeled as your inference. Either way it's a suggestion for the orchestrator to accept or redirect — don't act on it unprompted.

Keep it short and actionable. The user wants to resume work, not read a report. If the project is new or has no history, say so plainly in a sentence.

If no handoff existed and the session had real substance worth preserving, mention that the `handoff` skill can write one at the end of this session so the next recap is a single file read instead of an excavation.
