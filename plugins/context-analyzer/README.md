# context-analyzer

A Claude Code plugin that analyzes chat history to identify what's consuming your context window and provides optimization recommendations.

## Features

- **Context breakdown** — Categorizes context consumption by type (images, file reads, bash output, screenshots, etc.)
- **File re-read detection** — Identifies files that are read repeatedly across sessions, wasting context
- **Largest session analysis** — Finds which sessions consumed the most context and why
- **Actionable recommendations** — Provides prioritized suggestions to reduce context bloat
- **Auto-detection** — Automatically finds the project history directory from your current working directory

## Components

| Component | Name | Description |
|-----------|------|-------------|
| Command | `/context-analyzer:analyze-context` | Run the full analysis and get a report |
| Agent | `context-analyzer` | Subagent for autonomous context diagnostics |
| Skill | Context Optimization | Knowledge about context optimization patterns |
| Script | `analyze_context.py` | Python analysis engine (no dependencies beyond stdlib) |

## Installation

### From a marketplace

```
/plugin install context-analyzer@your-marketplace
```

### Local testing

```bash
claude --plugin-dir /path/to/context-analyzer
```

## Usage

### Slash command

```
/context-analyzer:analyze-context
```

Runs the analysis on the current project and presents a formatted report.

### Agent (automatic)

The context-analyzer agent triggers when you ask questions like:
- "Why is my context filling up?"
- "Analyze my context usage"
- "What's consuming my context window?"

### Direct script execution

```bash
# Markdown report (default)
python3 scripts/analyze_context.py ~/.claude/projects/-Your-Project-Path/

# JSON output for programmatic use
python3 scripts/analyze_context.py ~/.claude/projects/-Your-Project-Path/ --json
```

## Prerequisites

- Python 3.8+ (uses only stdlib — no pip install needed)
- Claude Code chat history in `~/.claude/projects/`

## How It Works

The plugin parses JSONL chat history files that Claude Code stores in `~/.claude/projects/{encoded-project-path}/`. Each line is a JSON message representing a conversation event. The analyzer categorizes every message into context consumption buckets and tracks file read patterns across all sessions.

See `skills/context-optimization/references/analysis-methodology.md` for details.
