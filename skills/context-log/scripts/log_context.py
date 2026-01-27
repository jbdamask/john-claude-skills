#!/usr/bin/env python3
"""
Calculate and log Claude Code context usage from session transcript.

Reads the JSONL transcript file to get exact cumulative token counts,
then logs to context-log.jsonl in the current directory.

Usage:
  python3 log_context.py [--session-id UUID] [--output-dir PATH] [--prompt-summary "summary"]

If --session-id is not provided, uses CLAUDE_SESSION_ID env var.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def find_transcript_file(session_id: str) -> Optional[Path]:
    """Find the transcript JSONL file for a given session ID."""
    claude_dir = Path.home() / ".claude" / "projects"

    if not claude_dir.exists():
        return None

    # Search all project directories for the session file
    for project_dir in claude_dir.iterdir():
        if project_dir.is_dir():
            transcript = project_dir / f"{session_id}.jsonl"
            if transcript.exists():
                return transcript

    return None


def get_context_usage(transcript_path: Path) -> Optional[dict]:
    """
    Extract cumulative token usage from transcript.

    Based on Claude Code's method:
    - Skip sidechain (agent) entries
    - Skip entries without usage data
    - Get the most recent main chain entry by timestamp
    - API returns cumulative usage, so we only need the latest entry
    """
    entries = []

    with open(transcript_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Skip sidechain (agent) calls
            if entry.get('isSidechain', False):
                continue

            # Skip entries without message or usage data
            message = entry.get('message', {})
            usage = message.get('usage')
            if not usage:
                continue

            # Skip entries without timestamp
            timestamp = entry.get('timestamp')
            if not timestamp:
                continue

            entries.append({
                'timestamp': timestamp,
                'usage': usage,
                'model': message.get('model', 'unknown'),
                'session_id': entry.get('sessionId', 'unknown')
            })

    if not entries:
        return None

    # Sort by timestamp and get the most recent
    entries.sort(key=lambda x: x['timestamp'], reverse=True)
    latest = entries[0]

    usage = latest['usage']
    input_tokens = usage.get('input_tokens', 0)
    cache_read = usage.get('cache_read_input_tokens', 0)
    cache_creation = usage.get('cache_creation_input_tokens', 0)
    output_tokens = usage.get('output_tokens', 0)

    # Total context = all input tokens (cumulative from API)
    total_input = input_tokens + cache_read + cache_creation

    return {
        'model': latest['model'],
        'session_id': latest['session_id'],
        'input_tokens': input_tokens,
        'cache_read_input_tokens': cache_read,
        'cache_creation_input_tokens': cache_creation,
        'output_tokens': output_tokens,
        'total_input': total_input,
        'total_tokens': total_input + output_tokens
    }


def estimate_categories(total_input: int, max_tokens: int = 200000) -> dict:
    """
    Estimate category breakdown based on known Claude Code baselines.

    These are approximations - the actual categorical data is computed
    client-side by Claude Code and not available via API.
    """
    # Known baseline values (tokens) - these are estimates
    SYSTEM_PROMPT = 2300
    SYSTEM_TOOLS = 16600
    CUSTOM_AGENTS = 100
    MEMORY_FILES = 500
    SKILLS = 2600

    # Buffer is 22.5% of max context
    autocompact_buffer = int(max_tokens * 0.225)

    # Baseline total (what we expect without messages)
    baseline_total = SYSTEM_PROMPT + SYSTEM_TOOLS + CUSTOM_AGENTS + MEMORY_FILES + SKILLS

    # Messages = total - baseline
    messages = max(0, total_input - baseline_total)

    # Scale down if total is less than baseline
    if total_input < baseline_total and baseline_total > 0:
        scale = total_input / baseline_total
        SYSTEM_PROMPT = int(SYSTEM_PROMPT * scale)
        SYSTEM_TOOLS = int(SYSTEM_TOOLS * scale)
        CUSTOM_AGENTS = int(CUSTOM_AGENTS * scale)
        MEMORY_FILES = int(MEMORY_FILES * scale)
        SKILLS = int(SKILLS * scale)
        messages = 0

    # Free space
    free_space = max(0, max_tokens - total_input - autocompact_buffer)

    def pct(val):
        return round((val / max_tokens) * 100, 2) if max_tokens > 0 else 0

    return {
        "system_prompt": {"tokens": SYSTEM_PROMPT, "percent": pct(SYSTEM_PROMPT)},
        "system_tools": {"tokens": SYSTEM_TOOLS, "percent": pct(SYSTEM_TOOLS)},
        "custom_agents": {"tokens": CUSTOM_AGENTS, "percent": pct(CUSTOM_AGENTS)},
        "memory_files": {"tokens": MEMORY_FILES, "percent": pct(MEMORY_FILES)},
        "skills": {"tokens": SKILLS, "percent": pct(SKILLS)},
        "messages": {"tokens": messages, "percent": pct(messages)},
        "free_space": {"tokens": free_space, "percent": pct(free_space)},
        "autocompact_buffer": {"tokens": autocompact_buffer, "percent": pct(autocompact_buffer)}
    }


def main():
    parser = argparse.ArgumentParser(description='Log Claude Code context usage')
    parser.add_argument('--session-id', help='Session UUID (default: CLAUDE_SESSION_ID env var)')
    parser.add_argument('--output-dir', default='.', help='Output directory for context-log.jsonl')
    parser.add_argument('--prompt-summary', default='', help='Brief summary of the prompt/task')
    args = parser.parse_args()

    # Get session ID
    session_id = args.session_id or os.environ.get('CLAUDE_SESSION_ID')
    if not session_id:
        print("Error: No session ID. Provide --session-id or set CLAUDE_SESSION_ID", file=sys.stderr)
        sys.exit(1)

    # Find transcript file
    transcript_path = find_transcript_file(session_id)
    if not transcript_path:
        print(f"Error: Could not find transcript for session {session_id}", file=sys.stderr)
        sys.exit(1)

    # Get context usage
    usage = get_context_usage(transcript_path)
    if not usage:
        print(f"Error: No usage data found in transcript", file=sys.stderr)
        sys.exit(1)

    max_tokens = 200000
    total_input = usage['total_input']
    usage_percent = round((total_input / max_tokens) * 100, 2)

    # Build log entry
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": usage['session_id'],
        "model": usage['model'],
        "prompt_summary": args.prompt_summary,
        "total_tokens": total_input,
        "max_tokens": max_tokens,
        "usage_percent": usage_percent,
        "usage": {
            "input_tokens": usage['input_tokens'],
            "cache_read_input_tokens": usage['cache_read_input_tokens'],
            "cache_creation_input_tokens": usage['cache_creation_input_tokens'],
            "output_tokens": usage['output_tokens']
        },
        "categories": estimate_categories(total_input, max_tokens)
    }

    # Write to context-log.jsonl
    output_file = Path(args.output_dir) / "context-log.jsonl"
    with open(output_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

    # Report
    print(f"Logged: {total_input:,} / {max_tokens:,} tokens ({usage_percent}%)")


if __name__ == "__main__":
    main()
