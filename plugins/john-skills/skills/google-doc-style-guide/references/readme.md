# Open source READMEs

> **Extension.** The Google developer documentation style guide doesn't cover READMEs.
> This file applies that guide's rules — procedures, code formatting, timeless
> documentation, excessive claims, accessibility — to the README as a document type. The
> rules elsewhere in this skill all still apply; nothing here overrides them.

A README is a front door, not a manual. It exists to move a stranger from "what is this?"
to a working install as fast as possible, and then to hand them off to the real
documentation. Every sentence that doesn't serve that is competing with the sentences
that do.

**The size test.** If a section runs past roughly one screen, it belongs in `docs/` with
a link from the README. If the whole README runs past what a reader will scroll, the
quick start is no longer above the fold and the README has failed at its one job.

---

## Structure

| # | Section | Purpose |
|---|---|---|
| 1 | Title and one-line description | What it is, in one sentence |
| 2 | Context (2-4 sentences) | What problem it solves, who it's for |
| 3 | Quick start | Shortest path to a verifiable working result |
| 4 | Installation | Every supported install path |
| 5 | Configuration | Minimum working config, then the option reference |
| 6 | Usage | The few tasks most readers actually perform |
| 7 | Troubleshooting | Only the failures readers actually hit |
| 8 | Documentation | Links to the real docs |
| 9 | Contributing | Or a link to `CONTRIBUTING.md` |
| 10 | License | One line |

Sections 3, 4, and 5 are the core. Everything else earns its place or gets cut.

### Annotated skeleton

```markdown
# projectname

One sentence: what it is and what it does.

[![Build](…)](…) [![Version](…)](…) [![License](…)](…)

Two to four sentences of context. What problem this solves, who it's for, and the
one thing that makes it different — stated as a fact, not a boast. Link anything
deeper: for the design rationale, see docs/architecture.md.

## Quick start

Prerequisites: Python 3.12 or later. To check, run `python3 --version`.

1. Install the package:

       pip install projectname

2. Create a configuration file at `~/.config/projectname/config.toml`:

       [server]
       host = "127.0.0.1"
       port = 8080

3. Start the server:

       projectname serve

   The output is similar to the following:

       projectname 2.4.0 listening on http://127.0.0.1:8080

4. In a second terminal, confirm the server responds:

       curl http://127.0.0.1:8080/healthz

   The output is the following:

       {"status":"ok"}

For what to do next, see [Usage](#usage).

## Installation

### pip

    pip install projectname

### Docker

    docker run --rm -p 8080:8080 ghcr.io/example/projectname:2.4.0

### From source

Use this path if you're contributing.

    git clone https://github.com/example/projectname.git
    cd projectname
    pip install --editable .

### Supported platforms

| Platform | Versions |
|---|---|
| Linux | glibc 2.31 or later |
| macOS | 13 or later |
| Windows | 10 or later, with WSL 2 |

To verify the installation, run `projectname --version`. To remove it, run
`pip uninstall projectname`.

## Configuration

### Minimum configuration

The smallest configuration that runs. Save it as
`~/.config/projectname/config.toml`:

    [server]
    host = "127.0.0.1"
    port = 8080

### Options

Settings are read from the configuration file, then environment variables, then
command-line flags. Later sources override earlier ones.

| Option | Environment variable | Type | Default | Description |
|---|---|---|---|---|
| `server.host` | `PROJECTNAME_HOST` | string | `127.0.0.1` | Address to bind to. |
| `server.port` | `PROJECTNAME_PORT` | integer | `8080` | Port to listen on. |
| `server.workers` | `PROJECTNAME_WORKERS` | integer | `4` | Worker processes. |
| `log.level` | `PROJECTNAME_LOG_LEVEL` | string | `info` | One of `debug`, `info`, `warn`, `error`. |

The API token is read from `PROJECTNAME_TOKEN`. Generate one in your account
settings. Don't put it in the configuration file.

## Usage
…
```

---

## The quick start

The quick start is a procedure. Everything in the Procedures section of
`structure.md` applies: an imperative verb per step, location before action, one action
per step, `Optional:` for optional steps, no directional language.

What's specific to a README quick start:

### Make every command exact

- **No notation the reader must strip.** No `[optional]`, no `{a|b}`, no `...`, no shell
  prompt characters, no angle-bracket placeholders. A reader should be able to select the
  block, paste it, and have it run. (This is the click-to-copy rule from
  `formatting.md`.)
- **No values the reader has to edit** unless there's no alternative. When there is no
  alternative, use the documented placeholder format — `UPPERCASE_WITH_UNDERSCORES` —
  and explain it in the sentence immediately after the block: "Replace `API_TOKEN` with
  the token from your account settings."
- **Pin what needs pinning.** A `docker run` line or a `curl | sh` line with a floating
  tag will drift. Use an explicit version, and put the version in one place if you can.

### Run the commands before you publish them

Copy commands out of a real terminal session. Invented flags, near-miss subcommand
names, and package names that don't exist on the registry are the most common README
defect and the most expensive one — the reader hits it in the first thirty seconds and
concludes the whole project is unmaintained.

When you're writing a README for code in front of you, check each command against the
actual CLI definition, `package.json` scripts, `Makefile`, or entry points. Check the
package name against the registry. Check the default values against the code.

### State prerequisites as checkable versions

Put them immediately before the first command, not in a separate section three screens
up.

| Recommended | Not recommended |
|---|---|
| Prerequisites: Node.js 20 or later. To check, run `node --version`. | Prerequisites: a recent version of Node.js. |
| Prerequisites: Docker 24 or later, and a Docker daemon that's running. | You'll need Docker installed. |

If the prerequisite list runs past three items, the quick start is too long — provide a
container image instead and let the image carry the dependencies.

### End with proof it worked

The last step must produce output the reader can compare against. Introduce it with the
standard phrasing — "The output is similar to the following:" when values vary, "The
output is the following:" when they don't — and show the real output.

Without a verification step, a reader can't distinguish success from a silent failure,
and every subsequent problem gets reported as a bug in your project.

### Don't teach here

No architecture, no vocabulary lesson, no explanation of why the tool works the way it
does, no discussion of alternatives. Link to all of it. The reader who wants concepts
will follow the link; the reader who wants a working install will not forgive the
detour.

---

## Installation

The quick start shows one way in. This section shows the rest.

- **One subsection per install path** — package manager, container image, prebuilt
  binary, from source. Give the exact command for each.
- **Say what each path is for** when it isn't obvious: "Use this path if you're
  contributing."
- **Put platform and version support in a table**, not in prose. A table survives updates;
  a sentence that says "we currently support macOS 13 and later" goes stale and violates
  the timeless-documentation rule. (A compatibility table is the correct place for
  version facts — see `names-and-claims.md`.)
- **Give the verification command** — usually `TOOL --version`.
- **Give the uninstall command.** It's two lines and it builds trust.
- **Don't document unreleased install paths.** No "Homebrew support is coming soon." See
  the future-features rule.

---

## Configuration

### Minimum working configuration

Give the smallest complete configuration that runs, as a copy-pasteable file, with one
sentence saying where the file goes. This is the thing readers copy; make it correct and
make it minimal. Don't pad it with commented-out options — that's the reference table's
job.

### Option reference

A table with a row per option: name, type, default, description. Add an environment
variable column if the project supports one.

- **Read every default out of the code.** Don't assume, and don't carry over a default
  from an older version. A wrong default in a README is worse than no default, because
  the reader trusts it and doesn't check.
- **State the precedence order explicitly** when settings can come from more than one
  source: "Settings are read from the configuration file, then environment variables,
  then command-line flags. Later sources override earlier ones."
- **Descriptions are sentence case and end with a period.** Enumerate valid values in
  code font: "One of `debug`, `info`, `warn`, `error`."
- **Say which options are required.** A required option with no default should say so
  rather than showing an empty default cell.

### Secrets

- Never a real token, key, password, hostname, or account ID — see the example-data table
  in `structure.md`.
- Say where the value comes from: "Generate one in your account settings."
- Say where it should live, and where it shouldn't: "The API token is read from
  `PROJECTNAME_TOKEN`. Don't put it in the configuration file."
- Don't show a secret being passed on a command line — that's a security problem worth a
  **Warning** notice if the project's CLI accepts one.

---

## Cut these

Move to `docs/` and link, or delete:

| Cut | Why |
|---|---|
| Philosophy, origin story, "why I built this" | Not what a reader at the front door needs. Link it. |
| Roadmaps, planned features, "coming soon" | Violates the future-features rule, and goes stale. |
| Exhaustive feature bullet lists | Nobody reads them, and they attract superlatives. |
| Comparison tables against other projects | Excessive claims. Wrong as soon as the other project ships. |
| Full API or CLI reference | Belongs in generated reference docs. Link it. |
| Screenshots of terminal output or code | Inaccessible and unsearchable. Use a code block. |
| A badge wall | Keep the ones a reader acts on: build, version, license. |
| Long acknowledgments and sponsor sections | Move below the license, or into their own file. |

---

## Common failure modes

- **Motivation before installation.** The most common ordering mistake. The reader
  scrolls past three paragraphs of context to find the install command.
- **`npm install` and nothing else.** Installing isn't the goal. Every quick start needs
  the step after the install and the output that proves it worked.
- **Commands that were never run.** Invented flags, wrong package name, a subcommand
  that was renamed two releases ago.
- **Placeholder-riddled commands.** A block the reader has to edit in four places isn't a
  quick start.
- **Defaults copied from an older version.** Read them from the code every time you touch
  the table.
- **A prerequisite discovered in step 4.** All prerequisites go before step 1.
- **Version facts in prose.** "Currently supports Python 3.9 through 3.12" — put it in
  the compatibility table.
- **Superlatives in the description.** "The fastest, simplest way to…" — see excessive
  claims in `names-and-claims.md`.
- **Headings in title case.** Sentence case, like every other heading.
- **Badges with no `alt` text.** Screen readers announce the filename.

---

## Applying the rest of the skill

| Rule | Where it bites in a README |
|---|---|
| Sentence case headings | "Quick start," not "Quick Start." |
| Second person, imperative | "Install the package," not "The user installs the package." |
| Present tense | "The server listens on port 8080," not "will listen." |
| Task headings start with a base-form verb | "Configure logging," not "Configuring logging." |
| Code font | Package names, commands, flags, filenames, paths, env vars, ports, config keys, defaults. |
| Not code font | Project names in prose, organization names, browser-facing URLs. |
| Introduce every code block | With a complete sentence ending in a colon. |
| Descriptive link text | "see the configuration reference," not "click here" or a bare URL. |
| No directional language | "the following table," not "the table below." |
| Timeless documentation | Except in `CHANGELOG.md`, where dates and *new* are the point. |
| Alt text | On every badge, diagram, and screenshot. Empty `alt=""` if decorative. |
| Example data | `example.com`, reserved IP ranges, the approved example names. |
