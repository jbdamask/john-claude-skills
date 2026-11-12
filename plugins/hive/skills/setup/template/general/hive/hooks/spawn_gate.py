#!/usr/bin/env python3
"""PreToolUse hook on the Agent tool: refuse a spawn that cannot or should not start.

The bead is the one in the spawn line (`Do bead <id>`, hive/LEAD.md "Spawning"). A prompt with no spawn line
(an agent's own sub-agents) passes, unless its agent type is a role that needs a bead.

1. Ready: a bead not in `bd ready` (open blocking dependency, claimed, deferred, closed) is refused with the
   reason, because a spawn that cannot start costs an agent run that does nothing. To respawn a dead agent's bead,
   `bd unclaim <id>` first.
2. Role: a bead labelled role:<name> must be spawned with that agent type, and an agent type that hive/ROLES.json
   says needs a bead must be spawned on a bead with its label; otherwise the agent works without the role's brief
   and nothing else notices.
3. Notes against text: a bead whose notes overrule its title, description or acceptance (a LEAD, DECIDED,
   CORRECTION, SCOPE or WAIT note saying "not <path or id>" the text still names, overriding the Read list or the
   scope, or a wait with no defer date) is refused until the note is folded into the bead and a `SPEC-OK:` note
   is added; notes before the last SPEC-OK are settled.

Every decision is appended to ~/.hive/<slug>/spawn_gate.jsonl (HIVE_SPAWN_GATE_LOG overrides). If bd fails,
the spawn goes through and the log says bd_error.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import project  # noqa: E402

SPAWN_LINE = re.compile(r"\bDo bead ([A-Za-z0-9][\w-]*(?:\.\d+)*)")
TOOLS = {"Agent", "Task"}
ROLES_FILE = project.ROOT / "hive" / "ROLES.json"


def bead_roles() -> set[str]:
    try:
        return {r["name"] for r in json.loads(ROLES_FILE.read_text(encoding="utf-8"))["roles"] if r.get("needs_bead")}
    except (OSError, ValueError, KeyError):
        return set()


def role_mismatch(agent_type: str, labels: list, known: set[str]) -> str | None:
    want = next((l[5:] for l in labels or [] if isinstance(l, str) and l.startswith("role:")), None)
    if want and agent_type != want:
        return (f"the bead is labelled role:{want} but the spawn's agent type is {agent_type or 'general-purpose'}; "
                f"spawn it with subagent_type \"{want}\"")
    if not want and agent_type in known:
        return (f"agent type {agent_type} needs a bead labelled role:{agent_type}; "
                f"add the label (bd update <id> --add-label role:{agent_type}) or spawn a plain one-shot agent")
    return None


def _bd(args: list[str], cwd: str):
    r = subprocess.run(["bd", *args], cwd=cwd or None, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise OSError(r.stderr.strip()[:200])
    return json.loads(r.stdout or "null")


def _one(shown):
    return (shown[0] if isinstance(shown, list) and shown else shown) or {}


def why_not_ready(bid: str, cwd: str) -> str | None:
    ready = _bd(["ready", "--json", "--limit", "0", "--brief"], cwd) or []
    if any(isinstance(b, dict) and b.get("id") == bid for b in ready):
        return None
    b = _one(_bd(["show", bid, "--json"], cwd))
    if not isinstance(b, dict) or not b.get("id"):
        return f"{bid} is not a known bead"
    deps = [d.get("id") for d in b.get("dependencies") or []
            if d.get("dependency_type") == "blocks" and d.get("status") != "closed"]
    if deps:
        return f"{bid} has open dependencies: {', '.join(deps)}"
    status = b.get("status") or "unknown"
    if status == "in_progress" or b.get("assignee"):
        return f"{bid} is claimed by {b.get('assignee') or 'someone'} ({status})"
    if b.get("defer_until"):
        return f"{bid} is deferred until {b['defer_until']}"
    return f"{bid} is {status}, not in bd ready"


OVERRULING = re.compile(r"^\s*(LEAD|DECIDED|CORRECTION|SCOPE|WAIT)\b", re.I)
SETTLED = re.compile(r"^\s*SPEC-OK\b")
NOT_TOKEN = re.compile(r"\b(?:not|instead of|rather than|replaces|no longer)\s+[`'\"(]?([\w./~-]{4,})", re.I)
OVERRIDES = re.compile(r"\boverrid\w*|\bsupersed\w*|\bcorrection\b", re.I)
READ_LIST = re.compile(r"\bRead( list| line|:)")
WAIT = re.compile(r"\b(wait|hold|start|resume|not before)\w*\b[^.\n]{0,40}\b(until|after|on|from)\b[^.\n]{0,20}"
                  r"(20\d\d-\d\d-\d\d)", re.I)


def stale_text(b: dict, today: str | None = None) -> list[str]:
    """Where a bead's notes overrule its title, description or acceptance; [] when they do not."""
    today = today or time.strftime("%Y-%m-%d", time.gmtime())
    task = "\n".join(str(b.get(k) or "") for k in ("title", "description", "acceptance_criteria"))
    lines = str(b.get("notes") or "").splitlines()
    last_ok = max((i for i, ln in enumerate(lines) if SETTLED.match(ln)), default=-1)
    out = []
    for ln in lines[last_ok + 1:]:
        if not OVERRULING.match(ln):
            continue
        quote = ln.strip()[:90]
        olds = [t.rstrip(".,)") for t in NOT_TOKEN.findall(ln)]
        olds = [t for t in olds if re.search(r"[\d/.]", t) and t in task]
        if olds:
            out.append(f"target: the note says not {olds[0]}, the task text still names it ('{quote}')")
        elif READ_LIST.search(ln) and OVERRIDES.search(ln):
            out.append(f"Read list: a note overrides it ('{quote}')")
        elif OVERRIDES.search(ln):
            out.append(f"scope: a note overrides the task text ('{quote}')")
        w = WAIT.search(ln)
        if w and w.group(3) > today and not b.get("defer_until"):
            out.append(f"start time: a note says wait until {w.group(3)}, with no defer date ('{quote}')")
    return out


def log(rec: dict) -> None:
    path = Path(os.environ.get("HIVE_SPAWN_GATE_LOG") or project.hive_home() / "spawn_gate.jsonl")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rec}) + "\n")
    except OSError:
        pass


def deny(text: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": text}}))


def deny_ready(reason: str) -> None:
    deny(f"Refused spawn: {reason}. Spawn only bd ready work (hive/LEAD.md \"Spawning\"): wait for its "
         "dependencies, or, if the agent with the claim is dead, run bd unclaim <id> first.")


def deny_role(reason: str) -> None:
    deny(f"Refused spawn: {reason} (roles: hive/ROLES.json; hive/LEAD.md \"Spawning\").")


def deny_stale(bid: str, fields: list[str]) -> None:
    deny(f"Refused spawn: {bid}'s task text disagrees with its own notes: " + "; ".join(fields[:3])
         + f". Fold the note into the bead (bd update {bid} --title/--description/--acceptance, or bd defer {bid} "
         f"--until for a wait), then bd note {bid} \"SPEC-OK: <what changed>\" and spawn again.")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in TOOLS:
        return 0
    inp = data.get("tool_input") or {}
    prompt = inp.get("prompt") or ""
    atype = inp.get("subagent_type") or "general-purpose"
    cwd = data.get("cwd") or ""
    known = bead_roles()
    m = SPAWN_LINE.search(prompt)
    if not m:
        if atype in known:
            log({"decision": "role_mismatch", "agent_type": atype, "reason": "no bead in the prompt"})
            deny_role(f"agent type {atype} needs a bead labelled role:{atype}, and the prompt names no bead")
            return 0
        log({"decision": "no_bead", "agent_type": atype})
        return 0
    bid = m.group(1)
    try:
        reason = why_not_ready(bid, cwd)
        bead = _one(_bd(["show", bid, "--json"], cwd)) if reason is None else {}
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        log({"decision": "bd_error", "bead": bid, "error": str(e)[:200]})
        return 0
    if reason:
        log({"decision": "refused", "bead": bid, "reason": reason})
        deny_ready(reason)
        return 0
    wrong = role_mismatch(atype, bead.get("labels") or [], known)
    if wrong:
        role = next((l[5:] for l in bead.get("labels") or [] if str(l).startswith("role:")), None)
        log({"decision": "role_mismatch", "bead": bid, "agent_type": atype, "role": role, "reason": wrong})
        deny_role(wrong)
        return 0
    fields = stale_text(bead)
    if fields:
        log({"decision": "stale_text", "bead": bid, "fields": fields})
        deny_stale(bid, fields)
        return 0
    log({"decision": "passed", "bead": bid, "agent_type": atype})
    return 0


if __name__ == "__main__":
    sys.exit(main())
