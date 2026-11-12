#!/usr/bin/env python3
"""PreToolUse hook: refuse `bd close` (or `bd done`) while a bead that blocks it is still open.

Why: a bead closed past an open blocker hides unfinished work. bd itself does not refuse it, so this hook does,
for every agent and the lead.

What counts: a dependency of type `blocks` whose status is not `closed` (`bd show <id> --json`). A blocker
closed in the same command counts as closed. `--force` does not get past it. A close whose reason says
superseded, duplicate, not needed or won't do is allowed. The way out is
the tracker's own: close the blocker first, or `bd dep remove <id> <blocker>` with a note saying why.
If bd fails or the bead is unknown, the hook lets the command through (bd reports the error itself).
"""
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Closes that are not "done" closes.
WASTE = re.compile(r"^(\w[\w ]{0,20}: )?(superseded|duplicate|not needed|won'?t (do|fix))\b", re.I)
QUICK = re.compile(r"\bbd\b.*\b(close|done)\b", re.S)
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n"}
GLOBAL_VALUE = {"-C", "--directory", "--db", "--database", "--actor", "--dolt-auto-commit"}
CLOSE_VALUE = {"-r", "--reason", "--reason-file", "--session", "--actor", "--db", "--database", "-C",
               "--directory", "--dolt-auto-commit"}


def _segments(cmd: str) -> list[list[str]]:
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=";&|()")
    lex.whitespace_split = True
    out, cur = [], []
    for tok in lex:
        if tok in SEPARATORS or set(tok) <= set(";&|()"):
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        out.append(cur)
    return out


def closes(cmd: str, depth: int = 0) -> list[dict]:
    """Every `bd close` in a shell command: {"ids", "reasons", "reason_files", "dir"}."""
    try:
        segs = _segments(cmd)
    except ValueError:
        return []
    found = []
    for seg in segs:
        i = 0
        while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
            i += 1  # leading VAR=value
        for j in range(i, len(seg)):
            tok = seg[j]
            if depth < 2 and " " in tok and QUICK.search(tok):
                found += closes(tok, depth + 1)  # zsh -c '...', with-key NAME '...'
        while i < len(seg) and Path(seg[i]).name != "bd":
            i += 1
        if i >= len(seg):
            continue
        i += 1
        bd_dir = None
        while i < len(seg) and seg[i].startswith("-"):
            flag = seg[i].split("=", 1)[0]
            if flag in ("-C", "--directory"):
                bd_dir = seg[i].split("=", 1)[1] if "=" in seg[i] else (seg[i + 1] if i + 1 < len(seg) else None)
            i += 2 if (seg[i] in GLOBAL_VALUE) else 1
        if i >= len(seg) or seg[i] not in ("close", "done"):
            continue
        rec = {"ids": [], "reasons": [], "reason_files": [], "dir": bd_dir}
        i += 1
        while i < len(seg):
            tok = seg[i]
            flag, eq, val = tok.partition("=")
            if tok.startswith("-") and flag in CLOSE_VALUE:
                if not eq:
                    val = seg[i + 1] if i + 1 < len(seg) else ""
                    i += 1
                if flag in ("-r", "--reason"):
                    rec["reasons"].append(val)
                elif flag == "--reason-file":
                    rec["reason_files"].append(val)
                elif flag in ("-C", "--directory"):
                    rec["dir"] = val
            elif not tok.startswith("-"):
                rec["ids"].append(tok)
            i += 1
        found.append(rec)
    return found


def _reason_text(rec: dict, cwd: str) -> list[str]:
    texts = list(rec["reasons"])
    for f in rec["reason_files"]:
        p = Path(f) if Path(f).is_absolute() else Path(cwd) / f
        try:
            texts.append(p.read_text(encoding="utf-8"))
        except OSError:
            pass
    return texts


def _show(ids: list[str], cwd: str, bd_dir: str | None) -> list[dict]:
    args = ["bd"] + (["-C", bd_dir] if bd_dir else []) + ["show", *ids, "--json"]
    try:
        r = subprocess.run(args, cwd=cwd or None, capture_output=True, text=True, timeout=20)
        data = json.loads(r.stdout or "[]")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return []
    return data if isinstance(data, list) else [data]


def open_blockers(rec: dict, cwd: str) -> dict[str, list[str]]:
    """{bead id: [open blocker ids]} for one close; empty when the close is allowed."""
    ids = rec["ids"]
    if not ids:
        return {}
    texts = _reason_text(rec, cwd)
    if texts and all(WASTE.match(t.strip()) for t in texts):
        return {}
    closing = set(ids)
    bad = {}
    for b in _show(ids, cwd, rec["dir"]):
        if not isinstance(b, dict):
            continue
        held = [d.get("id") for d in b.get("dependencies") or []
                if d.get("dependency_type") == "blocks" and d.get("status") != "closed"
                and d.get("id") not in closing and d.get("id") != b.get("id")]
        if held:
            bad[b.get("id")] = held
    return bad


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if not QUICK.search(cmd):
        return 0
    cwd = data.get("cwd") or ""
    bad = {}
    for rec in closes(cmd):
        bad.update(open_blockers(rec, cwd))
    if bad:
        print(json.dumps(deny(bad)))
    return 0


def deny(bad: dict[str, list[str]]) -> dict:
    what = "; ".join(f"{b} is blocked by {', '.join(h)}" for b, h in bad.items())
    reason = (f"Refused: {what} (still open). Never close a bead past an open blocker; --force does not get past this. Close the blocker first, or if the link is wrong, "
              "remove it with bd dep remove <id> <blocker> and a bd note saying why. If the bead is superseded "
              "or a duplicate, start the reason with that word.")
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}


if __name__ == "__main__":
    sys.exit(main())
