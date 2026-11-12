#!/usr/bin/env python3
"""Look up the project's glossary, hive/DEFINITIONS.jsonl (one JSON object per line: term, definition, source,
deprecated).

  python3 hive/tools/term.py <term or deprecated word>   print that entry
  python3 hive/tools/term.py --list                      print the compact list
  python3 hive/tools/term.py --hook <EventName>          the compact list as a hook's additionalContext JSON

Matching ignores case. A deprecated word finds its entry and says which term to use. Exit 1 when nothing matches.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GLOSSARY = ROOT / "hive" / "DEFINITIONS.jsonl"
HOOK_LINE = ("Terms (hive/DEFINITIONS.jsonl). Before you use one in work or in text a person reads, run "
             "`python3 hive/tools/term.py <term>` for its definition. Words after \"not:\" are deprecated: never use "
             "them; the term before them replaces them.")


def load(path: Path = GLOSSARY) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def find(word: str, rows: list[dict]) -> tuple[dict | None, bool]:
    key = word.strip().casefold()
    for row in rows:
        if row["term"].casefold() == key:
            return row, False
    for row in rows:
        if any(d.casefold() == key for d in row.get("deprecated", [])):
            return row, True
    return None, False


def compact(rows: list[dict]) -> str:
    return "; ".join(r["term"] + (" (not: " + ", ".join(r["deprecated"]) + ")" if r.get("deprecated") else "")
                     for r in rows)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if argv else 2
    rows = load()
    if argv[0] == "--list":
        print(compact(rows))
        return 0
    if argv[0] == "--hook":
        if not rows:
            return 0
        event = argv[1] if len(argv) > 1 else "SessionStart"
        print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                                 "additionalContext": HOOK_LINE + "\n" + compact(rows)}}))
        return 0
    word = " ".join(argv)
    row, by_dep = find(word, rows)
    if row is None:
        print(f'"{word}" is not in hive/DEFINITIONS.jsonl; a new term gets its entry there first.', file=sys.stderr)
        return 1
    if by_dep:
        print(f'"{word}" is deprecated: use "{row["term"]}".')
    print(f'{row["term"]}: {row["definition"]}')
    print(f'Source: {row.get("source", "own term")}.')
    if row.get("deprecated"):
        print("Deprecated (never use): " + ", ".join(row["deprecated"]) + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
