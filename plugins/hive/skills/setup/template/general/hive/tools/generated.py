#!/usr/bin/env python3
"""Check that every generated file matches a fresh build of its sources.

A file built from another file goes stale when someone edits the source and forgets the build. Every such file
has a row: the team's own rows are below, and the project adds its rows to hive/GENERATED.json as
{"files": [...], "check": "<command that exits 1 when stale>", "build": "<command that rebuilds>"}.
hive/tests runs `check` on every row, so a stale file fails the tests.

  python3 hive/tools/generated.py check     run every row's check; exit 1 if any fails
  python3 hive/tools/generated.py build     run every row's build
  python3 hive/tools/generated.py list      print the rows
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROWS = ROOT / "hive" / "GENERATED.json"
TEAM_ROWS = [
    {"files": [".claude/agents/*.md"], "check": "python3 hive/tools/roles.py check",
     "build": "python3 hive/tools/roles.py build"},
    {"files": [".beads/PRIME.md"], "check": "python3 hive/tools/brief.py check",
     "build": "python3 hive/tools/brief.py build"},
]


def rows() -> list[dict]:
    extra = []
    if PROJECT_ROWS.is_file():
        data = json.loads(PROJECT_ROWS.read_text(encoding="utf-8"))
        extra = data.get("rows", []) if isinstance(data, dict) else data
    return TEAM_ROWS + extra


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=600)


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    if cmd == "list":
        for r in rows():
            print(", ".join(r["files"]), "|", r["check"], "|", r.get("build", ""))
        return 0
    if cmd not in ("check", "build"):
        print(__doc__)
        return 2
    bad = 0
    for r in rows():
        p = run(r[cmd] if cmd == "check" else r.get("build", "true"))
        status = "ok" if p.returncode == 0 else "FAIL"
        bad += p.returncode != 0
        print(f"{status}  {', '.join(r['files'])}  ({r[cmd] if cmd == 'check' else r.get('build')})")
        if p.returncode != 0:
            print("      " + (p.stdout + p.stderr).strip().replace("\n", "\n      "))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
