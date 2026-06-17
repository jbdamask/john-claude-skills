---
name: Five Whys Root Cause Analysis
description: Evidence-based root cause diagnosis using a branching five-whys investigation. Produces a likelihood-ranked list of candidate root causes — diagnosis only, never a fix. Use ONLY when the user explicitly asks to diagnose a problem or find a root cause, with phrases like "find the root cause", "diagnose this", "do a five whys check", "root cause analysis", "why is this happening", or "run a five whys". Do NOT trigger on generic mentions of errors, bugs, or fix requests.
version: 0.2.0
---

# Five Whys Root Cause Analysis

## Purpose

Identify the root cause(s) of a reported problem through systematic, evidence-based
investigation — and stop there. This skill **diagnoses; it does not fix.** Diagnosis is
deliberately decoupled from solution so the user can review the findings and decide what
to do next.

The deliverable is a **likelihood-ranked list of candidate root causes**, each backed by
concrete evidence and a stated confidence level.

## When this skill applies

Trigger **only** on an explicit diagnostic request — e.g. "find the root cause of X",
"diagnose this", "do a five whys check", "run a root cause analysis", "why is this
happening". Do **not** trigger on a bare bug report or a "fix this" request. If the user
just wants something fixed, this skill is not in scope.

## Core problem this prevents

The default failure mode when facing a problem:

1. Observe symptom
2. Speculate about cause
3. Implement a speculative fix
4. Fix doesn't work or creates new problems
5. Repeat indefinitely

This skill breaks that loop by forcing **evidence before conclusions** and by separating
the act of diagnosis from the act of fixing.

## How to investigate

### Conducting the investigation

Read whatever you need, reason about the evidence, and assemble the ranked list. You may
read **any and all files** you judge relevant to finding the root cause — error sites, call
sites, dependencies, configs, tests, logs. Follow the evidence wherever it leads; do not
artificially limit which files you open.

**Use subagents freely.** When the investigation is large or naturally parallel — e.g. each
hypothesis from Phase 1 can be branch-tested independently, or a wide codebase needs
sweeping — dispatch subagents (the Explore agent for read-only searches, or general
agents) to investigate branches concurrently and report evidence back. Have each subagent
return its findings (causal chain, evidence, refute/support verdict); you synthesize the
results into the ranked list. This keeps the main context focused and speeds up
breadth-first investigation.

### Phase 0 — Define the problem

Before asking a single "why", pin down what you're actually diagnosing. A vague symptom
guarantees a low-confidence result.

1. **Review current context first.** Re-read what the user already said, the error/output
   in the transcript, and the relevant code. Most of what you need to frame the problem is
   usually already in front of you — extract it before asking anything.
2. **State the problem precisely:** what is the observed behavior, what is the *expected*
   behavior, and how do you know they differ. If you can't articulate "expected vs.
   actual", you don't yet have a problem definition.
3. **Ask clarifying questions only if something genuinely blocking is missing** — and only
   after step 1 confirms it isn't already available. Don't interrogate. Batch questions
   into one short round, ask only what changes the investigation, and prefer concrete asks
   ("can you paste the error log / the failing command output?") over open-ended ones. If
   the context is sufficient, skip this and proceed.

### Phase 1 — Enumerate hypotheses, then branch-test

Do **not** commit to the first causal chain that comes to mind — that tunnel vision is a
top cause of low-confidence output. Instead:

1. **Brainstorm the candidate causes up front.** List every plausible cause of the symptom
   you can think of, given the evidence so far. Breadth here is cheap and prevents missing
   the real one.
2. **Then branch-test each.** Treat the list as the top level of a causal tree and
   investigate each candidate with the branching five-whys below. Discard branches the
   evidence refutes; deepen the ones it supports.

### Phase 2 — The branching five-whys

For each surviving hypothesis, start from the symptom and iteratively ask "why?", grounding
every answer in evidence you actually checked. "Five" is just a name — continue until you
reach an actionable root cause, however many levels that takes.

**Causal chains branch.** Real problems often have more than one contributing cause at a
given level. When a "why" has multiple plausible answers supported by evidence, **split
into branches** and pursue each. Track the result as a small causal *tree*, not a single
rope. Different branches may terminate in different root causes — that's expected, and all
surviving candidates belong in the final ranked list.

```
Symptom
├── Hypothesis A ──→ Why? → Cause ──→ Why? → Root cause A1
│                                   └→ Why? → Root cause A2
├── Hypothesis B ──→ Why? → Root cause B1
└── Hypothesis C ──→ [refuted by evidence — discarded]
```

### Evidence-based answers

For each "why", gather concrete evidence before answering:

- **Read the code that actually runs** — files in error messages, call stacks, related
  modules and dependencies.
- **Examine outputs** — error messages, stack traces, logs, console output, test results.
- **Check configuration** — environment variables, config files, build settings,
  dependency versions.
- **Verify assumptions** — don't assume; check actual behavior and actual values present.

Base each answer on evidence, not speculation. If a branch rests on an unverified
assumption, either verify it or mark that candidate's confidence down accordingly.

## What counts as a root cause

A candidate qualifies as a root cause when:

1. **Actionable** — could be addressed with a code, config, or data change within our
   control. (We are not fixing it here — only confirming a fix is conceivable.)
2. **Directly explanatory** — fully accounts for the symptom along its branch, with no
   gaps in the causal chain. Removing this cause would eliminate the symptom.
3. **Terminal** — the next "why" would go outside our control (external system,
   architectural decision, business requirement) or would not lead anywhere more
   actionable.

### Root cause vs. symptom restatement

**Symptom:** "Tests are failing"
- ❌ Not a root cause: "The test expectations are wrong" (what made them wrong?)
- ❌ Not a root cause: "The code doesn't match tests" (why doesn't it match?)
- ✅ Root cause: "Function returns null when `user.profile` is undefined, but tests expect an empty object"

**Symptom:** "API returns 404"
- ❌ Not a root cause: "Route doesn't exist" (why doesn't it exist?)
- ✅ Root cause: "Route path is `/api/v1/users` but code defines `/api/users` — missing `/v1` prefix"

Don't stop at: symptom restatements, vague causes ("there's a config issue"), or the first
plausible explanation without verification.

## Confidence gate

After assembling candidates, **state your confidence in the top-ranked candidate** —
`high`, `medium`, or `low` — and say what drove that rating. The skill **terminates cleanly
only at high confidence.** Anything less means there is more investigation to do, so loop
back rather than presenting prematurely.

### If confidence is below high — diagnose *why*, then act

Low or medium confidence is itself a symptom. Identify which of these is the cause and
apply the remedy before re-ranking:

| Reason for low confidence | Remedy |
|---|---|
| **Incomplete hypothesis set** — committed to one chain without enumerating alternatives | Return to Phase 1; brainstorm the full candidate list, then branch-test each |
| **Missing critical information** — no logs, stack trace, runtime values, version info | Name the specific missing artifact; ask the user for it (or where to find it), or obtain it yourself |
| **Unverified assumption in the chain** — a "why" was a guess, never checked | Go verify it against actual code/values; if unverifiable, mark that candidate down |
| **Non-discriminating evidence** — two+ candidates fit equally well | Find a disambiguating observation that only one candidate predicts |
| **Correlation, not causation** — suspicious code but no proven link to the symptom | Trace the actual execution path from symptom back to the suspected cause |
| **Ill-defined symptom** — expected vs. actual still unclear | Return to Phase 0; resolve what "correct" looks like |
| **Stale / conflicting evidence** — code doesn't match what's running, or sources disagree | Reconcile which source is authoritative before trusting it |
| **Intermittent / non-deterministic** — race, flake, load-dependent (a confidence *ceiling*) | Note the timing/concurrency factor; declare the ceiling rather than spinning |
| **Inaccessible / opaque component** — external service or code you can't inspect (a *ceiling*) | Mark the branch as a boundary; the candidate stays explicitly hypothetical |

Re-investigate and re-rank. **Loop** until confidence reaches high — *or* a full pass turns
up no new evidence and the only remaining limiters are genuine ceilings (intermittent,
opaque). In that terminal-but-uncertain case, present the best-effort ranked list and state
plainly that confidence is capped, which reason caps it, and what would lift it.

### If confidence is high — pressure-test, then present

Before presenting, **pressure-test the diagnosis** by invoking the `phone-a-friend` skill
(via the Skill tool). Frame it as adversarial review of the top candidate: hand the friend
the symptom, the causal chain, and the evidence you relied on, and ask it to refute the
diagnosis or surface a more likely cause. Fold the outcome — confirmation, a downgrade, or
a new candidate — into the ranked list before showing it to the user. Rationale: a
confident-but-wrong diagnosis is the most dangerous output, and high confidence is the
skill's clean exit, so it earns one adversarial check before it ships.

## Output format

Present findings as a ranked list. Do **not** propose or implement a fix.

```markdown
## Root Cause Analysis: [symptom]

**Symptom observed:** [what was reported / observed]
**Files & evidence examined:** [key files, logs, outputs you inspected]

### Candidate root causes (most → least likely)

#### 1. [Candidate] — Likelihood: High · Confidence: [high/medium/low]
- **Causal chain:** Symptom → why → why → … → this cause
- **Evidence:** [concrete evidence: file:line, log excerpt, observed value]
- **Why it's a root cause:** [actionable · explanatory · terminal]
- **What would raise/lower confidence:** [if not high]

#### 2. [Candidate] — Likelihood: Medium · Confidence: [...]
- ...

#### 3. [Candidate] — Likelihood: Low · Confidence: [...]
- ...

### Confidence statement
Top candidate confidence: **[high/medium/low]** — [reasoning].
[If high: "Pressure-tested via phone-a-friend; outcome: …"]
```

## Boundaries

- **Diagnose, don't fix.** Never edit code or propose an implementation as part of this
  skill. If the user wants a fix, that's a separate, explicit request after they've
  reviewed the diagnosis.
- **Present multiple candidates** ranked by likelihood — not a single answer — unless the
  evidence genuinely supports exactly one.
- **Ground everything in evidence.** A candidate with no supporting evidence does not
  belong on the list.

## Success criteria

- ✅ Problem defined (expected vs. actual) before investigating; context reviewed before any clarifying question
- ✅ Hypotheses enumerated up front, then branch-tested — not a single committed chain
- ✅ Likelihood-ranked list of candidate root causes produced
- ✅ Each candidate backed by concrete evidence and a complete causal chain
- ✅ Confidence loop run: below-high confidence diagnosed via the taxonomy and re-investigated; clean exit only at high confidence or a declared ceiling
- ✅ phone-a-friend pressure-test run when confidence is high
- ✅ No fix proposed or applied
