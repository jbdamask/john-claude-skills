---
name: claude-code-where-were-we
description: Refresh Claude Code's memory at the start of a new session by gathering context from chat history, git commits, issue trackers, planning files, and devlogs. Use when starting a new session on an existing project, when the user asks "where were we?", "what were we working on?", "catch me up", "resume", or similar requests to understand recent project activity.
---

# Where Were We?

Gather and synthesize context from multiple sources to understand recent project activity.

## Workflow

### 1. Determine Project Path

```bash
PROJECT_PATH=$(pwd)
# Convert to chat history directory name (replace / with -)
CHAT_DIR=~/.claude/projects/-${PROJECT_PATH//\//-}
```

Example: `/home/user/code/myproject` → `~/.claude/projects/-home-user-code-myproject`

### 2. Gather Context from All Sources

Check each source in parallel where possible.

#### Chat History

```bash
# Find recent session files
ls -lt "$CHAT_DIR"/*.jsonl 2>/dev/null | head -5

# Extract recent messages from the most recent session (replace SESSIONFILE with actual path)
tail -200 SESSIONFILE.jsonl | jq -r 'select(.type == "human" or .type == "assistant") | .message.content[0].text // empty' 2>/dev/null | tail -50
```

Look for: decisions made, problems solved, features implemented, next steps discussed.

#### Git History

```bash
# Check if git repo exists
if [ -d .git ]; then
  git log --oneline -15
  git log --pretty=format:"%h %s (%ar)" -10
fi
```

For PRs (if using GitHub):
```bash
gh pr list --state all --limit 5 2>/dev/null
```

#### Issue Tracker

Ask the user what they use if unclear. Common options:

- **GitHub Issues**: `gh issue list --limit 10`
- **Beads**: `bd list`
- **Linear**: Check for `.linear` config
- **Other**: Ask user

#### Planning Files

```bash
# Check for planning documents
ls -la ~/.claude/plans/ 2>/dev/null
find . -maxdepth 2 -name "*.md" -type f | xargs grep -l -i "plan\|implementation\|todo" 2>/dev/null | head -10
```

#### Devlog / Changelog

```bash
# Check for devlog or changelog
for f in DEVLOG.md devlog.md CHANGELOG.md changelog.md; do
  [ -f "$f" ] && tail -100 "$f"
done
```

### 3. Synthesize and Present

Combine findings into a concise summary:

1. **Recent work** - What was accomplished in the last session(s)
2. **Current state** - Where the project stands now (branch, open PRs, pending issues)
3. **Next steps** - Any planned work or open items mentioned

Keep the summary brief and actionable. The goal is to get the human and Claude oriented quickly so work can continue.
