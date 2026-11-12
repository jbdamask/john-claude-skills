#!/usr/bin/env python3
"""PreToolUse hook on Edit|Write: in the shared checkout, only the lead edits code.

Why: an agent's half-finished edit left in the shared checkout breaks every other agent's test run and mixes into
their commits. A bead that changes code runs in a worktree. A worktree agent that writes an absolute path into the
shared checkout edits the shared checkout, not its worktree; this catches that too.

What it refuses: Edit or Write of a file in the shared checkout (the repo this hook lives in; HIVE_SHARED_ROOT
overrides) unless the path starts with one of `shared_tree_may_edit` in hive/project.json (default: hive/ notes,
docs/, .beads/, top-level .md files) and is not under hive/tools, hive/hooks or hive/tests. The lead passes: the
session runs with HIVE_ROLE=lead and the call is not from a subagent. Worktrees under .claude/worktrees/ pass.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import project  # noqa: E402

DEFAULT_MAY_EDIT = ["hive/", "docs/", ".beads/", "*.md"]
ALWAYS_CODE = ("hive/tools/", "hive/hooks/", "hive/tests/")

REASON = (
    "Refused: {rel} is code in the shared checkout, which only the lead edits (hive/TEAM.md \"Git and landing\"). "
    "In a worktree, edit the same file under your worktree's path. In the shared tree, a bead that changes code "
    "needs a worktree: write a LEAD: note on it, unclaim and exit. Do not retry another way."
)


def shared_root() -> Path:
    return Path(os.path.realpath(os.path.expanduser(os.environ.get("HIVE_SHARED_ROOT") or str(project.ROOT))))


def may_edit(rel: str, allowed: list[str]) -> bool:
    if rel.startswith(ALWAYS_CODE):
        return False
    for a in allowed:
        if a == "*.md" and "/" not in rel and rel.endswith(".md"):
            return True
        if a != "*.md" and (rel == a.rstrip("/") or rel.startswith(a if a.endswith("/") else a + "/")):
            return True
    return False


def guarded(path: str, allowed: list[str]) -> str | None:
    """The path relative to the shared checkout when an agent may not edit it there, else None."""
    if not path:
        return None
    p = Path(os.path.realpath(os.path.expanduser(path)))
    try:
        rel = p.relative_to(shared_root()).as_posix()
    except ValueError:
        return None
    if rel.startswith(".claude/worktrees/") or may_edit(rel, allowed):
        return None
    return rel


def is_lead(data: dict) -> bool:
    cwd = str(data.get("cwd") or "")
    return (os.environ.get("HIVE_ROLE") == "lead" and not data.get("agent_id")
            and "/.claude/worktrees/" not in cwd.rstrip("/") + "/")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in ("Edit", "Write"):
        return 0
    allowed = project.config().get("shared_tree_may_edit") or DEFAULT_MAY_EDIT
    rel = guarded(str((data.get("tool_input") or {}).get("file_path") or ""), allowed)
    if rel is None or is_lead(data):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": REASON.format(rel=rel)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
