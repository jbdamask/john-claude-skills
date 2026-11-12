# {{name}}: project rules

What is particular to this project. The team's general rules (hive/TEAM.md and the files it points to) are installed by the setup; this file is yours and the setup never overwrites it. Settings the tools read are in hive/project.json.

## About
{{user}}

## Checks every feature passes
DRAFT: written by the setup from the general case; {{owner}} rewrites them for this product.
1. **Nothing about one particular case in the code.** Code names no particular customer, record or example it was built on; what is particular lives in data.
2. **It works on a case it was not built on.** A feature that changes what the user sees is shown working on a case nobody looked at while building it, before its epic closes.
3. **No worse than today** (only for parts that make a judgment). Today's version and the new one run on the same stored cases; an agent that did none of the work reads the differences, blind to which side is which.

## Never
- None yet. Add one line per thing agents must never do on this project; `python3 hive/tools/brief.py build` puts them in the agent brief.

## Spend
{{spend}}

## Reports
Reports and questions for {{owner}} go to the lead's terminal session. DRAFT: name a channel here if {{owner}} wants them elsewhere.
