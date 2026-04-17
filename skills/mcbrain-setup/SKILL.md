---
name: mcbrain-setup
description: One-shot setup skill for McBrain — a persistent personal knowledge base built on Karpathy's LLM Wiki pattern, viewed in Obsidian and maintained by Claude. Use this skill when the user wants to set up McBrain, set up an LLM wiki, build a personal knowledge base, create a second brain with Claude, integrate Obsidian with Claude, or give Claude persistent memory. Handles vault directory scaffolding, the CLAUDE.md schema, and the filesystem MCP config block. Run this once to bootstrap; thereafter the companion `mcbrain` skill handles day-to-day operations.
---

# McBrain Setup

Sets up McBrain — a personal LLM-maintained knowledge base — end-to-end for Claude Desktop (Cowork) + Obsidian. Pattern is Karpathy's LLM Wiki.

**The idea in one sentence**: instead of re-deriving knowledge from raw sources every session, Claude builds and maintains a persistent markdown wiki that compounds over time. Obsidian is the IDE; Claude is the programmer; McBrain is the codebase.

## What this skill does

1. Names the vault and confirms its location
2. Sets up backup strategy — and if Git, creates the remote repo before any files exist
3. Creates the directory structure and initializes the vault
4. Writes the MCP filesystem config block for Claude Desktop
5. Walks through Obsidian and browser extension setup
6. Verifies everything works

---

## Step 1: Name and locate the vault

Ask the user:

> "What would you like to call this knowledge base? For example: 'AI Science', 'Finance', 'Clinical Guidelines', 'Personal'."

From their answer, derive:
- **MCP name**: lowercase, hyphenated, prefixed with `mcbrain-` — e.g., "AI Science" → `mcbrain-ai-science`
- **Default folder name**: same as MCP name

Then ask:

> "Where do you want it to live? I'll suggest `~/Documents/mcbrain` — or pick a different path if you prefer."

Adjust the suggestion to the user's OS:
- macOS: `~/Documents/<mcp-name>`
- Windows: `C:\Users\<username>\Documents\<mcp-name>`

Store the confirmed path as `VAULT_PATH` and the MCP name as `MCP_NAME`. Expand `~` to the full home directory path.

---

## Step 2: Choose backup strategy

Ask before creating any files — the backup choice affects how the vault is initialized.

> "Do you want to back McBrain up automatically? I recommend one of these:
> - **Git + GitHub** — stores every version of every wiki page with labeled history. If Claude ever makes a bad edit, you can roll back. Free private repo. Slightly more setup.
> - **Google Drive** — simplest option. Just syncs the folder automatically, like Dropbox. No terminal needed.
> - **None** — keeps everything local only. Not recommended, but fine if you're sure."

---

### Option A: Git + GitHub

Set up GitHub first — the remote repo needs to exist before the vault is created so you can set it as the origin immediately.

**A1 — Create a GitHub account (if the user doesn't have one)**

Tell the user: Go to [github.com](https://github.com) and create a free account. Come back when you have a username.

**A2 — Install the GitHub CLI**

- macOS (with Homebrew): `brew install gh`
  - If Homebrew isn't installed: `brew` won't be found. Tell the user to first run `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` in Terminal, then retry.
- Windows: `winget install --id GitHub.cli` (or direct them to [cli.github.com](https://cli.github.com))
- Linux: [cli.github.com/manual/installation](https://cli.github.com/manual/installation)

Verify: `gh --version`

**A3 — Authenticate**

```bash
gh auth login
```

Walk the user through the prompts:
- "What account do you want to log into?" → GitHub.com
- "What is your preferred protocol?" → HTTPS
- "Authenticate Git with your GitHub credentials?" → Yes
- "How would you like to authenticate?" → Login with a web browser → follow the one-time code flow

**A4 — Create the private repo on GitHub**

Create the remote repo now, before any local files exist:

```bash
gh repo create MCP_NAME --private
```

This creates an empty private repo on GitHub. Capture the repo URL:

```bash
gh repo view MCP_NAME --json url --jq .url
```

Store this as `REPO_URL` (e.g., `https://github.com/<username>/MCP_NAME`). You'll set this as the remote origin when the local vault is initialized in Step 3.

Confirm with the user: *"Created private repo at `REPO_URL`. We'll link the vault to it in the next step."*

---

### Option B: Google Drive

No setup needed at this stage. Note the selection and continue to Step 3.

---

### Option C: None

Confirm once before continuing:

> "Just to confirm — with no backup, if your computer is lost or the vault is accidentally deleted, McBrain can't be recovered. Are you sure?"

If confirmed, note the selection and continue to Step 3.

---

## Step 3: Create the vault

Create the following structure under `VAULT_PATH`:

```
VAULT_PATH/
├── raw/                    # Immutable source documents — LLM reads, never writes
│   ├── articles/           # Web clips, saved articles
│   ├── papers/             # PDFs, research papers
│   ├── notes/              # Personal notes, journal entries
│   └── assets/             # Downloaded images (set as Obsidian attachment folder)
├── wiki/                   # LLM-owned compiled markdown
│   ├── index.md            # Master catalog of all wiki pages
│   ├── log.md              # Append-only operation log
│   └── overview.md         # High-level synthesis of everything in McBrain
├── .obsidian/              # Created by Obsidian on first open — leave alone
└── CLAUDE.md               # Schema + instructions for Claude (the key config file)
```

Use bash to create these dirs. Also create placeholder files for index.md, log.md, overview.md, and CLAUDE.md using the templates in the reference files below.

Read `references/claude-md-template.md` to get the CLAUDE.md content.
Read `references/index-template.md` to get the index.md starter.
Read `references/log-template.md` to get the log.md starter.
Read `references/overview-template.md` to get the overview.md starter.

After writing CLAUDE.md from the template, append the following two sections:

**Web Ingestion Routing section** (always append, regardless of backup strategy):

```markdown
## Web Ingestion Routing

When fetching a URL to save into `raw/`, choose the right tool based on the situation:

- **Web fetch** (`mcp__workspace__web_fetch`): use first for any publicly accessible page. Fast and lightweight. Works well for open-access articles, documentation, Wikipedia, and plain HTML pages. If it returns incomplete content, an error, or a login wall, switch to Claude in Chrome.
- **Claude in Chrome** (Cowork extension): use when the page is paywalled, requires a login, or is a JavaScript-heavy single-page app that web fetch can't render. Claude navigates the page in the user's real browser session, so it handles authentication and dynamic content automatically.
- **Obsidian Web Clipper**: do not invoke this yourself — it is a browser extension the user operates. Recommend it when the user mentions they are actively browsing and want to save articles for later rather than ingesting right now. It saves directly to `raw/articles/` and is ideal for batch collecting during a browsing session.

Default behavior: attempt web fetch first. On failure or thin content, switch to Claude in Chrome. Suggest Obsidian Web Clipper only when the user's intent is save-for-later rather than ingest-now.
```

**Backup section** (content depends on strategy chosen in Step 2):

For Git:
```markdown
## Backup

- Strategy: git
- Remote: REPO_URL
- Push command: `git push origin main`
- To push after a session: run the push command from the vault directory in Terminal
- To revert a bad edit: `git log --oneline` to find the commit, then `git checkout <hash> -- wiki/<filename>.md`
```

For Google Drive:
```markdown
## Backup

- Strategy: google-drive
- Sync: Drive for Desktop watches VAULT_PATH and uploads changes automatically
- No extra steps needed after working in the vault — Drive syncs continuously
- To restore files: visit drive.google.com and navigate to the synced vault folder
```

For None:
```markdown
## Backup

- Strategy: none
- No backup is configured. To set one up later, ask Claude to "set up McBrain backup".
```

### Initialize git (Git strategy only)

After all files are written:

```bash
cd VAULT_PATH
git init -b main
printf '.DS_Store\n.obsidian/workspace*\n.obsidian/cache\n' > .gitignore
git remote add origin REPO_URL
git add -A
git commit -m "init: MCP_NAME vault scaffolding"
git push -u origin main
```

Confirm the push succeeded. If it fails, check that `gh auth login` completed correctly and that `REPO_URL` is reachable.

---

## Step 4: Google Drive sync (Google Drive strategy only)

**D1 — Install Google Drive for Desktop**

Go to [drive.google.com/drive/download](https://drive.google.com/drive/download), download and install the desktop app, sign in with a Google account.

**D2 — Add the vault folder to Drive sync**

Open the Google Drive for Desktop app → gear icon → Preferences → **My Computer** tab → **Add folder** → select `VAULT_PATH`.

Drive will now watch the folder and upload changes automatically.

**D3 — Verify sync**

Open [drive.google.com](https://drive.google.com) in a browser and confirm `CLAUDE.md` and the `wiki/` folder are visible. If they are, backup is live.

*(Skip this step entirely for Git and None strategies.)*

---

## Step 5: Configure filesystem MCP in Claude Desktop

The filesystem MCP gives Claude read/write access to the vault. Add it to `claude_desktop_config.json`:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Merge the following block under `"mcpServers"` (use the actual `MCP_NAME` value):

```json
"MCP_NAME": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "VAULT_PATH"
  ]
}
```

If the file doesn't exist yet, create it with the full structure. If other MCP servers already exist, merge carefully — don't overwrite them.

Show the user the final config before writing it and ask them to confirm.

---

## Step 6: Extensions and Obsidian setup

**Browser extensions to install first:**

- **Claude in Chrome** — lets Claude navigate pages in the user's real browser session, handling paywalls and logins that a plain web fetch can't reach. Install from the Chrome Web Store and sign in with the Anthropic account. This is what makes ingesting paywalled or authenticated content seamless.
- **Obsidian Web Clipper** — one-click capture of web articles into `raw/articles/` while browsing. Great for collecting articles in bulk to ingest later. Configure the clipper's vault to point at `VAULT_PATH` and its default folder to `raw/articles/`.

**Obsidian setup:**

1. **Open Obsidian** → click "Open folder as vault" → select `VAULT_PATH`
2. **Verify wikilinks are enabled**: Settings → Files & Links → confirm **"Use [[Wikilinks]]"** is on (default)
3. **Set default note location to `wiki/`**: Settings → Files & Links → Default location for new notes → "In the folder specified" → `wiki`
4. **Exclude `raw/` from search and graph**: Settings → Files & Links → Excluded files → add `raw/`
5. **Attachment folder**: Settings → Files & Links → Default location for new attachments → "In the folder specified below" → `raw/assets`
6. **Recommended Obsidian plugins** (all optional):
   - **Dataview** (community) — queryable YAML frontmatter
   - **Graph View** (built-in) — see the shape of the vault
   - **Marp** (community) — optional, for slide deck output
7. **Restart Claude Desktop** after editing the MCP config so the filesystem server loads

---

## Step 7: Verify

After the user restarts Claude Desktop, tell them to start a new conversation and say:

> "Using the MCP_NAME MCP, read CLAUDE.md and tell me the wiki structure."

If Claude can read `CLAUDE.md`, the MCP is working. If not, troubleshoot:
- Node.js is installed (`node --version`)
- The config JSON is valid (no trailing commas, correct path)
- Claude Desktop was fully restarted (quit from menu bar, not just closed)

---

## Step 8: Install the companion operating skill

Point the user at the `mcbrain` skill for day-to-day ingest/query/lint operations. It uses the `MCP_NAME` convention to route requests to the right vault — so "find insights from McBrain AI Science" maps to the `mcbrain-ai-science` MCP automatically.

---

## Step 9: First ingest

Walk the user through their first ingest:

1. Drop a source file into the appropriate `raw/` subfolder (or paste a URL)
2. In Claude: *"Ingest `raw/articles/filename.md` into McBrain. Update index.md and log.md."*

Claude will read the source, discuss key points, write wiki pages in `wiki/`, update `wiki/index.md` and `wiki/log.md`.

**For PDFs:**
1. Upload the PDF into the chat
2. Claude invokes Cowork's built-in `pdf` skill — handles extraction, page rendering, and visual inspection automatically
3. Claude saves extracted text to `raw/papers/<name>.md` via the vault MCP
4. Claude describes substantive figures as prose under `## Figure N — [Title]` headings
5. Normal ingest proceeds

---

## Key operations to teach the user

**Ingest**: `"Ingest raw/articles/[file] into McBrain. Update index and log."`
**Query**: `"Ask McBrain: [question]. Cite the pages you used."`
**Lint**: `"Lint McBrain. Find contradictions, orphan pages, stale claims, missing cross-references."`
**Save a query answer**: `"File your answer as a new wiki page at wiki/[topic].md"`

---

## Reference files

- `references/claude-md-template.md` — The CLAUDE.md schema template
- `references/index-template.md` — Starter index.md
- `references/log-template.md` — Starter log.md
- `references/overview-template.md` — Starter overview.md
