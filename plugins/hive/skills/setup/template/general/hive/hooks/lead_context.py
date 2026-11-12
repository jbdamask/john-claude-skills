#!/usr/bin/env python3
"""Give the lead its runbook, hive/LEAD.md, at the right moments. Never blocks.

  lead_context.py start    SessionStart: the whole of hive/LEAD.md, only when the session runs with HIVE_ROLE=lead,
                           so a plain `claude` never boots as a second lead.
  lead_context.py checkin  UserPromptSubmit: the "Check-in" section, only when the prompt starts "HIVE CHECK-IN".

Claude Code cuts a hook's added text at about 10,000 characters. Over BUDGET, the hook sends a short instruction
to read the file instead, so the lead never gets a silently cut-short runbook.
"""
import json
import os
import sys
from pathlib import Path

BUDGET = 8500
LEAD = Path(__file__).resolve().parents[1] / "LEAD.md"


def section(text: str, title: str) -> str:
    out, keep = [], False
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            keep = line[3:].startswith(title)
        if keep:
            out.append(line)
    return "".join(out)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "start":
        if os.environ.get("HIVE_ROLE") != "lead":
            return 0
        event, intro = "SessionStart", "You are the lead. This is the current hive/LEAD.md; follow it."
        title = None
    elif mode == "checkin":
        try:
            prompt = json.load(sys.stdin).get("prompt", "")
        except Exception:
            return 0
        if not prompt.lstrip().startswith("HIVE CHECK-IN"):
            return 0
        event, intro = "UserPromptSubmit", "Check-in: do every step of this section of the current hive/LEAD.md, in order."
        title = "Check-in"
    else:
        return 0
    try:
        text = LEAD.read_text(encoding="utf-8")
        body = text if title is None else section(text, title)
    except OSError:
        body = ""
    ctx = intro + "\n\n" + body
    if not body or len(ctx) > BUDGET:
        ctx = intro + f"\n\nThe text is too large to add or missing. Before anything else, read {LEAD}."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": ctx}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
