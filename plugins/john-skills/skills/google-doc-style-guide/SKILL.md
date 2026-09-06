---
name: google-doc-style-guide
description: Writes and edits technical documentation and application help content in a consistent house style derived from the Google developer documentation style guide — second person, active voice, present tense, sentence-case headings, procedures, lists, tables, code font, placeholders, notices, link text, accessible and inclusive language, and a word list of preferred and prohibited terms. Use whenever writing or revising a README, quickstart, how-to, tutorial, concept page, troubleshooting guide, CLI or API docs, API reference comments, release notes, in-app help, tooltips, or error-message text; also use when asked to "apply the Google style guide", "make these docs consistent", "edit this doc for style", "write docs for this", or to review documentation for style problems.
---

# Google developer documentation style

House style for technical documentation and application help. Derived from the
[Google developer documentation style guide](https://developers.google.com/style)
(CC BY 4.0). The goal is documentation that reads as if one careful person wrote all of
it: clear, direct, scannable, accessible, and translatable.

---

## Reference hierarchy

When guidance conflicts, follow this order:

1. **Project-specific style.** A `CLAUDE.md`, `STYLE.md`, contributing guide, or an
   established convention visible in the docs you're editing wins. Check for one before
   you start.
2. **This skill.**
3. **Third-party references.** Spelling: Merriam-Webster (use the first spelling
   listed). Nontechnical style: *The Chicago Manual of Style*. Technical style:
   Microsoft Writing Style Guide.

**Break the rules** when doing so serves the reader. These are guidelines, not laws.
When you depart from them, be consistent about it throughout the document.

---

## How to use this skill

1. **Identify the document type and the reader.** A quickstart, a concept page, a
   troubleshooting guide, and a tooltip are different jobs. Decide who "you" is — a
   developer? an operator? an end user? — and address that reader consistently. For a
   README, read `references/readme.md` before you start.
2. **Check for project-specific style** (step 1 of the reference hierarchy) and for the
   terminology already used in the surrounding docs. Consistency with neighbors beats
   consistency with this file.
3. **Draft against the core rules below.** Hold them in mind while writing rather than
   fixing violations afterward.
4. **Open a reference file when you need detail.** The core rules cover most decisions;
   the references cover the rest. See the index at the end.
5. **Run the review pass before delivering.** Use `references/checklist.md`. Deliver the
   document, not the checklist output — unless the user asked for a style review, in
   which case report findings with file and line.

**When reviewing rather than writing:** report what to change and why, quoting the
offending text. Don't rewrite wholesale unless asked. Rank findings by reader impact —
ambiguity and inaccessible constructions first, spelling and hyphenation last.

---

## Core rules

### Voice and tone

Aim for conversational, friendly, and respectful without being frivolous. Sound like a
knowledgeable friend who understands what the reader is trying to do. Don't write the
way you speak — speech is more verbose than documentation should be.

Avoid:

- Buzzwords, jargon, and figurative language, including metaphors and ableist idioms.
- Placeholder phrases: *please note*, *at this time*.
- Starting every sentence the same way (*You can…*, *To do…*).
- Pop-culture references, humor, wackiness, cuteness.
- Exclamation points. They read as unprofessional or alarming, and in some languages
  they read as shouting. Never in concept or reference docs. See `mechanics.md` for the
  narrow exceptions.
- *Simply*, *easy*, *just*, *quickly* in procedures. What's easy for you may not be
  easy for the reader.
- *Please* in instructions. "To view the document, click **View**" — not "please click."
  Reserve *please* for when you're asking a favor that inconveniences the reader.
- *Let's do X* phrasing.
- Internet slang and abbreviations: *tl;dr*, *ymmv*, *RTFM*.

| Too informal | About right | Too formal |
|---|---|---|
| Dude! This API is totally awesome! | This API lets you collect data about what your users like. | The API documented by this page may enable the acquisition of information pertaining to user preferences. |
| Then—BOOM—just garbage-collect, and you're golden. | To clean up, call the `collectGarbage` method. | Please note that completion of the task requires the following prerequisite: executing an automated memory management function. |

### Address the reader as *you*

Use second person. Assume the reader is the person doing the tasks.

- Recommended: "The following sections describe how you can create a website."
- Not recommended: "The following sections describe how we can create a website."
- Not recommended: "Let's add a description to our table."

Use the imperative for instructions — the *you* is implied: "Click **Submit**."

Reserve the word **user** for the user of the software your reader is building. Use
third person for what the software or an end user does, second person for what the
reader does.

*We*, *our*, and *us* are acceptable only for the organization authoring the document,
and only when the antecedent is clear: "Example Organization provides A and B, but we
don't provide C." Also acceptable in FAQ questions and in signed first-person commentary.

### Active voice

Make clear who performs the action.

- Recommended: "Send a query to the service. The server sends an acknowledgment."
- Not recommended: "The service is queried, and an acknowledgment is sent."

Passive is fine when you want to emphasize the object ("The file is saved"),
de-emphasize the actor ("Over 50 conflicts were found in the file"), or when the actor
is irrelevant ("The database was purged in January").

### Present tense

Describe general behavior in the present tense. "The server sends an acknowledgment,"
not "will send." Use future tense only for something that genuinely happens later:
"The file will be archived the next time the backup process runs." Avoid the
hypothetical *would*.

### Say what you mean: must, can, might

Write **prescriptive** documentation — recommend a path instead of listing every option.
Generally avoid *should*: it leaves the reader unsure whether an action is required.

| Intent | Use |
|---|---|
| Action is required | *must*, or an imperative: "Do the following before you continue." |
| Action is recommended | "We recommend…" (*should* is OK for widely recognized advice: "You should use a strong password") |
| Action is optional | *can*: "You can also use approach B." |
| Outcome is expected | State it: "The process returns 10 items." |
| Outcome is possible | *might* or *can*: "The process can take about 30 minutes." |
| State of something | Be explicit: "You must set the value to `true`" — not "The value should be `true`." |

Avoid *could*, *would*, and *shall*. Reserve *may* for permission in a legal or policy
sense.

### Sentence and paragraph structure

- **Put the condition before the instruction.** "To delete the entire document, click
  **Delete**" — not "Click **Delete** if you want to delete the entire document."
  Likewise "For more information, see X," not "See X for more information."
- **Put the most important information first** in the sentence and in the paragraph.
- **Keep paragraphs short** — one idea each. A paragraph past 5 or 6 sentences usually
  carries too much. One-sentence paragraphs are fine.
- **Keep sentences short** — aim under 26 words.
- **Left-align text.** Don't center, justify, or force line breaks inside sentences.

### Write timeless documentation

Document how the product works now. Don't anchor text to a moment.

Avoid: *as of this writing, currently, does not yet, eventually, existing, future,
in the future, latest, new, newer, now, old, older, presently, at present, soon.*

- Recommended: "These subcommands let you interact with HTTP load balancing."
- Not recommended: "These **new** subcommands…"
- Recommended: "The following options aren't supported:"
- Not recommended: "The following options aren't **currently** supported:"

Time-anchored words are fine in release notes, changelogs, and blog posts. If you must
say *new*, give a reference point: "The January 14, 2021 release includes a new
resource panel."

**Don't document future features.** Don't pre-announce anything.

### Don't overclaim

Avoid superlatives — *best*, *simplest*, *fastest*, *never*, *always*. Be careful with
*ensure* and *guarantee*. Cite a source for performance claims. Say a feature "helps
with security" or "is designed for security" rather than that it *is* secure — the
weaker claim stays true after an incident.

### Don't anthropomorphize

Software doesn't see, tell, want, or think.

- Recommended: "A `Delimiter` object specifies where to split a string."
- Not recommended: "A `Delimiter` object tells the splitter where a string should be broken."

### Jargon

Jargon hurts clarity, translation, and readers new to the domain. Before using a term
like *blast radius*, *shift left*, or *out-of-the-box*, ask:

1. Can you write around it? "When the project is finished, review what worked" beats
   "Hold a post-mortem."
2. Is there a more specific term? *affected area* for *blast radius*; *import* or
   *load* for *ingest*; *ready-made* for *off-the-shelf*.
3. Used once? Describe it in plain language and put the jargon in parentheses.
4. Used throughout? Define it in parentheses on first use, then use it consistently.

### Write for a global audience

Much of what follows exists because documentation gets translated and read by people
whose first language isn't English.

- **Use simple words.** *use* not *utilize* or *leverage*; *start* not *commence*;
  *so* not *consequently*; *to* not *in order to*.
- **Avoid phrasal verbs.** "This document uses the following terms," not "makes use of."
- **Don't stack modifiers.** No more than two nouns modifying another noun.
- **Place *only* immediately before what it modifies.** "Request only one token."
- **Keep helper words** that casual English drops: *then*, *that*, *of*, *and then*.
  - "If the key is not found, **then** the default value is returned."
  - "…assumes **that** you have the following knowledge:"
  - "Identify all **of** the datasets."
  - "Start the profiler, **and then** run the app."
- **Don't omit relative pronouns.** "the rules **that** you previously defined."
- **Avoid gerunds where a clause is clearer.** "You must configure the firewall rules
  before you deploy the VM," not "Configuring the firewall rules is required before
  deploying the VM."
- **Use words in their primary sense.** Avoid *once* for *after*, *since* for *because*,
  *while* for *although*, *as* for *because*.
- **Repeat a word if it removes ambiguity.** "creates both IAM segmentation and network
  segmentation," not "both IAM and network segmentation."
- **Use consistent terminology.** Same concept, same word, same capitalization, every
  time. Don't elegantly vary.
- **Skip culturally specific references** — holidays, seasons, sports, idioms.
- **Include articles** (*a*, *an*, *the*), even in headings: "Create a VM instance."
- **Don't skip prepositions**, and don't fear one at the end of a sentence.

---

## Structure

### Titles and headings

- **Sentence case.** Capitalize the first word, the first word after a colon, and proper
  nouns. No period at the end.
- **Task-based sections start with a base-form verb:** "Create an instance" — not
  "Creating an instance." Avoid `-ing` forms as the first word of any heading; they
  translate inconsistently. (*Billing*, *Pricing* are acceptable exceptions.)
- **Conceptual sections use a noun phrase:** "Migration to Google Cloud." Mixing both
  styles in one document is fine.
- **Optional sections use an `Optional:` prefix:** "Optional: Customize your alias" —
  not "Customize your alias (optional)."
- One `h1` per page, unique across the doc set. Don't repeat the page title verbatim in
  a section heading.
- Don't skip heading levels. Don't use heading tags for visual styling. Don't leave a
  heading with no content under it.
- No numbers to indicate sequence, no links in headings, and avoid code items in
  headings — if you must, add a descriptive noun: "The `config.yaml` file."
- To introduce a group of subsections, say "**the following sections**," never "this
  section" or "these sections."

### Lists

| Item shape | Use |
|---|---|
| Single units, sequence matters | Numbered list |
| Single units, no sequence | Bulleted list |
| Term + definition, want emphasis | Description list |
| Term + short explanation, save space | Bulleted run-in headings ("**Emu**: the best kind of bird") |
| Three or more related fields per item | Table |

- **Introduce a list with a complete sentence**, not a fragment the items complete.
  - Recommended: "Use the **Submit** button for any of the following purposes:"
  - Not recommended: "Use the **Submit** button to:"
- Colon if the intro immediately precedes the list; period if other material intervenes.
- **Capitalize each item.** End each with a period, except items that are a single word,
  have no verb, are entirely code font, or are entirely link text or a document title.
  If punctuation ends up inconsistent, rewrite for parallelism or punctuate everything.
- **Use parallel structure** across items.
- Never make a one-item list.
- Don't end a list with *etc.* or *and so on*. Introduce it so it's clear the list isn't
  exhaustive: "problems such as instability or high latency."

### Procedures

- Introduce with a complete sentence: "To customize the buttons, follow these steps:"
  or "To customize the buttons, do the following:" — not "To customize the buttons:".
- One action per step. Start each step with an imperative verb. Use complete sentences.
- **State the location before the action:** "In the Google Cloud console, go to the
  **Monitoring** page" — not "Go to the Monitoring page in the console."
- **State the goal before the action:** "To start a new document, click **File > New >
  Document**."
- **A single-step procedure is a bulleted item**, not a numbered list of one.
- Sub-steps use lowercase letters; sub-sub-steps use lowercase Roman numerals.
- Mark optional steps with `Optional:` as the first word — not `(Optional)`.
- **Don't use directional language** (*above*, *below*, *left-hand side*). Use
  *preceding*, *following*, *earlier*, *later*. If an element is hard to find, show a
  screenshot or name its icon.
- Don't include keyboard shortcuts as the documented path. Don't say "run the following
  command" — say what the command does: "In Cloud Shell, deploy the load generator:"
- Give one way to do a thing — the shortest, most accessible, most familiar. If you must
  document several, separate them into pages, headings, or tabs.
- Order inside a complex step: action → command → placeholder explanations → command
  explanation → output → result.

### Tables

- Introduce every table with a complete sentence; screen readers don't always announce
  them.
- Sentence case for headings, cells, and captions. No end punctuation in column heads.
- Header cells in the first row and first column only, marked up as headers with the
  `scope` attribute where the format supports it.
- Don't merge cells. Don't use tables for layout, code snippets, or one-dimensional
  lists. Avoid tables inside numbered procedures.
- Sort rows logically, or alphabetically if there's no logical order.
- If a document has more than one table close together, caption each: "**Table 1.**
  Prehistoric birds." Refer to them by number ("as shown in table 2"), lowercase.

### Notices

| Type | Meaning |
|---|---|
| **Note** | Useful but not critical. The reader still succeeds if they skip it. |
| **Caution** | Proceed carefully. |
| **Warning** | Don't do this, or this may be irreversible — data loss, cost, security. |
| **Success** | An error-free result. Interactive content only. |

Readers skip notices, so don't overuse them, and never stack two in a row. Write the
content as ordinary text first, then decide whether it needs offsetting.

Don't use a note for: cross-references, prerequisites, a full procedural step, anything
the reader needs in order to succeed, or a continuation of the preceding text.

### Links and cross-references

- **Be selective.** Every link is a decision and a chance to lose the reader. Prefer
  giving a couple of sentences of context on the page over linking away.
- **Link text is the page title or a descriptive phrase**, capitalized as part of the
  sentence. Put the important words first. Never *click here*, *this document*, *read
  this*, or a bare URL.
- **Introduce a standalone cross-reference consistently:** "For more information, see X."
  or "For more information about Y, see X." Use *about*, never *on*. Use *see*.
- Don't duplicate links to the same destination on a page.
- **Explain unexpected behavior.** Say when a link downloads a file, opens an email
  client, jumps to another section of the same page, or opens in a new tab. Don't force
  a new tab; if you must, say so in the link text.
- Punctuation goes outside the link. Don't put link text in quotation marks.
- Include the abbreviation inside the link text: "Google Kubernetes Engine (GKE)".
- When linking a code element, include the descriptive noun in the link: "run the
  `gcloud instances create` command."

### Example data

Never use real domains, emails, names, phone numbers, IPs, or addresses.

| Kind | Use |
|---|---|
| Domains | `example.com`, `example.org`, `example.net` |
| Email | A reserved domain plus an example name: `dana@example.com`, `support@example.net` |
| Person names | Alex, Amal, Ariel, Bola, Charlie, Cruz, Dana, Dani, Hao, Ira, Izumi, Jie, Kai, Kalani, Kim, Kiran, Lee, Lucian, Luka, Mahan, Noam, Nur, Quinn, Raha, Rosario, Sasha, Tal, Taylor, Tristan, Yuri — with an initial for a surname ("Dana A.") |
| Company | Example Organization |
| Phone (US) | `800-555-0100` through `800-555-0199` |
| IPv4 | `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` |
| IPv6 | `2001:db8::/32` |
| Street address | 1800 Amphibious Blvd., Mountain View, CA 94045 |
| Project names | Something meaningful: `staging`, `frontend-development`, `production-1`. Never `foo`, `bar`, `baz`. |

Use diverse names, and use singular *they*. Watch for stereotypes in which personas get
which job roles.

---

## Formatting

| Element | Use |
|---|---|
| **Bold** (`<b>` / `**`) | UI element names; run-in headings; the label at the start of a notice. Nothing else. |
| *Italic* (`<i>` / `_`) | A term you're defining on first mention; words as words; titles of full-length works; mathematical and version variables; emphasis. Use sparingly. |
| Underline | Links only. |
| `Code font` | Code and code-adjacent text, inline. |
| Code block | Code samples and commands. |

Prefer `_underscores_` for italic and `**asterisks**` for bold in Markdown — the two are
easier to tell apart that way. Don't use ampersands as shorthand for *and*. Don't
override font family, size, or color inline.

**Put in code font:** attribute names and values, class names, command output,
command-line utility names, data types, database rows and columns, constants, DNS record
types, element names (without angle brackets), enum names, environment variables,
filenames and paths, folders, HTTP content types, HTTP status codes and verbs, IAM role
names, IP addresses, language keywords, method and function names, namespaces, package
names, placeholders, port numbers, query parameters, strings used in code, text the
reader types, and UI values derived from earlier input.

**Don't put in code font:** domain names, product and organization names, and URLs the
reader is meant to open in a browser.

**Grammatical treatment of code:** don't inflect a code element. Add a noun and inflect
that instead.

- Recommended: "The `ADDRESS` constant's value is defined in the `settings.h` file."
- Not recommended: "`ADDRESS`'s value is defined in `settings.h`."
- Recommended: "To add the data, send a `POST` request." — Not: "`POST` the data."

**Placeholders:** `UPPERCASE_WITH_UNDERSCORES`. No possessives (`MY_`, `YOUR_`). Explain
every placeholder the first time it appears. One placeholder: "Replace `BUILD_ID` with
the ID of the build." Two or more: introduce with "Replace the following:" and list them
in the order they appear, each as `` `NAME` ``: lowercase description.

**Commands:** put a click-to-copy command in a code block, wrap lines at 80 characters
with the shell's continuation character, and follow it with the placeholder list. Keep
optional-argument syntax (`[]`, `{}`, `|`, `...`) out of copyable commands — those
characters break the command if the reader doesn't strip them. Introduce output with
"The output is similar to the following:".

For the full detail — code samples, command-line syntax notation, math notation,
figures and alt text, filenames — see `references/formatting.md`.

---

## Mechanics at a glance

- **Capitalization.** Sentence case for titles, headings, list items, table content,
  captions, and figure text. Don't capitalize for emphasis. Don't rely on capitalization
  to carry meaning. Lowercase after a colon unless what follows is a proper noun, a
  heading, a quotation, or a label.
- **Numbers.** Spell out zero through nine and any number starting a sentence. Use
  numerals for 10 and up, and always for versions, technical quantities, measurements,
  percentages, prices, dimensions, decimals, and ranges. `40%`, no space. Ranges use a
  hyphen: `2012-2016`. Commas in numbers of four or more digits: `1,532,784`.
- **Dates.** Spell out the month: "January 19, 2017". Never numeric-only formats with
  slashes. If you must go numeric, use ISO `YYYY-MM-DD`. Avoid seasons.
- **Times.** 12-hour clock, "3:45 PM" — caps, no periods, space before.
- **Units.** Nonbreaking space between number and unit: `64 GB`. No space for currency,
  percent, or degrees of angle. Repeat the unit in a range and use *to*: "-40 °C to
  85 °C". Don't write `MB` when you mean `MiB`.
- **Abbreviations.** Spell out on first use with the abbreviation in parentheses, both
  italicized, and capitalize the long form only if it's a proper noun: *data
  manipulation language (DML)*. AI, API, DVD, HTML, PC, PDF, RAM, REST, URL, USB, and
  file formats such as XML rarely need spelling out. No periods in acronyms. Never use an
  abbreviation as a verb. Never *i.e.* or *e.g.*
- **Serial commas.** Always: "zones, regions, and multi-regions."
- **Em dashes** for a break in a sentence, no spaces around them. Never en dashes.
- **Quotation marks:** straight, not curly. Commas and periods go inside — except around
  a literal string, where they go outside.
- **Semicolons and ellipses:** avoid. Screen readers may skip them.
- **Slashes:** avoid outside code. No *and/or*, no `3/4`, no date slashes.
- **Hyphens.** Close most prefixes (`preprocessing`, `metadata`) — hyphenate after
  *self-*, *cross-*, before a capital or number, and to avoid a misreading. Close
  compound nouns (`webpage`, `hostname`, `tradeoff`). Hyphenate compound modifiers
  before a noun (`well-designed app`) but not after a verb ("The app is well designed"),
  and never after an `-ly` adverb.
- **Possessives.** `'s` for singular nouns including those ending in *s*; apostrophe
  only for plurals ending in *s*. Never form a possessive or plural from a code item,
  product name, feature name, or trademark.
- **Plurals.** No `'s` for plurals: `APIs`, not `API's`. Don't pluralize a unit
  abbreviation: `64 GB`, not `64 GBs`. Never `(s)` — use "one or more."
- **Filenames.** Lowercase, hyphens not underscores, ASCII only. Refer to a file type by
  its formal name, not its extension: "a PNG file," not "a `.png` file."

Full detail in `references/mechanics.md`.

---

## Accessibility and inclusion

These are not optional polish — they change what you write.

- **Alt text on every image.** Empty `alt=""` if the image is decorative or duplicates
  adjacent text. Under 155 characters, no "Image of." Don't put new information only in
  an image, and never use images of text, code, or terminal output.
- **Descriptive link text** that makes sense read out of context.
- **No directional language.** Not *above*, *below*, *left-hand side*. Use *preceding*,
  *following*, *earlier*, *later*.
- **Refer to controls by their label**, not their appearance: "Click **Save**," not
  "Click the disk icon."
- **Don't rely on color, size, or position alone** to carry meaning.
- **Semantic markup**, real heading hierarchy, real `button` elements, labeled form
  fields.
- **Avoid ableist and figurative language:** not *sanity check*, *crazy*, *cripples*,
  *blind to*, *dummy variable*, *hangs*. Use *quick check*, *baffling*, *slows down*,
  *ignores*, *placeholder*, *stops responding*.
- **Avoid non-inclusive terms:** *blacklist/whitelist*, *master/slave*, *man-hours*,
  *grandfathered*, *first-class citizen*, *brown bag*, *sanity check*. See the word list
  for replacements. If the term is baked into code you're documenting, name it once in
  code font, in parentheses, then use the inclusive term throughout.
- **Gender-neutral throughout.** Singular *they*. Never *he/she* or *(s)he*.
- **Write about disability with care.** Not *normal* or *healthy* for people without
  disabilities; not *suffers from* or *wheelchair-bound*.

Full detail in `references/audience.md`.

---

## Open source READMEs

> An extension to the source guide, which doesn't cover READMEs. Everything above still
> applies — this section is about what goes in a README, in what order, and how short it
> should be.

A README is a front door, not a manual. Its job is to get a stranger from "what is
this?" to a working install in the fewest steps, then point them at the real docs. If
a section grows past roughly one screen, move it to `docs/` and link to it.

### Order

Put the actionable material first. A reader who has to scroll past your motivation,
your badge wall, and your architecture diagram to find `npm install` will leave.

1. **Project name and a one-line description.** What it is and what it does, in one
   sentence, no superlatives.
2. **Two to four sentences of context.** What problem it solves and who it's for. Stop
   there — background, design rationale, and comparisons belong in `docs/`.
3. **Quick start.** The first substantive section. See below.
4. **Installation.** The complete set of install paths.
5. **Configuration.** Minimum working config, then the option reference.
6. **Usage.** The handful of tasks most readers actually perform.
7. **Everything else:** troubleshooting, links to full documentation, how to contribute,
   license.

Badges, if any, go on one line under the title, and only ones a reader acts on — build
status, version, license. Give each an `alt` attribute.

### Quick start

The quick start is a procedure (see the Procedures rules above), held to the shortest
path that produces a verifiable result.

- **Every command must run exactly as written.** No `[optional]` or `{a|b}` notation, no
  values the reader must edit before pasting, no shell prompts to strip. If a value can't
  be avoided, make it a documented placeholder and explain it immediately.
- **Run the commands before you publish them.** Copy them from a real terminal session,
  not from memory. Fabricated flags and near-miss command names are the most common
  README defect and the most expensive one.
- **State prerequisites as checkable versions,** immediately before the first command —
  "Node.js 20 or later," not "a recent version of Node." Give the command that checks.
- **End with proof it worked.** A final step that produces output, followed by "The
  output is similar to the following:" and the actual output. Without it, the reader
  can't tell success from silent failure.
- **Don't teach concepts here.** No architecture, no vocabulary, no explanation of why
  the tool works the way it does. Link to it.

### Installation

The quick start shows one way in; this section shows the rest. For each supported path
— package manager, container image, prebuilt binary, from source — give the exact
command, and say what the path is for when it isn't obvious ("from source, if you're
contributing"). State the supported platforms and versions in a table rather than in
prose, so the facts stay current without a rewrite. Say how to verify the install and
how to uninstall.

### Configuration

Two parts, in this order:

1. **Minimum working configuration.** The smallest complete config that runs, as a
   copy-pasteable file, with a sentence saying where the file goes.
2. **The option reference.** A table: option name, type, default, description. Read every
   default out of the code rather than assuming it. If options come from more than one
   source — file, environment variable, command-line flag — state the precedence order
   explicitly.

Never put a real secret, token, key, or hostname in an example. Use a placeholder, say
where the value comes from, and don't imply that a committed config file is a safe place
for it.

### Keep it short

Cut from the README and link instead: philosophy and origin stories, roadmaps and
planned features (see the future-features rule), exhaustive feature lists, comparison
tables against other projects (see excessive claims), full API references, and
screenshots of text or terminal output.

Full detail, an annotated skeleton, and the common failure modes are in
`references/readme.md`.

---

## Adapting to output format

This guidance was written for HTML and Markdown documentation sites. Adapt it, don't
break it:

- **Plain-text contexts** (terminal output, commit messages, error strings): drop the
  markup-level rules — `&nbsp;`, `<var>`, `aria-label`, `srcset` — and keep everything
  about wording, structure, and terminology.
- **README and repo docs:** all of it applies. Sentence-case headings, second person,
  present tense, real heading hierarchy, code font for code. See the READMEs section
  above and `references/readme.md`.
- **UI text** (labels, buttons, tooltips, empty states): follow your design system's
  content guidelines for capitalization and list punctuation — Material Design and this
  guide differ there. The voice, tone, and terminology rules still apply.
- **Release notes and changelogs:** the timeless-documentation rule is relaxed. *New*,
  *now*, and *soon* are fine here, and dates are the point.

---

## Reference files

Open these when you need detail beyond the core rules.

| File | Covers |
|---|---|
| `references/word-list.md` | Alphabetical usage, spelling, and capitalization decisions; terms to avoid and their replacements. Check it whenever a term choice feels uncertain. |
| `references/structure.md` | Headings, lists, procedures, tables, notices, cross-references, example data, sentence and paragraph structure. |
| `references/formatting.md` | Text formatting, code in text, code samples, command-line syntax, placeholders, math notation, figures and alt text, filenames, HTML vs. Markdown. |
| `references/mechanics.md` | Capitalization, abbreviations, numbers, dates and times, units, phone numbers, plurals, possessives, all punctuation, footnotes. |
| `references/audience.md` | Accessible documentation, inclusive documentation, writing for a global audience. |
| `references/names-and-claims.md` | Product and feature names, trademarks, excessive claims, future features, timeless documentation, third-party content. |
| `references/api-reference.md` | API reference code comments: classes, methods, parameters, return values, exceptions, deprecations. |
| `references/readme.md` | Open source READMEs: section order, the quick start, installation, configuration, what to cut, common failure modes. Open it whenever you're writing or reviewing a README. |
| `references/checklist.md` | The review pass to run before delivering. |

---

Source: [Google developer documentation style guide](https://developers.google.com/style),
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Condensed,
reorganized, and adapted for use by coding agents.
