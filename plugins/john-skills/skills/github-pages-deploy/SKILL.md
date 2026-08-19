---
name: github-pages-deploy
description: Stand up a new static site (an index.html plus assets) on GitHub Pages from the terminal — creates the repo, pushes, enables Pages, waits for the build, and checks the live URL and its images actually load before handing it over. Use this whenever the user wants to put a static page, landing page, demo, report, or standalone HTML on the web, or says "deploy this", "host this", "publish this page", "put this online", "get me a link I can send someone", or "ship it to GitHub Pages" — including when they never say "GitHub Pages" and just want a public URL. Also use to push updates to a site published this way.
---

# Stand up a site on GitHub Pages

For a new static site in its own directory: one command creates the repo, publishes it, and gives back a URL that has been checked.

This is scoped to new sites. If the directory already has a git remote, stop and ask the user what they want — publishing an existing repo means deciding about its branches and history, which is a different conversation.

## Prerequisites

`git` and `gh` installed, and `gh auth status` showing an authenticated account. If auth fails, ask the user to run `gh auth login` themselves — it's interactive and needs a browser. In Claude Code they can run it inline by typing `! gh auth login`.

## Deploy

```bash
bash <skill-dir>/scripts/deploy.sh --dir <site-dir> --repo <repo-name>
```

That's the whole thing. It audits the site, initializes and commits, creates the repo, enables Pages, waits for the build, and verifies the live URL before printing it. Rerun the same command later to publish updates.

Confirm the repository name with the user first — it becomes the URL path (`https://<owner>.github.io/<repo>/`) and renaming it later breaks any link they've shared. Public is the default; `--private` works but needs a paid GitHub plan, and the published site is world-readable either way, so it buys less than people expect.

## What it does, and why each part is there

Four commands would technically publish a site. These are the parts that make it work on the first try instead of the third:

**Audits the site before pushing** (`scripts/preflight.py`, run automatically). It catches the failures that don't show up until the site is live:

- Root-relative paths like `src="/assets/logo.png"`. On a project site the leading `/` resolves to `https://<owner>.github.io/`, not your repo's subpath, so the image 404s. Use `assets/logo.png`.
- Case-only mismatches — `assets/Logo.png` on disk, `assets/logo.png` in the HTML. macOS doesn't care, the Pages server does. This one is nearly invisible locally.
- References to files that simply aren't there, and a missing `index.html`, which makes the whole site 404.

Errors stop the deploy. If the user knowingly wants to publish anyway, `--force` proceeds.

**Writes `.nojekyll`.** Pages runs everything through Jekyll by default, which silently skips any path starting with `_` or `.` (so `_next/`, `_assets/` never publish) and treats `{{ }}` in HTML as template syntax. The empty `.nojekyll` file turns that off.

**Treats 409 on the Pages API as success**, and retries the Pages call for a few seconds after repo creation — the endpoint 404s briefly while GitHub finishes provisioning the repo.

**Waits for the build, then fetches the site** (`scripts/verify.py`). A fresh build takes 30–90 seconds, during which the URL returns 404 with no holding page. An immediate 404 almost always means "not built yet", so don't interpret one as a failure. Once it's up, verify requests every local file the page references and reports any that don't load.

Report the live URL, the repo URL, and the verify result. Never hand over a URL you haven't seen return 200.

## If something is wrong

- **Still 404 after the build says `built`** — check `gh api "repos/$OWNER/$REPO/pages" --jq '.source, .html_url'`. Usually the URL is missing the `/<repo>/` path segment, or `index.html` isn't at the repo root.
- **Page loads, images don't** — rerun `python3 <skill-dir>/scripts/verify.py <url>` to get the exact 404s. Fix the paths, then rerun `deploy.sh` to push and recheck.
- **Build says `errored`** — `gh api "repos/$OWNER/$REPO/pages/builds/latest" --jq .error.message`. Nearly always Jekyll choking on something; confirm `.nojekyll` was committed (`git ls-files .nojekyll`) and force a rebuild with `gh api --method POST "repos/$OWNER/$REPO/pages/builds"`.
- **Repo name already taken** — pick another name; `gh repo view <owner>/<name>` shows what's already there.
