#!/usr/bin/env python3
"""What the team's rules and documents cost and whether agents use them. Read-only. For the gardener.

  python3 hive/tools/team_use.py rules              rule lines in each rule file, the team's total and the project's
  python3 hive/tools/team_use.py docs [--days N]    which tracked documents agents opened in the last N days (default 30)

A rule line is a bullet, a numbered item or a table row (headings, prose and table separators are not counted).
The team's rule files come with the hive set-up and together stay at or under 150 lines; the project's own files
are counted apart. docs reads the transcripts Claude Code stores for this repo's sessions and counts, per tracked
.md document, the sessions that opened it with the Read tool and the sessions that named it in a shell command.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402

ROOT = project.ROOT
TEAM_RULE_FILES = ["hive/BRIEF.md", "hive/TEAM.md", "hive/LEAD.md", "hive/BUILD.md", "hive/FIXES.md",
                   "hive/WRITING.md", "hive/CRONS.md", "hive/STRATEGIST.md", "hive/GARDENER.md", "hive/RED-TEAM.md",
                   "hive/EXPERIENCE.md", "hive/FRESH-EYES.md", "hive/PRODUCT-REVIEW.md", ".beads/PLANNING.md"]
PROJECT_RULE_FILES = ["hive/PROJECT.md", "hive/PRINCIPLES.md", "hive/REVIEW-CHECKLIST.md"]
TEAM_BUDGET = 150
DOC = re.compile(r"((?:hive|docs|\.beads)/[\w./-]+\.md|CLAUDE\.md|README\.md)")


def rule_lines(text: str) -> int:
    n = 0
    for line in text.splitlines():
        t = line.strip()
        if re.match(r"^([-*]|\d+\.)\s+\S", t) or (t.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", t)):
            n += 1
    return n


def rules(root: Path = ROOT) -> dict:
    def count(files):
        return {f: rule_lines((root / f).read_text(encoding="utf-8")) for f in files if (root / f).is_file()}
    team, proj = count(TEAM_RULE_FILES), count(PROJECT_RULE_FILES)
    return {"team": team, "team_total": sum(team.values()), "project": proj, "project_total": sum(proj.values())}


def tracked_docs() -> list[str]:
    r = subprocess.run(["git", "ls-files", "hive", "docs", ".beads", "CLAUDE.md", "README.md"],
                       cwd=ROOT, capture_output=True, text=True)
    return [p for p in r.stdout.split() if p.endswith(".md")]


def doc_use(days: int, projects: str | None = None, docs: list[str] | None = None,
            today: dt.date | None = None) -> dict:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    since = (today - dt.timedelta(days=days - 1)).isoformat()
    projects = projects or project.claude_projects_glob()
    files = (glob.glob(projects + "/*.jsonl") + glob.glob(projects + "/*/subagents/*.jsonl")
             + glob.glob(projects + "/*/subagents/*/*.jsonl"))
    read, shell = defaultdict(set), defaultdict(set)
    sessions = 0
    for f in files:
        if dt.date.fromtimestamp(os.path.getmtime(f)).isoformat() < since:
            continue
        sessions += 1
        with open(f, errors="replace") as fh:
            for line in fh:
                if '"tool_use"' not in line:
                    continue
                try:
                    content = (json.loads(line).get("message") or {}).get("content")
                except ValueError:
                    continue
                for b in content if isinstance(content, list) else []:
                    if not isinstance(b, dict) or b.get("type") != "tool_use":
                        continue
                    inp = b.get("input") or {}
                    if b.get("name") == "Read":
                        m = DOC.search(str(inp.get("file_path", "")))
                        if m:
                            read[m.group(1)].add(f)
                    elif b.get("name") == "Bash":
                        for p in set(DOC.findall(str(inp.get("command", "")))):
                            shell[p].add(f)
    docs = tracked_docs() if docs is None else docs
    per = {p: {"read": len(read.get(p, ())), "shell": len(shell.get(p, ()))} for p in docs}
    return {"from": since, "to": today.isoformat(), "sessions": sessions, "documents": len(docs),
            "never_read": sum(1 for v in per.values() if not v["read"]),
            "never_touched": sum(1 for v in per.values() if not v["read"] and not v["shell"]),
            "per_document": per}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["docs", "rules"])
    ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "rules":
        r = rules()
        for f, n in r["team"].items():
            print(f"{n:>5}  {f}")
        print(f"{r['team_total']:>5}  team total (budget {TEAM_BUDGET})")
        for f, n in r["project"].items():
            print(f"{n:>5}  {f}")
        print(f"{r['project_total']:>5}  project total")
        return 0
    rep = doc_use(a.days)
    print(f"{rep['from']} to {rep['to']}: {rep['sessions']} sessions, {rep['documents']} tracked documents")
    print(f"never opened with Read: {rep['never_read']}; never named in any command either: {rep['never_touched']}")
    print("\nopened  named-in-shell  document")
    for p, v in sorted(rep["per_document"].items(), key=lambda kv: -kv[1]["read"]):
        print(f"{v['read']:>6}  {v['shell']:>14}  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
