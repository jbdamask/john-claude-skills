# Team rules

One long-lived lead hands out work; one-shot agents each do one bead and exit; {{owner}} says what to build. The agent brief (hive/BRIEF.md, added to every agent at start as .beads/PRIME.md) holds the loop and the never-do list; they are not repeated here. This file holds what the brief has no room for. What is particular to this project is in hive/PROJECT.md.

## How we work
- {{owner}} states a feature on a GitHub issue; an agent writes the spec; {{owner}} approves it with the label `approved_spec`; the lead breaks it into beads; one-shot agents build them (hive/BUILD.md). Bugs: hive/FIXES.md.
- Agents never idle: the lead spawns an agent with a complete task, it writes its result on its bead and in files, sends one final message and exits, because an idle agent rebuilds its whole context on every wake-up.
- Context lives on beads, not in an agent's memory: notes with shas, follow-ups as new beads, `resume: <exact command>` for anything unfinished.
- The only message is the final one to the lead: a result, a decision only the lead can make, a blocker, or spend over a cap. No acknowledgements or status messages.
- One writer per step: one agent owns all the files its bead changes. A review is one-shot: the files to read in, one verdict out.
- Keep contexts small: point to files instead of pasting them; hand big reads to a sub-agent that returns a short result.

## Git and landing
- An agent lands work only with `python3 hive/tools/land.py`: it takes a lock, merges main, runs the fast tests on the merge, pushes only if they pass and releases the lock. A hook refuses an agent's own push to main.
- A bead whose diff changes code runs in a worktree (the lead spawns it with `isolation: "worktree"`); the shared checkout is for notes, docs and beads. Which paths count as code: `shared_tree_may_edit` in hive/project.json.
- No file that every task must edit (a changelog, a shared counter, an index every bead appends to): agents queue behind it and re-merge it. Generate such a file, or give each task its own file.

## Generated files
- A file built from another file (agent definitions, the agent brief, an index) has a row in hive/GENERATED.json naming the command that exits 1 when the file differs from a fresh build; hive/tests runs every row. Change the source, then rebuild; never hand-edit the built file.

## Spend and keys
- Caps are in hive/PROJECT.md "Spend"; the brief carries them. Log every paid run's cost as a bead note, and add up a bead's notes before its next run.

## Who decides
Check from the top; the first match decides. If {{owner}} asked for this exact thing and you can quote the words, it isn't a question: do it.
1. **Never done:** working around a hook refusal; changing a pass mark or a question after seeing results.
2. **{{owner}}:** accounts, passwords, new keys, permissions, hooks and guards.
3. **{{owner}}:** spend past the caps in hive/PROJECT.md, or any new paid service.
4. **{{owner}}:** showing the user less than today, or stopping a source of data.
5. **{{owner}}:** anything git cannot undo: deleting data outside the repo, force-pushing, rewriting history.
6. **{{owner}}:** publishing anything new to people other than {{owner}}.
7. **{{owner}}:** what to build, what the product is for and whom it serves, and two of {{owner}}'s goals in conflict.
8. **Lead:** everything else git can undo, within the caps: bugs, how a spec becomes beads, tools, naming, order of work, questions of analysis. The lead writes `DECIDED: <decision> (goal: <goal>)` on the bead.
9. **Agent:** anything inside its bead and its acceptance.

## Work tracking
- One bead is one one-shot task with one writer: a title, a description with the goal and a `Read:` list of the only files needed, and `--acceptance` that anyone can check and the agent can meet alone.
- A bead for a role carries the label `role:<name>` (hive/ROLES.json); every other bead is done by a plain agent.
- A start gate is a dependency (`bd dep add <blocked> <blocker>`), never text.
- A note that changes the work also goes into the bead's title, description or acceptance (`bd update`), then a `SPEC-OK: <what changed>` note; the spawn gate refuses a bead whose notes overrule its text until then.
- To reopen another agent's bead: `bd reopen <id>`, `bd update <id> --assignee ""`, then a note saying exactly what to fix.
- The agent brief stays under the hook limit (hive/tests): a line added to it replaces one.
