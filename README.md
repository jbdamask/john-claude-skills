# John's Claude Code Marketplace

A collection of Claude Code plugins for development workflows.

## Installation

Add this marketplace to Claude Code:

```shell
/plugin marketplace add jbdamask/john-claude-skills
```

Then install individual plugins:

```shell
/plugin install devlog@john-claude-skills
```

## Available Plugins

### devlog

Create and maintain a `DEVLOG.md` file capturing the development story of a project.

**Usage:** Run `/devlog` to update your project's development log.

**Features:**
- Gathers context from planning documents, chat history, and git commits
- Creates chronological entries with summaries, details, and references
- Maintains a structured format for easy reading and searching

## Contributing

To add a new plugin:

1. Create a directory under `plugins/<plugin-name>/`
2. Add `.claude-plugin/plugin.json` with plugin metadata
3. Add commands in `plugins/<plugin-name>/commands/`
4. Update the marketplace manifest in `.claude-plugin/marketplace.json`

## Resources

- [Claude Code Plugin Documentation](https://code.claude.com/docs/en/plugins)
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
