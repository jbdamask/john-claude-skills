#!/usr/bin/env python3
"""Check that a feature's brief for the owner can be read in a minute (hive/BUILD.md step 2).

  python3 hive/tools/spec_brief.py <issue number>     check the body of that GitHub issue
  python3 hive/tools/spec_brief.py --file <path>      check a draft before posting it
  python3 hive/tools/spec_brief.py --how              print the fixed line that says how to answer

It passes when it has the five parts in order, each starting in bold (**You asked for**, **You will get**,
**You will not get**, **Cost**, **Decide**), is at most 200 words, asks at most three questions under Decide,
each with a line starting "Recommended:", gives no time estimate under Cost, carries the fixed answer line, and
links one file under hive/specs/ that exists. Exit 1 with the reasons otherwise.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ["You asked for", "You will get", "You will not get", "Cost", "Decide"]
MAX_WORDS = 200
MAX_QUESTIONS = 3
HOW = ("**To answer:** add the label `approved_spec` to accept every recommendation. To answer a question "
       "differently, first comment with its number and your answer (for example \"1: no\"), then add the label.")
LINK = re.compile(r"\((?:https?://[^)\s]*/)?(hive/specs/[\w./-]+\.md)\)")


def problems(text: str, root: Path = ROOT) -> list[str]:
    out = []
    pos = [text.find(f"**{p}") for p in PARTS]
    for p, at in zip(PARTS, pos):
        if at < 0:
            out.append(f'missing part "**{p}**"')
    if all(a >= 0 for a in pos) and pos != sorted(pos):
        out.append("the five parts are out of order: " + ", ".join(PARTS))
    prose = LINK.sub("", re.sub(r"https?://\S+", "", text.replace(HOW, "")))
    words = len(re.findall(r"[\w'’$%.,-]*\w[\w'’$%.,-]*", prose))
    if words > MAX_WORDS:
        out.append(f"{words} words; the limit is {MAX_WORDS}. Move detail to the spec file")
    if pos[-1] >= 0:
        decide = text[pos[-1]:]
        questions = [l for l in decide.splitlines() if re.match(r"^\s*(\d+\.|-)\s+\S", l) and "?" in l]
        if len(questions) > MAX_QUESTIONS:
            out.append(f"{len(questions)} questions under Decide; the limit is {MAX_QUESTIONS}")
        if len(re.findall(r"Recommended:", decide)) < len(questions):
            out.append('every question under Decide needs a line starting "Recommended:"')
    if pos[3] >= 0 and pos[4] > pos[3]:
        m = re.search(r"\b(minute|hour|day|week|month)s?\b", text[pos[3]:pos[4]], re.I)
        if m:
            out.append(f'the Cost part gives a time estimate ("{m.group(0)}"); give tasks and money only')
    if HOW not in text:
        out.append("the line that says how to answer is missing or changed; print it with --how")
    links = LINK.findall(text)
    if not links:
        out.append("no link to the spec file under hive/specs/")
    elif not (root / links[0]).is_file():
        out.append(f"{links[0]} does not exist")
    return out


def main() -> int:
    args = sys.argv[1:]
    if args == ["--how"]:
        print(HOW)
        return 0
    if len(args) == 2 and args[0] == "--file":
        text = Path(args[1]).read_text(encoding="utf-8")
    elif len(args) == 1 and args[0].isdigit():
        r = subprocess.run(["gh", "issue", "view", args[0], "--json", "body"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr.strip())
            return 2
        text = json.loads(r.stdout)["body"]
    else:
        print(__doc__)
        return 2
    bad = problems(text)
    for b in bad:
        print("FAIL:", b)
    if not bad:
        print("brief ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
