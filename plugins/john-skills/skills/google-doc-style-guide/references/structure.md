# Structure

Headings, paragraphs, lists, procedures, tables, notices, cross-references, and example
data. Adapted from the Google developer documentation style guide (CC BY 4.0).

---

## Sentence structure

Mention the circumstance, condition, or goal before the instruction, so a reader who
isn't in that situation can skip the rest of the sentence.

| Recommended | Not recommended |
|---|---|
| For more information, see [link]. | See [link] for more information. |
| To delete the entire document, click **Delete**. | Click **Delete** if you want to delete the entire document. |
| If your app is in one of the following regions, custom domains might add noticeable latency: | Custom domains might add noticeable latency if your app is in one of the following regions: |

Use standard English word order: subject, verb, object. Keep the main subject and verb
near the start of the sentence.

## Paragraph structure

- One idea per paragraph, in the fewest words and sentences possible.
- Break up walls of text. Readers scan, on screens of many sizes.
- Don't lengthen sentences to reduce the sentence count. Use shorter sentences *and*
  shorter paragraphs.
- More than 5 or 6 sentences usually means the paragraph is doing too much — but a long
  paragraph about a single idea is fine, and so is a one-sentence paragraph.
- Put the key point first. Don't bury it at the end.
- Left-align. Don't center, full-justify, or right-align. Don't force hard line breaks
  inside sentences — they break on resize, on other devices, and at larger text sizes.

---

## Headings and titles

Use sentence case. Make headings descriptive and unique — they're how readers navigate.

### Choosing the phrasing

| Guidance | Recommended | Not recommended |
|---|---|---|
| Task-based heading: start with a base-form (bare infinitive) verb. Common in quickstarts, how-tos, tutorials. | Create an instance | Creating an instance |
| Conceptual heading: a noun phrase that doesn't start with an `-ing` verb. Common in concept docs. | Migration to Google Cloud | Migrating to Google Cloud |
| Section that doesn't apply to everyone: use an `Optional:` prefix. | Optional: Customize your alias | Customize your alias (optional) |

Write the document title from the document's primary purpose. If a doc is mostly a
tutorial with a conceptual introduction, give it a task-based title. Mixing task-based
and conceptual headings within one document is fine — match each section's own content.

Avoid `-ing` forms as the first word of any heading: they're translated inconsistently
and they lengthen titles in constrained spaces. *Billing* and *Pricing* are acceptable
exceptions. An `-ing` form later in a heading is fine: "Introduction to BigQuery
monitoring."

### Title and heading format

- One `h1` per page, unique within the doc set.
- Don't repeat the exact page title as a section heading. If the page is "Create and
  start VM instances," the sections can be "Create a VM" and "Start a VM."
- No period at the end. Keep punctuation simple — complicated punctuation is a sign the
  heading is too complicated.
- Contractions and articles follow the same rules as body text: "Create **a** VM
  instance."
- Use an abbreviation in a heading only if it's the better-known form of the word. If
  you do, define it in the first paragraph that follows.
- No numbers to indicate sequence — rely on hierarchy and order.
- No links in headings; a link reads as styling applied to the heading.
- Avoid code items in headings. If unavoidable, add a descriptive noun in ordinary font:
  "The `config.yaml` file."
- Use real heading elements (`h1`/`h2`/`h3`, or `#`/`##`/`###`) for hierarchy, and CSS
  for visual style. Never pick a heading level for how it looks.
- Don't skip levels: an `h3` goes under an `h2`.
- Don't leave a heading with no content under it. Put at least an introductory sentence
  between a heading and its subheadings.

### Referring to a group of sections

To introduce several subsections, write "**The following sections** describe…". Never
"this section" or "these sections" — both are ambiguous.

### Headings as link targets

Add a custom anchor when the auto-generated one is long, when the heading is likely to
be linked to often, or when you're about to change the heading text and want existing
links to keep working.

HTML — all acceptable:

```html
<section id="introduction-to-everything"><h2>Introduction to everything</h2>…</section>
<h2><a name="introduction-to-everything">Introduction to everything</a></h2>
<a name="introduction-to-everything"></a>
<h2>Introduction to everything</h2>
<h2 id="introduction-to-everything">Introduction to everything</h2>
```

Markdown:

```
## Help conserve habitat for pollinators {: #conserve-habitat }
```

Anchor text is lowercase with hyphens between words. When you revise a heading that has
an auto-generated anchor, add a custom anchor using the *old* ID string so existing
links keep working. Don't change an existing custom anchor unless it contains a term you
need to remove.

---

## Lists

### List or table?

| Each item is… | Present as |
|---|---|
| A single unit (language names, steps) | Numbered, lettered, or bulleted list |
| A pair of related pieces of data (term/definition) | Description list, or sometimes a table |
| Three or more related pieces of data (name, type, description) | Table |

### List types

- **Numbered list** (`ol`/`li`) — a set where sequence is significant: steps, phases,
  priorities. Nested sequential lists use lowercase letters, then lowercase Roman
  numerals.
- **Bulleted list** (`ul`/`li`) — a set that isn't a sequence. Make clear whether every
  item is required.
- **Description list** (`dl`/`dt`/`dd`) — terms with definitions, when you want to draw
  attention to the terms (a glossary, for example).
- **Description list with bulleted run-in headings** (`ul`/`li`) — introductory terms
  with explanations, when you want to save space: "**Emu**: the best kind of bird."

Never use a list for a single item. To set one item off from surrounding text, use some
other formatting.

Any list item can contain multiple paragraphs. Use `p` elements, not `br`.

### Introducing a list

Precede most lists with an introductory sentence. Use a colon if the intro immediately
precedes the list, a period if other material (such as a note) sits between them. Skip
the intro only when the heading immediately above already provides the context.

The introduction must be a complete sentence, not a fragment the list items complete.

| Recommended | Not recommended |
|---|---|
| Use the **Submit** button for any of the following purposes: | Use the **Submit** button to: |
| To get the USB driver, follow these steps: | To get the USB driver: |
| If you need to add an instance manually, do the following: | If you need to add an instance manually: |
| **Objectives**<br>• Create an instance | **Objectives**<br>In the following tutorial, you will complete the following tasks:<br>• Create an instance |

*The following* works as a noun phrase: "do the following:".

### Capitalization and end punctuation

**Numbered, lettered, and bulleted lists.** Start each item with a capital letter unless
case carries meaning (a list of glossary terms, for example). End each item with a
period or other sentence-ending punctuation, except when the item:

- consists of a single word,
- doesn't include a verb,
- is entirely in code font, or
- is entirely link text or a document title.

If that leaves the list inconsistently punctuated, either rewrite for parallel
construction or punctuate every item.

```
The following words are adjectives:      You can do any of the following:
- Big                                     - Create an item.
- Small                                   - Replace one item with another.
- Gratuitous                              - Update an item.
```

**Description lists.** Capitalize each term. No period after the term; a period at the
end of each description.

**Run-in headings.** Capitalize the heading. End it with a period or a colon, and be
consistent within the list. After a period, start the description with a capital and end
it with a period. After a colon, start with lowercase; end with a period only if the
description contains a verb or expresses a standalone thought.

```
The following words are adjectives:
- Big: a short word
- Relevant: a fancy word
- Purple: a vibrant color
```

Never use a dash to separate an item from its description — use a colon or a period.

Don't attach an explanatory phrase to only one item in a bulleted list. Convert the
whole thing to a description list instead.

> Note: these punctuation rules differ from Material Design's. If you're writing UI text
> rather than prose documentation, follow the design system.

### Other list guidance

- **Parallel syntax** across all items in a list.
- **Comma-separated lists in a paragraph** use serial commas. Don't end with *etc.* or
  *and so on* — introduce the list so it's clear it isn't exhaustive: "data like event
  logs, clickstream data, and e-commerce transactions."
- **Nonstandard numbering:** `reversed` for descending order; `value` to set a number
  manually (rarely a good idea — it breaks when items are added).

---

## Procedures

A procedure is a sequence of numbered steps for accomplishing a task.

### Introduction

Introduce with a sentence that adds context the heading doesn't already provide. If the
heading says it all, skip the intro. Colon if the intro immediately precedes the steps;
period if other material intervenes.

- Recommended: "To customize the buttons, follow these steps:"
- Also recommended: "Customize the buttons:"
- Also recommended: "To customize the buttons, do the following:"
- Not recommended: "To customize the buttons:" (a fragment completed by the steps)

### Single-step procedures

Write the step as one sentence and format it as a bulleted item.

- Recommended: "• To clear (flush) the entire log, click **Clear logcat**."
- Not recommended: "To clear the entire log, follow this step: 1. Click **Clear
  logcat**."

### Sub-steps

Lowercase letters for sub-steps, lowercase Roman numerals for sub-sub-steps. When a step
has sub-steps, treat it like a list introduction and end it with a colon or period.

### Order of components within a step

1. Describe the action.
2. Give the command, if any.
3. Explain the placeholders in the command.
4. Explain the command further, if needed.
5. Show the output, if it's useful.
6. In a separate paragraph, explain the result.

```
1. Plan the Terraform deployment:

       terraform plan -out=NAME

   Replace `NAME` with the name of your Terraform plan.

   The output is similar to the following:

       Plan: 26 to add, 0 to change, 0 to destroy.

   The output shows what resources to add, change, or destroy.
```

### Summary of procedure rules

| Guidance | Recommended | Not recommended |
|---|---|---|
| Start each step with an imperative verb | Clone the repository that contains the sample data. | You need the project ID later. Retrieve the project ID. |
| Use complete sentences | | |
| Use parallel structure and consistent verb forms | Download the service account key. Click **More**, and then click **Download**. | Download the key by clicking **More** and then clicking **Download file**. |
| Mark optional steps with `Optional:` | Optional: Type an arbitrary string… | (Optional) Type an arbitrary string… |
| Set the context (tool, environment) first — restate it in each procedure even when it repeats | In Cloud Shell, connect to the development cluster. | |
| State the location before the action | In Google Docs, click **File > New > Document**. | Click **File > New > Document** in Google Docs. |
| State the goal before the action | To start a new document, click **File > New > Document**. | Click **File > New > Document** to start a new document. |
| No directional language | Click **Menu**. / In the preceding diagram… | Click the button with three lines. / In the diagram below… |
| No *please* | To open a document, click **File > Open**. | To open a document, please click **File > Open**. |
| Say what the command does, not "run the following command" | In Cloud Shell, deploy the load generator:… | Run the following command:… |
| Include the Enter keypress in the step | Click the search box, type `custom function`, and then press Enter. | 1. Click the search box and type `custom function`. 2. Press Enter. |
| Don't document keyboard shortcuts as the path | Copy the command, and then paste it… | Press Ctrl+C, and then press Ctrl+V… |
| Give only the best way when several exist | | |
| Give prerequisites up front so the reader can prepare | The following hardware and software are required:… | |
| Use as few steps as possible; limit interruptions | | |
| One decision per step; one instruction per list item | | |

### Combining actions

Use one step per action, but you can combine sequential menu selections with angle
brackets: "Click **Next > Finish**." Don't let a step get long — split it instead.

### Steps that imply optionality

"To sort the data by date, click X" can read as optional. When the step is required and
the goal phrasing makes it sound otherwise, use the colon form: "Sort the data by date:
click X."

### Results and justifications

State the action first, the result second, in the same paragraph.

- Recommended: "Click **Run**. The query results appear after the query runs."
- Recommended: "1. Click **Enter**. 2. In the **New file** dialog that appears, click
  **Next**."
- Not recommended: "1. Click **Enter**. The **New file** dialog appears. 2. In the **New
  file** dialog, click **Next**."

Justifications work the same way: "Store the private key in a secure location. You need
it later."

### Repetition

Don't repeat a procedure. Reference and link to it: "Create a user as you did in the
previous step."

---

## Tables

### Where not to use tables

- Not for page layout — use CSS.
- Usually not for a single row.
- Not for a single column — make it a list.
- Not for code snippets.
- Not for long one-dimensional lists split into columns to save space. Tables are for
  two-dimensional data.
- Avoid tables in the middle of a numbered procedure.

### Table guidance

- **Introduce every table with a complete sentence** that describes its purpose — not
  all screen readers announce tables. Colon if the intro immediately precedes the table;
  period otherwise. Refer to position with "the following table" or "the preceding
  table."
- Don't put a table in the middle of a sentence.
- Avoid footnotes; if you must, place them immediately after the table.
- **Captions:** unnecessary if the document has only one table. With more than one in
  close proximity, caption each using a `caption` element as the first child of `table`,
  in the form "**Table 1.** Prehistoric birds". Sentence case, no period. Refer to
  tables by number ("as shown in table 2"), lowercase *table* except at the start of a
  sentence. Avoid linking to tables — refer to them by number.
- **Formatting:** no styling on the `table` element. Don't convey a header row through
  font or color — use `th`. Don't merge cells (`colspan`, `rowspan`). Sort rows
  logically, or alphabetically if there's no logical order. Split long or complex tables.
  Never present new information through an image or symbol alone — give it an `alt`
  attribute.
- **Column heads:** sentence case, concise, no end punctuation. Header cells in the
  first row and first column only, using `th` with an appropriate `scope`.
- Any cell can contain multiple paragraphs — use `p`, not `br`.
- Use responsive table CSS where you can.

---

## Notices

Offset information that isn't part of the flow of the text. But readers skip elements
outside their focus, so write the content as ordinary text first and then decide whether
it needs a notice at all.

Don't overuse notices — they lose their distinctiveness. Avoid putting two or more in a
row; if you need to, reorganize the content instead.

| Type | Use for |
|---|---|
| **Note** | An ordinary aside or tip. Useful but not critical. "Generating excessive amounts of traffic to external systems can resemble a denial-of-service attack." |
| **Caution** | Proceed carefully. "We don't recommend using a broad `0.0.0.0/0` range that would allow all traffic." |
| **Warning** | "Don't do this," or this step might be irreversible — lost money, lost work, a security breach. "Don't put a password on the command line; doing so is a security risk." |
| **Success** | A successful action or error-free status. Interactive or dynamic content only. |

### When a note is right

All three must be true:

- The information is relevant but not necessary right now — a reader who skips it still
  succeeds.
- Interrupting the reader here isn't an obstacle. The note isn't sending them down a
  different path.
- The information isn't part of the flow — not a continuation, a result, or a pointer to
  more information.

### When a note is wrong

- For cross-references.
- For prerequisites or steps the reader should have already taken — that belongs
  *before* the step.
- For a full procedural step.
- For anything the reader needs in order to succeed.
- For information that just describes what precedes it, such as expected results.

HTML, when your site doesn't specify its own:

```html
<aside class="note"><b>Note:</b> All VPC networks include firewall rules.</aside>
```

---

## Cross-references and linking

Cross-references generally point to nonessential information that adds to the reader's
understanding.

### Choose links selectively

Each link is a decision for the reader and a chance for them to lose their place.

- **Provide context on the page** instead of linking, when the reader needs only a
  definition, a brief concept, or a couple of steps. Link out when they'd need real
  depth in someone else's product or standard.
- **Don't duplicate links** to the same destination on a page. Exceptions: linking to a
  specific section, a very long page with links far apart, or a page with multiple entry
  points (a procedure section and a troubleshooting section, for example).
- **Link to the most relevant page**, and the most relevant heading on it.

### Write descriptive link text

Use the exact page title, or a descriptive phrase capitalized as part of the sentence.
Screen reader users often jump link to link without the words in between, and sighted
readers scan for links, so the text must stand alone.

- Put important words at the start of the link text.
- Don't reuse the same link text for different destinations in one document.
- Keep it short — never a sentence or paragraph.
- Never *this document*, *this article*, *click here*, or "Want more? Click here!"
- Don't use a URL as link text. (Exception: some legal documents.)
- Include the abbreviation: "Google Kubernetes Engine (GKE)" — all of it inside the link.
- Include the descriptive noun for code elements: "run the `gcloud instances create`
  command with the `--hostname` flag," with the whole phrase linked, not just the code.
- "This service supports the `GET`, `HEAD`, and `OPTIONS` methods" — not "the `GET`
  method, `HEAD` method, and `OPTIONS` method."

### Link introductions

Use consistent phrasing: "For more information, see X." or "For more information about
Y, see X." Include the *about* clause when the link text and surrounding context don't
make clear why you're sending the reader there. Use *about*, not *on*. Use *see*.

### Explain unexpected behavior

- **Downloads and email:** say so in the link text and name the file type. "download the
  security features PDF"; `<a href="mailto:…">send email to Technical Support</a>`.
- **Same-page links:** "see the Write descriptive link text **section of this
  document**."
- **Sections on another page:** if the section title matches one on the current page,
  add context: "see Install libraries in *Building new audiences…*."
- **New tabs:** don't force them. If you must, say so: "Accessible content (opens in a
  new tab)."
- **External domains:** don't use an external-link icon. If it matters that the reader
  is leaving, say so in the text.

### Punctuation and styling

- Punctuation goes outside the link tags: `see <a href="#Test">Test your code</a>.`
- Don't put linked cross-reference text in quotation marks.
- For an *unlinked* reference: quotation marks for a document section, short work, or
  part of a series; italics for a full-length work.
- Avoid linking outside the doc set from navigation. If you must, make it clear the
  reader is leaving.
- In sitewide CSS: contrast link color against body text, underline link text (and
  nothing else), and change the color of visited links using color-blind-friendly
  choices.

---

## Example domains, names, and other data

Never use real domain names, email addresses, people's names, phone numbers, project
names, credit card numbers, or other personally identifiable information. Use fictitious
examples or placeholders such as `USER_ID`.

| Kind | Use |
|---|---|
| Domains | `example.com`, `example.org`, `example.net` (IANA-reserved), or `altostrat.com`, `examplepetstore.com`, `example-pet-store.com`, `myownpersonaldomain.com`, `my-own-personal-domain.com`, `cymbalgroup.com` |
| Internationalized domains | An IDN Test TLD |
| Email | A reserved domain plus an example name: `dana@example.com`. Generic addresses like `support@example.net` are fine. Never person names, product names, or made-up names in the local part. |
| Person names | Alex, Amal, Ariel, Bola, Charlie, Cruz, Dana, Dani, Hao, Ira, Izumi, Jie, Kai, Kalani, Kim, Kiran, Lee, Lucian, Luka, Mahan, Noam, Nur, Quinn, Raha, Rosario, Sasha, Tal, Taylor, Tristan, Yuri |
| Surnames | An initial after the given name: "Quinn N.", "Dana A." |
| Company | Example Organization. To distinguish two: Enterprise Example Organization, Startup Example Organization. |
| Phone (US) | 800-555-0100 through 800-555-0199 |
| IPv4 | `192.0.2.0`–`192.0.2.255`, `198.51.100.0`–`198.51.100.255`, `203.0.113.0`–`203.0.113.255` (RFC 5737). Ranges: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`. |
| IPv6 | `2001:db8::`, `2001:db8:1:1:1:1:1:1`, … (RFC 3849). Range: `2001:db8::/32`. |
| Street addresses | 1800 Amphibious Blvd., Mountain View, CA 94045 · Avenida da Pastelaria, 1903, Lisbon, 1229-076 · 8 Rue du Nom Fictif, 341 Paris |
| Project names | Meaningful and descriptive, applicable to the reader's environment: `staging`, `frontend-development`, `production-1`. Never `foo`, `bar`, `baz`. |
| Service account IDs | `123456789012345678901` |

### Writing about fictitious people

Real people read your examples. Include a variety of people — different jobs, cultures,
and backgrounds. Use singular *they* and avoid specifying gender unless it's integral;
be aware that some names on the list imply a gender in some languages or cultures. Watch
for stereotypes: which personas get executive roles, which get engineering roles.

Don't use the Alice and Bob cast unless you're documenting a technical specification
that uses them — and then use only names from that cast.

---

## Format examples

| Guidance | Recommended | Not recommended |
|---|---|---|
| Short-to-medium example at the end of a sentence: set it off with a comma, parentheses, or an em dash. Avoid a semicolon. | Choose a strong encryption algorithm, such as AES-256.<br>You can monitor various metrics—for example, CPU utilization, storage capacity, and active connections.<br>The API supports common image formats like PNG and JPEG. | Enter a name for the instance, for example, `my-instance-99`.<br>Specify the region; for example, `us-central1`.<br>Enter a name for the instance (for example, `my-instance-99`). |
| Short example mid-sentence: keep it short, set it off with dashes, commas, or parentheses. | Enter a six-digit hex number (for example, `228B22`), and then click **OK**.<br>The VM requires an operating system, such as Ubuntu 22.04, to be installed. | Enter a six-digit hex number (for example, if you want forest green, enter `228B22`), and then click **OK**. |
| Longer example: make it its own sentence, using *for example* as an adverb. | You can assign tags to your VM instances to categorize them. For example, you could tag instances by environment with `env:prod` or `env:dev`. | |

*such as*, *like*, and *include* all introduce non-exhaustive lists — don't combine them
with *etc.*, *and so forth*, or *and more*. Don't use *for instance*: it collides with
the noun *instance*.
