---
name: setup
description: Sets up an agent team in the current git repository (requires Beads, the bd task tracker, plus the gh command and the beads-planner plugin 0.2.0 or later). Installs one long-lived lead and one-shot agents that each do one bead, eight role agents (strategist, gardener, spec writer, experience designer, red team, blind checker, product reviewer, fresh-eyes reader), the build flow from a GitHub issue to a finished feature, the guard hooks, the landing tool and their tests, all under hive/. Use when the user says "/hive:setup", "set up the hive", "install the agent team", "set up the team in this repo", or wants to update a repo's hive to the latest version.
---

# Set up the hive

**This team requires Beads, the `bd` task tracker** (https://github.com/steveyegge/beads): every task is a bead, and the agents, the spawn gate and the planner all read it. It also needs the `gh` command and the beads-planner plugin, 0.2.0 or later. Tell the user this first, before anything else. If `bd` is not installed, the script stops, says why and how to install it, and changes nothing.

The script does all the copying; you only ask the questions and run it.

## What it installs
- The general layer, the same in every repo and updated by each run: rule files and role briefs in hive/, tools in hive/tools/ (roles, brief, generated, land, scratch, spec_brief, issue_check, team_use, term), guard hooks in hive/hooks/, their tests in hive/tests/, .beads/PRIME.md and .beads/PLANNING.md, the hooks in .claude/settings.json, the role agents in .claude/agents/, a short block in CLAUDE.md. hive/VERSION says which version.
- The project layer, written once from the answers and never overwritten: hive/project.json, VISION.md, PROJECT.md, PRINCIPLES.md, strategy/PRODUCT-TEST.md, REVIEW-CHECKLIST.md, DEFINITIONS.jsonl, GENERATED.json. Parts the user did not say are marked DRAFT.

## Steps
1. If `hive/project.json` already exists, this is an update: ask nothing and go to step 3.
2. Ask the user these in ONE message, numbered, and wait for the answers:
   1. The project's name.
   2. Who the product's user is and what it is for, in a sentence or two.
   3. The fast test command (the one that must pass before any push, e.g. `pytest -q -m "not slow"`).
   4. Money caps (e.g. "no pay-per-use API spend; $10 a day on X"). Default: no pay-per-use spend without their yes.
   5. The lead's name, used as its bd actor. Default: `lead`.
   6. Create the GitHub labels now? Default: yes.
   Write the answers to a JSON file in your scratch folder with keys `name`, `user`, `fast_tests`, `spend`, `lead`, `labels` (true or false).
3. Run, from the repo root: `python3 <this skill's directory>/scripts/setup.py --answers <that file>` (on an update, no `--answers`). Add `--no-github` if the user said no to labels or has no GitHub remote yet.
4. Show the user what the script printed: what it added, updated or kept, the test result, the commit, and the two next steps it ends with (start the lead with `HIVE_ROLE=lead claude`; open a GitHub issue with one sentence). If it stopped, show its message as is.

The script commits only its own paths, with a plain message and no attribution lines. It never pushes.
