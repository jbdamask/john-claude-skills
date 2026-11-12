#!/usr/bin/env python3
"""PreToolUse hook on Bash: refuse any shell command that contains an email address.

Why: an address typed into a command (a curl User-Agent, a git config) ends up in logs and transcripts, and makes
Claude Code ask a person to approve the command by hand. A service that needs a contact address gets it from a
script that reads it from configuration, never from the command's text.
"""
import json
import re
import sys

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

REASON = ("Refused: this command contains an email address. Never type an email address in a command; if a "
          "service needs a contact address, a script reads it from configuration. Rewrite the command without it.")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    if not EMAIL.search((data.get("tool_input") or {}).get("command") or ""):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": REASON}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
