# Formatting

Text formatting, code, commands, placeholders, math, images, and filenames. Adapted from
the Google developer documentation style guide (CC BY 4.0).

---

## Text-formatting summary

| Element | Markup | Use for |
|---|---|---|
| Bold | `<b>` / `**` | UI element names; run-in headings; the label at the start of a notice. Nothing else. |
| Italic | `<i>` / `_` | New terms you're defining; words as words; abbreviation introductions; titles of full-length works; mathematical variables; version variables; emphasis (`<em>` for semantic emphasis). |
| Underline | — | Link text only. |
| Code font | `<code>` / `` ` `` | Code in text, inline code, user input. |
| Code block | `<pre>` / ``` | Code samples and commands. |

- In Markdown, prefer `**` for bold over `__`, and `_` for italic over `*` — the two are
  easier to tell apart in a text editor.
- Use italics sparingly. Usually the words carry the emphasis without it. When you do
  need emphasis, use italics — not bold, not underline.
- Don't override font family, size, or color inline. Use semantic markup and let the
  site's CSS handle appearance.
- Don't use `&` as shorthand for *and*, including in headings and navigation. Exception:
  referring to a UI element or menu that itself uses `&`.
- Quotation marks and end punctuation go outside link text.
- Sentence case in all headings, titles, and navigation. All-caps for placeholders only.

### Italics for terms

Two cases:

- **A new term you define immediately.** "A *Clos network* is a kind of multistage
  circuit switching network." Not bold, not quotation marks.
- **Words as words.** "Don't use *&* (ampersand) as a conjunction. Use the word *and*
  instead." "To form a possessive of a singular noun, add *'s* to the end of the word."

---

## HTML, Markdown, and semantic tagging

Either HTML or Markdown is fine. Markdown is easier to write and read; HTML is more
expressive, particularly for semantic tagging, and can do things Markdown can't. If your
team or template already uses one, use that.

Use HTML elements for what they're designed for:

- `cite` for the title of a standalone work.
- `em` means emphasis, not italics — use `i` for non-emphasis italics.
- `strong` means strong importance, not bold — use `b` to bold something that isn't
  strongly important. (This is why UI element names use `b`.)
- `br` is for line breaks that are part of the content, like poems and addresses. Don't
  use it for spacing; use `p` and CSS.
- Don't use frames, tables, or heading elements for visual layout.

### HTML source formatting

Follow Google's HTML/CSS style guide, except don't leave out optional elements. These
apply to YAML and Markdown source too:

- Spaces, never tabs. Two spaces per indentation level.
- Lowercase elements and attributes.
- No trailing spaces (except where Markdown requires them).
- Break lines at 80 characters, except: `meta` element content must stay on one line,
  and a URL can't contain a line break. For a long URL, put it on its own line with the
  `href`:

  ```html
  You can find more information in
  <a href="https://example.com/long-url/…-of-ulm.html"
  >his biography.</a>
  ```

- Break code in `<pre>` blocks at 80 characters. If an existing file uses a different
  consistent line length, match it rather than reformatting the file. When you add line
  breaks to code, don't change its meaning — ask someone who knows the language if
  you're unsure.

---

## Code in text

Code font signals that text is meant to be entered verbatim, shows where its boundaries
are, and separates it from the surrounding prose.

### Put in code font

Attribute names and values · class names · command output · command-line utility names
(`gcloud`, `kubectl`, `bq`) · data types · database elements such as row and column
names · defined constant values · DNS record types · HTML and XML element names (without
angle brackets) · enum names · environment variable names · filenames, extensions, and
paths · folders and directories · HTTP content-type values · HTTP status codes · HTTP
verbs · IAM role names · IP addresses · language keywords · method and function names ·
namespace aliases · placeholder variables · package names · port numbers · query
parameter names and values · strings such as URLs or domain names used inside commands
and code · text the reader types · UI elements rendered from previously entered text.

Generally don't put quotation marks around code unless the marks are part of the code.

### Put in ordinary font

- Domain names: "standard application offerings from example.com."
- Names of products, services, and organizations.
- URLs the reader is meant to open in a browser — though it's usually better to make
  them links with descriptive text.

### Sometimes code font

- **Boolean values.** Code font when referring to the literal value: "If the update
  succeeds, returns `true`." Ordinary font when referring to the evaluation of a
  condition: "If true, validates the SSL certificate before proceeding."
- **Command-line utility names** that share a name with a product: code font for the
  command, ordinary font for the project. "Invoke the GCC 8.3 compiler using `gcc`."
  "The options for the `curl` command are explained on the curl project website."
- **Email addresses.** Code font as computer input or output: "enter `alex`, not
  `alex@example.com`." Ordinary font and hyperlinked as a way to contact someone: "For
  help, contact support@example.com."

### Code in UI elements

If a UI element meets the requirements for code font, use both code font and bold: "In
the **`my-net-2`** list, select…" — "In the **Network** list, select `my-net-2`."

### Grammatical treatment of code elements

Don't use code elements as English verbs or nouns, and don't inflect them. Add a noun
and inflect the noun instead.

| Recommended | Not recommended |
|---|---|
| The `ADDRESS` constant's value is defined in the `settings.h` file. | `ADDRESS`'s value is defined in `settings.h`. |
| To add the data, send a `POST` request. | `POST` the data. |
| You can't call the `close` method for a file before you call `open`. | `Close`ing the file requires you to have `open`ed it first. |
| Takes an array of `INT64` values and returns `BYTES` values. | Takes an array of extended ASCII code points (ARRAY of INT64) and returns BYTES. |

### Method names and status codes

- Omit the class name when referring to a method, unless it prevents ambiguity: "call
  its `get` method," not "call its `animal.get` method."
- HTTP status codes: "an HTTP `400 Bad Request` status code." Call it a *status code*,
  not a response code or error code. Number and name both in code font; drop `HTTP` when
  it's implicit. Ranges: "an HTTP `2xx` or `400` status code," or "an HTTP status code
  in the `200`-`299` range."

---

## Code samples

- Follow the indentation guidelines in the relevant language's style guide — usually
  spaces, two per level, though some contexts use four spaces or tabs.
- Wrap lines at 80 characters. Wrap narrower if readers will have narrow windows or
  print the page.
- Mark code blocks as preformatted: `pre` in HTML, a fence or four-space indent in
  Markdown.
- **Indicate omitted code with a comment in the language's own syntax**, not three dots
  and not an ellipsis character. A block containing an omission shouldn't be
  click-to-copy.

  ```yaml
  apiVersion: serving.knative.dev/v1
  kind: Service
  # Several lines of code are omitted here.
  spec:
    template:
  ```

- **Introduce a sample** with a sentence or paragraph. Colon if the intro immediately
  precedes the sample; period if there's other material in between, or if the intro ends
  on a sentence unrelated to the sample.
  - Recommended: "The following code sample shows how to use the `get` method. For
    information about other methods, see [link]. [sample]"
  - Recommended: "The following code sample shows how to use the `get` method: [sample]
    For information about other methods, see [link]."
  - Not recommended: "…shows how to use the `get` method. For information about other
    methods, see [link]: [sample]"

Language style guides: Google publishes public style guides for C++, HTML/CSS, Java,
JavaScript, Python, and others on GitHub. Some open source projects override them (Java
in AOSP, for example).

---

## Command-line syntax

### Best practices

- **Link to the command reference** inline, in the text that introduces the command or
  the series of steps.
- **Use as few arguments as possible** — enough to accomplish the task in the most
  common way. Rely on the reference for the full list.
- **Make the example copy-pasteable.** Include only runnable code and placeholders.
  Square brackets, braces, pipes, and ellipses break a command if the reader doesn't
  strip them, so keep them out of click-to-copy examples.

### Formatting a command

- `pre` in HTML, a code fence in Markdown.
- When a line exceeds 80 characters, break before a single hyphen, double hyphen,
  underscore, or quotation mark. Indent continuation lines by four spaces.
- Every line except the last needs the continuation character: `\` (preceded by a space)
  on Linux, `^` on Windows.
- Format placeholders as placeholders, and follow the command with a descriptive list of
  them.
- End punctuation for option and argument descriptions: use it for complete sentences,
  not for single words or noun phrases — unless the list mixes both.
- For `bash` or `sh` commands, follow the quotation-mark style in Google's shell style
  guide.

### Command prompt

- Start each input line with the prompt symbol when showing multiple lines of input. Turn
  off text selection for the symbol if you can.
- Don't show the current directory path before the prompt, even when the instructions
  change directories. Do add a prompt indicator when the context changes — from the local
  machine to a remote one, for example.

  ```
  $ adb shell
  shell@ $ screencap /sdcard/screen.png
  shell@ $ exit
  $ adb pull /sdcard/screen.png
  ```

- The prompt is optional for a single-line command. If a document mixes single-line and
  multi-line commands, use the prompt for all of them.
- Use separate code blocks for input and output.

### Argument notation

| Notation | Meaning |
|---|---|
| `[ARG]` | Optional. Each optional argument gets its own brackets: `gcloud dns GROUP [GLOBAL_FLAG] [FILENAME]` |
| `{A\|B}` | Mutually exclusive — choose exactly one: `{FILE_1\|FILE_2}` |
| `...` | The argument can repeat: `gcloud dns GROUP [GLOBAL_FLAG ...]` |

### Keeping click-to-copy commands clean

Because that notation breaks commands, choose one of these instead:

1. **Remove the optional arguments** and link to the command reference. "If you want to
   narrow the list to a zone, use the previous command with the `--zones` flag."
2. **Use a separate code block per option.** Show the base command, then "If you're
   importing an image with an existing license, specify the `--byol` flag:" followed by
   a second block.
3. **Document options as separate tasks** under their own headings.
4. **Tell the reader the command contains optional syntax** when you truly must include
   it: "In the following example, you optionally specify the `auto-delete` subflag…"

### Output

Don't show output for every command — only when it adds value, such as when the reader
must copy a value out of it or verify something in it.

Introduce it with "The output is similar to the following:" or "The output is the
following:". Customize when you want to call something out: "The output is similar to
the following, in which the `IP` column shows the IP address for each resource:".

Indicate omitted output lines with three dots (`...`) on their own line — not the
ellipsis character.

### Command-line terminology

Don't map one CLI's nomenclature onto another's. Describe what the whole command does
rather than naming each element, and ask whether the reader needs the element names at
all.

- **gcloud CLI:** a *command* or *command group*; docs generally just say *command*. A
  *flag* is anything other than the command or group name. Commands and flags can take
  *arguments*. *Option* works as a catchall when you don't want to get into
  nomenclature.
- **Linux:** commands take *options*, *parameters*, and *arguments*. `-follow` is an
  option (the hyphen is part of it); `-type f` is an option with a value; `*` is a
  metacharacter for globbing; `|` pipes; `>`, `<`, `<<`, `>>` redirect.

### Linux signals

These are the one context where words normally discouraged elsewhere are correct. Don't
substitute softer synonyms.

| Signal | Meaning | Don't substitute |
|---|---|---|
| `SIGKILL` | Kills a process; can't be caught, blocked, or ignored. | cancel, end, exit, quit, stop, terminate |
| `SIGTERM` | Requests termination, giving the process a chance to clean up. | cancel, end, exit, quit, stop |
| `SIGQUIT` | Quit signal from a keyboard; can be caught, blocked, or ignored. | cancel, end, exit, quit, stop |
| `SIGINT` | Interrupts immediately; terminates gracefully by default (Control+C). | suspend, end, exit, pause, terminate |
| `SIGPAUSE` | Pause, or sleep, until a signal arrives. | cancel, interrupt |
| `SIGSUSPEND` | Temporarily suspend execution. | pause, exit |
| `SIGSTOP` | Stop execution for later continuation; can't be caught, blocked, or ignored. | cancel, end, exit, interrupt, quit, terminate |

---

## Placeholders

Placeholders stand for values the reader must replace, and for values that vary in
example output.

### Format

**Text:** uppercase with underscore delimiters — `API_NAME`, `METHOD_NAME`. Not
`API-name`, `API_name`, `api_name`, `apiName`. If uppercase-with-underscores is a bad
fit for the context, pick something else and be internally consistent.

No possessive adjectives: not `MY_API_NAME`, not `YOUR_API_NAME`.

Avoid a bare `x` or a run of `x`s as a placeholder — use something informative. Exception:
contexts like HTTP status codes where `xx` is the convention.

**Markup:**

| Context | HTML | Markdown |
|---|---|---|
| Inline, in code | `<code><var>PLACEHOLDER</var></code>` | `` *`PLACEHOLDER`* `` |
| Inline, not code | `<var>PLACEHOLDER</var>` | — |
| In a code block | `<pre>…<var>PLACEHOLDER</var>…</pre>` | Plain text inside the fence (no formatting is possible there) |

Bracket, brace, and ellipsis notation goes *outside* the `var` element.

### Explaining placeholders

Explain each placeholder the first time you use it. Repeat the explanation only when
it helps — a long document, several placeholders in one long procedure, or a document
that isn't read start to finish.

**One placeholder:** "Replace `BUILD_ID` with the ID of the `WORKING` build that you
copied in the preceding step."

**Two or more:** introduce the list with "Replace the following:", list them in the
order they appear in the command, and give each as a code-and-`var` item followed by a
colon and a lowercase description.

```
    bq mk \
        --project_id=ADMIN_PROJECT_ID \
        --location=LOCATION \
        --reservation RESERVATION_NAME

Replace the following:

- `ADMIN_PROJECT_ID`: the project that owns the reservation
- `LOCATION`: the location of the reservation
- `RESERVATION_NAME`: the name of the reservation
```

If a description needs an example, introduce it with an em dash or *such as*: "`ZONE`: a
zone close to your location—for example, `us-east1`."

**In output:** same pattern, but introduce the list with "This output includes the
following values:".

---

## Mathematical notation

Use HTML entities rather than keyboard symbols, so the markup is valid and assistive
technology reads it correctly. Keyboard symbols are fine for `+`, `=`, and `/`.

| Symbol | Markup | | Symbol | Markup |
|---|---|---|---|---|
| − | `&minus;` | | ≈ | `&asymp;` |
| × | `&times;` | | ≉ | `&nap;` |
| ≠ | `&ne;` | | ≅ | `&cong;` |
| ± | `&plusmn;` | | ≤ | `&le;` |
| ∓ | `&mnplus;` | | ≥ | `&ge;` |
| < | `&lt;` | | ≡ | `&equiv;` |
| > | `&gt;` | | ≢ | `&nequiv;` |
| √ | `&radic;` | | ∑ | `&sum;` |

You can also use the dot operator (`&#8729;`) or asterisk operator (`&#42;`) for
multiplication to match a UI, and you can omit the multiplication symbol entirely when
that's unambiguous (*ab* rather than *a × b*). Don't use a plain asterisk for
multiplication in text.

- **Operators:** nonbreaking space on both sides, inside a single expression. Don't
  italicize them.
- **Variables:** italicize. HTML `<i>x</i>&nbsp;&ne;&nbsp;<i>y</i>`; Markdown
  `_x_&nbsp;&ne;&nbsp;_y_`.
- **Expressions and equations:** inline when short, with nonbreaking spaces between
  components. Put it on its own line when it causes an awkward line break.
- **Exponents:** `<sup>`, no space between base and exponent. Never the caret (`2^3`).
  **Subscripts:** `<sub>`.
- **Fractions:** express as decimals when you can. As words, hyphenate the numerator and
  denominator unless one is already hyphenated: *one and one-half*, *three-sevenths*,
  *three seventy-fourths*.
- **Notation as words:** use notation in running text when it's clearer — "Check whether
  *a* > *b*" beats "Check whether *a* is greater than *b*." Use words when notation
  would be ambiguous or ungrammatical — "The area is calculated by multiplying the length
  by the width" beats "…by multiplying *l* × *w*."
- For complex or multiline equations, use a dedicated math rendering tool, a diagram, or
  an image.

---

## Filenames and file types

### Naming

- Lowercase, with occasional exceptions for consistency. Most Unix-like systems are case
  sensitive, so `Impersonate-Service-Accounts.html` and
  `impersonate-service-accounts.html` are different files.
- Hyphens, not underscores — search engines read hyphens as word separators and
  generally don't recognize underscores.
- Standard ASCII alphanumerics only.
- No generic names like `document1.html`.

| Recommended | Sometimes OK | Not recommended |
|---|---|---|
| `avoiding-cliches.jd` | `avoiding_cliches.jd` | `avoidingcliches.jd`, `avoidingCliches.jd`, `avoiding-clichés.jd` |

Exception: if a directory already uses underscores throughout and changing it isn't
feasible, stay consistent — add `lesson_4.jd` next to `lesson_1.jd`. Generated reference
docs may also follow the naming conventions of the product or API.

### Referring to files

- Code font, and include the word *file* after the name: "In the following `build.sh`
  file, modify the default values."
- Use the exact spelling even when it breaks the naming guidelines.
- Don't use a file type as a verb: "Extract a zip file," not "Unzip a zip file."
- Refer to a file type by its formal name, not its extension: "a PNG file," not "a
  `.png` file"; "a Bash file," not "an `.sh` file."

| Extension | File type name | | Extension | File type name |
|---|---|---|---|---|
| `.adoc` | AsciiDoc file | | `.pdf` | PDF file |
| `.csv` | CSV file | | `.png` | PNG file |
| `.exe` | executable file | | `.ps` | PowerShell file |
| `.gif` | GIF file | | `.py` | Python file |
| `.img` | disk image file | | `.sh` | Bash file |
| `.ipynb` | IPYNB file | | `.sql` | SQL file |
| `.jar` | JAR file | | `.svg` | SVG file |
| `.jpg`, `.jpeg` | JPEG file | | `.tar` | tar file |
| `.json` | JSON file | | `.tf` | Terraform file |
| `.md` | Markdown file | | `.tiff` | TIFF file |
| `.txt` | text file | | `.wasm` | Wasm file |
| `.yaml` | YAML file | | `.zip` | zip file |

---

## Diagrams, figures, and other images

Use images only when they explain something that's genuinely hard to express in words.
For screenshots, capture only the UI that matters to the discussion.

### Creating and saving

- Never use images of text, code samples, or terminal output. Use actual text.
- Diagrams: SVG where possible (stays sharp when zoomed); otherwise PNG. Never a
  transparent background.
- Animation and video: not animated GIF. Use a more efficient format such as MP4.
- Be consistent across a doc set: same operating system for screenshots, same treatment
  of drop shadows.
- Crop screenshots to the relevant area. This helps the reader focus and future-proofs
  the image against unrelated UI changes.
- **Never include PII.** If the source includes it, cover it with a solid-color overlay
  at 100% opacity — blurs and mosaics can be reversed. Flatten layered exports (PDF,
  TIFF).
- No image maps: they're bad for accessibility, inconsistent across browsers, and hard
  to maintain. Provide a list of text references after the image instead.
- Descriptive filenames.

### Text associated with images

Introduce most images with a complete sentence — colon if it immediately precedes the
image, period otherwise. Screenshots that immediately follow procedural text describing
the UI don't need an introduction.

**Alt text.** A concise description that can stand in for the image. Required on every
`img` element, even when empty — without the attribute, screen readers may read the
filename aloud.

- Use `alt=""` for decorative images and for images that only restate adjacent text:
  screenshots showing how to fill out fields, UI icons, purely visual images.
- Don't write "Image of" or "Photo of."
- Include punctuation — screen readers pause at it.
- Consistent alt text for repeated images.
- Avoid all-caps; some screen readers read capitals letter by letter.
- Full sentences or a noun phrase: `alt="Architecture of an app that's built with Apps
  Script."`, `alt="A card message."`
- 155 characters or fewer. If the image carries more information than that, summarize in
  `alt` and give the full description in the body text.
- Introduce diagrams in the text, not in the alt text. Don't use a caption as alt text.
- Consider the image's context, not just its content.

**Figure captions.** Optional, as are figure numbers. Wrap `figcaption` and `img`
together in a `figure` element. Form: "**Figure 1.** Application capabilities are
separated into bounded contexts that migrate to services." Complete sentences, always
with end punctuation. Refer to figures by number ("as shown in figure 1"), lowercase
*figure* except at the start of a sentence. Never spatial references like "the image
above." Don't repeat the caption in the sentence that references the figure. If you
can't use figure numbers, show the figure again rather than referring back to it.

**Figure descriptions.** Body text conveying the same information as the figure. Any new
information must be in text, never only in an image. Use one when the caption can't
carry the figure's full meaning.

**Text inside figures.** Avoid it — it hurts accessibility and searchability and raises
localization cost. When you must: keep it brief, avoid complete sentences and
punctuation, don't invent abbreviations to fit, use sentence case, don't embed captions
or descriptions, use full trademarked product names, and use numbered callouts to
structure the figure description rather than for detailed annotation.

### High-resolution images

Use `srcset` alongside `src`:

```html
<img src="/assets/images/skateboard.png"
     srcset="/assets/images/skateboard.png 1x,
             /assets/images/skateboard_2x.png 2x"
     width="375" alt="" />
```

- `width` matches the CSS pixel size; height is calculated, so don't state it.
- `src` points at the 1x image, not the 2x — it's the fallback for older browsers on
  low-resolution devices.
- Name the double-resolution file `BASENAME_2x.EXTENSION`.
- The 2x image must be exactly twice the width and height, give or take a pixel.
- Never scale a 1x image up to make a 2x. Scale down from a high-resolution original.
- A browser that supports `srcset` ignores `src` entirely, so list every available
  resolution in `srcset`.

### Layout

- Don't position images manually with `style` attributes. Use the site's standard CSS.
- Don't make images too small; full column width is fine.
- Don't exceed the column width. Consider how the image prints.
- Don't center the image, and don't put an `img` inside a `p`.
- Don't link to a figure on the same page unless the page is very long and the link is
  far away.
