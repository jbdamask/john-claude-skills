#!/usr/bin/env bash
# Collect the factual state a handoff document needs. Read-only — touches nothing.
# Usage: scripts/gather.sh
set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT" || exit 1

section() { printf '\n===== %s =====\n' "$1"; }

section ROOT
echo "$ROOT"

section NOW
echo "slug:  $(date +'%Y-%m-%d-%H%M')"
echo "human: $(date +'%Y-%m-%d %H:%M %Z')"
echo "iso:   $(date +'%Y-%m-%dT%H:%M:%S%z')"

section SESSION
# Model, effort, and session identity, read from the harness rather than self-reported.
# Claude Code is handled concretely; other harnesses fall through to "unknown".
if [ -n "${CLAUDE_CODE_SESSION_ID:-}" ]; then
  echo "harness: claude-code"
  echo "session_id: $CLAUDE_CODE_SESSION_ID"
  [ -n "${CLAUDE_EFFORT:-}" ] && echo "effort_env: $CLAUDE_EFFORT"
  TRANSCRIPT="$HOME/.claude/projects/$(pwd | tr '/' '-')/${CLAUDE_CODE_SESSION_ID}.jsonl"
  if [ -f "$TRANSCRIPT" ]; then
    echo "transcript: $TRANSCRIPT"
    python3 - "$TRANSCRIPT" <<'PYEOF'
import json, sys
model = effort = version = None
for line in open(sys.argv[1], errors='replace'):
    try: d = json.loads(line)
    except Exception: continue
    if d.get('type') != 'assistant': continue
    model = d.get('message', {}).get('model') or model
    effort = d.get('effort') or effort
    version = d.get('version') or version
print(f"model: {model or 'unknown'}")
print(f"effort: {effort or 'unknown'}")
print(f"harness_version: {version or 'unknown'}")
PYEOF
  else
    echo "transcript: not found at expected path"
  fi
elif [ -n "${AI_AGENT:-}" ]; then
  echo "harness: $AI_AGENT (no known transcript layout — self-report model/effort)"
else
  echo "harness: unknown — self-report model/effort, or write 'unknown'"
fi

section PREVIOUS_HANDOFF
PREV=$(ls .handoff/*-HANDOFF.md 2>/dev/null | sort | tail -1)
if [ -n "$PREV" ]; then
  echo "file: ${PREV#./}"
  PREV_SHA=$(grep -m1 -E '^HEAD_SHA:' "$PREV" | sed 's/^HEAD_SHA:[[:space:]]*//' | tr -d '"')
  echo "head_sha: ${PREV_SHA:-unknown}"
  echo "--- frontmatter ---"
  sed -n '2,/^---$/p' "$PREV" | sed '$d'
else
  echo "none — this is the first handoff for this project"
  PREV_SHA=""
fi

section GIT
echo "remote:  $(git remote get-url origin 2>/dev/null || echo 'no origin')"
echo "branch:  $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'not a git repo')"
echo "head:    $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "upstream:$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null || echo 'no upstream')"
echo "ahead/behind: $(git rev-list --left-right --count '@{u}...HEAD' 2>/dev/null || echo 'n/a')"

section WORKING_TREE
git status --short 2>/dev/null | head -40
echo "--- diffstat (unstaged+staged vs HEAD) ---"
git diff HEAD --stat 2>/dev/null | tail -20

section COMMITS
if [ -n "${PREV_SHA:-}" ] && git cat-file -e "${PREV_SHA}^{commit}" 2>/dev/null; then
  echo "(since previous handoff $PREV_SHA)"
  git log --oneline --no-decorate "${PREV_SHA}..HEAD" 2>/dev/null | head -40
else
  echo "(no usable predecessor sha — last 15)"
  git log --oneline --no-decorate -15 2>/dev/null
fi

section STASHES
git stash list 2>/dev/null | head -10

section TRACKERS
[ -d .beads ] && echo "beads: .beads/ present"
[ -f beads.db ] && echo "beads: beads.db present"
[ -d .github ] && echo "github: .github/ present"
if [ -f .linear ] || [ -f linear.json ]; then echo "linear: config present"; fi
[ -d .jira ] && echo "jira: .jira present"
git remote get-url origin 2>/dev/null | grep -qi github && echo "origin is GitHub"

section BEADS
if [ -d .beads ] || [ -f beads.db ]; then
  bd stats 2>&1 | head -15
  echo "--- in flight ---"
  bd list 2>&1 | head -40
else
  echo "not a beads project"
fi

section OPEN_PRS
if command -v gh >/dev/null 2>&1 && git remote get-url origin 2>/dev/null | grep -qi github; then
  gh pr list --limit 10 2>&1 | head -15
else
  echo "gh unavailable or non-GitHub remote"
fi

section PROJECT_DOCS
for f in CLAUDE.md README.md DEVLOG.md CHANGELOG.md PLAN.md TODO.md; do
  [ -f "$f" ] && echo "$f"
done
ls .claude/plans/*.md 2>/dev/null | tail -5

section HANDOFF_DIR_TRACKED
if [ -d .handoff ]; then
  git check-ignore -q .handoff && echo "WARNING: .handoff is gitignored but handoffs are meant to be committed" || echo ".handoff is tracked (good)"
else
  echo ".handoff does not exist yet — will be created"
fi
