# CLAUDE.md — McBrain Schema

This is the schema file for McBrain, the user's personal LLM-maintained knowledge base. Read this at the start of every McBrain session before touching any files in this vault.

## What McBrain is

A personal knowledge base maintained by Claude. Raw sources live in `raw/`. Claude owns and maintains everything in `wiki/`. The user never writes wiki pages — Claude does. The user drops sources, asks questions, and directs the analysis.

## Directory layout

```
raw/          Immutable source documents. Never modify these.
  articles/   Web clips and saved articles
  papers/     Research papers and PDFs
  notes/      Personal notes, journal entries, transcripts
  assets/     Downloaded images and attachments

wiki/         LLM-maintained compiled knowledge
  index.md    Master catalog — update on every ingest
  log.md      Append-only operation log — update on every operation
  overview.md High-level synthesis — update periodically
  [topic].md  Topic/concept/entity pages — you create and maintain these
```

## Page conventions

Every wiki page must have YAML frontmatter:

```yaml
---
type: concept | entity | source | comparison | synthesis
tags: [tag1, tag2]
sources: [raw/articles/filename.md]
confidence: high | medium | low
updated: YYYY-MM-DD
research_date: YYYY-MM-DD
source_dates: YYYY to YYYY
---
```

**Date metadata rules — non-negotiable:**
- `updated`: the date this wiki page was last edited by Claude.
- `research_date`: the date Claude conducted the research behind this page. Must always be set. Tells the user how fresh the underlying research is.
- `source_dates`: the publication date range of sources cited (e.g. `2019 to 2026`). For a single source, use that date. For internal notes or email threads with no publication date, use the document date.

**Why this matters:** Knowledge bases go stale. Technology benchmarks, API terms, pricing, regulatory status, and competitive landscapes can shift within months. Every page must be auditable for currency so the user knows what to trust and what to refresh. During lint passes, flag any page where `research_date` is more than 6 months old and external claims may be stale.

Use `[[wikilinks]]` for every cross-reference. Every named thing (person, project, concept) that appears in more than one page gets its own wiki page. Link aggressively — the graph is the value.

Keep page filenames lowercase with hyphens (e.g. `machine-learning.md`). The filename is the canonical name.

### Page body format

After the YAML frontmatter, every wiki page should follow this structure:

```markdown
# Page Title

**Summary:** One to two sentences describing this page.

**Sources:** List of raw source files this page draws from (with publication dates where known).

**Research date:** YYYY-MM-DD — when Claude researched this page.

**Source dates:** YYYY to YYYY — publication date range of sources cited.

**Last updated:** YYYY-MM-DD

---

Main content goes here. Use clear headings and short paragraphs.

Link to related concepts using [[wikilinks]] throughout the text.

## Related pages

- [[related-concept-1]]
- [[related-concept-2]]
```

## Citation rules

- Every factual claim should reference its source file — use the format `(source: filename.md)` after the claim
- If two sources disagree, note the contradiction explicitly on the relevant page rather than silently picking one
- If a claim has no source, mark it `(source: unverified)` so it can be resolved later

## Operations

### Ingest
When told to ingest a source:
1. Read the source file in full
2. Discuss key takeaways (briefly, unless asked for more)
3. Write or update a source summary page in `wiki/`
4. Create or update entity and concept pages touched by this source
5. Update `wiki/index.md` with the new page(s)
6. Append to `wiki/log.md`: `## [YYYY-MM-DD] ingest | [source title]`

A single source may touch 5-15 wiki pages. That's normal.

### Query
When asked a question against the wiki:
1. Read `wiki/index.md` to find relevant pages
2. Read those pages
3. Synthesize an answer with citations (e.g., `[[wiki/topic]]`)
4. Offer to file the answer as a new wiki page if it's worth keeping

Answers don't have to be prose. Pick the format that fits the question:
- **Markdown page** — the default; file-able back into the wiki as a new synthesis page
- **Comparison table** — for "how does X differ from Y?" questions
- **Marp slide deck** (`.md` with Marp frontmatter) — for presentations or sequential walkthroughs
- **Chart** (matplotlib via `python3`, or a rendered image saved to `raw/assets/`) — for questions about trends, distributions, or quantitative comparisons
- **Canvas / diagram** — for questions about relationships, flows, or architecture

If the output form is reusable knowledge (not just a one-off), offer to file it as a wiki page so the exploration compounds.

### Lint
When asked to lint:
1. Read `wiki/index.md`
2. Sample wiki pages
3. Report:
   - **Contradictions** between pages
   - **Orphan pages** (no inbound links)
   - **Stale claims** that newer sources have superseded
   - **Missing cross-references** — pages that should `[[link]]` each other but don't
   - **Concept gaps** — important concepts mentioned but lacking their own page
   - **Format drift** — pages that don't follow the page body format
   - **Data gaps** — claims that could be verified or enriched with a web search; propose specific searches
   - **Suggested new sources** — topics or questions where the wiki would benefit from more material; name concrete sources (papers, articles, books) worth adding to `raw/`
   - **Stale pages** — any page where `research_date` is more than 6 months before today's date AND the page contains external claims (pricing, API terms, regulatory status, competitive landscape). Flag these explicitly with a suggested refresh action.
4. Propose specific fixes for each finding
5. Append to `wiki/log.md`: `## [YYYY-MM-DD] lint`

## Rules

- Never modify files in `raw/`. Read-only.
- Always update `wiki/index.md` and `wiki/log.md` on every operation.
- Use `[[wikilinks]]` not bare text for every cross-reference.
- Prefer updating existing pages over creating new ones when the concept already has a page.
- If a source contradicts an existing wiki claim, note the contradiction on the relevant page — don't silently overwrite.
- Keep page filenames lowercase with hyphens — the filename is the canonical name.
- Write in clear, plain language. Short paragraphs, clear headings.
- When uncertain about how to categorize something, ask the user.

## Source ingestion paths

Sources can arrive in `raw/` through several paths. All feed the same ingest procedure once the file is on disk:

- **Obsidian Web Clipper** (browser extension) — clips web articles directly into `raw/articles/` as markdown. Fast one-click capture from any tab the user is already on.
- **Claude in Chrome via Cowork** — when the user asks Claude to ingest a URL, Claude can navigate the page (including authenticated/paywalled ones, since it shares the user's browser session), convert to markdown, and save to `raw/articles/<slug>.md`.
- **Hand drops** — the user drags PDFs into `raw/papers/`, pastes notes into `raw/notes/`, or otherwise adds files manually.

Treat all of these identically. Run the ingest procedure regardless of how the source got there.

## Handling images in sources

Articles clipped from the web often contain inline image references (Obsidian Web Clipper downloads them to `raw/assets/`). LLMs can't read markdown and its inline images in a single pass. The workflow:

1. Read the source markdown text first.
2. Note which images look substantive (diagrams, screenshots with data, photos central to the content) vs. decorative (hero images, stock photos).
3. View the substantive images separately, one or a few at a time, to extract what they convey.
4. Integrate image content into the relevant wiki pages. Link to the image file in `raw/assets/` if the image itself is worth referencing; otherwise just absorb the information into prose.

Skip decorative images — they waste context.

## Version control

The vault is a git repository. After any significant operation (ingest, lint pass, batch of edits), suggest a commit with a descriptive message. If the user agrees, run:

```
cd <VAULT_PATH> && git add -A && git commit -m "<message>"
```

Good commit messages mirror the log entry: `ingest: <source title>`, `lint: <summary>`, `synth: <topic>`. Git is the escape hatch — if an edit goes sideways, `git diff` and `git restore` are the user's friends.

## Log format

Each log entry:
```
## [YYYY-MM-DD] operation | title
One-line description of what was done.
Files touched: wiki/page1.md, wiki/page2.md
```

## Domain

[User fills this in — what is McBrain about? What's the primary focus area?]

## Notes from past sessions

