# The team

Everything the agent team needs lives here, apart from the product's code. Installed by the `/hive:setup` skill (version in hive/VERSION). A second run of the setup updates the team's files and never touches the project's.

**Requires Beads** (the `bd` task tracker, https://github.com/steveyegge/beads): every task is a bead, and the agents, the spawn gate and the planner all read it. Also the `gh` command and the beads-planner plugin, 0.2.0 or later.

Start the lead with `HIVE_ROLE=lead claude` in the repo root. Then open a GitHub issue with one sentence on what you want to see.

## The team's files (updated by the setup)
| File | What it holds |
|---|---|
| hive/BRIEF.md | The agent brief every one-shot agent gets at start (built into .beads/PRIME.md) |
| hive/TEAM.md | How we work, landing, generated files, who decides, beads |
| hive/LEAD.md | The lead's runbook |
| hive/BUILD.md | The flow from a GitHub issue to a finished feature |
| hive/FIXES.md | Bug fixes and the blind check |
| hive/WRITING.md | Rules for text people read |
| hive/CRONS.md | The lead's scheduled jobs |
| hive/ROLES.json | The roles, built into .claude/agents/ by hive/tools/roles.py |
| hive/STRATEGIST.md, hive/GARDENER.md, hive/RED-TEAM.md, hive/EXPERIENCE.md, hive/FRESH-EYES.md, hive/PRODUCT-REVIEW.md | Role briefs |
| .beads/PLANNING.md | Conventions for the beads-planner plugin |
| hive/tools/ | roles, brief, generated, land, scratch, spec_brief, issue_check, team_use, term |
| hive/hooks/ | The guards (wired in .claude/settings.json) |
| hive/tests/ | Tests for all of it: `python3 -m unittest discover -s hive/tests` |

## The project's files (yours; the setup never overwrites them)
| File | What it holds |
|---|---|
| hive/VISION.md | Who the product is for and what it is for |
| hive/PROJECT.md | Checks every feature passes, the never-do list, spend caps, where reports go |
| hive/project.json | Settings the tools read: name, fast tests, main branch, paths agents may edit in the shared checkout |
| hive/PRINCIPLES.md | How to choose when no rule does |
| hive/strategy/PRODUCT-TEST.md | The one test that says whether the product is worth using |
| hive/REVIEW-CHECKLIST.md | The product reviewer's checklist |
| hive/DEFINITIONS.jsonl | The glossary |
| hive/GENERATED.json | The project's own generated files and the commands that check them |
