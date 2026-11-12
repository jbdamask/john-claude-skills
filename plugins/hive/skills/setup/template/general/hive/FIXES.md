# Bug fixes

The lead files every bug found and gets it fixed without asking {{owner}}. A fix restores what was intended; a fix that changes what the user sees in a way nobody specified is a feature and needs a spec (hive/BUILD.md).

- A fix covers the class, not the reported case: before building, find every stored case the changed code reaches, and show the fix on cases it was not written from.
- A fix to a part that makes a judgment runs old and new code on the same stored cases and lists every case whose result moves; nothing outside the bug's scope may move.
- When a second fix to the same code fails its check, or a fix reopens a case an earlier fix closed, stop patching: revert to the last checked version and ask {{owner}} for a redesign spec.

## The blind check
The fixer files the blind check as its own bead labelled `role:blind-checker`; the fix bead depends on it and closes only after its verdict.
- The check file has two parts: each case's source text first, then the old and new results as A and B with the direction hidden. The checker judges each case from the source before it opens the results, because seeing the results first makes the check not blind.
- The check bead names the exact commit under test; the checker runs and reads everything at that commit, not in the shared checkout.
- The checker reads the whole new output against the sources and files a bead for every error, whether or not A and B differ there. Verdict: `PASS` or `FAIL` as a note on its bead and on the fix bead.
