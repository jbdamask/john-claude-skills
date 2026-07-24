#!/usr/bin/env python3
"""ledger.py — the spine of the bullshit-tests skill.

The skill audits test suites for tests that pass for no good reason. On a large
suite an LLM can't read every test, so it would sample and miss. This tool makes
coverage a *fact* instead of a claim: it enumerates every test into a ledger,
triages the mechanically-detectable cases deterministically (free, exhaustive, no
hallucination), and tracks a status per test so the LLM only spends judgment where
judgment is actually needed — and can stop, resume, or fan out to subagents
without losing its place.

The ledger lives in scratch space, never in the audited repo. It reads test files;
it never writes to them.

Subcommands
-----------
  build   enumerate tests → JSONL ledger, with assertion counts + mechanical flags
  stats   counts by status / priority / flag; the pending count is your progress bar
  next    emit the next N rows needing a human-judgment read (compact, for the agent)
  set     update one row's verdict in place (status, pattern, severity, evidence, story)
  report  emit a markdown verdict summary generated FROM the ledger (for the report)

A row can never reach status red/yellow without an `evidence` (file:line) and a
`story` — the tool refuses it. That is the structural check on fabrication: every
accusation carries its receipt.

Stdlib only. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Enumeration
# --------------------------------------------------------------------------- #

# Supported languages: python (pytest/unittest), js/ts (jest/vitest/mocha),
# go (testing/testify), ruby (rspec/minitest/rails), rust (#[test] family).
# Enumeration is exhaustive for these; anything else is not parsed and the build
# summary says so, so a missed language is a visible gap, not a silent "all clear".

# --- test detection, per language ---
PY_TEST = re.compile(r"^(?P<indent>\s*)(?:async\s+)?def\s+(?P<name>test_\w+)\s*\(")
# it(...) / test(...) / it.only(...) / it.skip(...) / xit(...) / test.each(...)
JS_TEST = re.compile(
    r"""^\s*(?:x?it|test)         # it / test / xit
        (?P<mod>\.(?:only|skip|todo|each|concurrent|failing|runIf|skipIf))?  # modifier
        \s*(?:\([^)]*\))?         # optional .each(table) args
        \s*\(\s*(?P<q>['"`])(?P<name>.*?)(?P=q)""",
    re.VERBOSE,
)
GO_TEST = re.compile(r"^func\s+(?P<name>(?:Test|Fuzz|Example)\w+)\s*\(")
RB_IT = re.compile(r"^\s*(?P<kw>x?it|specify|example|fit|scenario)\b\s*"
                   r"(?:\(\s*)?(?P<q>['\"])(?P<name>.+?)(?P=q)")
RB_RAILS = re.compile(r"^\s*test\s+(?P<q>['\"])(?P<name>.+?)(?P=q)\s+do")
RB_MINI = re.compile(r"^\s*def\s+(?P<name>test_\w+)")
RUST_ATTR = re.compile(r"^\s*#\[\s*(?:(?:tokio|async_std|actix_rt)::)?test\b"
                       r"|^\s*#\[\s*(?:rstest|test_case)\b")
RUST_FN = re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(?P<name>\w+)")

# --- assertion tokens, per language ---
ASSERT_PY = re.compile(
    r"\bassert\b|self\.assert|pytest\.raises|pytest\.warns|assert_called"
    r"|assert_not_called|assert_has_calls|assert_awaited|\.testing\.|np\.testing"
)
ASSERT_JS = re.compile(r"\bexpect\(|\bassert\.|\bassert\(|\.should\b|\bchai\.|\bthrows\(")
ASSERT_GO = re.compile(r"\bt\.(?:Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b"
                       r"|\b(?:assert|require)\.\w+\(|\bshould\.")
ASSERT_RB = re.compile(r"\bexpect\(|\bis_expected\b|\.to\b|\.to_not\b|\.not_to\b"
                       r"|\bassert\b|\bassert_\w+|\brefute\w*|\.must_\w+|\.wont_\w+")
ASSERT_RUST = re.compile(r"\bassert(?:_eq|_ne)?!|\bdebug_assert(?:_eq|_ne)?!|\bpanic!")
ASSERTS = {"py": ASSERT_PY, "js": ASSERT_JS, "go": ASSERT_GO,
           "rb": ASSERT_RB, "rust": ASSERT_RUST}

# Mechanical flags — the greppable patterns a linter could also catch. The tool
# raises these as *candidates*; the LLM still adjudicates (an assertion can hide
# in a helper), but every flagged row is guaranteed to get a human-judgment look.
# The regexes span languages; a rule that can't match a given language is simply
# inert there. Language-specific structural signals (rust #[should_panic]/#[ignore],
# js .only/.skip modifiers) are added as `extra` flags at detection time.
FLAG_RULES = {
    "no_assert":      None,  # computed from assertion count, below
    "tautology":      re.compile(r"assert\s+True\b|assert\s+1\s*==\s*1\b"
                                 r"|assertTrue\(\s*True\s*\)"
                                 r"|expect\(\s*(?:true|1)\s*\)\.(?:toBe|toEqual)\(\s*(?:true|1)\s*\)"
                                 r"|assert!\(\s*true\s*\)|assert_eq!\(\s*true\s*,\s*true\s*\)"
                                 r"|(?:assert|require)\.(?:True|Equal)\([^,]+,\s*true\b"),
    # Deliberately NOT a bare `\bskip\b`/`\bpending\b`: those are domain words
    # (a "pending request", a conditional `pytest.skip("no moto")` guard) and
    # flag half a real codebase. Match only the marker forms.
    "skip_or_xfail":  re.compile(r"@(?:pytest\.mark\.)?(?:skip|xfail)\b|@unittest\.skip"
                                 r"|\bit\.skip\b|\bxit\b|\bit\.todo\b|\bdescribe\.skip\b"
                                 r"|\bt\.Skipf?\(|\bpending\(|\bpending[ \t]+['\"]|\bpending[ \t]+do\b"),
    "only":           re.compile(r"\bit\.only\b|\btest\.only\b|\bdescribe\.only\b"),
    "empty_body":     None,  # computed from body, below
    "broad_raises":   re.compile(r"pytest\.raises\(\s*Exception\s*\)"
                                 r"|assertRaises\(\s*Exception\b"
                                 r"|\.toThrow\(\s*\)"
                                 r"|raise_error(?!\s*[\(A-Za-z:])"),
    "swallowed":      re.compile(r"except\s*\(?\s*(?:Exception|AssertionError|BaseException)"
                                 r"[^)]*\)?\s*:\s*(?:pass|continue)"
                                 r"|catch\s*\([^)]*\)\s*\{\s*\}"),
    "source_text":    re.compile(r"readFileSync|\.read_text\(\)|ioutil\.ReadFile|os\.ReadFile"
                                 r"|File\.read\b|include_str!"),
    "unawaited_async": re.compile(r"(?<!await\s)(?<!return\s)expect\([^)]*\)\.(?:resolves|rejects)"),
    "default_truth":  re.compile(r"except[^:]*:\s*return\s+True|\bor\s+True\b|\|\|\s*true\b"
                                 r"|\.get\([^)]+,\s*True\)"),
}

BODY_STOP_PY = ("#", "@", ")", "]", "}")
INDENT_LANGS = {"py", "rb"}      # block bounded by indentation
BRACE_LANGS = {"js", "go", "rust"}  # block bounded by { }


def _iter_test_files(root: Path):
    seen = set()
    def emit(p, lang):
        if p not in seen:
            seen.add(p)
            return (p, lang)
        return None
    # Python (pytest / unittest)
    for p in sorted(root.rglob("*.py")):
        s = str(p)
        if "__pycache__" in s or "/.pytest_cache/" in s:
            continue
        r = emit(p, "py")
        if r: yield r
    # JS/TS by filename convention (jest / vitest / mocha)
    for pat in ("*.test.js", "*.test.ts", "*.test.jsx", "*.test.tsx", "*.test.mjs",
                "*.test.cjs", "*.spec.js", "*.spec.ts", "*.spec.jsx", "*.spec.tsx"):
        for p in sorted(root.rglob(pat)):
            if "/node_modules/" in str(p):
                continue
            r = emit(p, "js")
            if r: yield r
    # JS/TS inside a __tests__/ directory, any filename (the other jest convention)
    for ext in ("js", "ts", "jsx", "tsx", "mjs", "cjs"):
        for p in sorted(root.rglob(f"*.{ext}")):
            s = str(p)
            if "/node_modules/" in s or "__tests__" not in p.parts:
                continue
            r = emit(p, "js")
            if r: yield r
    # Go
    for p in sorted(root.rglob("*_test.go")):
        if "/vendor/" in str(p):
            continue
        r = emit(p, "go")
        if r: yield r
    # Ruby (rspec / minitest / rails)
    for pat in ("*_spec.rb", "*_test.rb"):
        for p in sorted(root.rglob(pat)):
            r = emit(p, "rb")
            if r: yield r
    # Rust (test attribute; tests live inside src too, so scan all .rs)
    for p in sorted(root.rglob("*.rs")):
        if "/target/" in str(p):
            continue
        r = emit(p, "rust")
        if r: yield r


def _py_body(lines, start):
    indent = len(lines[start]) - len(lines[start].lstrip())
    for j in range(start + 1, len(lines)):
        l = lines[j]
        if l.strip() and (len(l) - len(l.lstrip())) <= indent \
                and not l.lstrip().startswith(BODY_STOP_PY):
            return "\n".join(lines[start:j]), j - start
    return "\n".join(lines[start:]), len(lines) - start


def _brace_body(lines, start):
    depth, started = 0, False
    for j in range(start, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if "{" in lines[j]:
            started = True
        if started and depth <= 0:
            return "\n".join(lines[start:j + 1]), j - start + 1
    return "\n".join(lines[start:]), len(lines) - start


def _body(lines, start, lang):
    return _py_body(lines, start) if lang in INDENT_LANGS else _brace_body(lines, start)


def _find_rust(lines):
    """Rust tests are marked by a #[test]-family attribute above the fn, not by
    name — so look ahead from each test attribute to the fn it decorates, and
    read #[should_panic] / #[ignore] off the attribute block as extra flags."""
    n = len(lines)
    i = 0
    while i < n:
        if RUST_ATTR.match(lines[i]):
            attrs, j = [], i
            while j < n and (lines[j].lstrip().startswith("#[") or not lines[j].strip()):
                attrs.append(lines[j])
                j += 1
            if j < n:
                fnm = RUST_FN.match(lines[j])
                if fnm:
                    at = "\n".join(attrs)
                    extra = []
                    if re.search(r"#\[\s*should_panic", at) and "expected" not in at:
                        extra.append("broad_raises")
                    if re.search(r"#\[\s*ignore", at):
                        extra.append("skip_or_xfail")
                    yield j, fnm.group("name"), extra
                    i = j + 1
                    continue
        i += 1


def _find_tests(lines, lang):
    """Yield (line_index, name, extra_flags) for every test in the file."""
    if lang == "py":
        for i, l in enumerate(lines):
            m = PY_TEST.match(l)
            if m:
                yield i, m.group("name"), []
    elif lang == "js":
        for i, l in enumerate(lines):
            m = JS_TEST.search(l)
            if m:
                mod = m.groupdict().get("mod") or ""
                extra = (["only"] if mod == ".only"
                         else ["skip_or_xfail"] if mod in (".skip", ".todo") else [])
                yield i, m.group("name"), extra
    elif lang == "go":
        for i, l in enumerate(lines):
            m = GO_TEST.match(l)
            if m:
                yield i, m.group("name"), []
    elif lang == "rb":
        for i, l in enumerate(lines):
            m = RB_IT.match(l)
            if m:
                yield i, m.group("name"), (["skip_or_xfail"] if m.group("kw") == "xit" else [])
                continue
            m = RB_RAILS.match(l) or RB_MINI.match(l)
            if m:
                yield i, m.group("name"), []
    elif lang == "rust":
        yield from _find_rust(lines)


def _flags(body: str, n_assert: int, extra: list) -> list:
    out = list(extra)
    for name, rule in FLAG_RULES.items():
        if rule is not None and rule.search(body) and name not in out:
            out.append(name)
    if n_assert == 0 and "no_assert" not in out:
        out.append("no_assert")
    stripped = "\n".join(l for l in body.splitlines()[1:] if l.strip())
    if (not stripped or re.fullmatch(r"\s*(?:pass|\.\.\.|\{\s*\}|end|return)\s*", stripped)) \
            and "empty_body" not in out:
        out.append("empty_body")
    # source_text is only interesting when an assertion sits near the file read
    if "source_text" in out and n_assert == 0:
        out.remove("source_text")
    return sorted(out)


def _priority(flags: list, n_assert: int) -> str:
    if flags:
        return "high"            # a mechanical candidate — always gets a look
    if n_assert <= 1:
        return "med"             # thin; needs a read
    return "low"                 # likely green; sampled, not read one-by-one


def build(args):
    root = Path(args.testdir).resolve()
    if not root.exists():
        sys.exit(f"no such directory: {root}")
    rows = []
    for path, lang in _iter_test_files(root):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except Exception:
            continue
        arx = ASSERTS[lang]
        for i, name, extra in _find_tests(lines, lang):
            body, loc = _body(lines, i, lang)
            n_assert = len(arx.findall(body))
            flags = _flags(body, n_assert, extra)
            rows.append({
                "id": f"{path.relative_to(root)}:{i + 1}",
                "file": str(path.relative_to(root)),
                "line": i + 1,
                "name": name,
                "lang": lang,
                "n_assert": n_assert,
                "loc": loc,
                "flags": flags,
                "priority": _priority(flags, n_assert),
                "status": "pending",      # pending | green | yellow | red | skip
                "pattern": None,
                "severity": None,
                "evidence": None,         # file:line the verdict rests on
                "story": None,            # the failure story (required for red/yellow)
                "verified": None,         # read | confirmed
            })
    out = Path(args.out)
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    _print_build_summary(rows, root, out)


def _print_build_summary(rows, root, out):
    from collections import Counter
    pr = Counter(r["priority"] for r in rows)
    fl = Counter(f for r in rows for f in r["flags"])
    langs = Counter(r["lang"] for r in rows)
    lang_str = ", ".join(f"{v} {k}" for k, v in langs.most_common()) or "none"
    print(f"ledger: {out}")
    print(f"enumerated {len(rows)} tests from {root}  ({lang_str})")
    if not rows:
        print("WARNING: found no tests. Either the path is wrong, or the suite is "
              "in a language this enumerator doesn't parse (supported: python, "
              "js/ts, go, ruby, rust). Say so — don't report a clean bill of health.")
    print(f"priority:  high={pr.get('high',0)} (mechanical candidates)  "
          f"med={pr.get('med',0)} (thin, read these)  "
          f"low={pr.get('low',0)} (likely green, sample)")
    if fl:
        print("flags:     " + "  ".join(f"{k}={v}" for k, v in fl.most_common()))
    print("\nnext: review high+med, sample low. `ledger.py next <ledger> "
          "--priority high` to pull a batch.")


# --------------------------------------------------------------------------- #
# Ledger I/O
# --------------------------------------------------------------------------- #

def _load(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def _save(path, rows):
    Path(path).write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def stats(args):
    from collections import Counter
    rows = _load(args.ledger)
    st = Counter(r["status"] for r in rows)
    pend = Counter(r["priority"] for r in rows if r["status"] == "pending")
    print(f"{len(rows)} tests | "
          f"red={st.get('red',0)} yellow={st.get('yellow',0)} "
          f"green={st.get('green',0)} skip={st.get('skip',0)} "
          f"pending={st.get('pending',0)}")
    if st.get("pending"):
        print(f"pending by priority: high={pend.get('high',0)} "
              f"med={pend.get('med',0)} low={pend.get('low',0)}")
    done = len(rows) - st.get("pending", 0)
    print(f"coverage: {done}/{len(rows)} adjudicated "
          f"({100*done//max(len(rows),1)}%)")


def nxt(args):
    rows = _load(args.ledger)
    sel = [r for r in rows if r["status"] == "pending"]
    if args.priority:
        sel = [r for r in sel if r["priority"] == args.priority]
    if args.flag:
        sel = [r for r in sel if args.flag in r["flags"]]
    sel = sel[: args.limit]
    if not sel:
        print("(nothing pending for that filter)")
        return
    for r in sel:
        fl = (" [" + ",".join(r["flags"]) + "]") if r["flags"] else ""
        print(f'{r["id"]}  a={r["n_assert"]} {r["loc"]}L  {r["name"]}{fl}')


def _set(args):
    rows = _load(args.ledger)
    idx = {r["id"]: r for r in rows}
    r = idx.get(args.id)
    if not r:
        sys.exit(f"no such id in ledger: {args.id}")
    if args.status in ("red", "yellow"):
        if not (args.evidence and args.story):
            sys.exit(f"refusing to mark {args.id} {args.status}: "
                     f"red/yellow require --evidence file:line AND --story "
                     f"(every accusation carries its receipt)")
    r["status"] = args.status
    if args.pattern:  r["pattern"] = args.pattern
    if args.severity: r["severity"] = args.severity
    if args.evidence: r["evidence"] = args.evidence
    if args.story:    r["story"] = args.story
    if args.verified: r["verified"] = args.verified
    _save(args.ledger, rows)
    print(f"{args.id} → {args.status}")


def report(args):
    rows = _load(args.ledger)
    from collections import Counter
    st = Counter(r["status"] for r in rows)
    reds = [r for r in rows if r["status"] == "red"]
    yels = [r for r in rows if r["status"] == "yellow"]
    pend = st.get("pending", 0)
    print(f"## Verdict\n")
    print(f"| | Count |\n|---|---:|")
    print(f"| 🔴 Cannot fail | {st.get('red',0)} |")
    print(f"| 🟡 Weak signal | {st.get('yellow',0)} |")
    print(f"| 🟢 Real signal | {st.get('green',0)} |")
    if pend:
        print(f"| ⚪ Not yet adjudicated | {pend} |")
    print(f"\n_{len(rows)-pend} of {len(rows)} tests adjudicated"
          + (f"; {pend} still pending — coverage is incomplete._" if pend
             else " — full coverage._"))
    for label, group in (("🔴 Cannot fail", reds), ("🟡 Weak signal", yels)):
        if not group:
            continue
        print(f"\n## {label}\n")
        for r in group:
            ev = f" · evidence `{r['evidence']}`" if r["evidence"] else ""
            sv = f" · {r['severity']}" if r["severity"] else ""
            vf = f" · {r['verified']}" if r["verified"] else ""
            print(f"- **`{r['id']}`** — {r['name']} "
                  f"({r.get('pattern') or 'unclassified'}{sv}{vf}){ev}\n"
                  f"  - {r['story'] or '(no story recorded)'}")


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="enumerate tests into a JSONL ledger")
    b.add_argument("testdir")
    b.add_argument("--out", required=True, help="ledger path (in scratch, NOT the repo)")
    b.set_defaults(fn=build)

    s = sub.add_parser("stats", help="progress: counts by status/priority")
    s.add_argument("ledger")
    s.set_defaults(fn=stats)

    n = sub.add_parser("next", help="pull the next batch of pending rows to review")
    n.add_argument("ledger")
    n.add_argument("--priority", choices=["high", "med", "low"])
    n.add_argument("--flag")
    n.add_argument("--limit", type=int, default=25)
    n.set_defaults(fn=nxt)

    st = sub.add_parser("set", help="record a verdict on one row")
    st.add_argument("ledger")
    st.add_argument("id")
    st.add_argument("--status", required=True,
                    choices=["red", "yellow", "green", "skip", "pending"])
    st.add_argument("--pattern")
    st.add_argument("--severity")
    st.add_argument("--evidence", help="file:line the verdict rests on")
    st.add_argument("--story", help="failure story (required for red/yellow)")
    st.add_argument("--verified", choices=["read", "confirmed"])
    st.set_defaults(fn=_set)

    r = sub.add_parser("report", help="emit a markdown verdict from the ledger")
    r.add_argument("ledger")
    r.set_defaults(fn=report)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
