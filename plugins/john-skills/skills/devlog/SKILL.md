---
name: devlog
description: Create and maintain a DEVLOG.md file capturing the development story of a project. Use this periodically over the course of a project to capture important information about the development story. Invoke when the user asks to update the devlog, create a devlog, document project progress, or capture development history. Also appropriate after completing significant milestones or before context switches.
---

# DevLog

Create and maintain `DEVLOG.md` in the project root. The devlog tells the story of the project - why it exists, how it evolved, what decisions were made and why, challenges encountered, and pivots taken. A reader should be able to read it end-to-end and understand the project's journey. It should be detailed enough to reconstruct the development narrative, but not an exhaustive transcript.

## Workflow

### 1. Determine Project Context

First, establish the current working directory and derive the chat history path:

```bash
pwd
```

Convert the project path to the chat history directory name by replacing `/` with `-`:
- Example: `/Users/johndamask/src/tries/2026-01-08-myproject`
- Becomes: `~/.claude/projects/-Users-johndamask-src-tries-2026-01-08-myproject`

### 2. Verify Source Access

Before gathering information, verify you can access the key sources. If any are unavailable, ask the user for guidance.

**Check for:**
- Git repository (`.git` directory or `git status`)
- Claude chat history (`~/.claude/projects/<converted-path>/`)
- Planning documents (`.claude/`, project root, or docs folders)
- Issue tracker (check for common indicators below)

If git is not found, ask the user: "I don't see a git repository here. How is source code tracked for this project?" The project may use a different VCS, or this may be a subdirectory of a larger repo.

### 3. Gather Information from Sources

Collect information from all available sources:

#### A. Planning Documents

Search for planning documents in the project:

```bash
find . -name "*.md" -type f | xargs grep -l -i "plan\|implementation\|architecture" 2>/dev/null | head -20
```

Also check for Claude plan mode artifacts (often in `.claude/` or project root). If planning documents exist, summarize key decisions and link to them in the devlog.

#### B. Claude Chat History

Read conversation history from the project's chat directory. Focus on sessions since the last devlog entry:

```bash
ls -lt ~/.claude/projects/<converted-path>/*.json 2>/dev/null | head -10
```

**Handling Large History Files:**

Chat history files can grow large and may not fit entirely in context. When this happens:

1. **Check file size first:**
   ```bash
   wc -l ~/.claude/projects/<converted-path>/*.json
   ```

2. **Process in chronological chunks** if files are large:
   - Start with the oldest entries and work forward
   - Use `head` and `tail` with line offsets to read manageable sections (e.g., 500-1000 lines at a time)
   - Track the date range of each chunk you've processed

3. **Use dates to detect gaps:**
   - Each devlog entry has a `YYYY-MM-DD` header
   - Compare dates in the chat history against existing devlog entries
   - If you see dates in chat history that aren't in the devlog, those periods need to be captured
   - This is why date/time in devlog sections is critical - it lets you identify missing coverage

4. **Iterative parsing strategy:**
   ```bash
   # Read first chunk (oldest)
   head -n 1000 <history-file>

   # Read subsequent chunks
   tail -n +1001 <history-file> | head -n 1000

   # Continue until you've covered the full date range
   ```

5. **Fill gaps systematically:** If the devlog has missing date ranges, work through them chronologically. If context limits force you to stop before completing all gaps, document where you stopped so the next update can continue from there.

Parse the JSON files to extract:
- Significant decisions made
- Problems encountered and solutions
- Features implemented
- Research conducted
- Direction changes

#### C. Git Commit History

First, verify git is available:

```bash
git status 2>/dev/null || echo "NOT_A_GIT_REPO"
```

**If git is not found:** Ask the user how source code is tracked. They may use a different VCS (Mercurial, SVN, etc.), or this directory may be part of a larger repository. Don't assume - ask.

**If git is available:** Review commits since the last devlog entry (check the "Last Updated" date in DEVLOG.md, or use a reasonable default):

```bash
git log --oneline --since="<last-devlog-date>" 2>/dev/null || git log --oneline -30
```

For more detail on specific commits:

```bash
git log --pretty=format:"%h - %s (%ai)" --since="<last-devlog-date>"
```

If the devlog hasn't been updated in a long time, you may need to cover a larger range. Focus on commits that represent meaningful changes rather than trying to document everything.

#### D. Issue Tracker

Issues provide valuable context for the devlog - they capture the "why" behind work, discussions, and decisions.

**Discover the issue tracker:**

1. Check for common indicators in the project:
   - `.github/` directory → likely GitHub Issues
   - `linear.json` or `.linear/` → Linear
   - `beads.json` or `.beads/` → Beads (`bd list` command)
   - `.jira/` or Jira references in commits → Jira
   - `notion.json` → Notion

2. Check git remote for GitHub/GitLab:
   ```bash
   git remote -v 2>/dev/null
   ```

3. If no tracker is obvious, ask the user: "Where are issues tracked for this project? (GitHub, Jira, Linear, Notion, Beads, or something else?)"

**Connecting to issue trackers:**

- **GitHub Issues:** Use `gh` CLI if available (`gh issue list`, `gh issue view <number>`)
- **Beads:** Use `bd list` and `bd show <id>`
- **Other trackers (Jira, Linear, Notion, etc.):** These typically require authentication or API access

If the issue tracker requires a connection that isn't available:
1. Tell the user: "I can't access [tracker] directly. This would require [authentication/API access]."
2. Search for whether a Claude MCP or native connector exists for that service
3. If one exists, suggest it: "There's an MCP server for [tracker] that could enable access: [name/link]. Would you like to set that up?"
4. **Do not attempt to install connectors yourself** - just inform the user of options

**Handling large issue histories:**

Apply the same chunked reading strategy as with chat history:
- Use date ranges to process issues in chronological batches
- Compare issue dates against existing devlog entries to find gaps
- Focus on issues that were created, resolved, or had significant discussion since the last devlog update

Extract from issues:
- Feature requests and their rationale
- Bug reports and how they were resolved
- Design discussions and decisions
- Scope changes or deprioritizations

### 4. Write or Update DEVLOG.md

Create or append to `DEVLOG.md` in the project root.

#### Entry Format

Each entry should include a date header and narrative content. Use subsections only when they add clarity - simple entries don't need heavy structure.

**Minimal entry:**
```markdown
## YYYY-MM-DD - [Brief Title]

[2-4 sentences describing what was accomplished, decided, or learned. Include the *why* behind decisions.]

---
```

**Detailed entry (for significant milestones, pivots, or complex decisions):**
```markdown
## YYYY-MM-DD - [Brief Title]

### Summary
[2-4 sentences describing what was accomplished or decided]

### Details
- [Specific changes, decisions, or discoveries]
- [Problems encountered and how they were resolved]
- [Key code or architectural decisions with brief rationale]

### References (optional - include only if genuinely useful)
- Planning doc: [link if applicable]
- Related commits: [commit hashes if relevant]
- Related issues: [issue numbers/links if relevant]

---
```

**Entry granularity:** Create entries at natural breakpoints - completing a feature, making a significant decision, encountering and resolving a major problem, or pivoting direction. Not every work session needs an entry, but significant events should be captured close to when they happen.

#### Content Guidelines

**Include:**
- Significant architectural or design decisions with rationale
- Problems encountered and their resolutions
- New features or functionality added
- Research findings that influenced direction
- Direction changes and why they occurred (pivots are important to document)
- Dependencies added or configuration changes
- Notable refactoring or technical debt addressed
- Context that would help someone understand *why* decisions were made, not just *what* was done

**Omit:**
- Routine commits without significant context
- Minor typo fixes or formatting changes
- Redundant details already captured in commit messages
- Step-by-step implementation details (the code is the record)

**Remember:** The devlog is a narrative, not a changelog. Include technical details, but write them as part of a story. Someone reading it should come away understanding the project's journey - its origin, evolution, challenges overcome, and lessons learned - and stay engaged while reading.

### 5. Maintain Chronological Order

New entries go at the **end** of the file (chronological order). The devlog tells the story of the project from beginning to present - a reader should be able to read it top-to-bottom and understand the journey: why the project was created, what's been done, key design decisions, challenges, pivots, and current state.

#### File Structure

```markdown
# Development Log - [Project Name]

## About This Project

[Factual description of what the project does and why it exists. Write from the product perspective, not technical implementation. Answer: What problem does this solve? Who is it for? What does it do?]

**Status:** [Active | Maintenance | Complete]
**Started:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

Status definitions:
- **Active** - Under active development, features being added
- **Maintenance** - Stable, only bug fixes and minor updates
- **Complete** - No further development planned

---

## YYYY-MM-DD - Project Inception

[Why was this project started? What problem needed solving? What was the initial vision?]

---

## YYYY-MM-DD - [Milestone or Decision Title]

[What happened, what was decided, why it matters. Simple entries are fine.]

---

## YYYY-MM-DD - [Major Pivot or Complex Change]

### Summary
[Overview of the change]

### Details
- [Key decisions and rationale]
- [Challenges encountered]

---
```

#### About This Project Guidelines

The "About This Project" section should be:
- **Factual** - No marketing language or flowery prose
- **Product-focused** - Describe what users/consumers get, not how it's built
- **Purpose-driven** - Explain why the project exists and what problem it solves
- **Updated as needed** - If the project's purpose evolves, update this section

Bad: "A cutting-edge, blazingly fast microservices architecture leveraging React and Node.js"
Good: "A task management app for small teams who need to track work across multiple projects without the complexity of enterprise tools"

#### Writing Style

The devlog entries themselves should include technical details - architecture decisions, technology choices, implementation challenges - but written as a narrative, not a dry list. A good devlog is readable and has flow. Someone should be able to read it end-to-end and stay engaged.

**Avoid this (dry bullet list):**
```
- Added Redis caching
- Switched from REST to GraphQL
- Fixed N+1 query problem
- Updated Node to v20
```

**Prefer this (narrative with technical substance):**
```
Switched the API from REST to GraphQL after realizing our mobile app was making
12 separate requests to render the dashboard. GraphQL let us collapse that to one
request, but introduced an N+1 query problem that was hammering the database. Added
Redis caching for the user-preference lookups which were the main culprit - response
times dropped from 800ms to 120ms.
```

Both versions contain technical details, but the second tells a story: there was a problem, a solution was tried, a new problem emerged, it was solved, and here's the result.

## Tips

- When in doubt, include more detail - summarization is easier than reconstruction
- Link to planning documents rather than duplicating their content
- Note when conversations with Claude influenced significant decisions
- Update the devlog after completing logical chunks of work, not after every small change
- If a planning document exists, the devlog should complement it, not replace it
- If chat history is too large to load at once, process it in chronological chunks and use date gaps between the devlog and history to guide which sections need attention
- Keep the "About This Project" section current - if the project's purpose shifts, update it
- New entries always go at the end so the devlog reads as a continuous story
- Technical details belong in the devlog - just weave them into a narrative rather than listing them as bullets
- If you can't access a source (git, issue tracker, etc.), ask the user rather than skipping it silently
