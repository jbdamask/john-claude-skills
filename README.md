# John's Claude Code Skills

<img src="social-card.png" alt="John's Claude Code Skills" width="640" />

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

And plugins:

```shell
/plugin install beads-planner@john-claude-skills
/plugin install context-analyzer@john-claude-skills
``

## Skills

Browse the `skills/` directory to see available skills. Each skill has a `SKILL.md` with its description and usage instructions.

## Contributing

To add a new skill:

1. Create a directory under `skills/<skill-name>/`
2. Add a `SKILL.md` file with YAML frontmatter (`name`, `description`) and instructions
3. Optionally add `references/`, `scripts/`, or `assets/` subdirectories

### Dev setup (required after cloning)

```sh
git config core.hooksPath .githooks
```

This enables the committed pre-commit hook that auto-bumps a plugin's patch version in `.claude-plugin/plugin.json` whenever that plugin's files change. Claude Code only re-syncs an installed plugin when its version changes, so a commit without a bump never reaches installed copies. CI (`plugin-version-check`) fails any push or PR that changes a plugin without bumping it.
