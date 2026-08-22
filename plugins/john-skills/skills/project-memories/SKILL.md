---
name: project-memories
description: Maintain durable project memories as files in the repo, using the llms.txt pattern — a docs/memories/ folder with one markdown file per memory plus a docs/memories/llms.txt index. Use when the user says "remember this for the project", "save a project memory", "add to project memories", "update a project memory", "retire a memory", "migrate memories", "set up project memories", or wants project knowledge to travel with the repo instead of living in an ad-hoc mechanism like beads' `bd remember`.
---

# Project Memories

Keep durable project knowledge in files that travel with the repo: one markdown file per memory under `docs/memories/`, indexed by `docs/memories/llms.txt`. This replaces ad-hoc memory mechanisms — `bd remember`, a stray notes file, an agent's own session memory — for anything that should outlive the session and the tool that recorded it.

A memory holds a durable fact or decision: a convention, a gotcha, a reason something is the way it is. It is not a changelog entry and not a TODO. Write it so an agent or teammate who never saw the session can read it and act correctly.

## Memory, ADR, or doc?

Durable knowledge has three homes, and a memory is the narrowest of them. Put content in the wrong home and docs rot while decisions get relitigated.

- **Standard docs** (`docs/ARCHITECTURE.md`, `docs/STYLE_GUIDE.md`, `docs/DEPLOYMENT_STEPS.md`) describe the system **as it is** — what it does and how to work on it, for a general reader. They are living text: when reality changes you rewrite them, and the old version has no value.
- **ADRs** (`docs/adr/`) record a **choice among alternatives** with lasting consequences — "use async queue processing for distributed jobs", "put all objects in S3" — along with the context that forced the choice. They are point-in-time and immutable: a new ADR supersedes an old one, and you never edit one into a new position.
- **Memories** hold what was learned the hard way: how something actually behaves, or why something that looks wrong has to stay. "Keep-both merge resolutions produce syntax damage that diff review misses — run typecheck, not a marker grep." "This unused hook is deliberately dormant, don't remove it." "A red test in a package you didn't touch means rebuild, not bug." A doc would never think to say it, and an ADR has no alternatives to weigh.

The test, in order:

1. Does it describe how the system works today, for anyone reading the code fresh? → **doc**. Update the doc; skip the memory.
2. Does it record a choice among alternatives with architectural consequences? → **ADR**. Offer to write one. A memory can still hold the decision *trail* — the incidents and the arguments — while the ADR holds the decision.
3. Is it a learned fact a future agent needs in order to act correctly, and that would otherwise be lost? → **memory**.

Memories also graduate. Once a memory's content turns normative — a rule everyone must follow, a section a real doc should own — move the rule into that doc or ADR, then retire the memory (or slim it down to the decision trail) with a pointer to its new home. Never let a memory fork a normative document: one of them wins, and the memory has to say which.

## Classify before you write

These files get committed, so anything in one is as exposed as the rest of the repo. If the repo is public, or might ever become public, a memory must contain **no secrets, credentials, account identifiers, IP addresses, hostnames, internal URLs, or other private infrastructure detail.**

Before writing any memory:

1. Ask whether the repo's visibility makes this content safe to commit. If you don't know, ask the user — don't assume public or private.
2. If the memory is sensitive, **don't half-scrub it.** Swapping a credential for `<REDACTED>` and shipping the rest is not good enough. Leave the memory out of the repo and tell the user it belongs somewhere private: local agent memory, `bd remember` kept private, a password manager, private notes.
3. When a memory needs sensitive knowledge to be useful, point at *where the value lives* — "the deploy key is the `rocky-surf-deploy` entry in 1Password" — never the value itself.

When in doubt, leave it out and say why. A missing memory is recoverable; a leaked credential in git history is not.

## Format

### The index: `docs/memories/llms.txt`

One [llms.txt](https://llmstxt.org/) file, one bullet per memory. Group the bullets or keep them flat — most projects stay small enough for a flat list.

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

`YYYY-MM-DD` is the date the memory was established — look it up, don't assume it. `<key>` is a short slug, lowercase and dash-separated, matching the `KEY` field.

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
- `KEY` — the slug; matches the index entry and the filename
- `DATE` — when the memory was first established, which is usually but not always the day the file was written
- `UPDATED` — last revision date; equals `DATE` until the first update
- `STATUS` — `active` or `retired`
- `SOURCE` — where the memory came from, e.g. `"session decision"`, `"bd remember, migrated 2026-08-21"`, `"code review, PR #142"`

Body: prose, not bullet fragments. State the memory plainly, then the reasoning behind it. A paragraph or two — this is a record, not documentation.

## Operations

### Add a memory

1. Look up today's date:
   ```bash
   date +%Y-%m-%d
   ```
2. Resolve the project root, so you never write into a skill or plugin directory:
   ```bash
   git rev-parse --show-toplevel 2>/dev/null || pwd
   ```
   If the root looks like a skills or plugin checkout (it contains `/.claude/skills/` or `/skills/`, or has a `plugin.json` at the top), stop and ask the user which project the memory belongs to.
3. Classify the content for sensitivity. If it fails, stop, say why, and suggest where the memory should live instead.
4. Create `docs/memories/` and its `llms.txt` (header only, no entries) if they don't exist yet.
5. Pick a short, descriptive key and check `llms.txt` for a collision. A key that already exists means this is an update, not a new memory.
6. Write `docs/memories/YYYY-MM-DD-<key>.md` with the frontmatter and body above.
7. Add one bullet to `llms.txt`.
8. Report the file path and key. Don't dump the file into chat.

### Update a memory in place

Use this when the underlying fact is still true but needs correction or more detail. If it is no longer true and the old version is worth keeping, retire it and write a new memory instead.

1. Edit the body of the existing file.
2. Bump `UPDATED` to today. Leave `DATE` alone — it marks when the memory was first established.
3. Revise the one-line summary in `llms.txt` if the substance moved enough to make the old summary misleading.

### Retire a memory

Use this when a memory is no longer true or no longer relevant, but the history is worth keeping — "why we used to do X before switching to Y".

1. Set `STATUS: retired` in the frontmatter and bump `UPDATED`.
2. **Never delete the file.** Retiring instead of deleting is what lets a future reader find out why something used to be true.
3. Change the `llms.txt` entry to `[retired]`, noting what superseded it if that helps.
4. If a new memory replaces this one, say so in the retired file's body and cross-reference the new key.

### Read / consult memories

Read `docs/memories/llms.txt` first — never the whole directory — and open only the files whose one-line summaries bear on the task at hand. Same discipline as an ADR index: scan, then fetch selectively.

## Migrating from `bd remember`

When a project has been using beads' memory feature and wants its durable, shareable knowledge in files:

1. List what's there:
   ```bash
   bd memories
   ```
2. Read each one worth keeping:
   ```bash
   bd recall <key>
   ```
3. Classify each one:
   - **Safe to commit** — conventions, architectural decisions, gotchas with no infrastructure specifics → write it as a `docs/memories/` file with `SOURCE: bd remember, migrated YYYY-MM-DD`.
   - **Sensitive** — credentials, account IDs, internal hosts, anything that exposes infrastructure → leave it in `bd remember`, or move it to whatever private mechanism the project actually uses. No scrubbed versions in the repo: either it's safe as-is or it doesn't go in.
4. Don't delete anything from `bd remember` as part of the migration unless the user asks. Treat it as a copy until they confirm the beads memories are no longer needed.
5. Report a short table: memory key → migrated (file path), or kept in beads (why).

## CLAUDE.md / AGENTS.md integration

Offer to add a pointer so agents find the index on their own, in whatever instructions file the project uses (`CLAUDE.md`, `AGENTS.md`):

```markdown
## Project Memories

Durable project knowledge lives in `docs/memories/llms.txt` (index) and
`docs/memories/*.md` (one file per memory). Read the index first; open
only the files relevant to the current task. To add, update, or retire a
memory, use the project-memories skill.
```

## Quality checklist

Before telling the user a memory is done:

- [ ] Routed correctly — learned, intrinsic knowledge, not something a doc or ADR should own
- [ ] Classified for sensitivity before anything got written
- [ ] Date looked up, not assumed
- [ ] `KEY` matches the filename slug and the `llms.txt` entry
- [ ] Body states the memory plainly, then the reasoning — not a bare fact
- [ ] `SOURCE` reflects where this actually came from
- [ ] `llms.txt` updated: new entry, or summary and status revised

## Do / Don't

**Do**
- Keep each memory self-contained — nobody should need two files to understand one memory
- Reference where a sensitive value lives, never the value itself
- Ask about repo visibility when you're unsure whether public-safe applies
- Retire stale memories instead of deleting them

**Don't**
- Write a memory when the content belongs in a doc or an ADR — route it there
- Half-scrub a sensitive memory and commit it anyway
- Write a memory into a skill or plugin directory instead of the user's project
- Silently overwrite a memory's original `DATE` on update
- Treat `docs/memories/` as a changelog
