# How we build

{{owner}} says what to see; agents write the spec and build it. Labels on the GitHub issue say where each request is: `drafting`, `pending_approval`, `approved_spec`, `proposal`, `in_progress`, `bug`. `python3 hive/tools/issue_check.py` tells the lead which issues need it, so {{owner}} never has to say an issue exists.

## The flow
1. **{{owner}} states the feature** in a GitHub issue: a sentence or a paragraph on the outcome wanted. The lead labels it `drafting`. An issue labelled `bug` skips the spec and goes to hive/FIXES.md.
2. **A spec writer writes the spec in two parts.** For agents, a file `hive/specs/<issue number>-<short name>.md`: {{owner}}'s words at the top, word for word; what will be built; the acceptance, which anyone can check with a yes or no; how each check in hive/PROJECT.md "Checks every feature passes" will be met; how it serves the product test; and a `DECIDED:` line for every question {{owner}}'s goals settle. For {{owner}}, the issue body: a brief of at most 200 words in five parts (You asked for, You will get, You will not get, Cost, Decide) that links the file and passes `python3 hive/tools/spec_brief.py <issue number>`. Cost is tasks and money, never days or hours. Decide holds at most three questions only {{owner}} can answer (hive/TEAM.md "Who decides"), each with a recommendation. Where the feature changes what a user does, an experience designer then writes the user's steps into the spec (hive/EXPERIENCE.md). A red team agent that wrote none of it tries to show it is wrong (hive/RED-TEAM.md). The spec is revised once; the lead settles the rest, and what only {{owner}} can settle becomes a Decide question. The lead swaps `drafting` for `pending_approval`.
3. **{{owner}} approves by adding the label `approved_spec`,** which accepts every recommendation. To answer a question differently, first comment with its number and the answer; the lead records it in the spec file. An issue without that label is not work.
4. **The lead breaks it down** with `/beads-planner:issue-to-beads <issue number>`, which reads .beads/PLANNING.md: one epic whose title carries `#<number>` and whose acceptance is the spec's, one bead per one-shot task. The lead removes `pending_approval` and adds `in_progress`.
5. **One-shot agents build the beads** (the agent brief).
6. **Done is the epic's acceptance met on the running product.** A red team agent first tries to show the evidence does not hold. Then the lead comments on the issue in at most 150 words (what {{owner}} can now see and where, what changed for the user, anything left over), puts the full evidence in the spec file and closes the issue; {{owner}} reopens it to disagree.

- What {{owner}} asks for is the requirement, never a hypothesis: build it to the words as written and report what it changed.
- If building shows the spec is wrong for the user, the agent writes a `PREMISE:` note and the lead takes it to {{owner}} the same day.

## The product test
One test says whether the product is worth using: hive/strategy/PRODUCT-TEST.md. The strategist owns it and reports its result and age each week. No milestone is called done on how much shipped.

## New ideas
The weekly idea round (hive/STRATEGIST.md) files at most two issues labelled `proposal`. {{owner}} says yes by removing the label, which makes it a request like any other. Nothing is built from a proposal.

## Changing the rules
- A rule file changes when {{owner}} says so, or to record a fact about a tool. A new rule line replaces an old one; the total in `python3 hive/tools/team_use.py rules` does not rise.
- A mistake made twice gets a mechanism (a hook that refuses, a test, a setting, removing the option), never one more sentence. If none is possible, the lead tells {{owner}}.
- Each week the gardener (hive/GARDENER.md) reports what the rules cost and whether agents use them, and proposes cuts as one batch.
- Edit a role's brief in its source file, then run `python3 hive/tools/roles.py build`; the brief is rebuilt with `python3 hive/tools/brief.py build`.
