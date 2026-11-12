#!/usr/bin/env python3
"""Check a beads graph plan before `bd create --graph` runs it. Standard library only.

Usage: python3 check_plan.py <plan.json> [--root <repo dir>] [--issue <n>]

Fails (exit 1, one FAIL line per problem) when:
  - a key is missing or repeated, or an edge or parent_key names a key that is not in the plan
  - there is not exactly one epic, or a non-epic node has no parent
  - a non-epic node has no acceptance_criteria, or none of its lines can be settled by a command or an
    observation, or a line is one of the known vague phrases
  - the blocking edges plus parent links contain a cycle
  - a file path the bead names (metadata.files, or a path in its description or acceptance) does not
    exist under --root and is not listed in metadata.new_files
  - two beads that can run at the same time (neither waits on the other) both list a file in
    metadata.files
  - --issue is given and a node's external_ref is not gh-<n>
Exit 0 prints "OK" and the counts.
"""
import argparse
import json
import re
import sys
from pathlib import Path

VAGUE = re.compile(r"\b(works( correctly| as expected| well)?|handles edge cases|good ux|user-friendly|"
                   r"as expected|clean code|is robust|properly|appropriately)\s*\.?$", re.I)
# A line can be settled when it names something to run or look at: a `code span`, a number or
# comparison, or an observable verb.
CHECKABLE = re.compile(r"`[^`]+`|\d|[<>=]|\b(exists?|returns?|exits?|prints?|shows?|lists?|contains?|"
                       r"equals?|matches|reports?|has|have|is (absent|present|empty)|fails?|passes|"
                       r"refuses?|renders?|appears?|reads?|names?)\b", re.I)
PATH = re.compile(r"(?<![\w~/.:-])((?:[\w.-]+/)+[\w.-]*\.[A-Za-z0-9]{1,8})(?![\w/])")
BLOCKING = {"blocks", "waits-for", "conditional-blocks"}


def paths_named(text: str) -> set[str]:
    out = set()
    for m in PATH.finditer(text or ""):
        p = m.group(1)
        if p.startswith(("http", "www.")) or "<" in p or "*" in p or "{" in p:
            continue
        out.add(p.rstrip("."))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--root", default=".")
    ap.add_argument("--issue")
    a = ap.parse_args()
    root = Path(a.root)
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    nodes = plan.get("nodes") or []
    edges = plan.get("edges") or []
    fails: list[str] = []

    keys = [n.get("key") for n in nodes]
    by_key = {}
    for n in nodes:
        k = n.get("key")
        if not k:
            fails.append(f"node {n.get('title')!r}: no key")
        elif k in by_key:
            fails.append(f"key {k}: used twice")
        by_key[k] = n
    epics = [k for k in keys if by_key[k].get("type") == "epic"]
    if len(epics) != 1:
        fails.append(f"plan has {len(epics)} epics; it needs exactly one")

    parent = {}
    for k, n in by_key.items():
        p = n.get("parent_key") or n.get("parent")
        if p:
            if p not in by_key:
                fails.append(f"{k}: parent_key {p} is not a key in the plan")
            parent[k] = p
        elif n.get("type") != "epic" and not n.get("parent_id"):
            fails.append(f"{k}: no parent_key; every bead belongs under the epic")

    # waits_on[a] = keys a must wait for (edge from a to b of a blocking type: a depends on b)
    waits_on: dict[str, set[str]] = {k: set() for k in by_key}
    for i, e in enumerate(edges):
        f, t = e.get("from_key"), e.get("to_key")
        for side in (f, t):
            if side is not None and side not in by_key:
                fails.append(f"edge {i}: key {side} is not in the plan")
        if f in by_key and t in by_key and (e.get("type") or "blocks") in BLOCKING:
            waits_on[f].add(t)

    # Cycles over blocking edges plus child->parent links.
    graph = {k: set(waits_on[k]) | ({parent[k]} if k in parent and parent[k] in by_key else set())
             for k in by_key}
    state: dict[str, int] = {}

    def visit(k: str, stack: list[str]) -> None:
        state[k] = 1
        for nxt in graph[k]:
            if state.get(nxt) == 1:
                path = stack + [k]
                fails.append("cycle: " + " -> ".join(path[path.index(nxt):] + [nxt]))
            elif nxt not in state:
                visit(nxt, stack + [k])
        state[k] = 2

    for k in by_key:
        if k not in state:
            visit(k, [])

    def reach(k: str) -> set[str]:
        seen, todo = set(), [k]
        while todo:
            for nxt in waits_on.get(todo.pop(), ()):
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append(nxt)
        return seen

    def ancestors(k: str) -> set[str]:
        out = set()
        while k in parent and parent[k] not in out:
            k = parent[k]
            out.add(k)
        return out

    # A file another bead in the plan creates counts as existing.
    plan_new = {p for n in nodes for p in ((n.get("metadata") or {}).get("new_files") or [])}
    owners: dict[str, list[str]] = {}
    for k, n in by_key.items():
        md = n.get("metadata") or {}
        files = set(md.get("files") or [])
        new = set(md.get("new_files") or [])
        is_epic = n.get("type") == "epic"
        acc = (n.get("acceptance_criteria") or "").strip()
        if not acc:
            fails.append(f"{k}: no acceptance_criteria")
        elif not is_epic:
            lines = [ln.strip(" -*\t") for ln in acc.splitlines() if ln.strip(" -*\t")]
            if not any(CHECKABLE.search(ln) for ln in lines):
                fails.append(f"{k}: no acceptance line a command or an observation can settle")
            for ln in lines:
                if VAGUE.search(ln):
                    fails.append(f"{k}: vague acceptance line: {ln!r}")
        named = files | paths_named(n.get("description", "")) | paths_named(acc)
        for p in sorted(named - new - plan_new):
            if not (root / p).exists():
                fails.append(f"{k}: names {p}, which does not exist (add it to metadata.new_files if the bead creates it)")
        for p in files:
            owners.setdefault(p, []).append(k)
        if a.issue and n.get("external_ref") != f"gh-{a.issue}":
            fails.append(f"{k}: external_ref is {n.get('external_ref')!r}, expected 'gh-{a.issue}'")

    for p, ks in owners.items():
        for i, x in enumerate(ks):
            for y in ks[i + 1:]:
                if y in reach(x) or x in reach(y) or y in ancestors(x) or x in ancestors(y):
                    continue
                fails.append(f"{x} and {y} can run at the same time and both own {p}; add a blocks edge or merge them")

    if fails:
        for f in fails:
            print("FAIL", f)
        return 1
    n_edges = len(edges) + len(parent)
    print(f"OK: {len(nodes)} nodes, {len(edges)} edges, {len(parent)} parent links ({n_edges} dependencies)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
