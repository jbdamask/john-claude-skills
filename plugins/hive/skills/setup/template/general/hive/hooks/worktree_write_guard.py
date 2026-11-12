#!/usr/bin/env python3
"""PreToolUse hook on Bash: in a worktree, refuse writing a file through the shell.

Why: a file written through the shell (a heredoc, a redirect, sed -i) escapes the checks the Edit and Write
tools get, and a written rule against it was broken again and again; this hook refuses it with one message.

When: only when the call runs in a worktree (the hook input's cwd is under `.claude/worktrees/`). The lead and
shared-tree agents are never checked here.

What it refuses, when the file written is not under a scratch folder (~/.hive/<slug>/scratch/<name>/, or the
session scratchpad /tmp/claude-*) and not /dev/null or another /dev/ stream:
- a `>`, `>>`, `>|`, `&>` redirect, including a heredoc into a file (`cat > x <<EOF`);
- `tee <file>`;
- `sed -i` on a file;
- `python - <<EOF` (or `python3`, `.venv/bin/python`) whose heredoc body opens a file for writing
  (open(..., "w"/"a"/"x"), write_text, write_bytes), unless the body names a scratch folder.
Reading commands, tests, git, bd and fd duplication (2>&1) pass. A command the parser cannot read passes (the
isolation guard still checks it).
"""
import json
import os
import re
import shlex
import sys

REASON = (
    "Refused: write files with the Edit or Write tool in a worktree (the agent brief, \"Never\"). "
    "This command writes a file through the shell ({what}). Shell output may go only to your "
    "scratch folder ~/.hive/<project>/scratch/<your name>/ or /dev/null. Redo it once: the Edit or Write tool for "
    "the file, then the rest as a plain command; note GUARD on your bead."
)

HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
REDIRECTS = {">", ">>", ">|", "&>", "&>>", ">&", ">>&"}
SEPARATORS = {"|", "||", "&&", ";", "&", "|&", ";;", "(", ")"}
PY_WRITE = re.compile(r"""open\([^)]*['"][wax]b?\+?['"]|\.write_text\(|\.write_bytes\(|mode\s*=\s*['"][wax]""")
PYTHON = re.compile(r"(^|/)python[0-9.]*$")
SCRATCH = re.compile(r"/\.hive/[^/]+/scratch/[^/]+(/|$)|^/(private/)?tmp/claude-[^/]+(/|$)")


def _expand(path: str) -> str:
    home = os.path.expanduser("~")
    for pre in ("~", "$HOME", "${HOME}"):
        if path == pre or path.startswith(pre + "/"):
            return home + path[len(pre):]
    return path


def allowed_target(path: str) -> bool:
    p = _expand(path)
    if p.startswith("/dev/"):
        return True
    return bool(SCRATCH.search(os.path.normpath(p)) if p.startswith("/") else False)


def split_heredocs(cmd: str) -> tuple[str, list[str]]:
    """(the command lines without heredoc bodies, the bodies)."""
    lines, bodies, out = cmd.split("\n"), [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        i += 1
        for m in HEREDOC.finditer(line):
            if line[max(0, m.start() - 1):m.start()] == "<":
                continue  # a here-string (<<<) has no body
            delim, body = m.group(2), []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            i += 1  # the delimiter line
            bodies.append("\n".join(body))
    return "\n".join(out), bodies


def segments(text: str) -> list[list[str]]:
    lex = shlex.shlex(text.replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""
    segs, cur = [], []
    for tok in lex:
        if tok in SEPARATORS:
            if cur:
                segs.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        segs.append(cur)
    return segs


def _command(seg: list[str]) -> tuple[str, list[str]]:
    """(command word, its arguments), skipping VAR=value prefixes and redirects."""
    i = 0
    while i < len(seg) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", seg[i]):
        i += 1
    words, j = [], i
    while j < len(seg):
        if seg[j] in REDIRECTS or seg[j] in ("<", "<<", "<<-", "<<<"):
            j += 2
            continue
        if seg[j].isdigit() and j + 1 < len(seg) and seg[j + 1] in REDIRECTS:
            j += 1  # the fd number of a redirect (2>/dev/null)
            continue
        words.append(seg[j])
        j += 1
    return (words[0] if words else ""), words[1:]


def segment_reason(seg: list[str], bodies: list[str]) -> str | None:
    for k, tok in enumerate(seg):
        if tok in REDIRECTS and k + 1 < len(seg):
            target = seg[k + 1]
            if tok.endswith("&") and re.fullmatch(r"\d+-?|-", target):
                continue  # fd duplication, e.g. 2>&1
            if not allowed_target(target):
                what = "a heredoc into " + target if any(t in ("<<", "<<-") for t in seg) else tok + " " + target
                return what
    word, args = _command(seg)
    base = word.rsplit("/", 1)[-1]
    if base == "tee":
        files = [a for a in args if not a.startswith("-")]
        bad = [f for f in files if not allowed_target(f)]
        if bad:
            return "tee " + bad[0]
    if base in ("sed", "gsed") and any(a == "--in-place" or a.startswith("--in-place=")
                                       or re.fullmatch(r"-[A-Za-z]*i\S*", a) for a in args):
        rest, script_given = [], any(a in ("-e", "-f") or a.startswith(("--expression", "--file")) for a in args)
        skip = False
        for a in args:
            if skip:
                skip = False
                continue
            if a in ("-e", "-f"):
                skip = True
                continue
            if a and not a.startswith("-"):  # '' is the BSD `sed -i ''` backup suffix
                rest.append(a)
        files = rest if script_given else rest[1:]
        bad = [f for f in files if not allowed_target(f)] or ([] if files else ["a file"])
        if bad:
            return "sed -i on " + bad[0]
    if PYTHON.search(word) and any(t in ("<<", "<<-") for t in seg):
        for body in bodies:
            if PY_WRITE.search(body) and not SCRATCH.search(_expand_all(body)):
                return "a python heredoc that opens a file for writing"
    return None


def _expand_all(text: str) -> str:
    home = os.path.expanduser("~")
    return re.sub(r"(~|\$\{HOME\}|\$HOME)(?=/)", home, text)


def bash_reason(cmd: str) -> str | None:
    text, bodies = split_heredocs(cmd)
    try:
        segs = segments(text)
    except ValueError:
        return None  # unreadable: the isolation guard still checks it
    for seg in segs:
        what = segment_reason(seg, bodies)
        if what:
            return REASON.format(what=what)
    return None


def in_worktree(cwd: str) -> bool:
    return "/.claude/worktrees/" in (cwd.rstrip("/") + "/")


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash" or not in_worktree(str(data.get("cwd") or "")):
        return 0
    reason = bash_reason(str((data.get("tool_input") or {}).get("command") or ""))
    if not reason:
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
