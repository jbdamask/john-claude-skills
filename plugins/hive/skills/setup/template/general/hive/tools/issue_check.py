#!/usr/bin/env python3
"""Tell the lead which GitHub issues need it to act. It only asks GitHub and beads; no model calls.

  python3 hive/tools/issue_check.py            check every 60 s; print the issues that need action and exit 0
  python3 hive/tools/issue_check.py --once     check once; print them (or nothing) and exit 0

An issue's labels say where it is (hive/BUILD.md "The flow"):
  no workflow label   a new request        -> "new": the lead adds `drafting` and has the spec written
  bug                 a bug report         -> "bug": the lead adds `in_progress` and has it fixed (hive/FIXES.md)
  drafting, pending_approval, proposal, in_progress   nothing to do here
  approved_spec       approved             -> "approved" until an epic's title carries `#<number>`

Only issues opened on or after `flow_since` in hive/project.json count as new requests.
Exits 3 without waiting if ~/.hive/STOP exists.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402

ROOT = project.ROOT
STOP = Path.home() / ".hive" / "STOP"
WORKFLOW = {"drafting", "pending_approval", "approved_spec", "proposal", "in_progress"}


def needs_action(issues: list[dict], epic_titles: list[str], since: str = "") -> list[dict]:
    out = []
    for i in issues:
        labels = {l["name"] if isinstance(l, dict) else l for l in i.get("labels") or []}
        row = {"number": i["number"], "title": i.get("title", "")}
        if "approved_spec" in labels:
            mark = re.compile(rf"#{i['number']}(?!\d)")
            if not any(mark.search(t or "") for t in epic_titles):
                out.append({**row, "state": "approved"})
        elif labels & WORKFLOW:
            continue
        elif str(i.get("createdAt", ""))[:10] >= since:
            out.append({**row, "state": "bug" if "bug" in labels else "new"})
    return out


def _json(cmd: list[str]):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise OSError(r.stderr.strip()[:200])
    return json.loads(r.stdout or "[]")


def check() -> list[dict]:
    issues = _json(["gh", "issue", "list", "--state", "open", "--json", "number,title,labels,createdAt",
                    "--limit", "200"])
    epics = []
    if any("approved_spec" in {l["name"] for l in i.get("labels") or []} for i in issues):
        epics = [e.get("title", "") for e in _json(["bd", "list", "-t", "epic", "--all", "--limit", "0", "--json"])]
    return needs_action(issues, epics, project.config().get("flow_since", ""))


def main() -> int:
    once = "--once" in sys.argv[1:]
    while True:
        if STOP.exists():
            print("STOP file present; not checking")
            return 3
        try:
            found = check()
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            found = []
            print(f"check failed, will retry: {e}", file=sys.stderr)
        if found or once:
            for f in found:
                print(json.dumps(f))
            return 0
        time.sleep(60)


if __name__ == "__main__":
    sys.exit(main())
