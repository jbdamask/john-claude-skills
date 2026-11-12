# hive

A Claude Code plugin that sets up an agent team in any git repository with one command, `/hive:setup`.

## Requires Beads

**The team requires [Beads](https://github.com/steveyegge/beads), the `bd` task tracker.** Every task is a bead, and the agents, the spawn gate and the planner all read it. Without `bd` the setup stops before changing anything and tells you how to install it (`brew install beads`, or `npm install -g @beads/bd`).

It also needs:
- the GitHub CLI, `gh`, authenticated for the repo (or run with `--no-github` and create the labels later);
- the [beads-planner](../beads-planner) plugin, 0.2.0 or later, which the lead uses to turn an approved spec into beads;
- `python3` (the tools and tests use the standard library only) and `jq` (for the agent-brief hook).

## What you get
- **One lead** (`HIVE_ROLE=lead claude`) that hands out work, decides, and talks to you. **One-shot agents** that each do one bead and exit.
- **Eight roles**, each answering one question, built into `.claude/agents/`: strategist, gardener, spec writer, experience designer, red team, blind checker, product reviewer, fresh-eyes reader.
- **The build flow**: you open a GitHub issue with a sentence; a spec writer drafts a spec and a 200-word brief; the experience designer and red team go over it; you approve with the label `approved_spec`; the lead breaks it into beads; agents build; the red team attacks the evidence; you get a done comment of at most 150 words. Labels: `drafting`, `pending_approval`, `approved_spec`, `proposal`, `in_progress`, `bug`.
- **A weekly idea round** (three scouts, the strategist, the red team, at most two proposals) and **a weekly gardener report** on what the rules cost.
- **Mechanisms, not rules**: agents land work only through `hive/tools/land.py` (lock, merge main, fast tests, push only if they pass; a hook refuses a direct push to main); a spawn gate that refuses a bead that is not ready or a role spawned as the wrong agent type; guards on shell writes in worktrees, code edits in the shared checkout, closing past a blocker and email addresses in commands; a protected-folders guard (`protected_folders` in hive/project.json, empty by default) that lets only the agent of a bead carrying the folder's label read or list a folder of items that must stay unseen; a check that every generated file matches a fresh build; and `hive/tools/scratch.py`, which lists closed beads' scratch folders for a person to delete.
- **A small rule budget**: the team's rule files carry at most 150 rule lines, and a test holds it there.

## Two layers
The **general layer** is the same in every repo, and each run of the setup brings it up to date (`hive/VERSION` says which version). The **project layer** is yours: your vision, product test, the checks every feature passes, your never-do list, the product reviewer's checklist and your glossary. The setup writes it once from six questions, marks what you did not say as DRAFT, and never overwrites it.

## Install
```
/plugin marketplace add jbdamask/john-claude-skills
/plugin install hive@john-claude-skills
```

## Use
```
/hive:setup
```
The skill asks six questions in one message (name, who the product is for, the fast test command, money caps, the lead's name, whether to create the GitHub labels), then runs `skills/setup/scripts/setup.py`. That script checks the prerequisites, writes both layers, runs `bd init` if needed, builds the agent definitions and the agent brief, runs `hive/tests`, creates the labels and commits. Run it again at any time to update: it asks nothing, keeps your files and says what changed.

Then start the lead with `HIVE_ROLE=lead claude` and open a GitHub issue with one sentence on what you want to see.

## Structure
```
hive/
├── .claude-plugin/plugin.json
└── skills/setup/
    ├── SKILL.md
    ├── scripts/setup.py
    └── template/
        ├── general/            # copied into the repo on every run
        ├── project/            # written once, never overwritten
        └── settings-hooks.json # merged into .claude/settings.json
```
