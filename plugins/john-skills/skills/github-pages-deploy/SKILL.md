---
name: github-pages-deploy
description: Publish a static site (an index.html plus assets) to GitHub Pages from the terminal using git and the gh CLI — creating the repo, pushing, enabling Pages, waiting for the build, and verifying the live URL and its assets actually load. Use this whenever the user wants to put a static page, landing page, demo, report, dashboard, slide deck, or any standalone HTML on the web, or asks to "deploy this", "host this", "publish this page", "put this online", "make this public", "get me a link to this", "share this HTML", "ship it to GitHub Pages", or "set up gh-pages" — including when they never say the words "GitHub Pages" and just want a URL they can send to someone. Also use for redeploying or updating a site already published this way, and for diagnosing a Pages site that returns 404 or renders without its images and CSS.
---

# Deploy a static site to GitHub Pages

Getting a static site online is mostly a solved problem — `gh` can create the repo, push it, and turn on Pages in about four commands. What actually goes wrong is everything around those four commands: the site renders locally but its images 404 in production, Pages is already enabled so the create call fails, the build hasn't finished so the URL 404s and you report success anyway, or Jekyll silently eats a directory whose name starts with an underscore.

So the shape of this skill is: audit the site before pushing, deploy idempotently, then prove the live site works before telling the user it's done. Never hand over a URL you haven't fetched.

## Prerequisites

- `git` and `gh` installed, and `gh auth status` showing an authenticated account with `repo` scope.
- If `gh auth status` fails, tell the user to run `gh auth login` themselves — it's interactive and needs a browser. In Claude Code they can run it inline by typing `! gh auth login`.

## Step 1 — Work out which situation you're in

The issue-of-record flow assumes a fresh directory that isn't a repo yet. Reality is usually one of five cases. Figure out which one before touching anything:

```bash
cd <site-dir>
git rev-parse --show-toplevel 2>/dev/null   # empty => not a repo
git remote get-url origin 2>/dev/null       # empty => no remote yet
```

| Situation | What to do |
| --- | --- |
| Not a git repo | Full flow: `git init` → commit → `gh repo create --source=. --push` → enable Pages |
| A repo, no `origin` | Skip `git init`; same `gh repo create --source=. --push` |
| A repo with `origin`, Pages off | Skip repo creation entirely. Commit, push, enable Pages on the existing repo |
| A repo with `origin`, Pages already on | Just commit and push. Pages redeploys itself; confirm with the build poll |
| The site is in a subdirectory of a bigger repo | See "Publishing from a subdirectory" below — GitHub only publishes `/` or `/docs` from a branch |

`scripts/deploy.sh` detects all of these and does the right thing, so in practice you run it and read what it reports. Look at the detection yourself when something surprises you.

Two things to confirm with the user before creating anything, because both are hard to walk back:

- **Repository name.** It becomes the URL path: `https://<owner>.github.io/<repo>/`. A repo named exactly `<owner>.github.io` is special — it's the account's user site and publishes at the domain root, one per account.
- **Public or private.** Default to public. Pages on a private repo requires a paid plan (Pro, Team, or Enterprise), and the published site is world-readable regardless, so "private" buys less than users expect. If they ask for private, say that plainly rather than letting the API 4xx explain it for you.

## Step 2 — Audit the site before you push

Run the preflight check. It's the step that catches the failures users actually hit:

```bash
python3 <skill-dir>/scripts/preflight.py <site-dir>
```

It reports:

- **Missing `index.html`** at the publish root — Pages has nothing to serve and returns 404 for the whole site.
- **Root-relative references** like `src="/assets/logo.png"`. These work when you open the file locally and break on a project site, because `/` resolves to `https://<owner>.github.io/`, not to your repo's subpath. Rewrite them as `assets/logo.png`. (On a user site — the `<owner>.github.io` repo — they're fine, and preflight says so.)
- **References to files that don't exist**, including **case mismatches**. macOS filesystems are case-insensitive, GitHub Pages is not, so `assets/Logo.png` referenced as `assets/logo.png` renders locally and 404s in production. This one is nearly invisible without a checker.
- **Paths beginning with `_` or `.`** — Jekyll, which Pages runs by default, skips them. `scripts/deploy.sh` writes a `.nojekyll` file at the publish root to turn Jekyll off, which also protects HTML containing `{{ }}` from being mangled as Liquid templates.
- **Files over 100 MB** (git rejects them) and a total repo over ~1 GB (Pages' soft limit).

Fix what it finds, or tell the user why you're proceeding anyway. External `https://` URLs, `data:` URIs, anchors, and `mailto:` are ignored — only local files are checked.

## Step 3 — Deploy

```bash
bash <skill-dir>/scripts/deploy.sh --dir <site-dir> --repo <repo-name> [--private] [--branch main]
```

The script is idempotent — safe to rerun after a failure or for a routine update. It:

1. Verifies `git`, `gh`, and auth.
2. Writes `.nojekyll` if absent.
3. `git init` / renames the branch to `main` only if needed, commits anything uncommitted.
4. Creates the GitHub repo and pushes, or pushes to the existing `origin`.
5. Enables Pages via `POST /repos/{owner}/{repo}/pages` with `source[branch]` and `source[path]`, treating **409 Conflict as success** — that just means Pages was already on. If the existing config points at a different branch or path, it issues a `PUT` to correct it.
6. Polls `GET /repos/{owner}/{repo}/pages/builds/latest` until the status leaves `building`, then prints the URL.

If you'd rather run it by hand, the equivalent core is:

```bash
OWNER=$(gh api user --jq .login)
REPO=$(basename "$(git rev-parse --show-toplevel)")

gh repo create "$REPO" --public --source=. --remote=origin --push

gh api --method POST "repos/$OWNER/$REPO/pages" \
  -f 'source[branch]=main' -f 'source[path]=/'

gh api "repos/$OWNER/$REPO/pages" --jq .html_url
```

One timing note if you do it manually: the Pages `POST` can return 404 for a few seconds after `gh repo create`, because the repo isn't fully provisioned yet. Retry rather than concluding something is wrong.

## Step 4 — Verify before declaring victory

A Pages build takes 30 seconds to a couple of minutes. During that window the URL returns 404, which means "not built yet" far more often than it means "broken". Don't guess — check:

```bash
python3 <skill-dir>/scripts/verify.py <url>
```

It waits for the page to return 200, then parses the served HTML and issues a request for every local asset it references, reporting any that 404. This is what turns "I pushed it" into "the site works", and it catches the case-sensitivity and path bugs that preflight can only predict from the local filesystem.

Report to the user: the live URL, the repo URL, and the verify result. If assets 404, fix the paths, commit, push, and rerun verify — the fix loop is fast.

## Publishing from a subdirectory

When publishing from a branch, GitHub only accepts two source paths: the repository root (`/`) or `/docs`. There is no way to point the branch builder at `site/` or `public/`. Three options, in order of preference:

1. **Move or rename the directory to `docs/`** and set `source[path]=/docs`. Simplest, no CI involved. `deploy.sh --path /docs` does this.
2. **Publish the subdirectory to its own repository** — reasonable when the site is genuinely a separate artifact.
3. **Switch to an Actions-based build** (`build_type: workflow`), which can upload any directory. Copy `assets/pages-actions-workflow.yml` to `.github/workflows/pages.yml`, edit its `path:` value, and commit. Use this when the site must stay where it is inside a larger repo, or when it needs a build step. Note that this requires `workflow` scope on the token to push.

## When something is wrong

`references/troubleshooting.md` covers the failure modes with their specific fixes: blank or 404 sites, assets loading locally but not in production, Jekyll build failures, `gh repo create` name collisions, custom domains and CNAME, HTTPS enforcement, and removing a Pages site. Read it when a symptom doesn't have an obvious cause rather than guessing at the API.
