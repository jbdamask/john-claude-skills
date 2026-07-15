---
name: sefam
description: Produces a concise, plain-language write-up of a technical subject that a smart but non-technical reader (like a manager) can fully understand — no jargon, but not dumbed down — and delivers it as a great-looking styled web page (an Artifact) by default, or as plain markdown if the user prefers. SEFAM means "Simple Enough For A Manager". Works on either a technical CHANGE (a PR, diff, commit, bug fix, GitHub issue) or a technical CONCEPT in a repo (a function, a process/workflow, an architecture, a system, a service, a design decision). Use when the user says "sefam", "SEFAM", "explain it like I'm not an engineer", or asks to explain how some function/process/architecture/system works for a non-technical audience.
---

# SEFAM — Simple Enough For A Manager

Your job: take a technical subject and produce a short, plain-language write-up that a smart but NON-technical reader (e.g. a manager) can fully understand, and deliver it as a great-looking styled web page. No jargon, but never dumbed down. Respect the reader's intelligence.

**Before anything else, ask the user which format they want (step 0).** The default and preferred deliverable is a styled web page (an Artifact) — but the user may choose plain markdown instead, so ask first and honor the answer. When it's a web page, do all the thinking and drafting below, then publish the finished write-up as a styled HTML page using one of the visual styles in step 8. Everything about the *content* — plain language, no jargon, no invented facts — applies exactly the same either way; the page is how it's presented, not an excuse to pad it.

The subject can be either:
- **A change** — a PR, diff, commit, bug fix, or issue (something that happened or is being done).
- **A concept** — a function, a process or workflow, an architecture, a system, a service, or a design decision (how something works or why it's built the way it is).

The method below covers both. Figure out which kind you're dealing with, then use the matching structure in step 4.

## Method

Follow these steps every time.

### 0. Ask which format — do this FIRST, every time
Before reading anything or drafting, ask the user how they want the result delivered. This step is not optional and is not overridden by anything else in this skill: even though a web page is the preferred default, you must still ask. Two things to settle:

1. **Web page or plain markdown?** If they want a web page, tell them the style options (the catalog in step 8) so they can pick one or let you choose. If they want markdown, skip step 8 and output the write-up as markdown.
2. **If a web page: local HTML file, or a shareable Claude Artifact?** A *local HTML file* is written to disk (their machine) and stays private — nothing is published. A *shareable Claude Artifact* is published to claude.ai and gets a URL they can send to others. Default to the shareable Artifact unless they choose the file.

Do not start step 1 until you have the answers.

### 1. Get the facts first — never hand-wave
Identify exactly what you're explaining, and READ IT before writing. Match the source to the subject:

For a **change**:
- A PR: `gh pr view <n>` (and `gh pr diff <n>` for the changes)
- An issue: `gh issue view <n>`
- A commit or diff: `git show <sha>` / `git diff`

For a **concept**:
- A function or code path: read the file(s) directly; trace what calls it and what it calls.
- A process or workflow: follow it end-to-end through the code — entry point, steps, outputs.
- An architecture or system: read the design docs / README / ADRs first, then confirm against the code. For a broad or unfamiliar codebase, use an Explore agent to map it before writing.

If the user did NOT point you at anything specific, ask them what to explain. Do not guess.

**Only state facts you can trace to the source.** Every specific claim — a number, a dollar amount, a timeframe, how long something took to build, how often something happens, how many users are affected — must come from the material you read (the diff, the code, the docs, the issue) or from something the user told you. Do NOT invent them to make the write-up more concrete or more compelling. If you don't know how long a feature took to build, don't say "a few days." If you don't know the cost, don't name one. A plausible-sounding fabricated detail is worse than a missing one — it destroys the reader's trust the moment they catch it. When a detail would strengthen the explanation but you don't have it, either leave it out or say plainly what you don't know (e.g. "the exact cost isn't recorded here"). Analogies are fine and expected; invented facts are not — keep the two clearly distinct.

### 2. Write for a smart non-technical reader
- Everyday language and analogies. Zero unexplained jargon.
- Translate EVERY technical term into its plain-language meaning. Never leave in things like "SQS", "Lambda", "DLQ", "max_tokens", "visibility timeout", "race condition", "idempotency", "cache", "API", "webhook", "retry with backoff" — say what they mean for people, money, or the product instead.
- Be concise. Don't be condescending. The reader is smart; they just aren't an engineer.

### 3. Lead with impact or purpose, not implementation
- For a **change**: open with what it means in human/business terms — money, time, user experience, risk.
- For a **concept**: open with what it's *for* — the job it does and why it matters to the business or user.

The technical "how" is secondary and mostly gets translated away.

### 4. Use the structure that fits (adapt; drop sections that don't apply)

**For a change:**
- **What broke / What this is** — the situation in one short paragraph.
- **Why** — the underlying cause, with an analogy if it helps.
- **What this fixes / does** — a short numbered list, each item a plain outcome.
- **Bottom line** — one or two sentences on what changes for users or the business.
- **Honest caveat** — any real limitation, flagged plainly. This builds trust; never oversell.

**For a concept:**
- **What it is** — a one-paragraph plain-language definition. Lead with the job it does.
- **Why it matters** — what the business or user gets from it; what would happen without it.
- **How it works** — the key steps or pieces, as a short numbered list, each in plain terms. Use an analogy for the whole thing where it helps.
- **Bottom line** — one or two sentences a manager could repeat to someone else.
- **Honest caveat** — any real limitation, trade-off, or known weak spot. Never oversell.

### 5. Write like a sharp human, not a language model
Plain language is not the same as slop. As you draft, avoid the tells that fingerprint machine-written text — a manager can smell them, and they cost you credibility. Hold these in mind while composing, don't clean them up afterward:

**Words**
- Never reach for AI-fingerprint vocabulary: *delve, tapestry, landscape (abstract), realm, underscore (verb), pivotal, robust, leverage, harness, streamline, empower, unlock, seamless, cutting-edge, game-changer, holistic, transformative, elevate, foster, navigate (abstract), unpack.* Say the concrete thing instead.
- Prefer the short plain word over the fancy one: start not commence, use not utilize, help not facilitate, show not demonstrate, get not obtain, enough not sufficient.
- Cut weak qualifiers (very, quite, somewhat, fairly, a bit) and loose superlatives/absolutes (revolutionary, unprecedented, completely, always, never). Make the accurate claim and let the reader judge.

**Sentences**
- Active voice: "the system rewrites the page," not "the page is rewritten."
- State things in the positive: "it usually finishes," not "it doesn't often fail."
- Cut needless words as you go: "to" not "in order to," "because" not "due to the fact that." Never write "it is important to note that" or "the fact that."
- Use verbs, not nominalizations: "decide," not "make a decision."
- Vary sentence length and rhythm. A short sentence lands hardest after a long one — but only when it carries new meaning, never as filler cadence. Don't stack short fragments for drama.
- Use em dashes only for a genuine aside, never as a drum-roll before a restatement.

**Rhetoric**
- Open each sentence with the actual claim, not a transition. Banned openers: Notably, Importantly, Furthermore, Moreover, Consequently, Additionally, "It's worth noting that," "At its core," "At the end of the day," "The bottom line is" (as a filler phrase, not the labeled section).
- No bro-speak declaratives: "Here's the thing," "Here's why that matters," "Let that sink in," "Think about that for a second," "The result? X," "Let's unpack that," "But here's the kicker." Just make the claim.
- No mic-drop lines — a lone dramatic sentence that adds no new information.
- Don't preview or recap. Don't open a section by saying what you're about to say, or close it by restating what you just said. Say it once, well.
- Don't pose a rhetorical question and answer it yourself. "It quietly ran up the bill," not "So why does this matter? Because it ran up the bill."
- End on substance, not a summary flourish like "By understanding this, you can see why it matters."

**Substance**
- Be specific: name real numbers, real components, real outcomes — but only ones you can trace to the source (see step 1). Being specific is not license to invent. Never manufacture a number, cost, timeframe, or effort estimate to sound concrete, and never lean on "research shows" or vague authority.
- Anchor every "this / that / these" to a clear referent. If "this" could point to three things, name the one you mean.
- Every sentence must inform a reader who doesn't already know the answer. A grammatically fluent sentence that teaches nothing is still slop.

This is not license to write flat, hedged, or voiceless prose. The target is writing that sounds like a thoughtful human wrote it on purpose — specific, varied, with a clear point of view.

### 6. Keep it tight
Aim for something readable in under a minute. Short paragraphs and a small numbered list beat walls of text. Every sentence earns its place: if cutting it doesn't make the write-up worse, cut it.

### 7. Optional technical footer
You may add a single line at the end pointing engineers to the PR/issue/commit/file — clearly separated from the plain-language part (e.g. "For engineers: see PR #123" or "For engineers: see `src/merge/worker.py`"). Keep the main body jargon-free regardless. On the page, render this as small, muted text in a footer, visually set apart from the body.

### 8. Build it as a styled web page (when the user chose a web page in step 0)
If the user asked for markdown in step 0, skip this step and deliver the write-up as markdown. Otherwise, once the write-up is right, publish it as a self-contained HTML Artifact. The content rules above are non-negotiable; the styling makes it something a manager is glad to open.

**Pick a style that fits, then say so.** Choose the one visual style from the catalog below that best suits the subject and tone, and tell the user which you picked and why in one short line (e.g. "Rendered in *Academic Scholar* — it suits a careful architecture explainer"). The user can name a different style and you re-render. Rough fit guide: serious/architectural → Academic Scholar or Earth Tones; bold announcement or exec summary → Vintage Travel Poster; blunt technical honesty → Neo-brutalist; modern product/UI → Glassmorphism; warm or human-scale → Miyazaki Sketchbook; celebratory/high-energy/internal-fun → sefam (the signature style). When nothing stands out, default to **Academic Scholar** — it's the safe, credible choice for a manager audience.

**Once you've picked a style, read its prompt file in `references/` and follow it when building the page.** Each style has a self-contained build prompt (palette, type, treatment) in its own file:

| Style | Feel | Prompt file |
|---|---|---|
| **Academic Scholar** | Scholarly serif on parchment + charcoal | `references/academic-scholar.md` |
| **Neo-brutalist** | Raw, nostalgic, intentionally disruptive | `references/neo-brutalist.md` |
| **Earth Tones** | Warm linen + amber editorial | `references/earth-tones.md` |
| **Vintage Travel Poster** | WPA-era flat lithography | `references/vintage-travel-poster.md` |
| **Miyazaki Sketchbook** | Hayao Miyazaki storyboard | `references/miyazaki-sketchbook.md` |
| **Glassmorphism** | Apple-inspired translucent depth | `references/glassmorphism.md` |
| **sefam** (signature) | Maximalist joyful anime/manga poster | `references/sefam.md` |

**How to build it:**
1. Load the `artifact-design` skill first (it applies to both delivery modes), read the chosen style's prompt file in `references/`, then write the page to an HTML file. Put the file in the scratchpad directory unless the user names a location. Then deliver it per the choice from step 0:
   - **Shareable Claude Artifact** (default): publish the file with the Artifact tool to get a claude.ai URL.
   - **Local HTML file**: leave it as a file on disk and give the user the path — do NOT publish it with the Artifact tool, since that would put it on claude.ai. The same self-contained, CSP-safe build rules below still apply so the file opens correctly in a browser.
2. One `<h1>` for the subject, then the SEFAM sections as headed blocks (What broke/What it is, Why, What this fixes/How it works, Bottom line, Honest caveat). The numbered list stays a real `<ol>`. Keep it to one screen or a short scroll — the under-a-minute read still holds; a page is not license to inflate.
3. Fully self-contained: inline all CSS, embed any texture/pattern as CSS or a data URI, no external fonts/scripts/images (the Artifact CSP blocks them). Use a common web-safe or system font stack that evokes the style rather than loading a webfont.
4. Responsive and legible: real body-text size (~1.1rem), comfortable line length (~60–70ch), enough contrast to read. A distinctive style must not cost readability — a manager has to be able to actually read it.
5. Set a stable `<title>`, pass a one-line `description`, and a fitting `favicon` emoji. Don't change the favicon on re-renders of the same write-up.

The style prompts in `references/` are opinionated single-look designs — commit to one; most are deliberately light- or dark-only, so don't force theme-switching. When the user asks for a style not listed, build a tasteful interpretation of what they asked for rather than refusing — the catalog is a starting set, not a hard limit.

## Reference examples (the target quality/voice)

These are the gold standard for tone, structure, and level of translation — they model the *content* that goes onto the page. Match them, then render that content in the chosen style (step 8).

### Example A — explaining a change (a bug fix)

---
**What broke:** When you approve a batch of edits to a wiki, the system applies them one at a time in the background. A couple of weeks ago, someone approved 8 edits to a large vault. Five went through; three got stuck spinning forever, showing "merging…" and never finishing — while quietly running up an AI bill trying and failing over and over.

**Why:** The pages were big. To apply an edit, the system rewrites the whole page using AI. On a large page that rewrite took longer than the system's built-in time limit for a single task, so it got cut off mid-rewrite, gave up, and started over from scratch — endlessly. It never gave up cleanly, so it never told anyone it had failed.

**What this fixes (five things):**
1. The rewrites no longer get cut off on large pages — they now have enough room and time to finish.
2. When something does fail for good, it now says so. Before, a permanently-failed edit sat there looking like it was still working. Now it clearly shows "merge failed" instead of a forever spinner.
3. A stuck job can no longer retry forever and burn money — after a few honest attempts it stops and is flagged.
4. A safety cushion so the system doesn't accidentally start processing the same page twice at once.
5. A recovery fix so that when an operator manually retries a failed job, it actually succeeds instead of failing again immediately.

**Bottom line:** Approving edits on big vaults won't silently hang or quietly waste money anymore — it either finishes, or it fails loudly so someone can act.

**One honest caveat:** there's a rarer, deeper version of the "rewrite takes too long" problem I've only reduced, not eliminated. Fully solving it safely needs a measurement in the test environment first.
---

### Example B — explaining a concept (an architecture)

---
**What it is:** The system is split into two halves that talk to each other through a "waiting line." The front half takes requests from users and drops each one into the line the moment it arrives. The back half pulls jobs off that line one at a time and does the slow work — generating reports. The two halves never wait on each other.

**Why it matters:** Users get an instant "we've got it" instead of staring at a spinner while a report is built. And if a flood of requests comes in at once, nothing crashes — they just queue up and get worked through steadily. It's the difference between a restaurant that seats everyone and takes their order right away versus one where the line out the door gives up and leaves.

**How it works:**
1. A request comes in and is immediately written down in the waiting line, so it can never be lost — even if something crashes a second later.
2. Workers in the back pick up jobs when they're free. Add more workers and the line clears faster; that's the main dial we turn when things get busy.
3. If a job fails, it goes back in line and is retried a few times before it's set aside and flagged for a human — it doesn't just vanish.

**Bottom line:** The design trades a few seconds of "your report is being prepared" for a system that stays fast and doesn't fall over under load.

**One honest caveat:** because the work happens in the background, a report isn't ready the instant someone asks for it. For very time-sensitive requests, that short delay is a real trade-off we chose on purpose.
---

## Anti-patterns to avoid
- Leaving in acronyms or jargon (SQS, DLQ, max_tokens, race condition, API, webhook, etc.) instead of translating them.
- Burying the impact or purpose under implementation detail — lead with what it means or what it's for.
- Being condescending — the reader is smart, just not an engineer.
- Overselling by hiding limitations or trade-offs — always include the honest caveat.
- Inventing facts to sound concrete — a made-up development time ("the team spent a few days"), cost, user count, or frequency that isn't in the source. If you can't trace it to the material or the user, leave it out or say you don't know. Fabrication is the fastest way to lose the reader's trust.
- Explaining a concept as a pile of parts with no throughline — give it one clear job and, where it helps, one analogy.
- AI-slop tells: fingerprint words (delve, leverage, robust, seamless, streamline), bro-speak openers ("Here's the thing," "Let's unpack that"), mic-drop closers, self-answered rhetorical questions, and empty summary flourishes. Write like a sharp human, not a language model.
- Going long — if it takes more than a minute to read, cut it. A styled page is not permission to inflate the word count.
- Letting the style hurt the reading: tiny text, poor contrast, or decoration that fights the words. The manager has to be able to read it comfortably.
- Half-committing to a style — muddled visuals that don't clearly read as any one look. Pick one from the catalog and commit.
- Loading external fonts, scripts, or images — the Artifact CSP blocks them and the page breaks. Everything inline or as a data URI.
