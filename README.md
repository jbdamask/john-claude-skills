# John's Claude Code Skills

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

## Skills

Browse the `skills/` directory to see available skills. Each skill has a `SKILL.md` with its description and usage instructions.

## Contributing

To add a new skill:

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` file with YAML frontmatter (`name`, `description`) and instructions
3. Optionally add `references/`, `scripts/`, or `assets/` subdirectories
