---
name: til
description: Condense an AI session (or a single learning) into a very short, standardized TIL document — a concise title, one-line description, and a briefing of what was done, in Markdown by default or HTML on request. Use when the user says "TIL", "today I learned", or "write a TIL", or wants a short shareable write-up of something learned or done in a session.
---

# Today I Learned (TIL)

Turn the current session — or one thing learned in it — into a document a person reads in under a minute and an AI agent can parse without guessing. The output is the deliverable; the making of it should take a minute or two.

## Core principles

These govern every TIL. When a judgment call comes up, resolve it with the first principle that applies.

1. **One learning per TIL.** A TIL captures exactly one insight. If the session produced two, write two TILs (confirm with the user first). A TIL that teaches two things teaches neither.
2. **The title sells the learning — clear first, then engaging.** The reader must instantly know what it's about and why they'd care; then earn the click with a hook. Never ship your first draft of a title (see the title rules in the format section). Max 70 characters.
3. **Short as possible, but no shorter.** Body of 100–200 words; 250 is the hard cap, excluding one code block or image. If it won't fit, the scope is wrong — narrow the learning, don't compress the prose into fragments.
4. **Show the receipt.** One concrete artifact — a command, a code snippet, a diff, a diagram — teaches faster than a paragraph describing it. Include exactly one when it carries the learning; include none when it doesn't.
5. **Standard shape, always.** Same frontmatter fields, same section order, every time. Humans skim on rhythm; agents parse on structure. Never rearrange or invent sections.
6. **Facts only.** Everything in the TIL must come from the session or from the user. No invented numbers, no "typically", no padding a thin learning with background research. If the learning wasn't verified in the session, say so in one line.
7. **No fluff.** Draft against the writing rules bundled in `references/lint-rules.md`: plain words, active voice, no AI-fingerprint vocabulary (delve, robust, leverage, seamless, game-changer…), no "Here's the thing", no mic-drop closers, no recap endings. Every sentence must inform.
8. **A TIL is safe to share by construction.** TILs exist to be passed around — Slack, blogs, wikis — so treat every TIL as if it will be public. No secrets, credentials, PHI, or personal data ever appear in one, even when they appeared in the session. The workflow enforces this with a guardrail at the start and another at the end; both are mandatory.

## The TIL format

A TIL is a Markdown file with YAML frontmatter and a fixed body shape.

```markdown
---
title: <the learning as a claim, ≤70 chars>
description: <one sentence expanding the title — what and why it matters>
author: <name>
date: <YYYY-MM-DD>
tags: [<1-3 tags from references/tag-taxonomy.md>]
---

# <title, repeated>

**Context.** One or two sentences: what you were doing when this came up.

**The learning.** The core of the TIL, 2–5 sentences. State the insight, the mechanism behind it, and what you did about it.

<optional: ONE code block, command, or image — the receipt>

**Watch out.** (optional, one sentence) The caveat, edge case, or thing not yet verified. Omit the section if there isn't one.
```

### Title rules

A TIL lives or dies on its title. A great one carries three elements in ≤70 characters: a **specific claim** (what happens, stated boldly), **key terms** (the searchable nouns — the technology, the behavior, the outcome), and when it fits, a **hook** (the surprising or contrary angle). Apply these rules, in priority order:

1. **Clear, not clever.** The title alone must answer what this is about and why the reader should care. No riddles, no clichés, no wordplay that hides the subject.
2. **Specific, not generic.** Never a topic label ("Monkey behavior", "Notes on caching") or a big abstraction ("Lessons from a debugging session"). Climb the specificity ladder until the title states the finding: "Monkey behavior" → "The effects of sugar on monkey behavior" → "Sugar stimulates tail-twitch behavior in Panamanian monkeys". The last one makes the claim and names the actors; that's the target.
3. **Load the key terms.** The title doubles as the TIL's index entry — humans scan it in a feed and agents match queries against it. Name the actual technology and behavior; a title without its key terms is unfindable no matter how catchy.
4. **Speak to the reader.** Use "you/your" when it fits naturally — "Why your Lambda retries twice" beats "Lambda retry behavior". Frame the learning as their problem, not your diary entry.
5. **Use the engaging shapes.** "Why X happens", "How to X", "Stop doing X", "X doesn't work the way you think", or a claim with a number. Questions are fine if the body answers them.
6. **Hold back at most one thing.** A curiosity gap (the mechanism, the fix) earns the click — but never at the cost of key terms or the claim, and never promising what the body doesn't deliver.
7. **Draft at least five candidates, then choose.** First-draft titles are reliably the weakest. Write five or more, judge them against rules 1–6, pick the strongest. Don't show the rejects unless asked.

### Description rules

The description is the second hook, read in previews and by agents deciding whether to fetch the full TIL. One sentence. It pays off or raises the stakes on what the title left open — the cost, the surprise, the fix — and never restates the title in different words.

### Tag rules

Tags come only from `references/tag-taxonomy.md` — a fixed hierarchy, max three levels (`data/databases/dynamodb`), broad preferred over fine. Read it before tagging; 1–3 tags per TIL; never invent tags outside its rules.

### Body rules

- The three bold labels (**Context**, **The learning**, **Watch out**) are the only structure. No headers beyond the H1, no bullet lists unless the items are genuinely parallel and enumerable.
- **The learning must contain a "because."** A phenomenon alone ("day-old pagination tokens skip rows") is trivia; the mechanism ("because the token is a key snapshot, not a live cursor") is what lets the reader predict adjacent behavior. If you can't state the mechanism, say so in **Watch out** rather than implying you understand it.
- **Name the symptom in the reader's terms.** Many readers arrive mid-problem, searching what they observe — an error message, missing rows, a doubled charge. Describe the observable behavior as they would encounter it, not as your session narrative. Findable beats autobiographical.
- **Generalize exactly one level up, when there's a real one.** After the specific learning, one plain sentence naming the general class it belongs to (e.g. "any pagination token that encodes a position, not a snapshot, has this problem"). This is what makes the TIL useful to readers outside the specific technology. One level only, stated plainly — no strained analogies, no profundity. If the learning doesn't genuinely generalize, skip the sentence.
- Canonical filename, for whenever a TIL is saved or exported: `YYYY-MM-DD-<slug-of-title>.md`.
- Images: allowed but rare — a simple diagram (Mermaid or inline SVG) only when the learning is structural (a flow, a topology, a before/after) and the picture teaches faster than the sentences it replaces. Never decorative images.

## Workflow

0. **Guardrail: flag sensitive material before drafting.** Before harvesting, note what in the session must never reach the TIL: passwords, API keys, tokens, private keys, connection strings, `.env` contents; PHI or any patient/medical detail; SSNs, credit card numbers, dates of birth; customer or employee names and emails; internal hostnames, IPs, account IDs, and non-public URLs. If the learning itself involves one of these (e.g. a debugging session on an auth token), the TIL states the mechanism with placeholders (`<API_KEY>`, `example.com`, `123456789012`) — the real value never appears, even partially.
1. **Get the date and author.** Never assume the date — run `date +%Y-%m-%d` if a shell is available, otherwise take it from session context or ask. Author: `git config user.name` if available, else the user's name from session context, else ask once.
2. **Harvest the session.** Identify the candidate learnings: what surprised you, what was debugged, what turned out to work differently than expected. A summary of activity ("we built X") is not a learning; the learning is the transferable insight ("X's API rejects Y unless Z").
   - If exactly one clear learning: proceed.
   - If several: list them in one line each and ask the user which to write (or "all", as separate TILs).
   - If the user handed you the learning directly (a topic, a pasted snippet), skip harvesting and use that.
3. **Draft to the format.** Hold the core principles while writing — don't draft loose and trim later. Pick the one receipt worth including, or none.
4. **Lint.** Read `references/lint-rules.md` (bundled with this skill) and check the draft against every rule; fix all hits, re-check once, then stop — max 2 passes. Then check the hard constraints: title ≤70 chars, body ≤250 words, one artifact max, all frontmatter fields present.
5. **Guardrail: security sweep before delivery.** Reread the finished TIL — frontmatter, body, and especially the receipt (code blocks and commands are where secrets hide) — against the step-0 list. Check for high-entropy strings, anything shaped like a key or token (`AKIA…`, `sk-…`, `ghp_…`, `eyJ…`), email addresses, 9- and 16-digit numbers, and real hostnames or account IDs. Redact with placeholders, never with partial masking. If you're unsure whether something is sensitive, ask the user before delivering — don't guess in the shareable direction.
6. **Deliver in-session.** This skill produces content, not files. Present the complete TIL — full frontmatter and body — as a Markdown code block in your final message, along with the suggested filename (`YYYY-MM-DD-<slug>.md`). Don't write it to disk, and don't narrate the lint loop or the process.
   - HTML on request: render the same content using `references/html-template.html` — substitute the placeholders, keep the content identical to the Markdown version.
   - If the user then asks to save it somewhere, send it to a connected app (Slack, a wiki, a blog), or publish it, do that with whatever tools the session has — those are follow-ups the user directs, not defaults. If they name a filesystem location, write it there as a one-off.

This skill does not persist or publish on its own. Users route TILs through their own connectors and storage; the standard format is what makes that hand-off trivial.

## Example

```markdown
---
title: Don't save your DynamoDB pagination token for tomorrow
description: Resuming a day-old scan silently skips or repeats rows — here's what bit us and the rule we adopted.
author: John Damask
date: 2026-08-11
tags: [data/databases/dynamodb, cloud/aws]
---

# Don't save your DynamoDB pagination token for tomorrow

**Context.** Our list endpoint stored `LastEvaluatedKey` client-side so users could resume paging later.

**The learning.** Rows went silently missing from resumed listings because a `LastEvaluatedKey` is a snapshot of one item's key, not a live cursor — delete that item and resuming from it skips or repeats rows. We stopped persisting tokens across sessions and capped resume windows at one request cycle. Any pagination token that encodes a position rather than a snapshot has the same problem.

**Watch out.** This bit us on Scan; Query against a stable partition behaves better but we haven't verified it.
```

That's the target: readable in under a minute, one insight, one caveat, nothing wasted.
