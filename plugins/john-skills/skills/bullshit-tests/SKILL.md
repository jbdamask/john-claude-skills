---
name: bullshit-tests
description: Audit a codebase's test suite for tests that pass for no good reason — no assertions, tautologies, assertions on mocks only, swallowed exceptions, unawaited async assertions, permanently skipped tests, and other patterns that stay green no matter how broken the code is. Produces a red/yellow/green report. Use when the user says "bullshit tests", "find fake tests", "audit my test suite", "which tests are useless", "are these tests actually testing anything", "check test quality", "find tests that always pass", or asks whether green CI means anything.
version: 0.1.0
---

# Bullshit Tests

Find tests that pass for no good reason.

A test suite's value is entirely in its ability to **fail when the code is wrong**. A test
that cannot fail is worse than no test: it costs CI time, it costs maintenance, and it
buys false confidence. This skill audits a test suite for those tests and reports them.

**Deterministic first, judgment last.** A bundled script ([`scripts/ledger.py`](scripts/ledger.py))
enumerates every test and does the mechanical triage — the part a linter does better than a
model — exhaustively and for free. The LLM is spent only on the judgment a script can't do:
name-vs-behavior, assertion-true-by-construction, artifact-vs-behavior, and the
false-positive filtering. That split is what makes this work on a suite of thousands without
missing tests, inventing findings, or burning tokens reading code that a grep already
cleared. The ledger tracks coverage as a number, so "we checked everything" is verifiable
rather than asserted.

## Model routing

Two roles, two models. **The models are configurable — the defaults are below, and the
user may override either.** What must not change is the separation of concerns: a cheap
model does the high-volume reading and hands *candidates* to a stronger model; only the
stronger model writes a verdict.

| Role | Runs | Default | Why |
|---|---|---|---|
| **Judgment** | the main loop (Step 4) + report | Sonnet-tier | Writes every red/yellow. This is the fabrication-prone step; a wrong finding here destroys trust in all the others. |
| **Fan-out** | Step 3 subagents, on large suites | Haiku-tier | Reads a slice, clears obvious greens, and *flags suspects* — bounded reading + triage, never a verdict. |

Two constraints follow, and they hold **whatever** models the user picks:

1. **The fan-out never writes a red/yellow.** It surfaces candidates; the judgment model
   adjudicates them. A cheap model wrongly clearing a green is a recall miss (backstopped by
   the ledger's mechanical triage and a spot-check); a cheap model *writing a verdict* is a
   fabrication, which the whole skill exists to prevent.
2. **The fan-out returns structured output.** Its job is to feed another agent, so it must
   emit a machine-consumable payload against a fixed schema — not prose the primary has to
   re-parse. The schema is in Step 3.

The judgment model rides the session's main loop, so the skill can't set it — the user
launches the session on their chosen judgment model. The skill *can* set the fan-out
model, and does (Step 3).

## Scope

**This skill diagnoses. It does not fix.** Do not rewrite, delete, or repair tests unless
the user asks in a follow-up. The deliverable is a report.

**It audits signal, not suite economy.** A test that passes for no good reason is in scope.
A test that is an exact duplicate of another, or pins behavior nobody wants, or covers dead
code is *waste* — it can still fail, so it isn't false confidence. Note it in passing if you
trip over it, but that's a different audit; don't stretch this one to cover it.

## Hard rule — never modify the user's code

**Under no circumstances modify any file in the user's working tree — above all on `main`
or any other shared/default branch.** Not source, not tests, not "just for a second, I'll
revert it." Other people work in that checkout, and a clean `git status` afterward is not
proof that nothing went wrong in between. Writing the report into the audited repo counts
as touching it (Step 6).

This skill reaches its conclusions by **reading**, which is nearly always sufficient. When
it isn't, you stop and ask (Step 5). A weaker finding always beats touching a checkout
someone else is using.

## The one question

For every test examined, answer exactly one question:

> **If I broke the code this test claims to cover, would this test go red?**

If the answer is "no", it's RED. If the answer is "only for some breakages, and not the
obvious ones", it's YELLOW. Everything else is GREEN.

**Judge the promise-signal pair.** A test is a promise — its name, plus whatever its
docstring and comments claim — bound to a signal, which is whatever its assertions can
actually detect. The defect is always the *gap* between them. Which side gets fixed
(rename the test, or strengthen it) is the maintainer's call, not yours; report the gap and
leave the direction to them.

Never flag a test on pattern-matching alone. Every finding must come with a concrete
**failure story**: a specific way the production code could be broken while this test
stays green. If you cannot write that sentence, you do not have a finding — drop it.

This rule buys precision by paying recall, deliberately. Crying wolf once costs you every
later finding. But it under-reports diffuse rot that resists a one-sentence story —
snapshot decay, expected values retrofitted to match output, suites that only ever test
the happy path. Say so in the report's Coverage section.

## Workflow

### Step 1 — Confirm scope

First, establish the ground state and **report it in the same message you ask in**:
current branch, whether the working tree is clean, and whether the repo supports
`git worktree`. Never start an audit without knowing what branch you're standing on.

Then ask, in one message, only what you actually need: which directory / package / test
suite to audit, if the repo has more than one, and how deep to go (full read vs. a sample,
for a suite in the thousands).

Do **not** ask about mutation up front. The audit is read-only, and most findings never
need it. If a specific finding later turns out to be unresolvable by reading, ask then —
about that one finding, with the reason (Step 5).

If the user already named a path or said "the whole thing", just proceed — but still
report the branch and tree state.

### Step 2 — Map the suite, then build the ledger

**Why a ledger.** On a suite of thousands of tests you cannot read every test in one
context, so reading-only means sampling, and sampling silently misses. The bundled
[`scripts/ledger.py`](scripts/ledger.py) fixes that: it enumerates *every* test into a
JSONL worklist in scratch space, triages the mechanically-detectable cases deterministically
(free, exhaustive, no hallucination), and tracks a status per test. Coverage becomes a
number you can check — `pending` — not a claim. The work is resumable and fannable-out: any
number of turns or subagents can draw pending rows and record verdicts without losing place.

First, know the stack so you read it idiomatically — runners (pytest, Jest, Vitest, Mocha,
JUnit, Go `testing`, RSpec…), config files, and above all the **shared helpers, custom
matchers, fixtures, and conftest**. Read those first; most false positives come from an
assertion living in `assert_valid_user()` or a `roundTrips()` helper.

Then build the ledger (writes to scratch, never the repo):

```
python3 <skill>/scripts/ledger.py build <testdir> --out <scratch>/audit.ledger.jsonl
```

It reports the inventory and the triage: `high` = mechanical candidates (a flag fired —
these are where reds concentrate), `med` = thin (0–1 assertions, need a read), `low` =
likely green (≥2 assertions, no flag).

The enumerator parses **Python** (pytest/unittest), **JavaScript/TypeScript**
(Jest/Vitest/Mocha, including `__tests__/` dirs), **Go** (`testing`/testify), **Ruby**
(RSpec/Minitest/Rails), and **Rust** (`#[test]` family). For any other language it finds
nothing and prints a warning — if the suite is in Kotlin, C#, PHP, Elixir, etc., the ledger
is empty and you must **say so**, not report a clean bill of health. Even for a supported
language, the count is only as complete as the regex parsed (e.g. a JS file outside the
naming conventions is missed); if the total looks low against the codebase, flag it. Report
the counts to the user before adjudicating.

### Step 3 — Work the ledger, highest-priority first

The mechanical sweep is already done and it was exhaustive; the LLM's job is the judgment
the script can't do. Pull batches and adjudicate — do **not** re-derive the whole suite by
reading it top to bottom.

```
python3 ledger.py next  <ledger> --priority high        # every mechanical candidate — read all
python3 ledger.py next  <ledger> --priority med         # thin tests — read all
python3 ledger.py stats <ledger>                        # your progress bar (pending count)
```

- **`high`** and **`med`**: read each one (Step 4) and record a verdict. These are the
  whole judgment surface — usually a small fraction of the suite.
- **`low`**: do not read all of them. Read a disclosed sample (say how many), enough to
  validate that "≥2 assertions, no flag" really does mean green in *this* codebase. If the
  sample turns up a bullshit test the flags missed, widen the sample and note the miss.

#### Fanning out on a large suite (the fan-out model)

For a big suite, parallelize the *reading*, not the *verdicts*. Spawn fan-out subagents on
the configured fan-out model (default Haiku-tier — pass `model: haiku` on the Agent call),
each handed a disjoint slice (a `--priority`/`--flag` filter or a file range). Their job is
to **clear obvious greens and flag suspects — never to write a red or yellow.** Every real
finding is adjudicated by the judgment model (Step 4).

The fan-out is providing input to another agent, so it **returns structured output**, not
prose. Instruct each subagent to reply with a JSON object against exactly this schema and
nothing else:

```json
{
  "reviewed": [
    {
      "id": "tests/foo.py:42",          // ledger id, verbatim
      "call": "green" | "suspect",       // green = confidently real; suspect = needs judgment
      "reason": "one line: why green, or what smells off",
      "evidence": "file:line the reason rests on, or null"
    }
  ],
  "unsure": ["tests/bar.py:9"]           // ids it couldn't reach a call on — treat as suspect
}
```

The primary consumes that payload deterministically: **`suspect` and `unsure` rows go to
Step 4** for adjudication on the judgment model; **`green` rows** are bulk-set green, with a
disclosed random sample re-read by the judgment model to confirm the fan-out's greens hold
(a wrongly-cleared green is a miss, so sample enough to trust the heuristic). A fan-out
subagent must never call `ledger.py set --status red`/`yellow`; if it thinks it found one,
that's a `suspect`.

Record every verdict with the tool — this is what makes coverage auditable and keeps you
honest:

```
python3 ledger.py set <ledger> <id> --status green --pattern "..." --verified read
python3 ledger.py set <ledger> <id> --status red   --pattern "..." \
        --severity "only guard on X" --evidence src/foo.py:88 --story "..." --verified read
```

The tool **refuses** a `red`/`yellow` without both `--evidence` (a real `file:line`) and
`--story`. That is the structural brake on fabrication: no accusation without its receipt.

### Step 4 — Adjudicate one row by reading it

For each `high`/`med` row (and each sampled `low`), open the test and everything it calls.
Assign a verdict only when you can write the failure story. Check:

- Does a helper, fixture, custom matcher, or teardown hook contain the real assertion?
- Is this a deliberate smoke/import/compile/type test? Those are legitimate — but they
  belong in YELLOW if their name promises behavior they don't check.
- Is the mock assertion actually a **contract test** (the point is that the collaborator
  gets called correctly)? That's legitimate GREEN.
- Does the framework fail the test implicitly (unmatched HTTP mocks at teardown, strict
  mock verification, `--strict-markers`, snapshot obsolescence checks)?

**Cite where you verified any runtime-semantics claim.** This is the failure mode that
makes a *wrong* finding more convincing than a right one. If a failure story rests on a
claim about what the code does — "`parse_page` raises on an empty title", "this helper
returns `None` on miss" — you must have read the line that establishes it, **and** checked
that fixtures, `conftest`, autouse setup, or module-level patching don't replace that
symbol as the test actually imports it. In dynamic languages a confident static read can be
confidently wrong, and the failure-story rule will dress the error up persuasively. Name
the source line in the finding. If you can't verify the claim, downgrade the finding rather
than assert it.

Then read the **siblings** — the other tests in the same file and module. This is required,
not optional: it's what tells you whether the gap you found is a shipping risk or a
redundant test with better coverage next to it. It also catches your own overreach; a
finding that looks severe alone often turns out to be guarded three tests down.

Assign a category and a severity (both factors — see Categories). Only report findings
you'd defend.

### Step 5 — Blast radius (usually: don't run code)

Reading establishes whether a test *can* fail, and reading the siblings establishes whether
the module covers the gap — both are part of Step 4's failure story. What reading can't do
at acceptable cost is the **suite-wide** claim: *nothing anywhere catches this*. That claim
needs execution, and it's the one thing that turns "this test is weak" into "this behavior
ships unverified."

Don't improvise it. For anything systematic, recommend a real mutation tool in the report —
`mutmut`, `cosmic-ray`, Stryker, PIT — pointed at the module. They do this properly, and
they don't need to touch anyone's checkout.

For a one-off on a headline finding, ask first, offering: **(1) skip it** — report as READ
with its failure story, usually the right call; **(2) an isolated copy** (`git clone` /
`cp -r` to `/tmp`); or **(3) an issue + branch + throwaway worktree**
(`git worktree add /tmp/bullshit-tests-<slug> -b <branch>`). Wait for a real answer — an
earlier "yes, audit this" is not consent to edit their code.

If approved: inside the isolated copy only, break the code crudely (wrong constant,
`raise NotImplementedError`), **re-run the full suite** — that's the whole point, a
single-test re-run only re-proves what reading showed — then restore before the next
finding. Still green → mark it **CONFIRMED** and record the exact mutation as evidence.
Went red → the test was fine; drop the finding and say so.

### Step 6 — Write the report

The ledger is the source of truth. Generate the skeleton from it, then write the prose:

```
python3 ledger.py stats  <ledger>     # final counts + the pending number
python3 ledger.py report <ledger>     # verdict table + every red/yellow with its receipt
```

If `pending` is non-zero, the report must say so — coverage is incomplete and the
percentages are partial. Do not round a partially-worked ledger up to "audited." Follow
[references/report-template.md](references/report-template.md) for the shape.

**Never write the report into the audited repo.** It is your output, not their source
tree, and it should not show up in their `git status` or risk being committed.

**Ask the user where they want it before writing it.** Offer a sensible default so it's a
one-word answer — e.g. "Where should the report go? Default is your scratchpad
(`<path>`); or name a path (not inside the repo)." Use whatever they say.

Only skip the question when you can't ask — a named path already given earlier, or a
non-interactive run. Then fall back in this order and state where it went: (1) the path
they named, (2) the session scratchpad, (3) `~/scratch/` if it exists, (4) `/tmp/`.

Filename: `bullshit-tests-report-<repo>-YYYY-MM-DD-HHMM.md`, using the real current
date/time — look it up, don't guess.

Then print to the user: the counts per category, the three worst findings, and the path.

## Categories

Judge by signal, not by style. A short test with one sharp assertion is GREEN.

### 🔴 RED — cannot fail

Passes regardless of what the production code does. Zero signal, false confidence.

### 🟡 YELLOW — weak or misleading signal

Stays green under a breakage that a reader of the test's name would expect it to catch.
(Not "misses some breakage" — every test misses some breakage.)

### 🟢 GREEN — real signal

Asserts observable behavior of the code under test, using values it did not itself supply,
and would go red if that behavior changed. Includes legitimate contract tests on mocks,
deliberate and clearly-named smoke tests, and property-based tests.

### Severity is two-factor

The category above is only factor one. Before assigning severity, answer factor two:
**is the behavior this test names covered by anything nearby?** Read the sibling tests in
the same file and module — that check is part of the failure story, not optional.

- Weak test, **strong** sibling coverage → a cleanup note. Real, but nobody needs to act.
- Weak test that is the **only** guard on a shipped behavior → this is the finding the
  whole report exists for. Say so explicitly and rank it first.

A list of individually-correct verdicts that doesn't separate these two is worse than
useless — it reads as uniform risk and buries the one thing worth doing. The suite-wide
version of factor two ("*nothing anywhere* covers this") can't be established by reading;
see Step 5.

## Rules

- **No fixes.** Report only, unless asked.
- **No pattern-only findings.** Failure story or it doesn't ship.
- **Read helpers before judging.** The assertion is often one call away.
- **Rank by factor two.** The only-guard-on-shipped-behavior findings go first. Everything
  else is a cleanup note, and should read like one.
- **Don't moralize.** Report the pattern, the risk, and the file:line. Some of these were
  deliberate trade-offs by people with more context than you.
- **Say what you didn't cover** — sampling, skipped directories, and the recall blind spot
  above. A silent cap reads as full coverage.
- **Announce every suite run before it happens**, with why and roughly how long. Test runs
  are minutes of the user's time; don't spend them silently.
- **Never edit the user's tree; never write the report into their repo.** See the hard rule.
