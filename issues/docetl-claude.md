# docetl claude

## Summary

Modify the DocETL skill to use Claude models instead of OpenAI models.

## Current State

The existing DocETL skill (from [ucbepic/docetl](https://github.com/ucbepic/docetl/blob/main/.claude/skills/docetl/SKILL.md)) uses OpenAI models:
- `gpt-5-nano` / `gpt-5-mini` - for high-volume extraction tasks
- `gpt-4.1` / `gpt-5.1` - for summarization and synthesis tasks

## Requested Changes

Replace the OpenAI model references with Claude models:
- **Default model**: Use `claude-haiku-4` (Haiku) for extraction and general tasks
- Update all model references in the SKILL.md documentation
- Ensure pipeline examples use the Claude model naming convention

## Model Mapping

| Current (OpenAI)        | New (Claude)     |
|-------------------------|------------------|
| gpt-5-nano / gpt-5-mini | claude-haiku-4   |
| gpt-4.1 / gpt-5.1       | claude-haiku-4   |

## Notes

- DocETL supports multiple LLM providers including Anthropic Claude
- Haiku is the preferred model for this implementation due to its speed and cost-effectiveness
- The skill should maintain the same iterative workflow philosophy: write → run → inspect → iterate

## Source Reference

Original SKILL.md: https://github.com/ucbepic/docetl/blob/main/.claude/skills/docetl/SKILL.md
