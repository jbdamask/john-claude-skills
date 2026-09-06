# Audience: accessibility, inclusion, and a global readership

Adapted from the Google developer documentation style guide (CC BY 4.0).

These three concerns overlap heavily, and most of the guidance elsewhere in this skill
exists because of them: simple words, short sentences, consistent terminology, active
voice, real heading hierarchy, and non-directional language all serve readers using
assistive technology, readers whose first language isn't English, and translators.

---

## Write accessible documentation

An estimated 15% of the world's population — more than a billion people — have an
accessibility need. Writing with accessibility in mind improves the document for
everyone.

### General

- **No ableist language.** See "Write inclusive documentation" below.
- Every part of the document — tabs, buttons, interactive elements — must be reachable
  with a keyboard alone.
- **Test with a screen reader.** It's also a good self-editing pass.
- Use semantic HTML. `em` means emphasis, not "make this italic."
- Prefer native elements over custom-styled ones.
- Avoid unnecessary font formatting; screen readers announce text modifications
  explicitly.
- Don't force line breaks inside sentences and paragraphs — they break at other window
  sizes and text sizes.
- Avoid camel case and all caps. Some screen readers read capitals letter by letter, and
  some languages are unicase.
- Not all punctuation is read aloud, depending on the screen reader and its settings.
  The meaning must survive without it — which is why exclamation marks, question marks,
  and semicolons are discouraged.
- Don't use `&` for *and* in headings, text, navigation, or tables of contents. It's
  acceptable when referencing a UI element that uses `&`, and in table headings or
  diagram labels where space forces abbreviation.
- If the product has accessibility features, document them explicitly.

### Ease of reading

- Break up walls of text with paragraphs, headings, and lists.
- Shorter sentences — aim under 26 words.
- Define acronyms and abbreviations on first use, and again if they recur only rarely.
- Parallel structure for similar things.
- Put the distinguishing information first in each paragraph.
- **Avoid double negatives and exceptions to exceptions.**
  - Recommended: "You can continue without a path."
  - Not recommended: "A missing path won't prevent you from continuing."
- Left-align text. Don't center or full-justify.

### Headings, links, lists

- Real heading elements, correct hierarchy, no skipped levels, no empty headings, one
  `h1` for the page title. Use CSS for visual changes, never a wrong heading level.
- Link text that makes sense read out of context. Never *click here* or *read this
  document*. Screen reader users jump link to link to scan a page.
- Use *see* for links and cross-references — research indicates sight-related language
  is fine for a wide range of readers.
- Explain any link that downloads a file, opens a new tab, or jumps within the page.
- Avoid adjacent links; put a separating character between them.
- In procedures, make each instruction its own list item.

### Images, video, tables

- Every image gets an `alt` attribute — descriptive if the image is informative, empty
  (`alt=""`) if it's decorative or duplicates nearby text.
- **Don't present new information only in an image.** Always give an equivalent text
  explanation.
- Don't repeat images unless you must.
- Never use images of text, code samples, or terminal output.
- Prefer SVG to PNG — it stays sharp when zoomed.
- Provide captions, transcripts, or descriptions for audio and video, and make sure
  captions can be translated.
- **No flickering or flashing elements** — they can cause motion sickness or seizures.
- Introduce tables in the preceding text; not all screen readers announce them.
- Table headers in the first row and column only, using `th`. Use `scope` when there are
  both row and column headings; use `headers` with unique IDs when there's more than one
  header row.
- Don't merge cells. Avoid tables inside numbered procedures. Don't use a table unless
  it's genuinely the best presentation.
- Never convey new information through an image or symbol in a table without a
  descriptive `alt`.

### UI, forms, and interactive elements

- Introduce an interactive element (an expander, for example) in the text before it: "To
  see a list of requirements, expand the **Requirements** section."
- When you use angle brackets for menu paths, wrap them so screen readers say "and then"
  rather than "greater than":
  `<span aria-label="and then">></span>`.
- Label every input field with a `label` element, placed outside the field.
- Error messages state what went wrong and how to fix it: "Name is a required field."
- Form-submission buttons use the native `button` element.

### CSS and JavaScript

- Color contrast ratios of at least 4.5:1 for text.
- Never `visibility:hidden` or `display:none` — both hide content from screen readers.
- Avoid mouseover events; if you use them, add matching focus and blur events for
  keyboard users.
- Ordering and positioning in styles must match the DOM and the reading order.

### Document rendering

The document must convey everything you intended when read without sound, using only
sound, without images or animation, without color, with a keyboard only, with screen
magnification, and without punctuation.

- Never use color, size, or position as the only way to communicate something. If color,
  an icon, or outline thickness conveys state, add a text cue too.
- **Refer to controls by their label**, not their appearance. "Click **Save**." "Click
  **Notifications**." Not "Click the bell icon." For visual elements with no text, use
  the element's `aria-label`.
- **No directional language.** Not *above*, *below*, *right-hand side* — what's on the
  right in a left-to-right language is on the left in a right-to-left one, and nothing is
  "below" when a screen reader is reading it. Use *earlier*, *preceding*, *later*,
  *following*.
  - Recommended: "In the preceding diagram, clients run jobs on multi-team clusters."
  - Not recommended: "In the diagram above…"
- If a UI element is hard to find, provide a screenshot, name its icon, or give context
  ("On the Cloud Run toolbar, click **Refresh**") — not "In the left-side panel, click
  the button with three lines."

---

## Write inclusive documentation

> This section names potentially disrespectful terms in order to give usage guidance and
> alternatives.

Writing with inclusivity and diversity in mind makes content more precise and clearer
for everyone. Most of it comes down to avoiding figurative language that can be
misinterpreted or distracting.

### Avoid unnecessarily gendered language

| Recommended | Not recommended |
|---|---|
| Equipment installation takes around 16 person-hours to complete. | …16 man-hours… |
| Build AI that benefits humanity. | Build AI that benefits mankind. |

Use singular *they*. Never *he/she*, *(s)he*, or a gendered pronoun as a generic.

### Avoid figurative language

Use terms in their primary sense. Don't use metaphors — avoid, for example, the
"pets versus cattle" metaphor for stateful versus stateless systems.

**Ableist language** — *crazy*, *insane*, *blind to*, *cripple*, *dumb*, *lame*, *sanity
check*:

| Recommended | Not recommended |
|---|---|
| Give everything a final check for completeness and clarity. | Give everything a final sanity-check. |
| There are some baffling outliers in the data. | There are some crazy outliers in the data. |
| It slows down the service, causing a poor user experience. | It cripples the service… |
| Replace the placeholder in this example with the appropriate value. | Replace the dummy variable… |

**Graphic or metaphorical language.** Prefer a precise term — "fence failed nodes"
rather than STONITH. If you must name such a term, mention it once when you first explain
the feature, phrased so it's de-emphasized: "This approach might require you to fence
failed nodes (sometimes referred to as STONITH)."

| Recommended | Not recommended |
|---|---|
| If the connection doesn't respond, check for errors. | If the connection hangs, check for errors. |
| Point to **File**, and then click **New**. | Hover over **File**, and hit **New**. |

Some industry-established terms have a precise technical meaning with no accurate
synonym — see *terminate* and *execute* in the word list, and the Linux signals table in
`formatting.md`.

### Write diverse and inclusive examples

- Follow the gender-neutral pronoun guidance.
- Avoid being culturally specific to the US: holidays, cultural practices, sports,
  figures of speech.
- Use a diverse set of names (see the example-names table in `structure.md`).
- Writing about older adults: not *the elderly*, *the aged*, *seniors*, *senior
  citizens*, or *80 years young*. Use *older adults* or *aging population*, or mention a
  relative age only when it's relevant.

### Write about features and users inclusively

Don't describe people in divisive ways — rather than *native speakers* and *non-native
speakers*, consider whether the document needs to discuss it at all, then rewrite in
terms that work regardless of what languages the reader knows.

Avoid socially charged terms for technical concepts: *blacklist*, *native feature*,
*first-class citizen* — even though they're still widely used.

### Replacing established non-inclusive terms

When a non-inclusive term is so established that replacing it outright would confuse
readers, name it once in parentheses on first use, then use the replacement throughout:

- "…add them to an allowlist (sometimes called a whitelist). Anyone who isn't on the
  allowlist is blocked…"
- "In this model, a Jenkins controller (master) handles HTTP requests. The Jenkins
  controller is designed to…"
- "…servers are treated as commodities (sometimes described by using the metaphor
  cattle, not pets)."

Often a rewrite beats a word swap. Rather than replacing the verb *whitelist* with
*allowlist*:

- Recommended: "You can allow requests from a range of IP addresses by entering a CIDR
  block instead of a single address in the field."
- Not recommended: "You can allowlist a range of IP addresses…"

### Non-inclusive terms in code

Sometimes the term is a name or keyword you can't change — a cluster named `master`, or
the SQL keyword `SLAVE`. Minimize its use so you don't propagate it as a term of art,
while still documenting clearly. **Never use a non-inclusive name or keyword outside of
code font.**

On the first reference to the code item, you can name it directly, in code font, in
parentheses where possible:

- "The configuration file helps you create a parent node (which is named `master` in the
  file)."
- "Start the replica by using the `START SLAVE` statement."

After that, use the preferred term — *parent node*, *replica*. If you need to refer to
the entity name or keyword again, keep it in code font.

### Writing about disability and accessibility

Research how the communities you're writing about prefer to be identified before you
write about them.

- **Don't describe people without disabilities as *normal* or *healthy*.** That implies
  people with disabilities are abnormal or sick. Use *nondisabled person*, *sighted
  person*, *hearing person*, *person without disabilities*, *neurotypical person*.
- **Generally avoid terms that define a person by their disability** — not *the
  disabled*, not *a quadriplegic*; use *people with disabilities*, *a quadriplegic
  person*. But many communities prefer identity-first language, notably autistic, blind,
  and Deaf communities, and capitalization conventions vary. Research and use the terms
  people use for themselves.
- **Avoid terms that project feelings or judgments:** not *victim of*, *suffering from*,
  *wheelchair-bound*. Use *experiencing*, *living with*, *uses a wheelchair*.
- **Avoid euphemisms and patronizing terms:** *physically challenged*, *special*,
  *differently abled*, *handi-capable*.

---

## Write for a global audience

Documentation gets translated, and it's read by developers whose primary language isn't
English. Write with localization, translation, and internationalization in mind.

- **Localization** — adapting a product and its documentation for a specific country.
  More than translation: local currencies, units of measurement.
- **Translation** — converting one language to another. May involve localization; not a
  synonym for it.
- **Internationalization** — designing the product and docs to minimize localization
  effort, such as by keeping UI strings in a separate file.

### Clear, concise, unambiguous language

**Simpler words, shorter sentences.**

- Don't use *commence* for *start*; *consequently* for *so*; *utilize* or *leverage* for
  *use*. (These words are fine when you genuinely mean them: "Cloud Spanner utilizes up
  to 100% of the available CPU resources.")
- A single word beats a phrase: *some* or *many* rather than *a number of*.
- Short sentences translate better. An average-length English sentence can become a long
  sentence in another language, causing rendering problems and raising translation cost.

**Avoid phrasal verbs.** "This document uses the following terms," not "This document
makes use of the following terms." Some are unavoidable and fine: *set up*, *log in*,
*sign in*.

**Use modifiers carefully.**

- No more than two nouns modifying another noun: "A cloud-native DevSecOps pipeline in a
  hybrid environment," not "A hybrid cloud-native DevSecOps pipeline."
- Place *only* immediately before what it modifies: "Request only one token," or
  "Request no more than one token" — not "Only request one token."

**Active voice, present tense**, and avoid complex or uncommon verb forms.

**Avoid participles and gerunds** where a clause is clearer. Replace *using* with *by
using*, *that use*, or *you use*.

| Recommended | Not recommended |
|---|---|
| You must configure the VPC firewall rules before you deploy the VM instance. | Configuring the VPC firewall rules is required before deploying the VM instance. |
| This guide describes how to set up database replication. | This guide describes setting up database replication. |

**Use words in their primary sense.** Don't use the same word to mean different things,
and avoid using a word as both a noun and a verb close together. See the word list for
*once*, *while*, *as*, and *since*.

**Avoid directional language** in procedural documentation.

### Helper and optional words

**Qualifying nouns for technical keywords:** call it "the `example.yaml` file," not
"`example.yaml`."

**Repeat a word when the redundancy improves comprehension.**

| Recommended | Not recommended |
|---|---|
| If the VM has started and if you're able to connect… | If the VM has started and you're able to connect… |
| …creates both IAM segmentation and network segmentation by default. | …creates both IAM and network segmentation by default. |
| An egress rule whose action is `allow`, whose destination is `0.0.0.0/0`, and whose priority is the lowest possible. | An egress rule whose action is `allow`, destination is `0.0.0.0/0`, and priority is the lowest possible. |

**Keep the helper words** conversational English drops — *then*, *that*, *of*, *and
then*.

| Recommended | Not recommended |
|---|---|
| If the attribute key is not found, then the default value is returned. | If the attribute key is not found, the default value is returned. |
| …assumes that you have the following knowledge: | …assumes you have the following knowledge: |
| Identify all of the datasets. | Identify all the datasets. |
| Start the profiler, and then run the app. | Start the profiler, then run the app. |

**Don't omit relative pronouns:** "the rules **that** you previously defined," not "the
rules you previously defined."

### Abbreviations, pronouns, apostrophes

- Define abbreviations; they're confusing out of context and translate badly.
- **Clarify antecedents.** Translators work with small, unconnected strings. If a pronoun
  is ambiguous, replace it with the noun: "If you use the term *green beer* in an ad,
  then make sure that **the ad** is targeted."
- Be careful with plurals and possessives: no `'s` plurals, no possessive or plural forms
  of trademarks, no uncommon contractions.

### Address the reader directly

- Use *you*, not *the user* or *they* — unless you mean the user of the software your
  reader is building.
- Provide context. Don't assume the reader already knows what you're talking about.
- Avoid negative constructions. Consider whether the reader needs to be told what they
  can't do instead of what they can.

### Be consistent

- **Consistent terminology.** Same concept, same term, same capitalization, everywhere.
  Different names for the same thing make translators think you mean different concepts,
  and inconsistency raises translation cost — particularly where translation memory and
  machine translation do the first pass.
- **Standardized phrases** for common jobs: introducing links, introducing output,
  introducing code samples.
- **Standard English word order**: subject, verb, object. Keep subject and verb near the
  start.
- **Condition first**, then the instruction.
- **Parallel, consistently punctuated list items.**
- **Consistent typographic formats.** Don't switch from italics to underlining for
  emphasis. Consistent capitalization.

### Be inclusive and culture-neutral

- Unambiguous dates and times.
- No holidays, cultural practices, or sports unless they're known worldwide.
- Diverse example names.
- No colloquialisms, idioms, or slang — *ballpark figure*, *back burner*, *hang in
  there*.
- **No humor.** Most humor is hard to translate, and much of it is culturally specific.
- No geographically specific references such as seasons. August isn't summer in the
  southern hemisphere.

### Images

Use screenshots and text in figures sparingly — images don't get translated. Any new
information must be in text, not introduced in a figure.
