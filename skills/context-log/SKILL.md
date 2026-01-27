---
name: context-log
description: Log context window usage to context-log.jsonl in the current directory. Triggers on "log context" anywhere in the prompt.
---

# Context Log

When you see "log context" in the user's prompt, log context usage after completing the main task.

## Action

Run the logging script with a brief summary of what was requested:

```bash
python3 ~/.claude/skills/context-log/scripts/log_context.py --prompt-summary "<2-5 word summary>"
```

The script:
1. Reads the session transcript from `~/.claude/projects/`
2. Extracts **exact** cumulative token usage from the most recent API response
3. Estimates category breakdown based on known baselines
4. Appends to `context-log.jsonl` in the current directory

## How It Works

Claude Code's API returns cumulative token usage in each response. The script:
- Finds the transcript JSONL for the current session (via `$CLAUDE_SESSION_ID`)
- Filters out sidechain (agent) calls
- Gets the most recent main chain entry
- Extracts: `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`

## Output Format

```json
{
  "timestamp": "2026-01-26T23:45:00Z",
  "session_id": "abc-123-uuid",
  "model": "claude-opus-4-5-20251101",
  "prompt_summary": "Add user authentication",
  "total_tokens": 24500,
  "max_tokens": 200000,
  "usage_percent": 12.25,
  "usage": {
    "input_tokens": 1,
    "cache_read_input_tokens": 24000,
    "cache_creation_input_tokens": 499,
    "output_tokens": 150
  },
  "categories": {
    "system_prompt": {"tokens": 2300, "percent": 1.15},
    "system_tools": {"tokens": 16600, "percent": 8.3},
    "custom_agents": {"tokens": 100, "percent": 0.05},
    "memory_files": {"tokens": 500, "percent": 0.25},
    "skills": {"tokens": 2600, "percent": 1.3},
    "messages": {"tokens": 2400, "percent": 1.2},
    "free_space": {"tokens": 130500, "percent": 65.25},
    "autocompact_buffer": {"tokens": 45000, "percent": 22.5}
  }
}
```

## Data Accuracy

| Field | Accuracy | Source |
|-------|----------|--------|
| total_tokens | **Exact** | Cumulative from API response |
| usage breakdown | **Exact** | API response fields |
| categories | Estimated | Based on known baselines |

## Important

- Complete the user's main request first, then run the script
- Keep prompt_summary concise - for correlating context with features later
- Do not mention logging to the user unless they ask
