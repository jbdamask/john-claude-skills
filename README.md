# John's Claude Code Skills Marketplace

A collection of Claude Code skills for development workflows.

## Installation

Add this marketplace to Claude Code:

```shell
/plugin marketplace add jbdamask/john-claude-skills
```

Then install the skills:

```shell
/plugin install john-skills@john-claude-skills
```

## Available Skills

### devlog

Create and maintain a `DEVLOG.md` file capturing the development story of a project.

**Invoke when:**
- You want to update the devlog
- You need to document project progress
- After completing significant milestones
- Before context switches

**Features:**
- Gathers context from planning documents, chat history, and git commits
- Creates chronological entries with summaries, details, and references
- Maintains a structured format for easy reading and searching

## Contributing

To add a new skill:

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` file with YAML frontmatter (`name`, `description`) and instructions
3. Update the `skills` array in `.claude-plugin/marketplace.json`

## Resources

- [Agent Skills Specification](https://agentskills.io/specification)
- [Claude Code Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
