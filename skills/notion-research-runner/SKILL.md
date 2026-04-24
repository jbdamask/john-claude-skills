---
name: notion-research-runner
description: Pull up to 5 "To do" tasks from a Notion research tracker database, flip them to "In progress", spawn a planning-then-executing research subagent for each, and write the findings plus sources back onto each task's Notion page. Use when the user says things like "run my research queue", "process the Notion research backlog", "kick off the research tasks", "work through the To do items in my Notion tracker", or otherwise asks to execute queued research tasks from Notion.
---

# Notion Research Runner

Drain the "To do" queue of a Notion research tracker (the kind produced by the `notion-research-db` skill) by researching each task with a subagent and writing findings back to the task's page.

## Prerequisite: a Notion MCP connection

This skill needs **some** Notion MCP connector to be available — it does not matter which one (Anthropic's claude.ai Notion connector, Notion's official `@notionhq/notion-mcp-server`, a community server, etc.). Tool names differ per connector, so match by capability rather than exact name.

Required capabilities (with the kinds of tool names to look for):

| Capability | Typical name fragments |
|---|---|
| Search Notion for pages/databases | `*search*`, `API-post-search` |
| Fetch a database and its rows (query database) | `*fetch*`, `*query-database*`, `API-post-database-query` |
| Read a page's properties and body blocks | `*fetch*page*`, `*retrieve*page*`, `API-get-page`, `API-get-block-children` |
| Update a page's properties | `*update-page*`, `API-patch-page` |
| Append block children to a page body | `*append*block*`, `*update-page*` (some connectors overload this), `API-patch-block-children` |

At startup, enumerate available tools and pick the best match for each capability. If no Notion-like tools exist, stop and tell the user: "I need a Notion MCP connector to be connected. Please enable one (the claude.ai Notion connector, Notion's official MCP server, or equivalent) and re-run." If a tool call fails with a schema error, read the tool's actual schema and adapt — some connectors expect raw Notion API JSON, others simplified parameters.

Also required:
- `Agent` tool with `subagent_type: "general-purpose"` for spawning research workers.
- `WebSearch` / `WebFetch` are used *by the subagents*, not by this skill directly.

## Inputs to Collect

1. **Which database.** If the user did not name one, use the identified search tool to find databases titled `— Research Tracker` and confirm. Do not guess.
2. **Batch size.** Default 5. If the user asked for a different cap, honor it. Never exceed 5 in one run without explicit confirmation — parallel research burns tokens fast.

## Workflow

Execute these phases in order. Do not skip steps.

### Phase 1 — Fetch candidates

1. Use the identified fetch/query-database tool on the chosen database to get its rows.
2. Filter client-side to rows where `Status` is `To do` (or `Not started` if the DB uses the default Notion status group and the "To do" bucket contains that option — inspect the schema once).
3. Sort by `Priority` (High → Medium → Low), then by `Created date` ascending (older first).
4. Take at most the batch-size (default 5).
5. If zero rows match, tell the user the queue is empty and stop.

### Phase 2 — Claim the tasks

For each selected row, **immediately** use the identified update-page tool to set `Status` to `In progress`. Do this *before* starting research so a second run of this skill won't re-pick the same rows.

Report to the user: the N tasks claimed, with titles and priorities.

### Phase 3 — Plan + research (parallel subagents)

Spawn one `general-purpose` subagent per claimed task, **in a single message with multiple `Agent` tool calls** so they run in parallel.

Use the prompt template at `references/research_subagent_prompt.md`. Fill in `RESEARCH_TOPIC` (the database's topic name, not the full DB title), `TASK_NAME`, `PRIORITY`, and `NOTES_OR_"(none)"` (existing content of the `Notes` property, if any).

The template instructs each subagent to:
1. First plan its approach (restate question, enumerate sub-questions, pick source types).
2. Then execute with web search/fetch and synthesize.
3. Return a fixed-format Markdown document with Summary, Key Findings, Open Questions, and a numbered Sources list.

Do not paraphrase the template — load it from the reference file and substitute fields.

### Phase 4 — Write findings back

**This is the critical step. The full research output must land on the Notion page in its entirety — every section, every bullet, every source. Do not summarize, truncate, paraphrase, or drop anything.**

For each completed subagent:

1. **Write the complete Markdown output to the page body** via the connector's append-block-children tool (or update-page if that's how this connector exposes body edits). That means **all four sections verbatim**: `## Summary`, `## Key Findings`, `## Open Questions`, and `## Sources` — with every bullet and every numbered source preserved. If the tool requires Notion blocks instead of raw Markdown, convert faithfully: headings → heading_2, bullets → bulleted_list_item, numbered sources → numbered_list_item, links → rich_text with `href`. Do not collapse the Sources list into a single paragraph. Do not drop Open Questions even if empty — render it as "None." so the reader sees nothing was missed.

2. **Append, do not overwrite.** If the page already has body content, insert a horizontal divider and a dated heading (`## Research run — YYYY-MM-DD`) *before* the new content. Look up today's date before writing — do not guess it.

3. **Separately, mirror the Summary paragraph into the `Notes` property** (first section only, truncated to fit Notion's rich-text limits) so the database view is scannable. This is *in addition to* the full content on the page body, never a replacement for it. If the Notes property update fails, still ensure the page body write succeeded — the page body is the source of truth.

**Sanity check before moving on:** after writing, the page body for each task must contain at minimum the four section headings and at least one source link. If it doesn't, the write failed silently — retry or surface the error per the failure-modes section below.

Do **not** flip status to `Done` automatically. Leave it at `In progress` so the user can review and close it out. Tell the user this explicitly in the final report.

### Phase 5 — Report

Return a compact summary to the user: each task title, a one-line takeaway, and the page URL. If any subagent failed or any write-back failed, flag the specific task and leave its status at `In progress` so it can be retried.

## Failure Modes to Handle

- **Notion write fails for a task after research succeeded.** Do not lose the research output — paste the Markdown into the chat so the user can recover it, and tell them which page failed.
- **Subagent returns malformed output** (missing Sources, wrong headings). Ask it once to reformat; if it fails again, write what you got with a `> NOTE: output did not match expected format` callout at the top of the page.
- **Database has no `Status` property or uses different option names.** Inspect the schema via the fetch/query-database tool, map the user's intent ("To do" → whatever the first status-group option is called), and confirm with the user before flipping anything.
- **Rate limits / tool errors on Notion.** Retry once with a short backoff; if it still fails, stop and report rather than leaving the queue in a half-claimed state.

## Non-Goals

- Do not create new database rows.
- Do not change `Priority` or any property other than `Status` and `Notes`.
- Do not mark tasks `Done`.
- Do not research more than the batch cap in a single run.
