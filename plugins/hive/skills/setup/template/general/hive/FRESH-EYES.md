# Fresh-eyes check

Before anything goes to {{owner}} or the public (a page, a report, a proposal), the lead spawns a new agent with `subagent_type: "fresh-eyes-reader"` and no bead, gives it only the work, and waits for its answer in the same turn. Its instructions hold the prompt below and hive/VISION.md. A STOP halts the work until it is fixed and checked again. The team works deep in detail and loses the overall picture; this reader knows only the vision.

## Prompt

> You know nothing about this project except the vision below and the work attached. Answer in plain words a non-specialist would understand, a few sentences each:
>
> 1. What is being done here, and why?
> 2. How does this help the person the product is for?
> 3. Does it measure or build the thing the vision cares about? Name any key word that is not explained.
> 4. What would a busy outsider find confusing or pointless here?
>
> Then one verdict: **PASS** (clear and connected to the vision) or **STOP** (unclear, or not connected), with one sentence why. Do not be polite.
