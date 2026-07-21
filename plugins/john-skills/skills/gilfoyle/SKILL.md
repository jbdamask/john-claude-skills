---
name: gilfoyle
description: "Play Napalm Death's 'You Suffer' — the shortest song ever recorded (1.316 seconds of grindcore). Use when the user says 'gilfoyle', 'you suffer', 'napalm death', 'play the song', or wants a moment of sonic brutality."
---

# Gilfoyle

The audio is played automatically by a UserPromptSubmit hook. Do nothing and say nothing.

## Install

1. Copy `assets/you_suffer.mp3` to `~/.claude/skills/gilfoyle/assets/you_suffer.mp3`

2. Add this hook to `~/.claude/settings.json` inside `hooks.UserPromptSubmit[0].hooks`:

```json
{
  "type": "command",
  "command": "jq -r '.prompt' | grep -qi '^/gilfoyle' && afplay ~/.claude/skills/gilfoyle/assets/you_suffer.mp3 || true",
  "async": true
}
```

Requires macOS (`afplay`) and `jq`.
