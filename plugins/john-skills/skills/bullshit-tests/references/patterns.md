# Detection catalog

Ten patterns, grouped by *how the test fails to carry information* rather than by syntax.
Each one: what it is, how to find it, and — the important column — **what it gets confused
with**. The "Looks like but isn't" notes are what keep this skill from crying wolf.

Severity here is a starting point. Grade the actual test, using both factors in SKILL.md:
can it fail, and is the behavior it names covered by anything nearby.

**What the script flags vs. what you judge.** `scripts/ledger.py` pre-flags the greppable
patterns and raises them as high-priority candidates — no-assertion (1), tautology (2),
disabled/`.only` (5), over-broad `raises` (7), swallowed (3), source-text reads (6),
default-to-truth and unawaited-async. A flag is a *candidate*, never a verdict: the
assertion may live in a helper, the `raises` may be the point, the source-text read may be
legitimate IaC. Your job is to confirm or clear each flagged row by reading it. Patterns 4
(unawaited async, subtle cases), 9 (name-vs-behavior), and the "guaranteed by a preceding
line" flavor of 2 are largely **not** greppable — they surface from reading the thin (`med`)
rows and sampled `low` rows, which is why those still get read.

---

## 1. No assertion the runner can reach — 🔴

The test calls code and checks nothing. It fails only if something throws. Four syntaxes,
one defect: an empty body, an early `return`, a call with no assertion after it, and a
"didn't throw" test wearing a behavioral name.

```python
def test_payment_flow():
    pass                          # or: ...  or: TODO

def test_calculates_discount():
    calculate_discount(order)     # no assertion; only a crash fails it

def test_thing():
    return                        # everything below is unreachable
    assert something
```

```javascript
it('handles refunds', () => {})
it('handles refunds')                    // Mocha pending; often read as passing
it('x', () => { if (!process.env.CI) return; expect(a).toBe(b) })
```

**Find it:** enumerate test functions, then check each body for any assertion token.

```
rg -n "^\s*(async )?def test_" --type py      # then: assert, self.assert, pytest.raises, assert_called
rg -n "(it|test)\(['\"\`]" --type ts --type js # then: expect(, assert., should., .toMatchSnapshot(
rg -n "^func Test" --type go                   # then: t.Error, t.Fatal, require., assert.
rg -n "@Test" --type java                      # then: assert, verify(, Assertions.
```

**Looks like but isn't:**
- Assertions live in a shared helper (`_check_response(r)`, `roundTrips(a, b)`). **Follow
  the call before judging** — this is the single most common false positive.
- The framework asserts implicitly: `pytest-httpx`/`responses` fail at teardown on
  unmatched requests; `autospec` mocks raise on bad signatures; strict stubs (Mockito,
  `testify/mock` `AssertExpectations`) fail on unused or unmet stubs.
- Deliberate crash-regression tests ("this used to segfault") and named smoke tests. Real,
  but 🟡 if the name promises behavior the body never checks.
- Type-level tests (`tsd`, `expectTypeOf`, mypy) — the checker is the assertion.

---

## 2. Assertion true by construction — 🔴

The assertion cannot convey information about the code under test, because something other
than that code already guarantees it. Three flavors:

**Tautology** — true regardless of anything:

```python
assert True
assert result == result
assert len(items) >= 0
```
```javascript
expect(true).toBe(true)
expect(x).toEqual(x)
```

**Closed over its own input** — the expected value came from the test itself, or from a
mock the test configured:

```python
mock_db.get.return_value = {"id": 1}
assert service.fetch(1) == {"id": 1}      # asserts the mock, not the service

expected = transform(data)
assert transform(data) == expected        # compares the function to itself
```

**Guaranteed by a preceding line** — the subtlest and easiest to miss. A prior call's
contract already forces the assertion true:

```python
page = parse_page(fixed, path=path)   # raises PageError if title is empty
assert page.title                     # ...so this can never fail
```

**Find it:** `rg -n "assert True|assert 1 == 1|assertTrue\(True\)"`,
`rg -n "expect\((true|1)\)\.(toBe|toEqual)\((true|1)\)"`, any assertion whose two sides are
the same expression, and any `return_value`/`mockResolvedValue` whose value reappears in an
assertion. For the third flavor there is no grep — read the lines above the assertion and
ask what they already guarantee.

**Related, as bullets:**
- **Default-to-truth helpers** — a helper returning a truthy value on its own failure path
  makes every downstream assertion vacuous: `except Exception: return True`,
  `status = get_status() or "ok"`, `response.get("valid", True)`.
  Grep: `rg -n "except.*:\s*return True|or True\b|\|\| true\b|\.get\([^)]+,\s*True\)"`.
- **Testing the language or the framework** — `assert User(name="bob").name == "bob"`
  exercises the dataclass, not your logic. Harmless, but not coverage.

**Looks like but isn't:**
- **Contract tests.** `mock_db.get.assert_called_once_with(1)` is a real assertion about
  the SUT's behavior. 🟢.
- **Round-trips.** `decode(encode(x)) == x` is a genuine property. 🟢.
- Pass-through adapters where "returns what the dependency returned" *is* the spec — but
  the test should also pin the mapping and the error handling. 🟡.

---

## 3. Assertion the runtime can skip or swallow — 🔴

The assertion exists in the source but doesn't run, or runs and has its failure discarded.

```python
for item in results:              # results == [] → zero assertions, green test
    assert item.valid

if user is not None:              # None → nothing checked
    assert user.name == "x"

try:
    assert result == expected
except Exception:                 # AssertionError IS an Exception
    pass
```
```javascript
try { expect(a).toBe(b) } catch (e) {}
it('x', async () => { await run().catch(() => {}) })
```

**Find it:** `rg -n "except (Exception|AssertionError|BaseException).*:\s*(pass|continue)"`,
`rg -n "catch\s*\([^)]*\)\s*\{\s*\}"`, and any loop or conditional wrapping the only
assertion in a test.

**Looks like but isn't:**
- A loop over a **hardcoded** collection always iterates — not this pattern.
- A guard precedes it: `assert results` / `expect.assertions(n)` / `expect.hasAssertions()`.
  With that, 🟢.
- `try/finally` cleanup with no `except`, and `pytest.raises` blocks. Both fine.

---

## 4. Unawaited async assertions — 🔴

The test returns before the assertion runs; the runner sees a resolved promise and reports
green. Non-obvious and very common.

```javascript
it('rejects bad input', () => {
  expect(api.call(bad)).rejects.toThrow()        // no await/return — always passes
})
it('works', async () => {
  somethingAsync().then(r => expect(r).toBe(1))  // assertion escapes the test
})
it('cb', (done) => { fetchIt(r => { expect(r).toBe(1) }) })   // done() never called
```
```python
def test_thing():
    result = async_fn()     # coroutine never awaited
    assert result           # a coroutine object is always truthy
```

**Find it:** `rg -n "expect\([^)]*\)\.(resolves|rejects)"` and require a preceding
`await`/`return`; `.then(` inside a test body with no `return`; an `async def test_` with
no `@pytest.mark.asyncio`/anyio marker (silently never awaited under some configs).

**Corroborate by running the suite once** and grepping output for
`coroutine ... was never awaited`, `UnhandledPromiseRejection`, or Jest's "test finished
but async work remained."

---

## 5. Disabled, but reported as green — 🔴 / 🟡

```python
@pytest.mark.skip(reason="fix later")
@pytest.mark.xfail                       # without strict=True, passes BOTH ways
```
```javascript
it.skip(...)   xit(...)   it.only(...)   it.todo(...)
```

**Grade by age and reason.** `git blame` the line: a skip older than ~6 months with no
linked issue is 🔴 — dead code reading as coverage. A recent skip with an issue link is 🟡.
`xfail` without `strict=True` is 🔴 regardless.

**`.only(` committed in JS is always 🔴** — it silently disables every *other* test in the
file, which is worse than disabling itself.

**Looks like but isn't:** environment guards that don't fire (`pytest.skip("moto not
installed")` in a repo where moto is installed). Confirm with a real run: 0 skipped means
0 skipped.

---

## 6. Asserts on an artifact of the code, not its behavior — 🟡

The test inspects the *source text*, a *string constant*, or a *config file* instead of
running anything. It passes whenever the characters are present, regardless of whether the
code does what the characters imply.

```javascript
// passes even if the call is inside `if (false)`, a comment, or a dead branch
const shareIdx = pwaJsSource.indexOf("appendShareAffordance(ai,");
expect(shareIdx).toBeLessThan(pwaJsSource.indexOf("appendChatExtras(ai,"));
expect(appJsSource).toMatch(/mcpTool\(\s*"list_page_versions"/);
```
```python
# passes even if the call site stops passing this constant to the model
from shared.ingest import DRAFT_UPDATE_SYSTEM
assert "contradiction" in DRAFT_UPDATE_SYSTEM.lower()
```

**Find it:** `rg -ln "readFileSync|\.read_text\(\)" <test dirs>`, then look for assertions
against that text. Also: any assertion on an imported constant that the *call site*, not
the test, is supposed to use.

Common and often deliberate — it's the standard fallback for code that resists importing
(monolithic IIFEs, non-module scripts, prompt strings). Say so in the finding, and note
that fixing it usually means a refactor (make the closure importable), not a better
assertion. Two extra failure modes worth flagging: a slice-window match
(`source.slice(idx, idx + 900)`) breaks on unrelated edits, so it's wrong in both
directions; and the test tends to be named for the behavior it cannot see.

**Looks like but isn't:**
- **Infrastructure-as-code.** Assertions on a parsed CloudFormation/Terraform/k8s template
  are behavior — the template *is* the artifact being shipped. 🟢.
- **Lint rules and codegen** tested against their own text output. 🟢.
- Tests that read a file as *fixture input* and then exercise real code with it. 🟢.

---

## 7. Over-broad exception assertions — 🟡

```python
with pytest.raises(Exception):     # a typo inside the block satisfies this
    parse(bad_input)
```
```javascript
expect(() => parse(bad)).toThrow()   // any error, including TypeError from a bad call
```

A `NameError`, `TypeError`, or import failure inside the block satisfies the assertion —
so the test passes while the code under test never ran. Worst on **security tests**, where
"rejected for some reason" and "rejected for the right reason" are different claims.

**Tighten to:** `pytest.raises(ValueError, match="...")`, `toThrow(ValidationError)`.
Missing `match=` on a narrow type is a minor version of the same thing.

---

## 8. Weak assertions on a rich value — 🟡

```python
assert result is not None
assert len(items) > 0
assert "id" in payload           # key exists; value could be anything
```
```javascript
expect(result).toBeTruthy()
expect(html).not.toMatch(/font-size:\s*[0-9.]+px/)   // also passes on ""
```

Fine as a precondition guard before real assertions. A problem when it's the *only*
assertion on a large structured result — most breakages still return something non-null.

**Negative-only assertions** are the sharp case: a test whose every assertion is
`not.toContain` / `not.toMatch` / `toBeNull` passes when the function returns nothing at
all. Require at least one positive anchor.

**Related, as a bullet:** **unreviewed snapshots.** Snapshot tests are legitimate until
nobody reads the snapshot. Signals: snapshot files not committed; `--ci` absent from the CI
command so new snapshots are written instead of failing; snapshots rubber-stamped with `-u`
in the same commit as every source change.

---

## 9. Name doesn't match what it exercises — 🟡

`test_handles_concurrent_writes` doing one sequential write. `test_retries_on_timeout` with
no timeout injected and no retry counted. `test_falls_back_to_path` whose input never
reaches the path branch.

**No grep will do this for you.** Read the name, predict the assertions, compare. It is the
highest-value manual pass in the catalog and it feeds directly into the two-factor severity
call: a test that doesn't exercise what it names means the named behavior may be uncovered
entirely.

Concentrate on names containing: `concurrent`, `race`, `retry`, `timeout`, `rollback`,
`permission`, `auth`, `expire`, `invalid`, `failure`, `error`, `fallback`, `edge`.

---

## 10. Corroborating signals — not findings on their own

- **One clean baseline run, read carefully.** Cheapest high-yield check in the audit, and it
  mutates nothing. Confirms how many tests actually ran vs. skipped, surfaces
  never-awaited-coroutine and unhandled-rejection warnings, and the wall-clock time tells
  you whether an "integration" suite is mocked down to nothing (a 200ms integration suite
  is not integrating anything). Announce it before running it.
- **Coverage vs. assertion density.** High line coverage plus near-zero assertions per test
  means the suite executes code without checking it.
- **Existing mutation-testing config** (`mutmut`, `cosmic-ray`, Stryker, PIT): surviving
  mutants point straight at bullshit tests. Don't install it — recommend it.
- **`git log` on test files.** A test changed in the same commit that "fixed" the code,
  with the expected value edited to match the new output, is an assertion retrofitted to
  whatever the code happened to do.
