---
name: cringelinter
description: Lints writing for AI slop tells, including overused words, cringe phrases, structural patterns, and bro-speak declaratives that are fingerprints of LLM-generated text. Use this skill any time the user asks to check, clean, lint, or review writing for AI tells, AI slop, cringe phrases, or generic LLM-sounding language. Also use it when the user says things like "does this sound AI-written?", "make this sound more human", "remove the AI vibes", "de-slop this", or "clean up my draft". If the user shares a piece of writing and expresses any concern about it sounding robotic, generic, or artificial, use this skill.
---

# Cringelinter

Lints a piece of writing for the tells that signal LLM-generated text. Returns a flagged report and a cleaned version.

---

## Rules

### 100 — Vocabulary

#### Rule 101: AI Fingerprint Words
These appear statistically far more often in AI output than in human writing. Flag every instance:

> delve, tapestry, landscape (used abstractly), realm, underscore (as a verb), pivotal, robust, leverage, harness, streamline, empower, unlock, innovative, seamless, cutting-edge, game-changer, synergy, underpinnings, nuanced, palpable, camaraderie, intricate, utilize, holistic, transformative, elevate, foster, navigate, unpack

**Fix:** Replace with a plain, specific alternative.

#### Rule 102: Fancy/Latinate Words
Flag Latinate or formal words where a plain equivalent exists:

> "commence" → "start" / "terminate" → "end" / "facilitate" → "help" / "endeavor" → "try" / "purchase" → "buy" / "demonstrate" → "show" / "assistance" → "help" / "utilize" → "use" / "obtain" → "get"

**Fix:** Replace with the plain equivalent. Fancy words signal effort spent on dressing rather than substance.

#### Rule 103: Qualifiers
Flag weak qualifiers that dilute the sentence: *rather, very, little, pretty, quite, somewhat, fairly, kind of, sort of, a bit, slightly.*

**Fix:** Cut the qualifier. If the claim can't stand without it, reconsider whether the claim belongs.

#### Rule 104: Overstatement
Flag superlatives and absolutes used loosely: "the most important," "revolutionary," "absolutely," "completely," "totally," "always," "never," "the best ever," "unprecedented."

**Fix:** Replace with an accurate, specific claim, or cut. Let the reader decide if it's impressive.

---

### 200 — Syntax

#### Rule 201: Passive Voice
Flag passive constructions that could be active. "The results were analyzed by the team" → "The team analyzed the results."

**Fix:** Rewrite as active. Exception: leave passive when the actor is unknown, irrelevant, or deliberately de-emphasized.

#### Rule 202: Negative Form
Flag negative formulations when a positive would be more direct. "He was not very often on time" → "He usually came late." "The approach is not without merit" → "The approach has merit." "Not unlike" → "similar to."

**Fix:** Rewrite in positive form. The positive says the thing; the negative circles around it.

#### Rule 203: Needless Words
Flag phrases where words can be cut without losing meaning:

- "the fact that" → cut or restructure
- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "it is important to note that" → cut; just say the thing
- "as previously mentioned" → cut
- "The reason for this is that" / "The reasoning is that" → cut; make the claim directly
- Redundant pairs: "each and every," "first and foremost," "various different"
- Filler openers: "So," / "Well," / "Look," / "Basically," / "Essentially," — flag when they introduce nothing

**Fix:** Cut or restructure as shown above.

#### Rule 204: Adjective and Adverb Overload
Flag writing that leans on adjectives and adverbs where strong nouns and verbs would do more work. "She walked quickly and nervously" → "She hurried." "A very large number of significant problems" → "Many problems."

**Fix:** Replace adjective/adverb combinations with stronger nouns and verbs.

#### Rule 205: Fragmented Punchy Sentences
Flag stacked short declarative sentences. "These are not bad words. They are fingerprints."

**Fix:** Combine using End-Focus (Joseph Williams). "These aren't bad words so much as fingerprints."

#### Rule 206: Flat Sentence Rhythm
Flag passages where every sentence is roughly the same length. Monotonous rhythm signals no sentence is being emphasized over others.

**Fix:** Vary sentence length. Do not add filler — restructure or combine to create contrast.

#### Rule 207: Wrong Subject
Flag sentences where the grammatical subject doesn't match what the sentence is actually about. "Readers are better guided when the subject matches the main idea" is about sentence structure, not readers.

**Fix:** Rewrite so the grammatical subject is the thing the sentence is actually about. "Choosing the right subject keeps the writing clear."

#### Rule 208: Misused Em Dash
Flag em dashes used purely as a dramatic pause before a punchline or restatement — where the clause after the dash adds nothing the sentence doesn't already imply.

**Fix:** Cut the clause after the dash, or restructure the sentence to remove the pause entirely. Do not flag em dashes used to insert a clarifying detail or sharp aside.

#### Rule 209: Nominalization
Flag nominalized verbs where the verb form is stronger: "make a decision" → "decide," "provide a summary" → "summarize," "conduct an analysis" → "analyze," "give consideration to" → "consider."

**Fix:** Replace with the verb form. Nominalizations bury the action; verbs surface it.

---

### 300 — Rhetorical Patterns

#### Rule 301: Banned Transition Openers
Flag sentences that open with:

> Notably, / Importantly, / Furthermore, / Moreover, / Consequently, / Additionally, / It's worth noting that / It is important to note that / In today's world, / At its core, / At the end of the day, / The bottom line is, / In conclusion,

**Fix:** Cut the opener and restructure the sentence to open with the actual claim.

#### Rule 302: Bro-Speak Declaratives
Flag these and close variants:

> "Here's the thing..." / "Here's why that matters." / "And that's the point." / "That's it. That's the whole idea." / "This is where it gets interesting." / "So what does that mean in practice?" / "Let that sink in." / "Think about that for a second." / "No, really." / "Seriously." / "Full stop." / "That's not a bug. That's a feature." / "The secret? [x]" / "The result? [restatement]" / "Stick with me here." / "Bear with me." / "This might sound obvious, but..." / "Stay with me." / "Let's dive in." / "Let's unpack that."

**Fix:** Cut entirely.

#### Rule 303: Mic-Drop
Flag a single short sentence dropped after a paragraph for dramatic effect, carrying no new information.

**Fix:** Cut entirely.

#### Rule 304: Performative Informality
Flag a breezy, hey-we're-all-friends tone the writing hasn't earned. Signs: unsolicited asides to the reader, rhetorical winks, conspiratorial "we." The test: would this register as warm from a stranger, or presumptuous?

**Fix:** Rewrite in a register the content has earned. Remove the aside or restate it as a direct claim.

#### Rule 305: Empty Summary Sentences
Flag sentences at the end of a paragraph that sound conclusive but say nothing new: "By following these steps, we achieve better performance." / "By internalizing these principles, you can cut through the noise."

**Fix:** Cut, or replace with a sentence that adds new information.

#### Rule 306: Preview/Summary Structure
Flag two related structural tells:
- **Outro summaries**: a closing paragraph that restates what the section just said
- **Intro previews**: an opening that describes what is about to be said instead of saying it

**Fix:** Cut the outro or preview. Say the thing directly.

#### Rule 307: Rhetorical Questions
Flag rhetorical questions posed and immediately answered in the next sentence. "So why does this matter? Because it affects everything downstream."

**Fix:** Rewrite as a direct statement. "It affects everything downstream."

---

### 400 — Substance

#### Rule 401: Vagueness and Unsupported Claims
Flag claims that invoke unnamed authority or avoid specificity: "some experts say," "research shows," "many people believe," "it has been shown that." Also flag adjectives that describe without specifying — "powerful, flexible, intuitive" applied without evidence.

**Fix:** Name the source or drop the attribution. Replace vague adjectives with specific evidence or cut them.

#### Rule 402: Fluency Without Understanding
Flag sentences that are grammatically correct but explain nothing — writing that sounds authoritative while glossing over substance. Signs: defining a term using itself, invoking jargon without unpacking it, describing a process without saying what it actually does.

**Fix:** Rewrite to actually explain, or cut if the content can't be substantiated. Read for whether the sentence would inform a reader who doesn't already know the answer.

#### Rule 403: Orphaned Demonstrative Pronouns
Flag "this," "that," "these," "those" when the noun they refer to is not in the same sentence or immediately before it. "This creates friction in production" — what is "this"?

**Fix:** Name the referent explicitly, or restructure the sentence.

---

### 500 — Formatting

#### Rule 501: Overuse of Headers
Flag documents where headers appear between short paragraphs or single-sentence sections. A header is justified when a document is long enough to need navigation, or when sections are genuinely distinct topics. It is not justified as a substitute for a good topic sentence.

**Fix:** Collapse over-headered sections into prose. Absorb the header as a topic sentence or cut it.

#### Rule 502: Bullet-Pointing Where Prose Would Do
Flag lists used where continuous prose would read better. Bullets fragment reasoning; prose connects it. If the bullets could be joined with "because," "therefore," or "which means," they belong in prose.

**Fix:** Rewrite as prose. Reserve lists for genuinely enumerable, parallel items with no logical flow between them.

#### Rule 503: Emojis
Flag emojis.

**Fix:** Remove.

---

## What NOT to Flag

Some patterns get labeled "LLM-like" but are fine when used intentionally:

- **Intentional repetition** — repeating a term for clarity or emphasis is a rhetorical choice, not a flaw
- **Parallel structure** — a repeated grammatical rhythm across clauses is often the clearest way to present related ideas
- **Signposting phrases** ("essentially," "in short," "the point is") — fine when followed by genuine clarification
- **Declarative openings** — starting a section with a bold claim is good when the writing backs it up
- **Short sentences** — a short sentence after a long one creates emphasis; the problem is stacking them for cadence when they add no new information
- **Section headings with clear content** — predictable structure is fine when the substance under each heading delivers

---

## Signal-to-Noise Principle
Every sentence should do work. If a sentence could be removed and the paragraph would be clearer, cut it. If a clause could be cut and the sentence would be tighter, cut it. The contribution should be commensurate with the length — the reader should finish each paragraph having learned something.

---

## Output Format

### 1. Lint Report
For each rule with hits, output a jsonl object that includes:
- The rule number and name (e.g., **Rule 302: Bro-Speak Declaratives**)
- The offending text (quoted)
- The fix applied or suggested

Group by rule number. Skip rules with zero hits. If the writing is clean across all rules, output "No issues found." and stop.

### 2. Cleaned Version
Rewrite the text with every flagged item resolved per its rule's **Fix** instruction. Preserve the author's voice and meaning. Do not add content. Do not introduce new AI tells while fixing the old ones.

---

## Tone
Be direct. This is a linter, not a book report. The lint report should read like compiler output — specific, terse, actionable. Don't praise the writing or pad the response.
