#!/usr/bin/env python3
"""PreToolUse hook on Bash, Read, Grep and Glob: only the bead named for a protected folder may read it.

Why: a set of items that must stay unseen (held-out test items, sealed answers) is kept unseen by instruction
alone until the first agent reads it by mistake. This makes the folder unreadable to everyone else.

The folders are `protected_folders` in hive/project.json, empty by default:
  "protected_folders": [{"path": "~/held-out", "label": "held-out-check", "lead_may_read": false}]
`path` may start with ~ or name $HOME; a relative path is taken from the repo root. Keep the folder outside the
repo, because a recursive search of any folder above it is refused too.

What it refuses, for every folder in the list:
- Read of a file in it; Grep or Glob in it, or a Grep or Glob that would reach into it from a folder above it.
- A Bash command that names the folder or anything in it in any form (~, $HOME, a variable set in the same
  command, a relative path after `cd`, a glob that matches it, a symlink that resolves into it), whatever the
  program (cat, ls, grep, python -c ...), and a recursive listing or search (grep -r, rg, find, tree, du, ls -R)
  of a folder above it.
- A sub-agent's bd command that adds a protected label to a bead: only the lead labels the one bead that may read.
It allows the call only when the caller may read the folder:
- a sub-agent whose spawn line (`Do bead <id>`) names a bead that carries the folder's label and is in progress;
- the main session (the lead) only when the folder's entry says `"lead_may_read": true`.

How the caller is known: Claude Code passes a sub-agent's tool calls to hooks with its `agent_id`, and keeps
each sub-agent's transcript at <session transcript without .jsonl>/subagents/agent-<agent_id>.jsonl; the first
line of that file is the spawn prompt. The hook reads the bead id from it and asks bd for the bead's labels. If
the transcript cannot be found or read, or bd fails, the call is refused (fail closed).

Weaknesses, said plainly: the transcript layout is Claude Code's, not a documented interface; if it changes,
every sub-agent is refused until this hook follows it. An agent that rewrites its own transcript's first line,
or hides a path from the command text (built from pieces at run time, or encoded), gets past the check. It stops
mistakes and casual reads, not a determined agent.
"""
from __future__ import annotations

import fnmatch
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import project  # noqa: E402

TOOLS = {"Bash", "Read", "Grep", "Glob"}
SPAWN_LINE = re.compile(r"\bDo bead ([A-Za-z0-9][\w-]*(?:\.\d+)*)")
SPLIT = re.compile(r"&&|\|\|?|;|\n")
WORD = re.compile(r"[^\s'\"(),;:<>|&`=]+")
ASSIGN = re.compile(r"(?:^|[\s;&|(])(?:export\s+)?([A-Za-z_]\w*)=(['\"]?)([^\s;&|'\"]+)\2")
VAR = re.compile(r"\$\{?([A-Za-z_]\w*)\}?")
CD = re.compile(r"^\s*(?:cd|pushd)\s+(['\"]?)([^\s'\"]+)\1\s*$")
RECURSIVE = re.compile(
    r"(^|[\s(/])(rg|ag|ack|fd|find|tree|du|rsync|tar|zip)(\s|$)|(^|[\s(/])(e?grep|ugrep)(\s[^\n]*?)?\s-\w*[rR]"
    r"|--recursive|(^|[\s(/])ls(\s[^\n]*?)?\s-\w*R|(^|[\s(/])cp(\s[^\n]*?)?\s-\w*[rRa]|os\.walk|rglob|\bglob\(|\*\*")
GLOB_CHARS = re.compile(r"[*?\[]")

READ_REASON = (
    "Refused: {folder} is a protected folder (hive/project.json \"protected_folders\"). Only an agent spawned on a "
    "bead labelled {label}{lead} may read or list it. Do not retry another way; if your bead needs it, write a "
    "LEAD: note on your bead."
)
UNKNOWN_REASON = (
    "Refused: {folder} is a protected folder, and this hook could not tell which bead you were spawned on "
    "({why}), so it refuses. Do not retry another way; write a LEAD: note on your bead."
)
LABEL_REASON = (
    "Refused: {label} is the label that lets a bead's agent read a protected folder (hive/project.json "
    "\"protected_folders\"); only the lead adds it. Write a LEAD: note on your bead instead."
)


def folders(cfg: dict) -> list[dict]:
    out = []
    for e in cfg.get("protected_folders") or []:
        if not isinstance(e, dict) or not e.get("path") or not e.get("label"):
            continue
        p = os.path.expanduser(expand(str(e["path"]), os.environ))
        p = os.path.realpath(p if os.path.isabs(p) else str(project.ROOT / p))
        out.append({**e, "real": p.rstrip("/") or "/"})
    return out


def expand(text: str, env) -> str:
    return VAR.sub(lambda m: env.get(m.group(1), m.group(0)), text)


def resolve(word: str, cwd: str, env) -> str:
    p = os.path.expanduser(expand(word, env))
    return os.path.realpath(p if os.path.isabs(p) else os.path.join(cwd or "/", p))


def inside(p: str, folder: str) -> bool:
    return p == folder or p.startswith(folder.rstrip("/") + "/")


def above(p: str, folder: str) -> bool:
    return p != folder and inside(folder, p)


def pattern_hits(pattern: str, folder: str) -> bool:
    """Whether a glob pattern (already absolute) names the folder or anything in it."""
    if fnmatch.fnmatch(folder, pattern) or fnmatch.fnmatch(folder + "/x", pattern):
        return True
    base = os.path.dirname(GLOB_CHARS.split(pattern, 1)[0]) or "/"
    if not (inside(base, folder) or inside(folder, base)):
        return False
    try:
        return any(inside(os.path.realpath(m), folder) for m in glob.glob(pattern, recursive=True)[:500])
    except (OSError, re.error):
        return False


def names(word: str, cwd: str, env, folder: str) -> bool:
    if GLOB_CHARS.search(word):
        return pattern_hits(resolve(word, cwd, env), folder)
    return inside(resolve(word, cwd, env), folder)


def spellings(folder: str) -> list[str]:
    home = os.path.realpath(os.path.expanduser("~"))
    out = [folder]
    if inside(folder, home) and folder != home:
        rest = folder[len(home):]
        out += ["~" + rest, "$HOME" + rest, "${HOME}" + rest]
    return out


def bash_hits(cmd: str, cwd: str, folder: str) -> str | None:
    """'read' when the command names the folder, 'above' when it searches a folder above it, else None."""
    for s in spellings(folder):
        if re.search(re.escape(s) + r"(?![\w.-])", cmd):
            return "read"
    env = dict(os.environ)
    for name, _, value in ASSIGN.findall(cmd):
        env[name] = os.path.expanduser(expand(value, env))
    here = cwd
    for seg in SPLIT.split(cmd):
        m = CD.match(seg)
        if m:
            here = resolve(m.group(2), here, env)
            if inside(here, folder):
                return "read"
            continue
        words = WORD.findall(seg)
        if any(names(w, here, env, folder) for w in words):
            return "read"
        if RECURSIVE.search(seg):
            paths = [resolve(w, here, env) for w in words if "/" in w or w in (".", "..", "~") or w.startswith("$")]
            if any(above(p, folder) for p in paths or [here]):
                return "above"
    return None


def tool_hits(tool: str, inp: dict, cwd: str, folder: str) -> bool:
    env = os.environ
    if tool == "Read":
        return bool(inp.get("file_path")) and inside(resolve(str(inp["file_path"]), cwd, env), folder)
    base = resolve(str(inp.get("path") or cwd or "."), cwd, env)
    if inside(base, folder):
        return True
    if tool == "Grep":
        return above(base, folder)
    pattern = str(inp.get("pattern") or "")
    full = resolve(pattern, base, env) if pattern else base
    return pattern_hits(full, folder) or (above(base, folder) and "**" in pattern)


def adds_label(cmd: str, labels: list[str]) -> str | None:
    for seg in SPLIT.split(cmd):
        if not re.search(r"(^|[\s/])bd\s", seg) or not re.search(r"label|create|\s-l\b|--set", seg):
            continue
        for label in labels:
            if re.search(r"(?<![\w:-])" + re.escape(label) + r"(?![\w-])", seg):
                return label
    return None


def spawn_prompt(data: dict) -> str:
    aid = str(data.get("agent_id") or "")
    paths = [data.get("agent_transcript_path")]
    tp = data.get("transcript_path")
    if tp:
        t = Path(str(tp))
        paths += [t.with_suffix("") / "subagents" / f"agent-{aid}.jsonl",
                  t.parent / str(data.get("session_id") or t.stem) / "subagents" / f"agent-{aid}.jsonl"]
    for p in paths:
        if not p or not Path(p).is_file():
            continue
        with open(p, encoding="utf-8") as f:
            first = json.loads(f.readline())
        if str(first.get("agentId") or aid) != aid:
            continue
        content = (first.get("message") or {}).get("content")
        if isinstance(content, list):
            content = "\n".join(str(c.get("text") or "") for c in content if isinstance(c, dict))
        return str(content or "")
    raise OSError("no transcript for agent " + aid)


def caller_bead(data: dict) -> tuple[dict | None, str]:
    """(the caller's bead from bd, or None, and why not)."""
    try:
        m = SPAWN_LINE.search(spawn_prompt(data))
    except (OSError, ValueError) as e:
        return None, f"its transcript could not be read: {str(e)[:80]}"
    if not m:
        return None, "its spawn prompt names no bead"
    for cwd in dict.fromkeys([str(data.get("cwd") or ""), str(project.ROOT)]):
        try:
            r = subprocess.run(["bd", "show", m.group(1), "--json"], cwd=cwd or None, capture_output=True,
                               text=True, timeout=20)
            shown = json.loads(r.stdout or "null") if r.returncode == 0 else None
        except (OSError, ValueError, subprocess.TimeoutExpired):
            shown = None
        bead = (shown[0] if isinstance(shown, list) and shown else shown) or None
        if isinstance(bead, dict) and bead.get("id"):
            return bead, ""
    return None, f"bd could not show {m.group(1)}"


def decide(data: dict, cfg: dict) -> str | None:
    """The refusal text, or None to let the call through."""
    tool = data.get("tool_name")
    if tool not in TOOLS:
        return None
    entries = folders(cfg)
    if not entries:
        return None
    inp = data.get("tool_input") or {}
    cwd = str(data.get("cwd") or project.ROOT)
    agent = bool(data.get("agent_id"))
    if tool == "Bash" and agent:
        label = adds_label(str(inp.get("command") or ""), [e["label"] for e in entries])
        if label:
            return LABEL_REASON.format(label=label)
    hit = [e for e in entries if (bash_hits(str(inp.get("command") or ""), cwd, e["real"]) if tool == "Bash"
                                  else tool_hits(tool, inp, cwd, e["real"]))]
    bead, why = None, ""
    for e in hit:
        lead = ", or the lead" if e.get("lead_may_read") else ""
        if not agent:
            if e.get("lead_may_read"):
                continue
            return READ_REASON.format(folder=e["path"], label=e["label"], lead=lead)
        if bead is None and not why:
            bead, why = caller_bead(data)
        if bead is None:
            return UNKNOWN_REASON.format(folder=e["path"], why=why)
        if e["label"] not in (bead.get("labels") or []) or bead.get("status") != "in_progress":
            return READ_REASON.format(folder=e["path"], label=e["label"], lead=lead)
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    reason = decide(data, project.config())
    if reason:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
