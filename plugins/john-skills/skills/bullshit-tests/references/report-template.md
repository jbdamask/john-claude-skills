# Report template

Write to `bullshit-tests-report-<repo>-YYYY-MM-DD-HHMM.md`, **outside the audited repo** —
the user's named path, else the session scratchpad, else `~/scratch/`, else `/tmp/`. Never
drop it into the source tree. Look up the real current date/time — never guess it.

**Shape: verdict and actions in the first screen; findings below as evidence.** Someone who
reads only the top should learn the state of the suite and what to do about it. Someone who
doubts a specific claim scrolls down and checks it.

---

```markdown
# Bullshit Test Report — <repo name>

**Date:** YYYY-MM-DD HH:MM · **Commit:** `<sha>`
**Scope:** <paths / sampling>
**Method:** read-only — findings traced through the source, no code modified

## Verdict

| | Count | |
|---|---:|---|
| 🔴 Cannot fail | 1 | |
| 🟡 Weak signal | 11 | |
| 🟢 Real signal | 88 | |

<Two sentences, maximum. The actual state of the suite, and where the risk sits. Name the
module, not the vibe.>

## Do these three things

1. **<Action>** — <one line of why. Lead with the finding that is the only guard on a
   shipped behavior; that is the whole reason the report exists.>
2. **<Action>** — <one line.>
3. **<Action>** — <one line.>

<Everything below is the evidence for the above.>

---

## 🔴 Cannot fail

### R1. `tests/billing/test_invoice.py:44` — `test_applies_late_fee`
**Pattern:** assertion true by construction · **Coverage:** no sibling covers late-fee math

```python
mock_calc.compute.return_value = Decimal("5.00")
assert invoice.apply_late_fee(order) == Decimal("5.00")
```

**Fails to catch:** any change to `apply_late_fee` — wrong rounding, skipped fee, wrong
sign, the function deleted entirely. The assertion checks the value the test handed to the
mock. **Nothing else in `tests/billing/` exercises the calculation**, so late-fee math
currently ships unverified.

**Fix:** assert against a real `LateFeeCalculator`, or at minimum
`mock_calc.compute.assert_called_once_with(order.balance, RATE)`.

---

## 🟡 Weak signal

### Y1. `tests/api/test_auth.py:88` — `test_rejects_expired_token`
**Pattern:** over-broad exception · **Coverage:** 3 siblings cover the reject path

```python
with pytest.raises(Exception):
    authorize(expired_token)
```

**Fails to catch:** a `TypeError` from a changed signature satisfies this, so the test
passes even when authorization never runs. It can't distinguish "rejected because expired"
from "rejected for any reason."
**Fix:** `pytest.raises(TokenExpired, match="expired")`.

---

## Everything else

<Cap detailed findings at ~8-10 total. The tail goes here as one table with a single
exemplar per pattern — not as sections. If a finding needs the sentence "listed for
completeness, not as work," it belongs in this table instead.>

| Pattern | Count | Exemplar | Severity |
|---|---:|---|---|
| Empty-in / empty-out only | 5 | `tests/test_grouping.py:69` | cleanup — siblings cover |
| Broad `raises` without `match=` | 2 | `tests/test_facts.py:191` | one-word hardening |

## 🟢 What's working

<One paragraph. Not a list. What the healthy parts do well, and the one file worth copying
as the house pattern.>

## Coverage of this audit

- **Read:** N of M test cases. If sampled, say how — the red/yellow percentages are sample
  estimates, not suite-wide counts.
- **Swept:** which greps ran across 100% of files, so the reader knows what *is* exhaustive.
- **Models:** which model wrote the verdicts and which did the fan-out (if any). If a
  fan-out model cleared greens, say how many, and how many the judgment model re-checked —
  every red/yellow was written by the judgment model.
- **Blind spot of this method:** the failure-story rule under-reports diffuse rot —
  snapshot decay, expected values retrofitted to match output, happy-path-only suites.
  Those need mutation testing or a human read, not this.
- **Can't see:** e.g. whether CI runs these suites at all; runtime-only skips.
```

---

## Writing rules

- **Failure story or cut it.** "Fails to catch:" must name a specific breakage that stays
  green. Vague risk language means the finding wasn't verified.
- **State coverage on every finding.** One clause: does anything nearby guard this behavior?
  That clause is what separates a shipping risk from a cleanup note.
- **Snippets short.** 3-6 lines. Enough to see the problem.
- **Every finding gets a fix**, one line, concrete. Preferably pointing at a better pattern
  that already exists elsewhere in their suite.
- **Verification status only when it isn't the default.** Everything is READ unless the user
  approved an isolated copy; then mark those `CONFIRMED` and say where they ran. Don't label
  every finding when the Method header already covers it.
- **No blame, no lecturing.** Some of these were deliberate trade-offs — say so when the
  code says so.
- **Report what you skipped.** A silent cap reads as full coverage.
