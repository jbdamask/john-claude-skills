---
name: handoff
description: Write a session handoff document to .handoff/<YYYY-MM-DD-HHMM>-HANDOFF.md capturing operational state — what moved, what is half-done, which loops are still open, and the traps that wasted time — with frontmatter metadata (model, repo, branch, HEAD sha, issue tracker, issues, beads) for the agent that picks the work up. Use when the user says "write a handoff", "/handoff", "I'm wrapping up", "hand this off", "save state for next session", "end of session notes", or is about to stop work, switch machines, or hand a branch to someone else. Also offer one proactively after a significant milestone or when context is about to compact. Companion to the session-recap skill, which reads these.
---

# Session Handoff

Write the document the *next* session needs — human or agent, possibly on another machine, with none of your context.

A handoff is not a summary of the conversation and not a changelog. Git already has the changelog. The handoff carries what git cannot: which work is half-finished and where the seam is, what you tried that did not work, what was decided and why, and what might have moved after you stopped.

**Recommend, but don't decide.** Whoever directs the next session — a human, an orchestrator agent — may be pointing it somewhere you know nothing about. You spent this session on Stripe payments; they may have already decided the next one is security hardening. So say what you'd do next and why, especially when scoped work went unfinished — that judgment is worth having. Just make sure it reads as *this session's recommendation*, held next to a neutral inventory of everything you left open, so it can be weighed and overruled. A recommendation stated as a directive gets obeyed, because the handoff is the most-trusted document in the next session's context.

## Output

`<repo root>/.handoff/<YYYY-MM-DD-HHMM>-HANDOFF.md` — local time, e.g. `.handoff/2026-08-19-1430-HANDOFF.md`.

One file per handoff. Never overwrite or edit an earlier one; the folder is an append-only chain, and each handoff names its predecessor. Handoffs are **committed to the repo**, so they travel with the branch — which means **never put secrets, tokens, or credentials in one**. Reference where a value lives (`the SA key is in 1Password / SSM at /foo/bar`), never the value.

## 1. Gather the facts

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/handoff/scripts/gather.sh"
```

Read-only. It returns the timestamp slug, the previous handoff and its `HEAD_SHA`, branch/remote/upstream state, the working tree, the commits since the last handoff, beads or other tracker state, open PRs, and whether `.handoff/` is properly tracked.

Everything else comes from the session you just lived through. The script supplies facts; you supply judgment about what those facts mean.

## 2. Frontmatter

```yaml
---
DATE: 2026-08-19T14:30:00-0400
TITLE: Wire the pack registry to the shop page
STATUS: in_progress          # in_progress | blocked | milestone_complete | abandoned
MODEL: claude-opus-5         # the API model id, not a harness label
MODEL_EFFORT: high           # low | medium | high | xhigh | max
HARNESS: claude-code 2.1.235
SESSION_ID: d14bf04b-e7f1-4a20-b851-e0f5abb0c04e
REPO: jbdamask/john-claude-skills
BRANCH: feat/pack-registry
HEAD_SHA: 1578eff
UPSTREAM: origin/feat/pack-registry (ahead 2)
WORKTREE: dirty              # clean | dirty — see "Uncommitted work" below if dirty
ISSUE_TRACKER: GitHub        # GitHub | Linear | Jira | Beads | none
ISSUES: ["#9", "#28"]
TASK_TRACKER: Beads          # omit if the project has none
BEADS: ["rockysurf-arym (epic, 11/13)", "rockysurf-4aed (ready, unclaimed)"]
PRS: ["#28 open, CI pending"]
OPEN_LOOPS: ["PR #28 open, CI unverified", "migrate.py handles users, not orgs", "webhook retry deliberately deferred"]
RECOMMENDED_NEXT: Finish migrate.py org handling — it is the only in-scope item left unfinished.  # this session's view, not a decision
SCOPE_COMPLETE: false        # was everything this session set out to do actually finished?
PREDECESSOR: .handoff/2026-08-18-0912-HANDOFF.md
PRIME: ["bd ready", "npm run dev"]   # commands the next session should run first
---
```

Rules for the fields:

- **MODEL / MODEL_EFFORT** — take these from the harness, not from self-report. Most coding agents record the model and reasoning effort in a local session transcript or in the environment, and that record is authoritative in a way your own introspection isn't: it carries the exact model id rather than a display name, and effort is usually not visible to you at all. `gather.sh` resolves them where it can. Precedence: harness transcript or environment → your own session context → `unknown`. Never guess a model id.
  - **MODEL** must be the id an API would accept (`claude-opus-5`), not a harness label. Claude Code shows the running model as `claude-opus-5[1m]`, where `[1m]` marks the 1M-context session variant — that suffix is client-side notation and is not a valid model id. The transcript's `message.model` has the clean value; use it.
  - **Concretely, for Claude Code**: `$CLAUDE_CODE_SESSION_ID` names the transcript at `~/.claude/projects/<cwd with / replaced by ->/<session-id>.jsonl`; each assistant record carries `message.model`, a top-level `effort`, and `version`. `$CLAUDE_EFFORT` holds the effort directly. Use the session id rather than the newest file — a project directory often holds several concurrent session logs.
  - **On another harness**: look for an equivalent local transcript or env var before falling back. If neither exists, `unknown` is the honest answer and is better than a plausible guess a later reader would trust.
- **HARNESS / SESSION_ID** — which agent tool ran the session, and its transcript identity. `SESSION_ID` is what lets a later session go read the raw log when this handoff leaves a gap. Omit both if the harness doesn't expose them.
- **HEAD_SHA** — the single most important field. session-recap uses it to run `git log <HEAD_SHA>..HEAD` and detect anything that landed *after* this handoff was written.
- **OPEN_LOOPS** — one line per thread this session left unclosed, in the order you happen to think of them. A neutral inventory, not a ranking. Empty only if you genuinely finished everything.
- **RECOMMENDED_NEXT** — one sentence: what you'd pick up first, if it were your call. It isn't your call, and the wording should not pretend otherwise. Omit it if you have no real basis for one — a fabricated recommendation is worse than none.
- **SCOPE_COMPLETE** — `false` if work the session set out to do went unfinished. This is the flag that tells an orchestrator your recommendation deserves weight: unfinished in-scope work is exactly the case where the session that did it knows best.
- **STATUS: blocked** — the body must say what the block is and who or what unblocks it.
- **PRIME** — how to boot the environment, not what to work on.
- Omit fields that don't apply (`TASK_TRACKER` in a project without one). Never write `N/A` filler.

## 3. Body

Lead with what could bite, not with what you accomplished. Use these headings so session-recap can find things; drop any section that is genuinely empty.

### `## Start here`
Two or three lines: the one-sentence state of the work, and the literal first commands to run. Point at the predecessor handoff and any plan or devlog that carries the narrative.

### `## May have moved since I stopped`
State you left in flight and could not confirm: a CI run still going, a PR awaiting checks, a deploy mid-flight, a background job, a rate limit that resets at a known time, a service someone else was restarting. Say what to check and what the expected outcome was. **This section is why the handoff exists** — put it first and be specific enough to verify.

### `## What this session did`
Headlines only, each with a pointer to the evidence — commit sha, PR number, bead id, file path. Do not restate the diff. Include the *why* where a reader could otherwise undo it: "split-horizon registry, because the owner ruled official packs ship in the tarball."

### `## Commits`
The list from the gather script, since the predecessor handoff. Bounded — if it runs past ~25, summarize the bulk and list only the ones that carry a decision or a risk. Note any commit that is *not* pushed.

### `## Uncommitted work`
Only if the tree is dirty. For each meaningful change: the file, what it does, and whether it is finished, half-finished, or a scratch experiment to delete. A next session cannot tell a deliberate WIP from abandoned debris — say which. Note stashes too.

### `## Open threads`
Every loop this session left open — the neutral inventory, unranked. Your recommendation goes in the next section; keep this one clean so it can be read independently.

For each: what it is, what state it's in (ready to pick up / blocked / needs a human decision), where the full context lives (bead, issue, ADR, file path), and what "done" would look like. Where a real dependency exists, state it as a constraint — "the schema migration has to land before the backfill" is a fact about the work, not a preference about priority. Mark which items were **in scope for this session** and went unfinished, versus which are new discoveries or deferred extras; an orchestrator weighs those differently.

If you left a piece of work mid-edit, say where the seam is: what's implemented, what isn't, and the approach in flight.

### `## Recommended next — this session's view`
What you'd do first if it were your call, and **why**. The reasoning matters more than the pick: an orchestrator redirecting to unrelated work still needs to know that the migration is half-applied, or that leaving the webhook un-retried has a deadline attached.

Keep the frame honest. You saw one session; the person reading this may be steering a program you know nothing about. Write "I'd finish the org branch of migrate.py first — it's the only in-scope item left, and the half-applied state is a hazard if anyone runs the migration meanwhile," not "next, finish migrate.py."

Flag consequences of *not* doing it, where real. That's the part an orchestrator genuinely cannot reconstruct, and it's what makes a recommendation worth overriding deliberately rather than by accident.

### `## Stated direction`
Only what the **user** actually said about what comes next, attributed and close to their words: "the user said the retry logic can wait until after the launch." This outranks your recommendation — if the two conflict, say so explicitly. Never put your own inference here, and omit the section entirely if they said nothing.

### `## Decisions and rules`
Choices made this session that constrain future work, each with its reason. Also any rule you learned the hard way — the thing that must not be done again. These are the entries most likely to be silently violated by a session that skips the handoff.

### `## Traps`
Things that cost time and will cost it again: a flaky test and its real cause, a command that resolves the wrong database, a tool whose flag is a lie, an error message that means something other than it says. Be blunt.

### `## Waiting on a human`
Decisions, approvals, credentials, or console clicks only the user can do. Name each one and what is blocked behind it.

### `## Housekeeping`
Scratch checkouts, temp files, env changes, running processes, anything left in a nonstandard state — and whether it's safe to clean up.

## 4. Finish

- Create `.handoff/` if it doesn't exist. If it's gitignored, tell the user — these are meant to be committed.
- `git add` the new handoff. Don't commit it unless the user asks; they usually want it in the same commit as their work.
- Tell the user the path, the open loops you recorded, and your recommendation, so they can correct any of it while they still remember.

## Quality bar

Before writing, check the draft against these. Every one of them is a real failure mode:

- Would this be useful to someone who was not in the session? Cut anything only you can decode.
- Does it say what is *unfinished*, not just what is done? A handoff of only accomplishments is a status report and is nearly useless.
- Is every open loop listed, including the embarrassing ones you'd rather not flag?
- Is the inventory of open threads separable from your recommendation, so someone can read the state without inheriting your read on it?
- Does the recommendation carry its reasoning and its consequences-of-skipping, so it can be overruled on the merits? And is it phrased as a view, not an instruction?
- Does every claim have a pointer — sha, PR, bead, file:line? Unsourced assertions get treated as facts and propagate.
- Did you record the failures? What you tried that did not work is worth more than what worked, because the next session will otherwise try it again.
- Is it honest? If something is broken, half-built, or was done badly under time pressure, say so plainly. A handoff that oversells state actively misleads the agent that trusts it.
