---
name: mcbrain
description: Operating skill for McBrain — the user's personal LLM-maintained knowledge base. Use this skill any time the user wants to ingest a source into McBrain, query McBrain, lint McBrain, file a synthesis page, or otherwise work with their personal knowledge base. Triggers on phrases like "ingest this", "ingest into mcbrain", "save to mcbrain", "add to mcbrain", "query mcbrain", "lint mcbrain", "what does mcbrain say about X", "ask my brain", "file this in mcbrain", "find insights from McBrain [name]", or any reference to the user's wiki, second brain, or knowledge base. Use it even if the user just says "my brain" or "the wiki" without naming McBrain — it's the only knowledge base they maintain.
---

# McBrain — Operating Skill

The user maintains one or more personal knowledge bases called **McBrain**. Each vault has its own MCP filesystem server. This skill governs day-to-day operations against any vault.

## Step 1: Identify which vault the user wants

The user may have multiple McBrain vaults (e.g., "McBrain AI Science", "McBrain Finance", "McBrain Clinical Guidelines"). Each vault has a corresponding MCP server whose name follows the pattern `mcbrain-<topic>` (e.g., `mcbrain-ai-science`, `mcbrain-finance`). A single default vault may just be named `mcbrain`.

From the user's request, determine which vault they mean:
- If they name a vault explicitly ("McBrain Finance", "my finance brain"), map it to the MCP name by lowercasing and hyphenating: `mcbrain-finance`.
- If they say "McBrain" with no qualifier and only one vault exists, use `mcbrain`.
- If ambiguous and multiple vaults are connected, ask: *"Which McBrain vault — [list the connected mcbrain-* MCPs]?"*

Use that MCP for all subsequent operations in this session.

## Step 2: Read CLAUDE.md

Before doing anything else, read the vault's schema file via the identified MCP:

```
CLAUDE.md
```

Read this from the vault root — do **not** hardcode an absolute path. The MCP root is the vault.

CLAUDE.md is the source of truth for:
- The vault's directory layout
- Page conventions (YAML frontmatter, `[[wikilinks]]`)
- The backup strategy configured during setup (GitHub, Google Drive, or none)
- The canonical procedures for **ingest**, **query**, and **lint** operations

Follow what CLAUDE.md says — this skill is the trigger and the router, but CLAUDE.md is the spec.

If `CLAUDE.md` is missing or unreadable, stop and tell the user — something is wrong with the MCP setup.

## Why this two-layer design

McBrain is a living document. Its conventions evolve as the user refines them, and CLAUDE.md is checked into the vault so those conventions travel with the knowledge base. Hardcoding the schema into this skill would mean two places to keep in sync. Instead: this skill catches the user's intent, routes to the right vault, and defers to CLAUDE.md for the spec.

## NON-NEGOTIABLE: raw source files must exist before wiki pages are written

**No wiki page may be created or updated based on web search results, synthesized summaries, or any content that has not first been saved as a file in `raw/`.** This is an immutable rule, not a preference.

The failure mode to avoid: Claude runs a web search, synthesizes findings, and writes wiki pages directly from the search output. This produces wiki pages with no backing source files — the claims are unverifiable, the frontmatter `sources:` field is a lie, and future sessions cannot re-read the original material.

**The correct sequence for any web-sourced content:**

1. Identify the URLs to fetch
2. Use `mcp__workspace__web_fetch` or Claude in Chrome to retrieve each article/page
3. Save the raw content as markdown to `raw/articles/<slug>.md` via the vault MCP
4. Only then run the ingest procedure from CLAUDE.md against those files

If a URL cannot be fetched (paywalled, blocked, returns an error), note it explicitly rather than synthesizing from the search snippet. Search snippets are not sources.

There is no exception to this rule. If the user says "just write the wiki page from the search results," explain the rule and offer to fetch the sources properly.

---

## Source ingestion paths

Sources can arrive in the vault through several routes. All feed the same ingest procedure in CLAUDE.md once the file is on disk:

- **Obsidian Web Clipper** — the user can one-click a web article into `raw/articles/` from their browser. When the user says "ingest the article I just clipped," check `raw/articles/` for the newest file.
- **Claude in Chrome via Cowork** — when the user asks to ingest a URL, navigate the page with the Claude in Chrome extension, convert to markdown, and save to `raw/articles/<slug>.md`. This works for paywalled or authenticated pages since it uses the user's real browser session.
- **Hand drops** — pasted text goes to `raw/notes/`, manual article markdown to `raw/articles/`. PDFs go to `raw/papers/` and require special handling — see below.

After the source is in `raw/`, run the ingest procedure from CLAUDE.md.

## Handling PDFs

When a `.pdf` exists in `raw/papers/` without a companion `.md`, the full workflow:

1. Ask the user to upload the PDF into the chat.
2. Invoke **Cowork's built-in `pdf` skill** — it handles the entire extraction: text, page rendering, and visual inspection.
3. Write the extracted text to `raw/papers/<name>.md` via the vault MCP.
4. Render pages containing substantive figures and write detailed prose descriptions under `## Figure N — [Title]` headings.
5. Proceed with the normal ingest procedure from CLAUDE.md.

**Do NOT save rendered PNGs to `raw/assets/`.** Prose descriptions are queryable; stored image files are not.

## Handling images in web-clipped articles

Read the text first, identify which images look substantive (diagrams, data screenshots) versus decorative (hero images, stock photos), then view only the substantive ones separately. Don't burn context on decorative images.

## Backup and version control

After reading CLAUDE.md, check the `## Backup` section for the `Strategy:` value. The strategy determines whether to do any git operations at all.

**Strategy: `git`**

The vault is a git repository. After meaningful operations (ingest, lint, batch synth), offer to commit and push:

```
cd <vault_path> && git add -A && git commit -m "<message>" && git push origin main
```

Mirror the log entry in the commit message: `ingest: <title>`, `lint: <summary>`, `synth: <topic>`. The CLAUDE.md `## Backup` section has the exact remote URL and push command.

**Strategy: `google-drive`**

No git operations. Drive for Desktop syncs the vault automatically — nothing extra is needed after writing files. Do not offer to commit.

**Strategy: `none`**

No git operations, no backup steps. Just write files. Do not offer to commit or mention backup.

## Always update index and log

Every operation (ingest, lint, filing a synthesis page) must update `wiki/index.md` and append to `wiki/log.md`. Don't skip this — the index is how future sessions discover what's in the vault, and the log is how the user audits what Claude did.

## Tone

The user values directness. Discuss the source briefly — key takeaways, tensions, things worth a dedicated page — before writing wiki pages, but don't pad it. After writing, list which pages were created or updated so the user can spot-check.
