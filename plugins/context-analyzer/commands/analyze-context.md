---
description: Analyze context window usage for the current project's Claude Code chat history
argument-hint: [optional-project-history-path]
allowed-tools: ["Bash", "Read", "Write"]
---

# Context Window Analysis

Analyze the current project's Claude Code chat history to identify what's consuming context window space and provide optimization recommendations.

## Step 1: Run the Analysis Script

Execute the Python analysis script to parse all JSONL session files for this project.

If the user provided an argument, use it as the project history path:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_context.py $ARGUMENTS
```

Otherwise, auto-detect from the current working directory:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_context.py
```

The script outputs a markdown report. Capture the full output.

## Step 2: Present Findings

Present the analysis report to the user. Highlight the top 3 context consumers and the most actionable recommendations.

If any category exceeds 15% of total context, call it out specifically with concrete advice.

## Step 3: Offer Follow-Up

After presenting the report, ask the user if they want to:
- Save the report to a file in the current working directory (suggest `./CONTEXT_OPTIMIZATIONS.md` in the project root, NEVER write to `~/.claude/projects/` or any other location outside the cwd)
- Get detailed advice on a specific finding
- Add file summaries to their project's CLAUDE.md to reduce re-reads
