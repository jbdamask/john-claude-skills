---
name: architecture-decision-records
description: Write and maintain Architecture Decision Records (ADRs) that capture the context and rationale behind significant technical decisions. Use when documenting an architectural or technology choice, recording a design trade-off, superseding a past decision, or setting up an ADR process. Also use proactively to offer an ADR when a significant decision is made during a coding session (database, framework, auth scheme, API style, integration pattern). Triggers on "write an ADR", "document this decision", "record this architecture choice", "add a decision record", "supersede ADR".
---

# Architecture Decision Records

Create, maintain, and supersede Architecture Decision Records (ADRs): short documents that capture *why* a significant technical decision was made, what was decided, and what follows from it. This skill is written for an agent working inside the codebase — you do the mechanics (numbering, file creation, index updates, cross-linking) yourself.

An ADR is not a design doc and not a changelog. It captures three things: the **context** that forced a decision, the **decision** itself, and the **consequences** that follow. Future readers — including future you — read ADRs to understand why the system is the way it is.

## The one rule that matters most

**Never fabricate the decision-making.** The most damaging failure mode for an agent writing an ADR is inventing a tidy "Considered Options" section with plausible pros and cons that were never actually weighed. That produces a document that looks authoritative and is fiction.

Every alternative, driver, and trade-off in an ADR must come from a real source:
- A discussion that actually happened in this session or a linked thread
- Evidence in the codebase (existing dependencies, benchmarks, prior ADRs)
- The user, when you ask them

If you don't know why an alternative was rejected, say so explicitly ("Not evaluated in depth") or ask the user — do not manufacture a rationale. An honest ADR with two real options beats a polished one with five imaginary ones. When you're inferring rather than reporting, mark it: "Inferred from current code" / "Assumed — confirm with team".

## Workflow

### 1. Decide whether an ADR is warranted

| Write an ADR | Skip it |
| --- | --- |
| New framework / language / major library adoption | Minor version upgrades |
| Database or storage technology choice | Bug fixes |
| API style (REST/GraphQL/gRPC), auth scheme | Implementation details the code already documents |
| Security or data-boundary architecture | Routine config changes |
| Integration / messaging patterns | Formatting, renames, refactors with no behavior change |
| Reversing or superseding a prior decision | Anything you'd never need to explain to a new engineer |

Rule of thumb: write an ADR when the decision is **costly to reverse** and a future reader would otherwise ask "why on earth did we do it this way?"

### 2. Offer before you write (proactive mode)

When you detect that a qualifying decision was just made during a session — you picked PostgreSQL, settled on JWT auth, chose an event-driven pattern — **offer, then wait**. Do not silently create files.

Surface a single line, e.g.:
> That's a significant decision. Want me to capture it as an ADR in `docs/adr/`?

Only proceed when the user agrees (or asked for the ADR in the first place). If they decline, drop it.

### 3. Look up today's date

Do not assume the date. Get it before stamping the ADR:

```bash
date +%Y-%m-%d
```

### 4. Locate (or create) the ADR directory

**ADRs always go in the user's project, never in this skill's directory.** Resolve the project root first and treat every ADR path as relative to it:

```bash
# Project root = the repo you're working in (not ~/.claude/skills/... or the plugin dir)
git rev-parse --show-toplevel 2>/dev/null || pwd
```

If the resolved root is inside a skills/plugin directory (e.g. a path containing `/.claude/skills/`, `/skills/`, or a `plugin.json` at the root), stop and ask the user which project the ADR belongs to — do not write the ADR into the skill folder.

Then detect an existing convention before imposing one (paths relative to the project root):

```bash
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ls -d "$ROOT"/docs/adr "$ROOT"/docs/decisions "$ROOT"/adr "$ROOT"/doc/adr "$ROOT"/.adr 2>/dev/null
```

- If a directory exists, **use it** and match its existing filename and format conventions.
- If none exists, default to `$ROOT/docs/adr/`. Create it, add an `llms.txt` index (see "ADR index (llms.txt)" below), and a `template.md`.

The index is a single [llms.txt](https://llmstxt.org/) file: each ADR is one self-contained Markdown file, and `llms.txt` links to all of them, grouped by category. This lets an agent (or human) scan categories + one-line descriptions and fetch only the relevant decision files instead of reading every ADR.

### 5. Compute the next ADR number

ADRs are numbered sequentially, zero-padded to 4 digits, starting at `0001`. Find the highest existing number and increment:

```bash
ls "$ROOT"/docs/adr/[0-9]*.md 2>/dev/null | sed 's#.*/##' | grep -oE '^[0-9]+' | sort -n | tail -1
```

Filename format: `NNNN-short-title-with-dashes.md` (e.g. `0007-use-postgresql.md`).

### 6. Write the ADR

Use the **full MADR format** below by default. Drop to the lightweight format only for a genuinely small decision, or escalate to the RFC format for a proposal that needs broad discussion before acceptance (see "Other formats").

Anchor the ADR to real code. Because you are working in the repo, you can cite the actual artifacts the decision touches — do so:
- File paths with line references (`src/db/pool.ts:42`)
- Commit SHAs and PR numbers that implement the decision
- Existing dependencies or config that constrain it

Assign the ADR a **category** — the architectural area it belongs to (e.g. `Data & Storage`, `API & Integration`, `Auth & Security`, `Infrastructure`, `Frontend`, `Messaging & Events`, `Observability`). Reuse an existing category from `llms.txt` when one fits; only create a new category when none does. The category is how the index stays scannable.

### 7. Update the index and cross-links

After writing the ADR:
- Add an entry to `llms.txt` under the ADR's category section (see "ADR index (llms.txt)" below). Keep entries within a category sorted by ADR number.
- If this ADR **supersedes** an earlier one, edit the old ADR's status to `Superseded by ADR-NNNN`, and update the old entry's description in `llms.txt` to reflect the new status. Don't rewrite the body of the superseded ADR — its original reasoning is the historical record.
- Link any related ADRs in the new ADR's "Related Decisions" section.

### 8. Report

Tell the user the path of the new ADR, its number/status, and any ADR you changed the status of. Don't dump the full file back into chat.

## Full MADR template (default)

```markdown
# ADR-NNNN: <Short decision title>

## Status

Proposed | Accepted | Deprecated | Superseded by ADR-NNNN | Rejected

## Date

YYYY-MM-DD

## Context

What situation forces a decision now? Constraints, requirements, scale, team
skills, deadlines. State the problem, not the solution. Cite real evidence —
existing code, dependencies, measured numbers — over generalities.

## Decision Drivers

- The criteria that actually mattered (e.g. "must be ACID for payments")
- Only list drivers that genuinely influenced the choice

## Considered Options

### Option 1: <name>  ← chosen
- Pros: <real, specific>
- Cons: <real, specific — every option has cons>

### Option 2: <name>
- Pros:
- Cons:

(Only include options that were actually considered. If an obvious option was
not evaluated, say so: "MongoDB — not evaluated; no team experience.")

## Decision

We will use **<option>**. State it in one or two sentences, unambiguously.

## Rationale

Why this option beat the others against the drivers above. Tie back to the
context. This is the heart of the ADR.

## Consequences

### Positive
- What gets easier / safer / cheaper

### Negative
- What gets harder / riskier / more expensive (be honest — there is always a cost)

### Risks & Mitigations
- Risk: <what could go wrong> → Mitigation: <plan>

## Implementation

- Where this lands in the code: `path/to/file.ext:line`
- Commit(s) / PR(s): <sha or #number>
- Follow-up tasks or tickets

## Related Decisions

- ADR-XXXX: <how it relates — complements / depends on / supersedes>

## References

- External docs, benchmarks, internal links
```

## Other formats

Use these only when they fit better than the default.

### Lightweight (small but worth recording)

```markdown
# ADR-NNNN: <Title>

**Status**: Accepted   **Date**: YYYY-MM-DD

## Context
2-4 sentences on why a decision was needed.

## Decision
What we decided, in one or two sentences.

## Consequences
**Good**: ...
**Bad**: ...
**Mitigations**: ...

## Implementation
`path/to/file.ext:line` · commit/PR ref
```

### RFC style (proposal needing discussion before acceptance)

Status starts as `Proposed`. Add sections the team can argue over before it's accepted: **Summary**, **Motivation**, **Detailed Design**, **Drawbacks**, **Alternatives**, **Unresolved Questions** (as a `- [ ]` checklist), **Implementation Plan**. Promote to a normal `Accepted` ADR once resolved.

### Superseding an earlier decision

When a new decision reverses an old one, write a new ADR (don't edit the old one's reasoning):
- New ADR status: `Accepted (Supersedes ADR-XXXX)`
- Include a **Migration Plan** if the change requires moving existing data/code in phases
- Include a **What changed since ADR-XXXX** section: what we now know that we didn't then. This honesty is the most valuable part — it's how the team learns.
- Edit the old ADR's status to `Superseded by ADR-NNNN`.

## ADR index (llms.txt)

Maintain `docs/adr/llms.txt` as the index, in [llms.txt](https://llmstxt.org/) format. It groups ADRs by **category**; each entry is a link to one self-contained ADR file followed by a one-line **description**. The description carries the status and a plain summary so a reader can decide whether to open the file. Update `llms.txt` every time you add or re-status an ADR.

Entry format — one bullet per ADR: `- [NNNN <name>](file): [Status] <one-line description>`

```text
# Architecture Decision Records

> Decision records for <Project>. Each link is a self-contained ADR. Newest
> decisions reflect current intent; superseded ones are kept for history.
> Statuses: Proposed | Accepted | Deprecated | Superseded by ADR-NNNN | Rejected.

## Data & Storage

- [0001 Use PostgreSQL as primary database](0001-use-postgresql.md): [Accepted] ACID + JSONB + full-text in one engine; avoids a separate search service.
- [0003 MongoDB for user profiles](0003-mongodb-user-profiles.md): [Superseded by ADR-0007] Chose MongoDB for schema flexibility; later reversed.
- [0007 Deprecate MongoDB](0007-deprecate-mongodb.md): [Accepted] Migrate user profiles to PostgreSQL; schema stabilized, dual-DB cost too high.

## Auth & Security

- [0004 JWT access tokens with refresh rotation](0004-jwt-auth.md): [Accepted] Stateless auth for the API; refresh tokens rotated server-side.

## API & Integration

- [0005 GraphQL for the mobile-facing API](0005-graphql-api.md): [Proposed] Collapse multi-request dashboard loads into one query.
```

Categories are free-form but should stay consistent — reuse an existing section before inventing a new one. Suggested starters: `Data & Storage`, `API & Integration`, `Auth & Security`, `Infrastructure`, `Frontend`, `Messaging & Events`, `Observability`.

### How to read the index (for an agent)

When you need to know why something is the way it is, **fetch `llms.txt` first**, scan the category sections relevant to the task, and open only the ADR files whose descriptions match. Don't read every ADR.

### Statuses

- **Proposed** — under discussion
- **Accepted** — decided, implementing or implemented
- **Deprecated** — no longer relevant, not replaced
- **Superseded by ADR-NNNN** — replaced by a newer ADR (linked)
- **Rejected** — considered and declined (kept because the reasoning is useful)

## Quality checklist

Before you tell the user the ADR is done, verify:

- [ ] Title states the decision, not the topic ("Use PostgreSQL", not "Database")
- [ ] Context explains the forcing problem, with real evidence — not generic filler
- [ ] Every considered option was *actually* considered; unevaluated ones are marked as such
- [ ] Each option has honest cons; the chosen one's downsides are stated, not hidden
- [ ] Consequences include real negatives and risks, not just upside
- [ ] Decision is unambiguous and specific (versions, names)
- [ ] Linked to the code/commits/PR that implement it
- [ ] Index updated; any superseded ADR re-statused and cross-linked
- [ ] Date was looked up, not assumed
- [ ] No invented rationale anywhere — inferences are labeled as inferences

## Do / Don't

**Do**
- Write the ADR close to when the decision is made, while the reasoning is fresh
- Keep it to 1–2 pages — an ADR is a record, not a textbook
- Be honest about trade-offs and about what you don't know
- Build the decision graph by linking related ADRs

**Don't**
- Rewrite an accepted ADR — supersede it with a new one
- Invent options, drivers, or consequences to look thorough (this is the cardinal sin)
- Skip the context because "it's obvious" — it won't be in a year
- Create ADR files without offering first when acting proactively
- Bury a rejected decision — rejections are valuable history
