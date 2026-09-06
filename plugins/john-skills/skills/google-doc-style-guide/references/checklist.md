# Review checklist

Run this pass before delivering a document, and use it as the finding taxonomy when the
user asks for a style review.

Work top to bottom — the sections are ordered by reader impact. When reviewing someone
else's doc, report findings in that order too, with file and line, quoting the offending
text and giving the replacement.

---

## 1. Audience and purpose

- [ ] The document has one clear purpose, and the title states it.
- [ ] It's obvious who *you* refers to, and it's the same person throughout.
- [ ] The document is prescriptive: it recommends a path rather than listing every
      option. Where several approaches exist, it gives the best one.
- [ ] Terminology matches the surrounding documentation set and any project style guide.

## 2. Accuracy and claims

- [ ] No superlatives (*best*, *fastest*, *simplest*, *never*, *always*) and no
      unverifiable performance or cost claims.
- [ ] No claim that something *is* secure, *ensures*, or *guarantees* an outcome.
- [ ] No future features, roadmap hints, or pre-announcements.
- [ ] No content copied from a third party. Paraphrased and linked instead.
- [ ] No real domains, emails, names, phone numbers, IPs, addresses, or other PII —
      including inside screenshots.

## 3. Voice, tone, and grammar

- [ ] Second person. *You*, not *we* or *the user* (unless *user* means the reader's own
      end user).
- [ ] Active voice, with the actor clear.
- [ ] Present tense. No hypothetical *would*.
- [ ] *must* / *can* / *might* used precisely; *should* avoided except for widely
      recognized recommendations.
- [ ] No *please*, *simply*, *easy*, *just*, *quickly*, *let's*.
- [ ] No exclamation points (outside the narrow exceptions).
- [ ] No anthropomorphism — software doesn't see, tell, want, or think.
- [ ] Jargon written around, replaced, or defined on first use.
- [ ] No figurative language, idioms, humor, pop-culture references, or culturally
      specific references.
- [ ] Contractions used naturally, especially negations (*don't*, *isn't*, *can't*).

## 4. Timelessness

- [ ] None of: *as of this writing, currently, does not yet, eventually, existing,
      future, latest, new, newer, now, old, older, presently, at present, soon* — unless
      this is a release note, changelog, or blog post.
- [ ] Where *new* or *latest* is unavoidable, a version number or date anchors it.

## 5. Structure

- [ ] Sentence case in every heading and title; no trailing periods.
- [ ] Task headings start with a base-form verb; concept headings are noun phrases; no
      heading starts with an `-ing` verb.
- [ ] One `h1`. No skipped heading levels. No empty headings. No links, sequence numbers,
      or bare code items in headings.
- [ ] Optional sections and steps use an `Optional:` prefix, not `(optional)`.
- [ ] Condition, circumstance, or goal comes before the instruction.
- [ ] Most important information first, in each paragraph and each sentence.
- [ ] Paragraphs are short and single-idea; sentences are under about 26 words.
- [ ] Lists, tables, and code samples are introduced by a complete sentence — colon if
      adjacent, period if something intervenes.
- [ ] List items are parallel, consistently capitalized, and consistently punctuated.
- [ ] No one-item lists. No `etc.` or *and so on* at the end of a list.
- [ ] Procedures: one action per step, imperative verb first, location before action,
      goal before action, single-step procedures as a bullet.
- [ ] Notices are few, never stacked, and are the right severity. Nothing essential lives
      in a note.

## 6. Links

- [ ] Link text is a page title or a descriptive phrase, meaningful out of context.
      Never *click here*, *this document*, or a bare URL.
- [ ] Standalone cross-references use "For more information, see X." or "For more
      information about Y, see X." — *about*, not *on*.
- [ ] Abbreviations and code-element descriptors are inside the link text.
- [ ] Downloads, mailto links, same-page jumps, and new tabs are called out.
- [ ] Punctuation sits outside the link. No quotation marks around linked text.
- [ ] No duplicate links to the same destination on the page.

## 7. Formatting

- [ ] Bold for UI elements and run-in headings only.
- [ ] Italics used sparingly: new terms, words as words, full-length work titles,
      variables.
- [ ] Code font on everything code-adjacent: filenames, paths, commands, flags, class
      and method names, env vars, ports, HTTP status codes, placeholders, literal input.
- [ ] Product names, org names, domain names, and browser-facing URLs are *not* in code
      font.
- [ ] No code element inflected, pluralized, or made possessive — a noun follows it
      instead.
- [ ] Placeholders are `UPPERCASE_WITH_UNDERSCORES`, with no `MY_`/`YOUR_`, and every
      one is explained on first use.
- [ ] Copyable commands contain no `[]`, `{}`, `|`, or `...` notation.
- [ ] Code blocks wrap at 80 characters; omissions are marked with a language-appropriate
      comment, not an ellipsis.
- [ ] Output is introduced with "The output is similar to the following:".

## 8. Mechanics

- [ ] Serial commas throughout.
- [ ] Sentence case in list items, table cells, headings, captions, and figure text.
- [ ] Numbers: words for zero-nine, numerals for 10+ and for versions, measurements,
      percentages, prices, and decimals. Digit separators in numbers of four or more
      digits.
- [ ] Dates spelled out ("January 19, 2017") or ISO `YYYY-MM-DD`. No slashes, no seasons.
- [ ] Nonbreaking space between number and unit; no space for `%`, currency, and degrees
      of angle.
- [ ] Abbreviations spelled out on first use, italicized, with the long form capitalized
      only if it's a proper noun. No *i.e.*, *e.g.*, *tl;dr*. No abbreviation used as a
      verb.
- [ ] Em dashes, not en dashes, and no spaces around them.
- [ ] Straight quotation marks and apostrophes. Commas and periods inside — outside only
      around a literal string.
- [ ] Semicolons, ellipses, and slashes avoided. No *and/or*.
- [ ] Hyphenation follows the prefix, compound-noun, and compound-modifier rules; no
      hyphen after an `-ly` adverb.
- [ ] No `'s` plurals, no `(s)` optional plurals, no possessives of product names,
      trademarks, or code items.
- [ ] File types named formally ("a PNG file"), filenames lowercase-with-hyphens.

## 9. Accessibility

- [ ] Every image has an `alt` attribute — descriptive, or empty if decorative.
      Under 155 characters, no "Image of."
- [ ] No information exists only in an image, and no images of text, code, or terminal
      output.
- [ ] No directional language: *above*, *below*, *left-hand side*, *higher*, *lower*.
      Uses *preceding*, *following*, *earlier*, *later* instead.
- [ ] Controls are referred to by label, never by appearance ("Click **Save**", not
      "click the disk icon").
- [ ] Color, size, and position aren't the only carriers of meaning.
- [ ] Tables are introduced in the preceding text, use real `th` headers, and have no
      merged cells.
- [ ] Menu-path angle brackets carry an `aria-label="and then"`.
- [ ] Heading hierarchy is real markup, not visual styling.

## 10. Inclusion

- [ ] No ableist language: *sanity check*, *crazy*, *insane*, *cripples*, *blind to*,
      *dumb*, *lame*, *hangs*, *dummy variable*.
- [ ] No non-inclusive terms: *blacklist*/*whitelist*, *master*/*slave*, *man-hours*,
      *manned*, *grandfathered*, *first-class citizen*, *brown bag*, *war room*,
      *guru*/*ninja*/*sherpa*, *native* (of people).
- [ ] Where such a term is baked into code, it appears once in code font in parentheses,
      and the inclusive term is used thereafter.
- [ ] Gender-neutral throughout; singular *they*; no *he/she* or *(s)he*.
- [ ] Example names are diverse; personas don't reinforce role stereotypes.
- [ ] Disability described with care — no *normal*/*healthy* for nondisabled people, no
      *suffers from*, no *wheelchair-bound*.

## 11. Global readership

- [ ] Simple words: *use* not *utilize*/*leverage*, *start* not *commence*, *to* not *in
      order to*.
- [ ] Helper words kept: *then*, *that*, *of*, *and then*, and relative pronouns.
- [ ] No more than two nouns modifying another noun.
- [ ] *only* placed immediately before what it modifies.
- [ ] Words used in their primary sense: *after* not *once*, *because* not *since* or
      *as*, *although* not *while*.
- [ ] Articles included, even in headings.
- [ ] The same concept is called the same thing, with the same capitalization,
      everywhere.

## 12. READMEs only

Skip this section for any other document type. Full guidance in `readme.md`.

- [ ] Title, one-line description, then at most four sentences of context — the quick
      start is above the fold.
- [ ] Badges, if any, are on one line, limited to ones a reader acts on, and each has
      `alt` text.
- [ ] Quick start comes before installation, configuration, usage, and everything else.
- [ ] Prerequisites are checkable versions ("Node.js 20 or later"), stated immediately
      before the first command, with the command that checks them.
- [ ] **Every command runs exactly as written** — verified against the actual CLI,
      scripts, entry points, and registry, not written from memory.
- [ ] No command requires editing before it can be pasted. Unavoidable values use the
      documented placeholder format and are explained right after the block.
- [ ] Versions are pinned where a floating tag would drift.
- [ ] The quick start ends with a verification step and its real output, introduced with
      "The output is similar to the following:".
- [ ] No concepts, architecture, or rationale in the quick start — linked instead.
- [ ] Installation covers every supported path, says what each is for, and gives the
      verify and uninstall commands.
- [ ] Platform and version support is a table, not prose.
- [ ] Configuration gives a minimum working config first, then an option table with
      name, type, default, and description.
- [ ] **Every default was read out of the code**, not assumed or carried over.
- [ ] Precedence order is stated when settings come from more than one source.
- [ ] No real secrets, tokens, keys, or hostnames. Each says where the value comes from
      and where it should live.
- [ ] Cut and linked instead: philosophy, roadmap, exhaustive feature lists, competitor
      comparisons, full API reference, screenshots of text.
- [ ] No section runs past about one screen.

---

## Reporting

When the deliverable is the document, deliver the document. Don't print this checklist,
the number of passes, or commentary about how clean the result is.

When the deliverable is a review, report:

1. **Findings**, most impactful first, each with file:line, the offending text, the fix,
   and the rule it violates.
2. **Patterns** — a rule broken repeatedly is one finding with a count, not twenty
   findings.
3. **What you didn't change**, if you also applied fixes, and why.
