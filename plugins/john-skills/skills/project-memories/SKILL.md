---
name: project-memories
description: Maintain durable project memories as files in the repo, using the llms.txt pattern — a docs/memories/ folder with one markdown file per memory plus a docs/memories/llms.txt index. Use when the user says "remember this for the project", "save a project memory", "add to project memories", "update a project memory", "retire a memory", "migrate memories", "set up project memories", or wants project knowledge to travel with the repo instead of living in an ad-hoc mechanism like beads' `bd remember`.
---

# Project Memories

Maintain durable project knowledge as files that live and travel with the repo: one markdown file per memory under `docs/memories/`, indexed by `docs/memories/llms.txt`. This replaces ad-hoc memory mechanisms — `bd remember`, a stray notes file, an agent's own session memory — for anything that should outlive the session and the tool that recorded it.

A project memory is not a changelog entry and not a TODO. It captures a durable fact or decision about the project — a convention, a gotcha, a "why we do it this way" — written so a future agent (or teammate) who has never seen this session can read it and act correctly.

## The one rule that matters most

**Classify before you write.** If the repo is public, or might ever become public, a memory file must contain **no secrets, credentials, account identifiers, IP addresses, hostnames, internal URLs, or other private infrastructure detail.** These files are committed to git; anything written into one is as exposed as the rest of the repo.

Before writing any memory:
1. Ask: does this repo's visibility make this content safe to commit? If you don't know, ask the user rather than assume public or private.
2. If the memory contains sensitive material, **do not half-scrub it.** Don't replace a credential with `<REDACTED>` and ship the rest — leave the whole memory out of the repo and tell the user it belongs in a private mechanism instead (local agent memory, `bd remember` kept private, a password manager, private notes).
3. When a memory needs to reference sensitive knowledge to be useful, reference *where the value lives*, never the value itself — e.g. "the deploy key is in the `rocky-surf-deploy` entry in 1Password", not the key.

When in doubt, leave it out and say why. A missing memory is recoverable; a leaked credential in git history is not.

## Format

### The index: `docs/memories/llms.txt`

One [llms.txt](https://llmstxt.org/) file, grouped free-form or flat (grouping is optional — most projects are small enough for a flat list). One bullet per memory:

```text
# Project Memories

> Durable project knowledge for <Project>. Each link is a self-contained
> memory file. Retired memories are kept for history, not deleted.
> Statuses: active | retired.

- [db-migration-strategy](2026-08-21-db-migration-strategy.md): [active] Migrations run forward-only, no down migrations — team decided rollback-by-redeploy is safer than reversible migrations.
- [legacy-auth-flag](2026-06-02-legacy-auth-flag.md): [retired] The LEGACY_AUTH env flag existed during the 2026 auth migration; removed once the migration completed.
```

Entry format: `- [key](filename.md): [status] one-line summary.`

### Per-memory file: `docs/memories/YYYY-MM-DD-<key>.md`

`YYYY-MM-DD` is the date the memory was established (see "Look up today's date" below) and `<key>` is a short slug — lowercase, dash-separated, matching the `KEY` field.

```markdown
---
KEY: db-migration-strategy
DATE: 2026-08-21
UPDATED: 2026-08-21
STATUS: active
SOURCE: session decision
---

We run database migrations forward-only; there are no down migrations.

The team decided this after a rollback attempt corrupted staging data in
[incident/context if known]. Rolling back by redeploying the previous
migrated state is safer than trusting a hand-written down migration that
is rarely tested. New migrations must be additive or reversible-by-forward-fix,
never destructive without a forward-only remediation path.
```

Frontmatter fields:
- `KEY` — the slug, matches the index entry and filename
- `DATE` — when the memory was first established (not when the file was written, if different — but usually the same)
- `UPDATED` — last revision date; equals `DATE` until the first update
- `STATUS` — `active` or `retired`
- `SOURCE` — where the memory came from, e.g. `"session decision"`, `"bd remember, migrated 2026-08-21"`, `"code review, PR #142"`

Body: prose, not bullet fragments. State the memory plainly, then the reasoning behind it. Keep it to a paragraph or two — this is a record, not documentation.

## Operations

### Add a memory

1. Look up today's date — do not assume it:
   ```bash
   date +%Y-%m-%d
   ```
2. Resolve the project root (never write into a skill/plugin directory):
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   ```
   If the resolved root looks like a skills/plugin checkout (contains `/.claude/skills/`, `/skills/`, or a `plugin.json` at the root), stop and ask the user which project the memory belongs to.
3. Run the sensitivity classification above. If it fails, stop and tell the user why, and suggest where the memory should live instead.
4. If `docs/memories/` doesn't exist, create it along with `llms.txt` (header only, no entries yet).
5. Choose a short, descriptive `key`. Check `llms.txt` for a collision; if the key exists, this is an **update**, not a new memory (see below).
6. Write `docs/memories/YYYY-MM-DD-<key>.md` with the frontmatter and body above.
7. Add one bullet to `llms.txt`.
8. Report the file path and key back to the user. Don't dump the full file into chat.

### Update a memory in place

Use this when the underlying fact is still true but needs correction or more detail — not when it has changed and the old version is now historically interesting (that's a retire + new memory).

1. Edit the body of the existing file.
2. Bump `UPDATED` to today's date. Leave `DATE` untouched — it marks when the memory was first established.
3. Update the one-line summary in `llms.txt` if the substance changed enough to make the old summary misleading.

### Retire a memory

Use this when a memory is no longer true or no longer relevant, but the history is worth keeping (e.g. "why we used to do X before switching to Y").

1. Set `STATUS: retired` in the file's frontmatter and bump `UPDATED`.
2. **Never delete the file.** The point of retiring instead of deleting is that future readers can still find out why something used to be true.
3. Update the `llms.txt` entry to `[retired]` and, if useful, note what superseded it in the one-line summary.
4. If a new, related memory replaces this one, mention the replacement in the retired file's body and cross-reference the new memory's key.

### Read / consult memories

Agents should read `docs/memories/llms.txt` first — never all of `docs/memories/` — and open only the files whose one-line summaries are relevant to the task at hand. This is the same discipline as an ADR index: scan, then fetch selectively.

## Migrating from `bd remember`

When a project has been using beads' memory feature and wants to move durable, shareable knowledge into files:

1. List existing memories:
   ```bash
   bd memories
   ```
2. For each one worth keeping, read its full content:
   ```bash
   bd recall <key>
   ```
3. **Classify each memory** per the sensitivity rule above:
   - **Public-safe** (conventions, architectural decisions, gotchas with no infrastructure specifics) → write as a `docs/memories/` file. Set `SOURCE: bd remember, migrated YYYY-MM-DD`.
   - **Sensitive** (credentials, account IDs, internal hosts, anything that would expose infrastructure) → leave it in `bd remember`, or move it to whatever private mechanism the project actually uses. Do not write a scrubbed version into the repo — either it's safe as-is or it doesn't go in.
4. Do not delete anything from `bd remember` as part of migration unless the user asks — treat this as an additive copy until the user confirms the beads memories are no longer needed.
5. Report a short table: memory key → migrated (file path) or kept-in-beads (why).

## CLAUDE.md / AGENTS.md integration

Suggest adding a short pointer so agents discover the index automatically, in whatever instructions file the project uses (`CLAUDE.md`, `AGENTS.md`):

```markdown
## Project Memories

Durable project knowledge lives in `docs/memories/llms.txt` (index) and
`docs/memories/*.md` (one file per memory). Read the index first; open
only the files relevant to the current task. To add, update, or retire a
memory, use the project-memories skill.
```

## Quality checklist

Before telling the user a memory is done, verify:

- [ ] Classified for sensitivity before writing — no secrets, credentials, account IDs, IPs, or private infra detail in the file
- [ ] Date looked up, not assumed
- [ ] `KEY` matches the filename slug and the `llms.txt` entry
- [ ] Body states the memory plainly, then the reasoning — not just a bare fact
- [ ] `SOURCE` reflects where this actually came from
- [ ] `llms.txt` updated (new entry, or summary/status revised)
- [ ] Retired, never deleted, when a memory goes stale

## Do / Don't

**Do**
- Keep each memory file self-contained — a reader shouldn't need to open two files to understand one memory
- Reference where a sensitive value lives, never the value itself
- Ask the user about repo visibility when you're not sure whether public-safe applies
- Retire memories that go stale instead of deleting them

**Don't**
- Half-scrub a sensitive memory and commit it anyway — leave it out entirely
- Write a memory into a skill/plugin directory instead of the user's project
- Silently overwrite a memory's original `DATE` when updating it
- Treat `docs/memories/` as a changelog — it's for durable facts, not a log of events
