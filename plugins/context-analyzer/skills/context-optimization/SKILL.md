---
name: Context Optimization
description: This skill should be used when the user asks about "context window optimization", "reduce context usage", "context is filling up", "running out of context", "context bloat", "optimize my sessions", "why is context so large", or when providing advice on how to keep Claude Code sessions efficient. Provides knowledge about what consumes context and strategies to minimize waste.
version: 0.1.0
---

# Context Optimization for Claude Code

## Overview

Claude Code sessions have a finite context window. Understanding what consumes context and how to minimize waste keeps sessions productive longer. This skill provides patterns and strategies for context-efficient workflows.

## What Consumes Context

Every interaction in a Claude Code session adds to context. The main consumers, ranked by typical impact:

### 1. Message Metadata Overhead (30-40%)
Every message carries a JSON envelope with sessionId, uuid, cwd, gitBranch, version, and other fields. This is not directly controllable but is the largest single category.

### 2. Progress/Streaming Messages (20-30%)
Hook progress events and streaming data accumulate significantly in long sessions. Not directly controllable.

### 3. User-Pasted Images (10-20%)
Screenshots pasted into chat are encoded as base64 PNG, inflating size ~33% over raw bytes. A single full-screen PNG screenshot can consume 500 KB to 2 MB of context.

### 4. File Read Results (5-10%)
Every `Read` tool invocation returns the full file content into context. Re-reading the same file multiple times multiplies its impact.

### 5. Browser Screenshots (3-5%)
Claude-in-Chrome screenshots are JPEG (~50-80 KB each) but accumulate in browser-heavy sessions.

### 6. Edit/Write Payloads (2-3%)
File content included in Edit and Write operations.

### 7. Bash Output (1-3%)
Command output returned to context. Usually small per-call but adds up with heavy Bash usage.

## Optimization Strategies

### Compress Screenshots Before Pasting
- Resize to ~800px wide before pasting
- Use JPEG format instead of PNG where possible
- Consider using Claude-in-Chrome's screenshot tool (produces ~50-70 KB JPEG) instead of pasting full-screen PNGs (500 KB-2 MB)
- On macOS, use Preview or a keyboard shortcut to downscale clipboard images

### Reduce File Re-Reads
- Add structural summaries of frequently-referenced files to the project's `CLAUDE.md`
- For infrastructure files (CloudFormation, Terraform, etc.), document resource names and relationships in `CLAUDE.md`
- Keep documentation files (DEVLOG.md, CHANGELOG.md) concise; archive old content

### Use /compact Proactively
- Run `/compact` after browser automation sequences with many screenshots
- Run `/compact` after completing a distinct phase of work
- Run `/compact` when switching between different parts of the codebase

### Optimize Bash Usage
- Pipe verbose output through `head` or `tail` when full output is unnecessary
- Redirect large outputs to files and read selectively
- Use `--quiet` or `--silent` flags where available

### Use .claudeignore
- Add build artifacts, node_modules, and generated files
- Add large data files that should not be searched
- Add log files and temporary outputs

### Prefer Edit Over Write
- `Edit` replaces specific strings (small payload)
- `Write` sends the entire file content (large payload)
- For modifications to existing files, Edit is more context-efficient

### Consolidate Subagent Usage
- Each Task/subagent invocation adds its result to context
- Combine related queries into a single subagent call when possible
- Use targeted prompts that return concise results

## Diagnosing Context Issues

To analyze what's consuming context in a specific project, run:

```
/context-analyzer:analyze-context
```

This parses the project's JSONL chat history files in `~/.claude/projects/` and produces a detailed breakdown with per-category sizes, most re-read files, and targeted recommendations.

For programmatic access, the analysis script supports JSON output:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_context.py --json
```

## Common Anti-Patterns

### Re-Reading the Same File Every Turn
**Problem**: Claude reads `types.ts` or `api.ts` every time it needs to reference types.
**Fix**: Add key type definitions or API surface to `CLAUDE.md`.

### Pasting Full-Screen Screenshots
**Problem**: Each PNG screenshot is 500 KB-2 MB in base64.
**Fix**: Crop to the relevant area and resize before pasting.

### Long Browser Automation Sequences Without Compacting
**Problem**: 20+ screenshots from scroll-screenshot-click sequences fill context.
**Fix**: Run `/compact` after browser testing. Use `read_page` (accessibility tree) instead of screenshots when visual verification isn't needed.

### Verbose Build/Test Output
**Problem**: Full test suite output or build logs dumped to context.
**Fix**: Pipe through `tail -20` or grep for failures only.

### Large Documentation Files Read on Every Session
**Problem**: DEVLOG.md or similar grows over time and is read at session start.
**Fix**: Keep it under 5 KB or move to Claude Code memory (`~/.claude/projects/.../memory/`).

## Additional Resources

For detailed analysis methodology and report interpretation, see:
- **`references/analysis-methodology.md`** — How the analysis script categorizes context consumption
