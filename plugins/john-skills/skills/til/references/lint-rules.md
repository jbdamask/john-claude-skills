# TIL lint rules

Rules for the pre-delivery lint pass. Extracted from the `cringelinter` skill so this skill is self-contained and agent-agnostic. Apply each rule to the draft TIL; fix every hit, then re-check once. Don't loop more than twice — a sanded-down voice is its own kind of slop.

## 100 — Vocabulary

**101 AI fingerprint words.** Flag every instance of: delve, tapestry, landscape (abstract), realm, underscore (verb), pivotal, robust, leverage, harness, streamline, empower, unlock, innovative, seamless, cutting-edge, game-changer, synergy, underpinnings, nuanced, palpable, camaraderie, intricate, utilize, holistic, transformative, elevate, foster, navigate, unpack. Fix: replace with a plain, specific alternative.

**102 Fancy/Latinate words.** commence→start, terminate→end, facilitate→help, endeavor→try, purchase→buy, demonstrate→show, assistance→help, utilize→use, obtain→get. Fix: use the plain equivalent.

**103 Qualifiers.** rather, very, little, pretty, quite, somewhat, fairly, kind of, sort of, a bit, slightly. Fix: cut; if the claim can't stand without it, reconsider the claim.

**104 Overstatement.** "the most important," "revolutionary," "absolutely," "completely," "totally," "always," "never," "the best ever," "unprecedented." Fix: make the accurate, specific claim or cut.

## 200 — Syntax

**201 Passive voice.** "The results were analyzed by the team" → "The team analyzed the results." Leave passive only when the actor is unknown, irrelevant, or deliberately de-emphasized.

**202 Negative form.** "not without merit" → "has merit"; "not unlike" → "similar to." Fix: state the positive.

**203 Needless words.** "the fact that" (cut), "in order to" → "to", "due to the fact that" → "because", "at this point in time" → "now", "it is important to note that" (cut), "as previously mentioned" (cut), redundant pairs ("each and every," "first and foremost," "various different"), filler openers ("So," "Well," "Basically," "Essentially," when they introduce nothing).

**204 Adjective/adverb overload.** "She walked quickly and nervously" → "She hurried." Fix: stronger nouns and verbs.

**205 Fragmented punchy sentences.** Stacked short declaratives for drama. Fix: combine so emphasis falls where it should.

**206 Flat rhythm.** Every sentence the same length. Fix: vary by restructuring, never by adding filler.

**207 Wrong subject.** The grammatical subject isn't what the sentence is about. Fix: make it so.

**208 Misused em dash.** A dash as a drum-roll pause before a restatement that adds nothing. Fix: cut the clause or restructure. Dashes for a genuine clarifying detail or aside are fine.

**209 Nominalization.** "make a decision" → "decide," "conduct an analysis" → "analyze," "give consideration to" → "consider."

## 300 — Rhetorical patterns

**301 Banned transition openers.** Notably, / Importantly, / Furthermore, / Moreover, / Consequently, / Additionally, / It's worth noting that / In today's world, / At its core, / At the end of the day, / The bottom line is, / In conclusion. Fix: open with the actual claim.

**302 Bro-speak declaratives.** "Here's the thing," "Here's why that matters," "And that's the point," "That's it. That's the whole idea," "This is where it gets interesting," "Let that sink in," "Think about that for a second," "No, really," "Full stop," "That's not a bug. That's a feature," "The secret? X," "The result? X," "Stick with me here," "This might sound obvious, but," "Let's dive in," "Let's unpack that." Fix: cut entirely.

**303 Mic-drop.** A lone dramatic sentence after a paragraph carrying no new information. Fix: cut.

**304 Performative informality.** Breezy asides and conspiratorial "we" the writing hasn't earned. Test: warm from a stranger, or presumptuous? Fix: state it as a direct claim.

**305 Empty summary sentences.** "By following these steps, we achieve better performance." Fix: cut or replace with new information.

**306 Preview/summary structure.** Openings that describe what's about to be said; closings that restate what was said. Fix: say it once, directly.

**307 Self-answered rhetorical questions.** "So why does this matter? Because…" Fix: make the direct statement.

## 400 — Substance

**401 Vagueness and unsupported claims.** "some experts say," "research shows," "many believe"; adjectives without evidence ("powerful, flexible, intuitive"). Fix: name the source or cut. (In a TIL, every fact must trace to the session anyway.)

**402 Fluency without understanding.** Grammatical sentences that explain nothing — defining a term with itself, jargon left unpacked, a process described without saying what it does. Fix: actually explain, or cut.

**403 Orphaned demonstratives.** "this," "that," "these," "those" with no referent in the same or previous sentence. Fix: name the referent.

## 500 — Formatting

**501 Header overuse.** In a TIL this is strict: the H1 is the only structure allowed — the body is plain paragraphs with no headers, section labels, or bold lead-ins.

**502 Bullets where prose would do.** If items could be joined with "because," "therefore," or "which means," write prose. Bullets only for genuinely parallel, enumerable items.

**503 Emojis.** Remove.

## What NOT to flag

Intentional repetition for emphasis; parallel structure; signposting followed by genuine clarification; a bold declarative opening the writing backs up; a short sentence after a long one that carries new meaning; the TIL's own fixed structure.

## Signal-to-noise

Every sentence does work. If cutting a sentence makes the TIL clearer, cut it. The reader should finish each paragraph having learned something — and a TIL has so few paragraphs that a single dead one is a large fraction of the whole.
