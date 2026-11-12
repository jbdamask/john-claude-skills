#!/usr/bin/env python3
"""List the scratch folders of closed beads, with sizes, and print the commands a person runs to delete them.

Agents cannot delete files, so their scratch folders (~/.hive/<slug>/scratch/<agent name>/) pile up. An agent's
name is e-<bead id> with dots as hyphens. This lists each folder whose bead is closed, its size and the total,
then the delete commands. It deletes nothing itself. Folders of open beads and folders it cannot match to a bead
are listed apart and get no command.

  python3 hive/tools/scratch.py
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402


def agent_name(bead_id: str) -> str:
    return "e-" + bead_id.replace(".", "-")


def size(path: Path) -> int:
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            try:
                total += os.lstat(os.path.join(dirpath, f)).st_size
            except OSError:
                pass
    return total


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def beads() -> dict:
    r = subprocess.run(["bd", "list", "--all", "--limit", "0", "--json"], cwd=project.ROOT,
                       capture_output=True, text=True, timeout=120)
    try:
        return {agent_name(b["id"]): b for b in json.loads(r.stdout or "[]")}
    except ValueError:
        return {}


def sort(root: Path, by_name: dict) -> dict:
    out = {"closed": [], "open": [], "unknown": []}
    if not root.is_dir():
        return out
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        b = by_name.get(d.name)
        kind = "unknown" if b is None else ("closed" if b.get("status") == "closed" else "open")
        out[kind].append((d, size(d), b["id"] if b else ""))
    return out


def main() -> int:
    root = project.scratch_root()
    groups = sort(root, beads())
    if not any(groups.values()):
        print(f"no scratch folders under {root}")
        return 0
    for kind in ("closed", "open", "unknown"):
        rows = groups[kind]
        if rows:
            print(f"\n{kind}: {len(rows)} folders, {human(sum(s for _, s, _ in rows))}")
            for d, s, bid in rows:
                print(f"  {human(s):>8}  {d.name}" + (f"  ({bid})" if bid else ""))
    if groups["closed"]:
        print("\nTo delete the closed beads' folders, a person runs:")
        for d, _, _ in groups["closed"]:
            print("rm -rf " + shlex.quote(str(d)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
