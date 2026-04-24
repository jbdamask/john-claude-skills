---
name: notion-research-db
description: Create a Notion database for tracking tasks related to a specific research topic. Use when the user wants to set up a Notion research tracker, create a Notion database for a project or topic, spin up a task database in Notion, or says things like "make me a Notion DB for researching X", "create a research tracker in Notion", or "new Notion database for my X project".
---

# Notion Research DB

Create a new Notion database scoped to a user-supplied research topic. The database has a fixed schema suited to tracking research tasks: Task name, Status, Priority, Created date, Last updated date, Notes.

## When to Use

- User wants a Notion database for a new research topic or project
- User asks to create a task tracker in Notion
- User mentions spinning up a research workspace in Notion

## Prerequisite: a Notion MCP connection

This skill needs **some** Notion MCP connector to be available — it does not matter which one (Anthropic's claude.ai Notion connector, Notion's official `@notionhq/notion-mcp-server`, a community server, etc.). The tool naming differs per connector.

At the start of the skill, scan the available tools for ones that look like Notion operations. Match by capability, not by exact name. The capabilities needed are:

- **Search Notion** — find pages/databases by query. Typical names: `*notion*search*`, `*search-pages*`, `API-post-search`.
- **Create a database** — typical names: `*create-database*`, `API-post-database`.

If no Notion-like tools are present, stop and tell the user: "I need a Notion MCP connector to be connected. Please enable one (the claude.ai Notion connector, Notion's official MCP server, or equivalent) and re-run."

Once matching tools are identified, use them throughout the workflow. If a tool call fails with a schema error, read the tool's actual schema and adapt the payload — different connectors wrap the Notion API differently (some take raw Notion API JSON, some take simplified parameters).

## Inputs to Collect

Before calling the tool, make sure you have:

1. **Research topic** — used to name the database (e.g. "CRISPR base editing", "AI evals literature"). If the user did not already provide one in the prompt, ask.
2. **Parent location** — where in Notion the database should live. Ask the user which page should be the parent, or offer to search. Use the identified Notion search tool with the topic or a user-supplied hint to find candidate parent pages, then confirm the choice before creating.

Do not guess the parent page. If search returns nothing useful, ask the user to paste a Notion page URL or page ID.

## Database Schema

Create the database with exactly these properties:

| Property          | Type                | Notes                                       |
|-------------------|---------------------|---------------------------------------------|
| Task name         | `title`             | Required title property                     |
| Status            | `status`            | Default Notion status groups (To-do/In progress/Done) |
| Priority          | `select`            | Options: `High` (red), `Medium` (yellow), `Low` (blue) |
| Created date      | `created_time`      | Auto-populated by Notion                    |
| Last updated date | `last_edited_time`  | Auto-populated by Notion                    |
| Notes             | `rich_text`         | Free-form notes                             |

Name the database `<Research Topic> — Research Tracker` unless the user specifies a different title.

## Workflow

1. Confirm the research topic and parent page with the user (search Notion if needed).
2. Call the connector's create-database tool with the parent page ID, the title, and the properties above.
3. Report back with the new database URL so the user can open it. Do not add sample rows unless the user asks.

## Notes on Property Types

- `title` must be present exactly once — it is `Task name` here.
- `created_time` and `last_edited_time` are Notion system properties; they take no options.
- If the connector's schema rejects `status`, fall back to a `select` property named `Status` with options `To do`, `In progress`, `Done` and tell the user you used select instead.
