#!/usr/bin/env python3
"""PreToolUse hook on Bash: an agent never pushes to main itself; it lands with hive/tools/land.py.

Why: an agent that pushes by hand can push after a failed or stale test run. land.py merges main, runs the fast
tests on the merge and pushes only if they pass, one landing at a time.

What it refuses, for a subagent (the hook input has an agent_id): a `git push` that could update main: no
refspec, a refspec whose target is main (`main`, `HEAD:main`, `refs/heads/main`, `+main`), `--all` or `--mirror`.
Pushing another branch passes. The lead and a person's own session pass. The main branch is `main_branch` in
hive/project.json (default main).
"""
import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import project  # noqa: E402

SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
VALUE_FLAGS = {"-o", "--push-option", "--repo", "--receive-pack", "--exec", "-C", "-c"}

REASON = ("Refused: agents do not push to {main} themselves. Run `python3 hive/tools/land.py` from your tree's "
          "root: it merges {main}, runs the fast tests on the merge and pushes only if they pass. Do not retry "
          "another way.")


def segments(cmd: str) -> list[list[str]]:
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


def pushes_main(cmd: str, main: str = "main") -> bool:
    try:
        segs = segments(cmd)
    except ValueError:
        return bool(re.search(r"\bgit\b[^;&|]*\bpush\b", cmd))  # unreadable: refuse what looks like a push
    for seg in segs:
        words = [w for w in seg if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w)]
        if not words or Path(words[0]).name != "git":
            continue
        i = 1
        while i < len(words) and words[i].startswith("-"):
            i += 2 if words[i] in ("-C", "-c") else 1
        if i >= len(words) or words[i] != "push":
            continue
        args, j = [], i + 1
        while j < len(words):
            w = words[j]
            if w in ("--all", "--mirror"):
                return True
            if w in VALUE_FLAGS:
                j += 2
                continue
            if not w.startswith("-"):
                args.append(w)
            j += 1
        refspecs = args[1:]
        if not refspecs:
            return True
        for r in refspecs:
            target = r.lstrip("+").split(":")[-1]
            if target in (main, f"refs/heads/{main}") or (":" not in r and r.lstrip("+") in ("HEAD", main)):
                return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash" or not data.get("agent_id"):
        return 0
    branch = project.config().get("main_branch", "main")
    if not pushes_main(str((data.get("tool_input") or {}).get("command") or ""), branch):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": REASON.format(main=branch)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
