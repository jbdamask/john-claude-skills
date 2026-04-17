---
name: cringelinter
description: Lints writing for AI slop tells, including overused words, cringe phrases, structural patterns, and bro-speak declaratives that are fingerprints of LLM-generated text. Use this skill any time the user asks to check, clean, lint, or review writing for AI tells, AI slop, cringe phrases, or generic LLM-sounding language. Also use it when the user says things like "does this sound AI-written?", "make this sound more human", "remove the AI vibes", "de-slop this", or "clean up my draft". If the user shares a piece of writing and expresses any concern about it sounding robotic, generic, or artificial, use this skill.
---

# Cringelinter

Lints a piece of writing for the tells that signal LLM-generated text. Returns a flagged report and a cleaned version.

---

## What to flag

### Banned words
These appear statistically far more often in AI output than in human writing. Flag every instance:

> delve, tapestry, landscape (used abstractly), realm, underscore (as a verb), pivotal, robust, leverage, harness, streamline, empower, unlock, innovative, seamless, cutting-edge, game-changer, synergy, underpinnings, nuanced, palpable, camaraderie, intricate, utilize, holistic, transformative, elevate, foster, navigate, unpack

### Banned transition openers
Flag sentences that open with these:

> Notably, / Importantly, / Furthermore, / Moreover, / Consequently, / Additionally, / It's worth noting that / It is important to note that / In today's world, / At its core, / At the end of the day, / The bottom line is, / In conclusion,

### Cringe bro-speak declaratives
These try to sound like a confident human but carry no information. Flag them and close variants:

> "Here's the thing..." / "Here's why that matters." / "And that's the point." / "That's it. That's the whole idea." / "This is where it gets interesting." / "So what does that mean in practice?" / "Let that sink in." / "Think about that for a second." / "No, really." / "Seriously." / "Full stop." / "That's not a bug. That's a feature." / "The secret? [x]" / "The result? [restatement]" / "Stick with me here." / "Bear with me." / "This might sound obvious, but..." / "Stay with me." / "Let's dive in." / "Let's unpack that."

Also flag the mic-drop: a single short sentence dropped after a paragraph for dramatic effect, carrying no new information.

Also flag performative informality — a breezy, hey-we're-all-friends tone that the writing hasn't earned. Fake casual is as bad as fake formal.

### Empty summary sentences
Flag sentences at the end of a paragraph that sound conclusive but say nothing new: "By following these steps, we achieve better performance." / "By internalizing these principles, you can cut through the noise." These restate the premise as if it were a finding. Cut them or replace with a sentence that adds something.

### Passive voice
Flag passive constructions that could be active. Active voice is more direct. "The results were analyzed by the team" → "The team analyzed the results." Exception: passive is appropriate when the actor is unknown, irrelevant, or deliberately de-emphasized.

### Negative form where positive is stronger
Flag negative formulations when a positive would be more direct: "He was not very often on time" → "He usually came late." "The approach is not without merit" → "The approach has merit." "Not unlike" → "similar to." The positive form says the thing; the negative form circles around it.

### Qualifiers
Flag weak qualifiers that dilute the sentence: *rather, very, little, pretty, quite, somewhat, fairly, kind of, sort of, a bit, slightly.* These are Strunk & White's "leeches that infest the pond of prose." If something is good, say it's good. If it's not good enough to say without qualification, reconsider whether it belongs.

### Adjective and adverb overload
Flag writing that leans on adjectives and adverbs where strong nouns and verbs would do more work. "She walked quickly and nervously" → "She hurried." "A very large number of significant problems" → "Many problems." Nouns and verbs carry meaning; adjectives and adverbs often just pad it.

### Overstatement
Flag superlatives and absolutes used loosely: "the most important," "revolutionary," "absolutely," "completely," "totally," "always," "never," "the best ever," "unprecedented." Overstatement is easy to ignore and erodes trust. Say what is true; let the reader decide if it's impressive.

### Fancy words
Flag Latinate or formal words where a plain equivalent exists. Prefer the short and the Saxon: "commence" → "start," "terminate" → "end," "facilitate" → "help," "endeavor" → "try," "purchase" → "buy," "demonstrate" → "show," "assistance" → "help," "utilize" → "use," "obtain" → "get." Fancy words signal effort spent on dressing rather than substance.

### Needless words
Flag phrases where words can be cut without losing meaning:

- "the fact that" → cut or restructure
- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "it is important to note that" → cut; just say the thing
- "as previously mentioned" → cut
- "The reason for this is that" / "The reasoning is that" → cut; make the claim directly
- Redundant pairs: "each and every," "first and foremost," "various different"
- Filler openers: "So," / "Well," / "Look," / "Basically," / "Essentially," — fine as signposts when followed by genuine clarification; flag when they introduce nothing

### Vagueness and unsupported claims
Flag claims that invoke unnamed authority or avoid specificity: "some experts say," "research shows," "many people believe," "it has been shown that." Name the source or drop the attribution. Also flag adjectives that describe without specifying — "powerful, flexible, intuitive" applied without evidence.

### Orphaned demonstrative pronouns
Flag "this," "that," "these," "those" when the noun they refer to is not in the same sentence or immediately before it. "This creates friction in production" — what is "this"? Name the referent or restructure.

### Fluency without understanding
Flag sentences that are grammatically correct but explain nothing — writing that sounds authoritative while glossing over substance. Defining a term using itself, invoking jargon without unpacking it for the audience, describing a process without saying what it actually does. Read for whether the sentence would inform a reader who doesn't already know the answer.

### Flat sentence rhythm
Flag passages where every sentence is roughly the same length. Monotonous rhythm makes writing harder to follow and signals no sentence is being emphasized over others. Good writing mixes long and short. Flag the monotony; short sentences in isolation are fine.

### Wrong subject
Flag sentences where the grammatical subject doesn't match what the sentence is actually about. "Readers are better guided when the subject matches the main idea" puts readers as the subject when the sentence is about sentence structure. "Choosing the right subject keeps the writing clear" is correct. When subjects drift from the topic, readers lose the thread.

### Structural tells
- Restating what was just said (outro paragraph that summarizes the section above)
- Restating what is about to be said (intro that previews rather than says)
- Bullet-pointing everything instead of writing in prose when prose would do
- Rhetorical questions posed and immediately answered in the next sentence

### Overuse of headers
Flag documents where headers appear between short paragraphs or single-sentence sections. A header is justified when a document is long enough to need navigation, or when sections are genuinely distinct topics. It is not justified as a substitute for a good topic sentence. Headers delineate major sections; paragraphs handle everything else. In the cleaned version, collapse over-headered sections into prose, absorbing the header as a topic sentence or cutting it.

### Simplicity
Flag writing more complex than the content requires: passive constructions that could be active (see above), nominalized verbs ("make a decision" → "decide," "provide a summary" → "summarize"), and jargon where a plain word exists. Einstein's standard: as simple as possible, but no simpler. Do not flag necessary technical terms or complexity that carries real meaning. Flag complexity doing no work.

### Em dashes — use judgment
Do not flag em dashes used to insert a clarifying detail, a quick shift, or a sharp aside. These are legitimate and add rhythm. Flag em dashes used purely as a dramatic pause before a punchline or restatement — where the clause after the dash adds nothing the sentence doesn't already imply.

---

## What NOT to flag

Some patterns get labeled "LLM-like" but are fine when used intentionally:

- **Intentional repetition** — repeating a term for clarity or emphasis is a rhetorical choice, not a flaw
- **Parallel structure** — a repeated grammatical rhythm across clauses is often the clearest way to present related ideas
- **Signposting phrases** ("essentially," "in short," "the point is") — fine when followed by genuine clarification
- **Declarative openings** — starting a section with a bold claim is good when the writing backs it up
- **Short sentences** — a short sentence after a long one creates emphasis; the problem is stacking them for cadence when they add no new information
- **Section headings with clear content** — predictable structure is fine when the substance under each heading delivers

---

## Signal-to-noise principle
Every sentence should do work. If a sentence could be removed and the paragraph would be clearer, cut it. If a clause could be cut and the sentence would be tighter, cut it. The contribution should be commensurate with the length — the reader should finish each paragraph having learned something.

---

## Output format

### 1. Lint report
List every flagged item with:
- The offending text (quoted)
- Which category it falls under
- A one-line suggestion (when a fix is non-obvious)

Group by category. Skip categories with zero hits. If the writing is clean, say "No issues found." and stop.

### 2. Cleaned version
Rewrite the text with all flagged items removed or replaced. Preserve the author's voice and meaning. Do not add content.

Rules for the rewrite:
- Replace banned and fancy words with plain, specific alternatives
- Cut bro-speak declaratives, empty summary sentences, and mic-drops entirely
- Cut banned transition openers and restructure the sentence
- Rewrite passive constructions as active where appropriate
- Rewrite negative formulations in positive form where stronger
- Cut qualifiers and replace adjective/adverb combinations with stronger nouns and verbs
- Rewrite rhetorical Q&A pairs as direct statements
- Cut needless words and redundant phrases
- Name the referent for orphaned demonstrative pronouns
- Do not introduce new AI tells while fixing the old ones

---

## Tone

Be direct. This is a linter, not a book report. The lint report should read like compiler output — specific, terse, actionable. Don't praise the writing or pad the response. If it's clean, say "No issues found." and stop.
