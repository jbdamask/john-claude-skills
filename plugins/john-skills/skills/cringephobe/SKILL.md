---
name: cringephobe
description: Writes documents in clear, human-sounding prose that avoids AI slop — the overused words, cringe phrases, structural tells, and bro-speak that fingerprint LLM-generated text. Use this skill whenever the user asks you to write, draft, compose, or put together a document of any kind: a blog post, essay, article, README, email, memo, announcement, newsletter, landing-page or marketing copy, report, proposal, cover letter, or similar prose. Use it by default for these writing tasks, not only when the user mentions sounding human or AI slop — though also use it when they say things like "write this without the AI vibes", "draft something that doesn't sound like ChatGPT", "make it sound human", or "no AI slop".
---

# Cringephobe

Writes a document that avoids AI slop before it ever hits the page. Internalize the rules, draft against them, then run a lint pass before delivering.

The goal is not to write defensively or blandly. It is to write the way a sharp human writer does — specific, varied, substantive — so the slop tells never appear in the first place.

---

## How to use this skill

1. **Get the brief.** Confirm what you're writing, who it's for, and roughly how long. If any of these is missing and it materially changes the draft, ask — once, briefly. Otherwise infer and proceed.
2. **Draft against the writing principles below.** Don't write a generic draft and clean it afterward. Hold the principles in mind while composing so the tells never appear.
3. **Run the lint loop before delivering (mandatory).** A writer rarely catches their own tells, so an external pass is required after drafting. The full procedure is in `## The lint loop` near the end of this file.
4. **Deliver the document only.** Output the finished piece. Do not output the lint reports, the pass count, or commentary about how clean it is. The user asked for a document, not a linter run. If they explicitly ask what you avoided or how many passes it took, then summarize.

---

## Writing principles

While drafting, do these things — don't write violations and catch them later.

### Vocabulary

- **Use plain, specific words.** Never reach for the AI-fingerprint vocabulary: *delve, tapestry, landscape (abstract), realm, underscore (verb), pivotal, robust, leverage, harness, streamline, empower, unlock, innovative, seamless, cutting-edge, game-changer, synergy, underpinnings, nuanced, palpable, camaraderie, intricate, utilize, holistic, transformative, elevate, foster, navigate, unpack.* These words make text statistically read as machine-written. Say the concrete thing instead.
- **Prefer the short Anglo-Saxon word over the Latinate one.** start not commence, end not terminate, help not facilitate, try not endeavor, buy not purchase, show not demonstrate, use not utilize, get not obtain. Fancy words signal effort spent dressing rather than thinking.
- **Cut qualifiers before you write them.** rather, very, quite, somewhat, fairly, kind of, sort of, a bit, slightly. If a claim needs propping up with "very," the claim is weak — sharpen it instead.
- **Don't overstate.** Avoid loose superlatives and absolutes: "the most important," "revolutionary," "completely," "always," "never," "unprecedented." Make the accurate claim and let the reader judge.

### Syntax

- **Write in active voice** unless the actor is unknown, irrelevant, or deliberately hidden. "The team shipped it," not "It was shipped."
- **Say things in the positive.** "She usually ran late," not "She was not very often on time." The positive states the fact; the negative circles it.
- **Cut needless words as you go.** "to" not "in order to," "because" not "due to the fact that," "now" not "at this point in time." Never write "it is important to note that," "the fact that," "as previously mentioned," or redundant pairs like "each and every."
- **Lean on strong nouns and verbs**, not stacks of adjectives and adverbs. "She hurried," not "She walked quickly and nervously."
- **Vary sentence length and rhythm.** Mix long and short. A short sentence lands hardest right after a long one — but only when it carries new meaning, never as filler cadence.
- **Don't stack short punchy fragments** for drama. Combine them so emphasis falls where it should.
- **Make the grammatical subject the thing the sentence is about.** If the sentence is about a method, the method is the subject — not "readers" or "you."
- **Use em dashes only for a genuine aside or clarifying detail** — never as a drum-roll pause before a restatement that adds nothing.
- **Use verbs, not nominalizations.** "decide," not "make a decision." "analyze," not "conduct an analysis."

### Rhetoric

- **Open sentences with the actual claim**, not a transition word. Banned openers: Notably, Importantly, Furthermore, Moreover, Consequently, Additionally, "It's worth noting that," "In today's world," "At its core," "At the end of the day," "The bottom line is," "In conclusion."
- **Never write bro-speak declaratives.** No "Here's the thing," "Here's why that matters," "And that's the point," "Let that sink in," "Think about that for a second," "The secret? X," "The result? X," "Let's dive in," "Let's unpack that," "But here's the kicker." Just make the claim.
- **No mic-drop lines** — a lone dramatic sentence after a paragraph that carries no new information.
- **Don't fake informality** the piece hasn't earned. No conspiratorial "we," no winking asides to a reader you haven't built rapport with.
- **End paragraphs on substance, not summary.** Don't close with "By following these steps, you can cut through the noise." Either add new information or stop.
- **Don't preview or recap.** Don't open a section by describing what you're about to say, and don't close it by restating what you just said. Say it once, in the middle, well.
- **Don't pose a rhetorical question and answer it yourself.** "It affects everything downstream," not "So why does this matter? Because it affects everything downstream."

### Substance

- **Be specific. Name names, cite real sources, use real numbers.** Never lean on "research shows," "some experts say," or "many believe." If you can't substantiate a claim, cut it rather than dress it in vague authority.
- **Every sentence must inform a reader who doesn't already know the answer.** Don't write grammatically fluent sentences that explain nothing — no defining a term with itself, no jargon left unexplained, no describing a process without saying what it does.
- **Anchor every "this," "that," "these," "those" to a clear referent** in the same or immediately preceding sentence. If "this" could point to three things, name the one you mean.

### Formatting

- **Use headers only when the document is long enough to need navigation** or has genuinely distinct sections. A header is not a substitute for a topic sentence. Short pieces usually need none.
- **Default to prose; reserve bullets for genuinely parallel, enumerable items** with no logical flow between them. If the items connect with "because," "therefore," or "which means," write them as prose — reasoning belongs in sentences, not fragments.
- **No emojis** unless the user explicitly wants them or the medium clearly calls for them (e.g., a casual Slack message they've asked to sound casual).

---

## The signal-to-noise rule

Every sentence earns its place. Before delivering, reread and ask of each sentence: if I cut this, is the piece worse? If not, cut it. The length of any passage should be proportional to what it teaches the reader. A paragraph the reader finishes having learned nothing should not exist.

---

## What this skill is NOT

Avoiding slop is not the same as writing flat, hedged, or voiceless prose. Don't overcorrect into:

- **Robotic terseness** — clipping every sentence to the bone until the writing has no rhythm or warmth.
- **Refusing all structure** — parallelism, intentional repetition, a bold declarative opening, and a short emphatic sentence are all good tools. The rules ban them only when they're empty cadence, not when they carry meaning.
- **Genericness** — the deepest AI tell is having no point of view. Write with a specific angle, real examples, and concrete detail. A clean draft with nothing to say still reads as slop.

The target is writing that sounds like a thoughtful, well-read human wrote it on purpose.

---

## The lint loop

The writing principles above cut most slop at the source, but not all of it — mic-drop closers, flat rhythm, and orphaned demonstratives are exactly the tells a writer misses in their own draft. So after drafting, run a real linter pass instead of trusting your own eye.

1. **Invoke the `cringelinter` skill** on the current draft (use the Skill tool). It returns a lint report and a cleaned version.
2. **Apply the fixes** to your draft. Prefer rewriting in your own voice over pasting the cleaned version verbatim — treat it as a reference, not the final answer. Never introduce a new tell while fixing an old one.
3. **Re-lint.** Run the linter again on the revised draft.
4. **Stop when** the report comes back "No issues found," **or** after **4 passes total** — whichever comes first. Four is the ceiling; do not loop forever chasing a perfect score, and don't let successive passes sand the voice out of the piece.
5. If hits remain after 4 passes, fix the remaining ones by hand and deliver. Mention nothing about the loop unless asked.

If the `cringelinter` skill isn't available in the session, fall back to the self-audit checklist below — but the linter is the intended path, because an external pass catches what self-review won't.

---

## Self-audit checklist (fallback only)

Use this only when the `cringelinter` skill isn't available in the session. The lint loop is the intended path. Run through each item — if you'd flag it in someone else's writing, fix it in yours.

- [ ] No AI-fingerprint words (delve, leverage, robust, seamless, tapestry, etc.)
- [ ] No Latinate word where a plain one fits (utilize, facilitate, commence)
- [ ] No weak qualifiers (very, quite, somewhat) or loose superlatives (revolutionary, unprecedented)
- [ ] Active voice unless passive is justified; claims stated in the positive
- [ ] No needless words ("in order to," "the fact that," "it is important to note")
- [ ] Strong nouns/verbs over adjective-adverb stacks; varied sentence length; no stacked fragments
- [ ] Verbs not nominalizations; correct grammatical subject; em dashes only for real asides
- [ ] No banned transition openers (Notably, Furthermore, Moreover, In conclusion)
- [ ] No bro-speak ("Here's the thing," "Let that sink in," "Let's dive in"), no mic-drops, no fake informality
- [ ] No previews, recaps, empty summary closers, or self-answered rhetorical questions
- [ ] Specific over vague; sources named; every sentence informs; demonstratives anchored
- [ ] Headers and bullets only where they earn their place; no stray emojis
- [ ] Has a real point of view — not clean-but-empty

If the draft passes, deliver it. If it doesn't, fix the draft, then deliver. Never deliver the checklist itself.
