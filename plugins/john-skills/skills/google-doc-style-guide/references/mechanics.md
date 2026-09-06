# Mechanics

Capitalization, abbreviations, numbers, dates, units, plurals, possessives, punctuation,
and footnotes. Adapted from the Google developer documentation style guide (CC BY 4.0).

---

## Capitalization

Follow standard American English rules, plus:

- **Don't capitalize unnecessarily.** Before capitalizing a word, ask why.
- **Don't rely on capitalization to convey meaning.** Readers familiar with Kubernetes
  may know a capitalized *Pod* is a Kubernetes unit and a lowercase *pod* is any other
  kind, but newcomers won't.
- **No all-uppercase**, except in official names, in abbreviations always written in
  caps, or when quoting code that uses caps.
- **No camel case**, except in official names or when quoting code that uses it.

**Titles and headings:** sentence case. Capitalize the first word, the first word after
a colon, and proper nouns or terms always capitalized a certain way. No period at the
end.

**References to titles and headings:** use sentence case for any title from a document
that follows this guide, even if that title currently uses title case — so the reference
still matches after the title is fixed. Keep the original capitalization when citing a
work that doesn't follow this guide.

**After a colon:** lowercase, unless what follows is a proper noun ("Open source
software: Hadoop"), a heading, a quotation ("Arthurian wit: 'Bring me yon sworde'"), or
text after a label such as **Caution** or **Note**.

**Also sentence case:** captions; labels, callouts, and other text inside images and
diagrams; every element of a table (contents, headings, labels, captions); all list
items; glossary definitions.

**Glossary and index terms:** lowercase unless the term is a proper noun or otherwise
requires capitalization.

**Hyphenated words at the start of a sentence or heading:** capitalize only the first
element, unless a later element is a proper noun or proper adjective.

**Don't name a casing style.** *camel case* and *snake case* don't localize well and
aren't standardized. Describe the requirement and give an example instead: "Enter the
value in the format where there are no spaces between words and the first letter of each
word is capitalized—for example, `AssertionAccount`."

---

## Abbreviations

Abbreviations include acronyms (pronounced as a word: NATO, scuba), initialisms
(pronounced letter by letter: CIA, FYI), shortened words (Dr., etc., min, CA), and
contractions.

The technical distinction between acronyms and initialisms rarely matters — *acronym*
covers both.

**Short forms aren't abbreviations.** *app*, *demo*, *sync* are short versions of longer
words, and they take no period. If you're unsure, use the speaking test: if you say the
short form as a word ("This is a demo version"), treat it as a word.

### When to use them

- Use standard abbreviations that save the reader time. If the reader has to stop and
  think about it, it isn't saving anything.
- Spell out on first reference.
- **Don't abbreviate terms unrelated to the document's main topic.** In a document about
  the internet of things: "The internet of things (IoT) service can be used for
  connecting to sensors in low Earth orbit" — not "The IoT (internet of things) service
  … in LEO (low Earth orbit)."
- Be wary of specialized abbreviations your readers may not know.

### When to spell out

Spell out on first mention with the abbreviation in parentheses, then use the
abbreviation alone thereafter: "Border Gateway Protocol (BGP)". If you use an
abbreviation only once, include it only if it's at least as commonly used as the
spelled-out term.

If the first mention is in a heading, you can use the abbreviation there and spell it out
in the first paragraph that follows.

Consider your audience. Spelling out helps translation — human and machine — and helps
readers less familiar with English. But if most of your audience knows the term, don't
bother; and if spelling it out doesn't help (*portable document format* for PDF), don't.

**Rarely need spelling out:** AI, API, DVD, file formats such as PDF or XML, HTML, PC,
RAM, REST, units of measurement (MB, MiB, GB, GiB), URL, USB.

### Formatting the introduction

- **Italicize both** the spelled-out term and the abbreviation: *Border Gateway Protocol
  (BGP)*.
- **Capitalize the long form only if it's a proper noun** or conventionally capitalized.
  Don't capitalize just because the abbreviation has capitals: *data manipulation
  language (DML)*, not *Data Manipulation Language (DML)*.
- **Include the abbreviation inside the link text** when the introduction is a link.

### Abbreviations not to use

- Never *i.e.* or *e.g.* Use *that is* and *for example*. People confuse the two.
- *etc.* is acceptable in narrow circumstances, but rephrase in most lists.
- No internet slang: *tl;dr*, *ymmv*, *RTFM*.
- Use the common form of a word — *approximately*, not *approx.*
- Spell out symbol substitutions: "10 times faster," not "10x faster."

### Periods, plurals, verbs, articles

- No periods in acronyms or initialisms.
- A period after a shortened word, except in date and time abbreviations.
- No period after a short form you'd say as a word (*app*, *sync*).
- No periods in country, US state, or District of Columbia abbreviations: US, DC.
- Plurals: see below.
- **Never use an abbreviation as a verb.** "Use SSH to log in to your remote shell," not
  "Then `ssh` into your remote shell."
- **Articles depend on pronunciation:** *a* before a consonant sound, *an* before a vowel
  sound. Base the decision on the pronunciation most common for your audience — *a SQL*
  ("a sequel"), *a FHIR* ("a fire"), *an SAP* ("an ess-ay-pee").

---

## Numbers

### Spell out

- Zero through nine: *two-day total*, *four options*, *five minutes*, *nine developers*.
- A number that starts a sentence: "Fifteen directories are created." Often it's better
  to rearrange: "In general, avoid sending files larger than 164 MB" beats "164 MB is
  generally considered too large." Exception: it's acceptable, though not ideal, to
  start a sentence with a four-digit year.
- A number followed by a numeral: "This procedure creates fifteen 100,000-byte files."
  (But: "This procedure creates 15 of the 100,000-byte files.")
- Indefinite and casual numbers: "thousands of combinations," "a list of a million
  songs." Use numerals for precise figures.

### Use numerals

Numbers 10 and greater — and always, regardless of size:

- Version numbers (*version 3*)
- Technical quantities: memory, disk space, query counts, usage limits (*6 queries per
  second*, *50 Mbps*, *128 bits*)
- Page, chapter, and section numbers
- Step numbers (avoid referring to step numbers at all when you can)
- Prices
- Numbers without units, such as in mathematical expressions
- Numbers under 10 appearing in a sentence with numbers over 9: "The menu contains 15
  options but 6 of them are deselected."
- Negative numbers
- Most fractions
- Percentages
- Dimensions
- Numbers with decimal points — treat decimals as plural even at or below 1.0 (*1.0
  inches*), and put a zero before the point (*0.3 inches*)
- Measurements (*8 pixels*)
- Numbers in a range

### Other number guidance

- **Ordinals:** spell out — *first*, *fifth*, *twelfth*, *forty-third*. Not *1st*, *5th*.
- **Roman numerals:** avoid; Arabic numerals scan more easily. Acceptable for
  sub-sub-steps in numbered procedures.
- **Fractions:** express as decimals when possible. As words, hyphenate the numerator
  and denominator unless one is already hyphenated: *one and one-half*, *two-fifths*,
  *five sixty-fourths*.
- **Percentages:** numerals and `%` with no space: `40%`. If a percentage starts a
  sentence, spell out both: "Forty percent of the files."
- **Ranges:** hyphen, no spaces, no en dash: `2012-2016`.
- **Suspended hyphens:** "one-, two-, or three-hour intervals."
- **Dimensions:** numerals with a lowercase `x`, no spaces: `192x192`.
- **Exponents:** standard notation, no space between base and exponent.
- **Digit separators:** commas every three digits for numbers four or more digits long:
  `1,532,784`; `2,000`. No separators to the right of the decimal point:
  `$0.031611/vCPU hour`, not `$0.031 611`. A period for the decimal point.
- **Currency:** always know which country's currency you mean; the `$` sign covers US,
  Canadian, Mexican, and other currencies. Use a currency indicator if there's any
  ambiguity: `US$10`. Comma for thousands, period before fractions, dollar sign first, no
  punctuation or spaces after the decimal: `$0.006653`, `$10,000`.
- **Give numbers practical meaning.** Link to a pricing calculator when a feature incurs
  fees, for example.
- Use a nonbreaking space between a number and its noun when they must stay on one line.

---

## Dates and times

### Times

- 12-hour clock, unless the product uses 24-hour time. If the UI, a command, or a code
  sample uses 24-hour format, use it consistently on that page.
- Exact times where possible; *noon* and *midnight* are fine.
- Time ranges use a hyphen with no spaces: "5-10 minutes ago."
- `AM` and `PM` capitalized, no periods, one space before: "3:45 PM."
- Drop the minutes on round hours: "3 PM."

**Time zones.** Avoid them unless necessary. When you need one:

- Tell the reader if the time is local: "10 AM your local time."
- Match the timestamp format shown in the UI if there is one.
- Spell out the region and give UTC or GMT in parentheses: "US and Canadian Pacific
  Standard Time (UTC-8)."
- Don't abbreviate the time zone name.
- If an event's time doesn't shift for daylight saving, name the specific zone with no
  UTC reference.

### Dates

Spell out months and days of the week in full. Four-digit years.

- "January 19, 2017"
- With the day of week: "Tuesday, April 27, 2021" (`DAY_OF_WEEK, MONTH DAY, YEAR`)
- Month and year only, no comma: "She was hired in January 2017."
- Mid-sentence `MONTH DAY, YEAR`, comma after the year: "The January 19, 2017, release
  of…" Month and year only, no comma: "The January 2017 release of…"

**Abbreviating.** Usually don't. When space is tight (a heading or table cell), use
three-letter abbreviations, capitalized, with no period: "Mon, Sep 3, 2018" — not "Mon,
September 3, 2018." Abbreviate the whole date or none of it, and be consistent about
where in the doc you abbreviate.

**Why spelled-out dates.** `04/05/09` means May 4, 2009 in the UK, April 5, 2009 in the
US, and May 9, 2004 in some other regions.

**Numeric format**, when you have no choice: ISO 8601 `YYYY-MM-DD`, hyphen-separated —
`2017-04-15`. In a fictional example, pick a day greater than 12 so it can't be mistaken
for a month.

**Date and time together:** date first. "2017-04-15 at 3 PM"; "May 4, 2009, at 6 PM."

**Divisions of the year.** Avoid seasons — spring in the northern hemisphere is autumn
in the southern. Use months, quarters, or temperature.

| Recommended | Not recommended |
|---|---|
| During warmer months, data centers face a higher risk of cooling failures. | During summer months… |
| In November and December, data centers experience higher traffic volume. | In winter… |
| Changes are released in October of each year. | Changes are released in the Fall of each year. |

---

## Units of measurement

- **Nonbreaking space between number and unit** (`&nbsp;`), in HTML and Markdown alike:
  `64 GB`, `25 mm`. Not `64GB`, and not a plain space.
- **No space** for money, percent, or degrees of an angle: `$10`, `£25`, `65%`, `180°`.
- **Temperature:** nonbreaking space between the number and the degree symbol, none
  between the symbol and the scale: `50&nbsp;&deg;C` → 50 °C. For Kelvin, no degree
  symbol but a nonbreaking space: `300&nbsp;K` → 300 K.
- **Don't hyphenate** a number plus an abbreviated unit modifying a noun, unless the
  hyphen is needed for clarity: `200 GB disk`. Do hyphenate when the unit is spelled out:
  *a 64-bit system*, *a five-minute wait*.
- **Ranges:** repeat the unit for each number and use the word *to*, not a hyphen — a
  hyphen reads as subtraction. "-40 °C to 85 °C", not "-40-85 °C". Units here means
  symbols and abbreviations, not nouns like *file*.
- **Multiplied units** are hyphenated: `5 vCPU-hours`, `40 person-hours`.
- **`k` for thousands:** no space, and add a noun so it isn't mistaken for kilobytes:
  "limited to 55k download operations per day."
- **Rates:** *per*, not a division slash, unless space is tight. Shorten *per* to *p*
  only in well-established rate abbreviations: `Gbps`, `MBps` — not `Gb/s`.
- **Decimal vs. binary:** use whichever system the technology uses. Don't write MB when
  you mean MiB.

| Decimal | Binary |
|---|---|
| kB (kilobyte, 1000 bytes) | KiB (kibibyte, 1024 bytes) |
| MB (megabyte) | MiB (mebibyte) |
| GB (gigabyte) | GiB (gibibyte) |

---

## Phone numbers

- **Examples:** always a US number in the range 800-555-0100 through 800-555-0199, which
  is reserved for examples and fiction. Never a real number.
- Use a nonbreaking hyphen (`&#8209;`) so the number doesn't wrap:
  `415&#8209;555&#8209;0132`.
- **North American (NANP):** nonbreaking hyphens between area code, exchange code, and
  the four-digit number: 415‑555‑0132.
- **International:** include country and area codes, with a plus sign immediately before
  the country code and no space: +1‑415‑555‑0132. The plus stands in for the exit code,
  which differs by country.
- **Extensions:** follow the number with the word *extension* and the number:
  "415‑555‑0132, extension 987."

---

## Pluralization

Follow standard US English plural rules. **Never form a plural with `'s`** — it gets
confused with possessives and contractions, and it causes translation problems.

**Agreement.** Watch long or complex subjects.

- Recommended: "Confirm that the number of entries listed in the directory **is**
  accurate."
- Not recommended: "The efficiency of algorithms that process data sets **depend** on
  memory allocation."
- Recommended: "The request payload and header information **are** logged."
- Recommended: "Either the API keys or service account **wasn't** authenticated."

Use a plural after *one or more*: "If one or more tests **fail**…" (or reword: "If any
one test fails…"). Use a singular after *more than one*: "You can create more than one
instance at a time."

**Abbreviations.** Treat as regular words: *APIs*, *SKEs*, *IDEs* — not *API's*. Add
*es* after *s*, *sh*, *ch*, or *x*: *OSes*, *DISHes*, *BMXes*. When spelling out a term,
match the number of both parts: *virtual machines (VMs)*, not *virtual machines (VM)*.

**Units.** Spell out the singular only for 1; use the plural for everything else,
including zero and decimals: *0 degrees*, *0.5 degrees*, *1 degree*, *15 degrees*. Don't
pluralize an abbreviated unit: `64 GB`, not `64 GBs`.

**Product, feature, and class names.** Don't pluralize a trademark or a class name. Add
a plural noun instead: `Intent` objects, `Activity` instances — not `Intent`s,
`Intents`, or `Activities`.

**Optional plurals.** Never `(s)`. Pick singular or plural and be consistent; use *one
or more* when you genuinely need both.

| Recommended | Not recommended |
|---|---|
| To find your API key, visit the **Credentials** page. | To find your API key(s)… |
| The value of the parent depends on the values of its children. | …the value(s) of its child(ren). |
| A physical linecard, which can contain one or more ports. | …which can contain port(s). |

---

## Possessives

- **Singular nouns, including those ending in *s*:** add `'s`. "Modify each vector's
  record." "Raise the storage class's quota."
- **Plural nouns ending in *s*:** apostrophe only. "Extend the models' capabilities."
- **Plural nouns not ending in *s*:** add `'s`.
- **If a possessive is awkward, rewrite.** "Analyze the business data," not "Analyze the
  businesses' data." "The rule that the Federal Trade Commission (FTC) issued," not "The
  Federal Trade Commission's (FTC's) rule."

**Product, feature, and company names.** When describing function or performance, don't
form a possessive from a feature name, product name, or trademark, regardless of who
owns it. Use the name as a modifier or rewrite with *of*.

- Recommended: "monitor Google Search performance" / "monitor the performance of Google
  Search"
- Not recommended: "monitor Google Search's performance"

A company name takes `'s` ("Google's new office is nearby"), but don't form the
possessive when using the name as a trademark ("The capabilities of Google's Search are
vast" — no).

**Code items.** Never form the possessive of a code item. Form it from the following
noun, or rewrite.

- Recommended: "Compare the number to the `wordCount` method's return value."
- Recommended: "Compare the number to the value returned by the `wordCount` method."
- Not recommended: "Compare the number to `wordCount`'s return value."

---

## Punctuation

### Periods and end punctuation

End a complete sentence with a period unless it's a question.

**With URLs.** A period right after a URL is hard to distinguish from part of it. Avoid
putting URLs in text at all; rewrite so the URL isn't at the end; or put the URL on its
own line with no final period. When you do put a period after a URL, no space before it.

**With quotation marks.** The period goes inside, even when it isn't part of the quoted
material: `you might say "Fixed typo."` Exception: quotation marks around a keyword or
literal string — then punctuation goes outside. If the quoted material ends with a
question mark or exclamation point, don't add a period: `Children always ask "Why?"`

**With parentheses.** Period outside if the parenthetical ends the sentence; inside if
the parentheses contain a complete sentence.

- "…even if that change occurs while your application isn't running)."
- "…easy to scale. (With App Engine, there are no servers for you to maintain.)"

**Elsewhere:** no periods at the end of headings; a period for the decimal point; one
space between sentences.

### Exclamation points

Avoid. They read as unprofessional or alarming, and in Japanese and Korean, among
others, they can read as shouting.

| Content type | Guidance |
|---|---|
| Concept and reference docs | Never. Keep a neutral, objective tone. |
| Procedural topics | Avoid. Use periods for completion steps: "The VM is created." |
| Blog posts | Acceptable for enthusiasm, not in every paragraph. |
| Code examples | Fine when the syntax requires it — the `!=` operator. |
| System literals | Fine when part of an error code or log message that must match exactly. |
| Tutorials and learning modules | Sparingly, to mark a real milestone: "Congratulations! You've completed the setup." |

### Commas

- **Serial (Oxford) comma** in a series of three or more: "zones, regions, and
  multi-regions."
- **After an introductory word or phrase:** "Finally, only groups that contain
  parameters appear in this list."
- **Between two independent clauses** joined by *and*, *but*, *or*, *nor*, *for*, *so*,
  *yet* — unless both clauses are very short. "The libraries make feed creation easier,
  and they ensure that only valid feeds are produced." But: "Type your ID and click
  **OK**."
- **Between an independent and a dependent clause** joined by a coordinating
  conjunction: only when the sentence could be misread. "Direct-access flags are plain
  variables and can be read directly" (no comma). "The manager acknowledged the last team
  member who entered the room, and started the meeting" (comma prevents a misreading).
- **Before *which*** at the start of a nonrestrictive clause: "Name of the group, which
  has a maximum length of 200 characters."
- **Around a conjunctive adverb:** semicolon, period, or dash before *otherwise*,
  *however*, *therefore*; comma after. "The variable must have a value; otherwise, the
  server returns an error."
- **Not before *because***, unless it starts a nonrestrictive clause: "You can use the
  same key name in multiple backend services and backend buckets, because each set of
  keys is independent" — the comma marks the clause as nonrestrictive.

### Colons

A colon signals that closely related information follows.

- **Text before a colon that introduces a list must stand alone as a complete
  sentence.** "The fields are defined as follows:" — not "The fields are:"
- Lowercase the first word after a colon, with the exceptions listed under
  Capitalization.
- "Tone: concise, conversational, friendly, respectful."

### Semicolons

Avoid where possible — screen readers may not indicate them. A few cases justify one:

- Joining two closely related independent clauses where a period or comma is less
  effective.
- Before a conjunctive adverb (*therefore*) or a phrase (*that is*) that joins two
  independent clauses.
- Separating a series of long or complex items that contain their own punctuation:
  "focus on what matters most to your users; what is most important to fix; and what is
  easy to fix in the available time."

### Dashes

**Em dash (—)** for a break in the flow of a sentence or an interruption. No space
before or after. HTML `&mdash;`; macOS Option+Shift+hyphen; Windows Alt+0151 on the
numeric keypad; Linux Compose key followed by three hyphens, or Control+Shift+U then
`2014`.

**En dash: don't use.** Use a hyphen or the word *to*.

**Don't use a dash to separate an item from its description.** Use a colon or a period,
and for a series use a description list.

| Recommended | Not recommended |
|---|---|
| Example: This is an example. | Example - This is an example. |
| Appendix A: My first appendix | Appendix A—My first appendix |

### Hyphens

Use a hyphen when it's needed for clarity — to prevent a misreading, or to bind words
that should be read as a unit. Hyphenation depends on where the term sits, whether the
sentence is ambiguous without it, and convention. When you're unsure, check, in order:
the docs you're working in, the word list, then Merriam-Webster.

**Prefixes:** generally close them up — *infrastructure*, *megabyte*, *metadata*,
*preprocessing*, *pseudocode*, *semiconductor*. Hyphenate when:

- The prefix is *self* or *cross*: *self-managing*, *cross-region*.
- The noun is capitalized or a number: *non-Google*, *post-2000*.
- It prevents confusion: *de-energize*, *intra-index*, *re-mark*, *re-sign*.
- The base already has hyphens or spaces: *un-Google-like*, *non-twentieth-century*.
- Consistency within a document requires it: *pre-processing*, *post-processing*.

***non*** follows the same rules but hyphenates often because it forms hard-to-parse
words. Both patterns are in use: *noncurrent*, *nonempty*, *noninteractive*, *nonpublic*
— but *non-existence*, *non-integer*, *non-key*, *non-managed*, *non-negative*. Always
hyphenate before a hyphenated compound: *non-KSA-based*, *non-self-sustaining*.

**Compound nouns:** prefer the closed form — *webpage*, *hostname*, *tradeoff*,
*workaround*. If Merriam-Webster shows the open or hyphenated form but the closed form
dominates in your context, use the closed form. The word list records exceptions such as
*multi-region* and *style sheet*.

**Compound modifiers before a noun:** hyphenate when it aids clarity — *a well-designed
app*, *Android-specific techniques*. It's almost never wrong to do so. Use a hyphen after
*more* or *most* when it clarifies what they modify: *edge locations with more-reliable
internet links*. Avoid compound modifiers longer than two words; move words after the
noun instead — "test cases that are specific to the 2023 edition," not
"edition-2023-specific test cases." *cross-data-center replication* is fine when you must.

**Exceptions:** never hyphenate after an `-ly` adverb (*publicly available
implementations*), and don't hyphenate compounds that are conventionally open (*a managed
instance group*, *a machine learning model*).

**Compounds after a verb:** generally no hyphen. "The app is well designed." "The logs
are written in real time." "The app uses techniques that are Android specific." Some
terms are always hyphenated even after a verb: *on-premises*, *add-on*, *cloud-based*,
*customer-facing*, *user-friendly*, *game-like*.

**Ranges:** a hyphen, not an en dash: *8-20 files*, *5-10 minutes*. If the hyphen is
ambiguous, use *from*, *to*, *through* — but don't mix: "from 8 to 20 files," never
"from 8-20 files."

**Spaces:** never around a hyphen, except after (not before) a suspended hyphen: "at
one-, two-, or three-hour intervals."

### Parentheses

Some readers skip anything in parentheses, so don't put important information there.
Even for minor information, consider whether commas, dashes, semicolons, or a separate
sentence would work better. Keep mid-sentence parentheticals short; otherwise use two
sentences. Never use parentheses for optional plurals.

- Recommended: "Enter a name for the instance—for example, `my-instance-99`."
- Recommended: "Enter a six-digit hex number (for example, `228B22`), and then click
  **OK**."
- Not recommended: "Enter a name for the instance (for example, `my-instance-99`)."

### Quotation marks

**Use straight quotation marks and apostrophes, never curly ones.** Code requires
straight marks; automatic conversion tools make mistakes; typing them by hand makes
mistakes; and it's hard to tell them apart when proofreading.

Technical writing uses quotation marks sparingly, mostly for code. Use them for:

| Situation | Example |
|---|---|
| A section of a larger document you can't link to directly | The technique is described in the section "Deploying containers" of the Containers overview video. |
| The parent document's title when you're already linking to a section | The ML workflow section of "Introduction to Vertex AI" describes… |
| Citing a person, slogan, or motto | Martin Fowler has said, "We are still learning the techniques to write software effectively." |
| A term used metaphorically, when it isn't established usage in the domain | This configuration forms an "island" within the network. |

Titles of shorter works — articles, episodes — take quotation marks unless they're part
of a link. Full-length works take italics.

**Commas and periods go inside** the quotation marks: `See the section titled "Care and
feeding of the emu."` Exception: around a keyword or literal string, punctuation goes
outside, because the marks indicate an exact string. Better still, use code font and no
quotation marks: "If you enter `escape`, the program crashes."

**Single quotation marks** only in code examples in languages that use them, and for a
quotation nested inside another: `She said, "I heard him shout 'Help,' and saw him
floundering in the water."`

### Ellipses

Generally don't use them.

- Never as suspension points to indicate hesitation.
- **In UI names:** drop them. A button labeled "Save …" is documented as "click
  **Save**."
- **In prose:** don't. Omit unnecessary information and include necessary information.
- **In quoted text:** acceptable to replace omitted material, but not at the beginning
  or end of the quotation. When the omitted material crosses a sentence boundary, use
  four dots — the fourth is a period.
- Build an ellipsis from three periods in a row, not the ellipsis character. Keep them
  together. One space before and after, unless a punctuation mark immediately follows.
- **In code and command output:** use `...` (three dots, no spaces) on its own line for
  omitted output, and a language-appropriate comment for omitted code.

### Slashes

Avoid outside code.

- **Dates:** never.
- **Alternatives:** never. "developed or is hosted by a commercial entity," not
  "developed/hosted." "five or six times," not "5/6 times."
- ***and/or*:** avoid. Often *and* implies *or*. "You can view and edit your own data."
  If you need both explicitly: "You can export raw events, processed events, or both."
  Acceptable only where space is tight, such as in a table.
- **File paths and URLs:** forward slashes, as appropriate — backslashes for Windows
  paths. Break a long URL immediately after a slash; never insert a hyphen into a URL to
  break it.
- **Fractions:** ambiguous — `3/4` could mean three-quarters or "4 as an alternative to
  3." Use `¾`, `0.75`, or `75%`.
- **Abbreviations:** spell them out. *care of*, *with* — not *c/o*, *w/*.

---

## Footnotes

Avoid footnotes: they aren't accessible and they complicate localization. Instead use a
cross-reference, a note, or a parenthetical.

If a footnote is genuinely the only option, use a superscript number (`<sup>1</sup>`) and
put the footnote at the bottom of the page. In a table, put footnotes immediately after
the table.
