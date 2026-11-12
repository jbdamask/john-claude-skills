#!/usr/bin/env python3
"""Land committed work on main: lock, merge main, run the fast tests on the merge, push only if they pass.

  python3 hive/tools/land.py              from the root of the tree whose HEAD holds your commits
  python3 hive/tools/land.py --dry-run    everything except the push

Why: an agent that pushes by hand can push after a failed or stale test run, and agents landing at once queue
behind each other re-merging. This takes one lock per repo (in the git directory every worktree shares), so
landings go one at a time, and every push is of a merge that passed the fast tests.

Steps: refuse if tracked files have uncommitted changes; refuse if a commit to land carries Claude or Anthropic
attribution lines; take the lock (waits up to --wait seconds); fetch and merge <remote>/<main> (a conflict is
aborted and left to you); run the team's tests (hive/tests, when present) and `fast_tests` from hive/project.json
on the merged tree; push HEAD to <remote>/<main>;
release the lock. A push rejected because main moved is retried from the merge, up to three times.
Exit codes: 0 landed, 1 tests failed, 2 refused (dirty tree, attribution, merge conflict, lock timeout, push failed).
"""
from __future__ import annotations

import argparse
import fcntl
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402

ATTRIBUTION = re.compile(r"co-authored-by:[^\n]*(claude|anthropic)|claude-session:|generated with \[claude code\]", re.I)


def git(*args: str, cwd: Path, check: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def say(msg: str) -> None:
    print(f"land: {msg}", flush=True)


def lock(top: Path, wait: int):
    common = Path(git("rev-parse", "--git-common-dir", cwd=top, check=True).stdout.strip())
    if not common.is_absolute():
        common = (top / common).resolve()
    f = open(common / "hive-land.lock", "a+")
    deadline = time.time() + wait
    told = False
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except BlockingIOError:
            if time.time() > deadline:
                f.close()
                return None
            if not told:
                say("another landing holds the lock; waiting")
                told = True
            time.sleep(2)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--wait", type=int, default=1800, help="seconds to wait for the lock")
    a = ap.parse_args(argv)
    top = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd(), check=True).stdout.strip())
    cfg = project.config(top) or project.config()
    remote, main_branch = cfg.get("remote", "origin"), cfg.get("main_branch", "main")
    tests = cfg.get("fast_tests")
    if not tests:
        say("no fast_tests command in hive/project.json; refusing to land untested work")
        return 2
    if git("status", "--porcelain", "--untracked-files=no", cwd=top).stdout.strip():
        say("tracked files have uncommitted changes: commit your own files first (git add <paths>; git commit)")
        return 2
    held = lock(top, a.wait)
    if held is None:
        say(f"the lock was held for over {a.wait} s; try again, or ask the lead what is landing")
        return 2
    try:
        for attempt in range(3):
            if git("fetch", remote, cwd=top).returncode != 0:
                say(f"git fetch {remote} failed")
                return 2
            target = f"{remote}/{main_branch}"
            has_main = git("rev-parse", "--verify", "--quiet", target, cwd=top).returncode == 0
            span = f"{target}..HEAD" if has_main else "HEAD"
            msgs = git("log", "--format=%B%x00", span, cwd=top).stdout
            if ATTRIBUTION.search(msgs):
                say("a commit to land carries Claude or Anthropic attribution lines; amend or revert it first")
                return 2
            if not git("rev-list", span, cwd=top).stdout.strip():
                say(f"nothing to land: HEAD is already on {target}")
                return 0
            if has_main:
                m = git("merge", "--no-edit", target, cwd=top)
                if m.returncode != 0:
                    git("merge", "--abort", cwd=top)
                    say(f"merging {target} conflicts; merge it yourself (git merge {target}), keep both sides' work, "
                        "commit, and land again")
                    return 2
            if (top / "hive" / "tests").is_dir():
                say("running the team's tests on the merge: python3 -m unittest discover -s hive/tests")
                h = subprocess.run([sys.executable, "-m", "unittest", "discover", "-q", "-s", "hive/tests"], cwd=top)
                if h.returncode != 0:
                    say("the team's tests failed; nothing was pushed")
                    return 1
            say(f"running the fast tests on the merge: {tests}")
            t = subprocess.run(tests, shell=True, cwd=top)
            if t.returncode != 0:
                say(f"the fast tests failed (exit {t.returncode}); nothing was pushed")
                return 1
            if a.dry_run:
                say("dry run: tests passed; not pushing")
                return 0
            p = git("push", remote, f"HEAD:{main_branch}", cwd=top)
            if p.returncode == 0:
                sha = git("rev-parse", "--short", "HEAD", cwd=top).stdout.strip()
                say(f"landed {sha} on {target}")
                return 0
            if "rejected" not in p.stderr and "fetch first" not in p.stderr:
                say("push failed: " + p.stderr.strip()[-300:])
                return 2
            say("main moved during the landing; merging again")
        say("main kept moving; three tries failed")
        return 2
    finally:
        fcntl.flock(held, fcntl.LOCK_UN)
        held.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
