---
name: devlog
description: Create and maintain a DEVLOG.md file capturing the development story of a project. Use this periodically over the course of a project to capture important information about the development story. Invoke when the user asks to update the devlog, create a devlog, document project progress, or capture development history. Also appropriate after completing significant milestones or before context switches.
---

# DevLog

Create and maintain `DEVLOG.md` in the project root with a chronological record of development activity. The devlog should be detailed enough to reconstruct the development narrative, but not an exhaustive transcript.

## Workflow

### 1. Determine Project Context

First, establish the current working directory and derive the chat history path:

```bash
pwd
```

Convert the project path to the chat history directory name by replacing `/` with `-`:
- Example: `/Users/johndamask/src/tries/2026-01-08-myproject`
- Becomes: `~/.claude/projects/-Users-johndamask-src-tries-2026-01-08-myproject`

### 2. Gather Information from Sources

Collect information from all three sources:

#### A. Planning Documents

Search for planning documents in the project:

```bash
find . -name "*.md" -type f | xargs grep -l -i "plan\|implementation\|architecture" 2>/dev/null | head -20
```

Also check for Claude plan mode artifacts (often in `.claude/` or project root). If planning documents exist, summarize key decisions and link to them in the devlog.

#### B. Claude Chat History

Read recent conversation history from the project's chat directory:

```bash
ls -lt ~/.claude/projects/<converted-path>/*.json 2>/dev/null | head -10
```

Parse the JSON files to extract:
- Significant decisions made
- Problems encountered and solutions
- Features implemented
- Research conducted
- Direction changes

#### C. Git Commit History

Review recent commits for development activity:

```bash
git log --oneline --since="1 week ago" 2>/dev/null || git log --oneline -20
```

For more detail on specific commits:

```bash
git log --pretty=format:"%h - %s (%ai)" --since="1 week ago"
```

### 3. Write or Update DEVLOG.md

Create or append to `DEVLOG.md` in the project root.

#### Entry Format

Each entry should include:

```markdown
## YYYY-MM-DD - [Brief Title]

### Summary
[2-4 sentences describing what was accomplished or decided]

### Details
- [Specific changes, decisions, or discoveries]
- [Problems encountered and how they were resolved]
- [Key code or architectural decisions with brief rationale]

### References
- Planning doc: [link if applicable]
- Related commits: [commit hashes if relevant]
- Chat context: [note if significant discussion informed decisions]

---
```

#### Content Guidelines

**Include:**
- Significant architectural or design decisions with rationale
- Problems encountered and their resolutions
- New features or functionality added
- Research findings that influenced direction
- Direction changes and why they occurred
- Dependencies added or configuration changes
- Notable refactoring or technical debt addressed

**Omit:**
- Routine commits without significant context
- Minor typo fixes or formatting changes
- Redundant details already captured in commit messages
- Step-by-step implementation details (the code is the record)

### 4. Maintain Chronological Order

New entries go at the top of the file (reverse chronological). Keep a header section with project overview that gets updated as the project evolves:

```markdown
# Development Log - [Project Name]

> [One-line project description]

**Status:** [Active/Maintenance/Complete]
**Started:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD

---

## [Most Recent Entry]
...
```

## Tips

- When in doubt, include more detail - summarization is easier than reconstruction
- Link to planning documents rather than duplicating their content
- Note when conversations with Claude influenced significant decisions
- Update the devlog after completing logical chunks of work, not after every small change
- If a planning document exists, the devlog should complement it, not replace it
