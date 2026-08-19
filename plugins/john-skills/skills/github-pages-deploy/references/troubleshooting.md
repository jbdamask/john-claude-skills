# GitHub Pages troubleshooting

Symptom-first. Each section assumes `OWNER` and `REPO` are set:

```bash
OWNER=$(gh api user --jq .login)
REPO=$(gh repo view --json name --jq .name)
```

## Contents

- [The URL returns 404](#the-url-returns-404)
- [The page loads but images, CSS, or JS are missing](#the-page-loads-but-images-css-or-js-are-missing)
- [A directory or file is missing from the published site](#a-directory-or-file-is-missing-from-the-published-site)
- [The build says "errored"](#the-build-says-errored)
- [`gh repo create` fails](#gh-repo-create-fails)
- [Enabling Pages fails](#enabling-pages-fails)
- [Changes pushed but the site is stale](#changes-pushed-but-the-site-is-stale)
- [Custom domains](#custom-domains)
- [HTTPS](#https)
- [Turning a site off](#turning-a-site-off)
- [Useful one-liners](#useful-one-liners)

## The URL returns 404

Work down this list; the first two explain most cases.

1. **The build hasn't finished.** First publish takes 30-90 seconds and there's no redirect or holding page — just a 404. Check the real state instead of refreshing:
   ```bash
   gh api "repos/$OWNER/$REPO/pages/builds/latest" --jq '.status, .error.message'
   ```
   `building` means wait. `built` means look further down this list.
2. **No `index.html` at the publish root.** Pages serves `index.html` as the homepage. If the source path is `/docs`, the file must be `docs/index.html` — a root-level `index.html` isn't published at all.
   ```bash
   gh api "repos/$OWNER/$REPO/pages" --jq '.source'
   git ls-tree -r --name-only HEAD | grep index.html
   ```
3. **Pages is watching a different branch.** Check `.source.branch` against what you actually pushed. Fix with a `PUT`:
   ```bash
   gh api --method PUT "repos/$OWNER/$REPO/pages" \
     -f 'source[branch]=main' -f 'source[path]=/'
   ```
4. **Wrong URL shape.** A project site lives at `https://<owner>.github.io/<repo>/` — the trailing repo segment is not optional. Only a repo named exactly `<owner>.github.io` publishes at the domain root. Take the URL from the API rather than assembling it:
   ```bash
   gh api "repos/$OWNER/$REPO/pages" --jq .html_url
   ```
5. **A subpage 404s but the homepage works.** Pages serves `about.html` at `/about.html`, not at `/about`. Extensionless URLs need either the extension in the link or a directory with its own `index.html` (`about/index.html` → `/about/`).

## The page loads but images, CSS, or JS are missing

Open the browser console — every one of these shows up as a 404 on a specific file.

- **Root-relative paths.** `src="/assets/logo.png"` resolves to `https://<owner>.github.io/assets/logo.png`, outside your repo's subpath. Use `assets/logo.png`. This is the single most common cause on project sites, and it's invisible locally because opening the file from disk resolves `/` to the filesystem root differently.
- **Case mismatch.** `assets/Logo.PNG` on disk, `assets/logo.png` in the HTML. macOS and Windows don't care; the Pages server does. `scripts/preflight.py` catches this by resolving each path segment against a real directory listing rather than trusting `exists()`.
- **The file was never committed.** A stray `.gitignore` rule, or `assets/` matching an ignore pattern:
  ```bash
  git ls-files assets | head
  git check-ignore -v assets/logo.png
  ```
- **Underscore-prefixed directory.** See the next section.
- **Mixed content.** An `http://` asset on an `https://` page is blocked by the browser and shows as blocked, not 404. Use protocol-relative or `https://` URLs.

`scripts/verify.py <url>` checks all of these against the live site in one pass.

## A directory or file is missing from the published site

GitHub Pages runs the site through Jekyll unless you tell it not to. Jekyll ignores anything whose name starts with `_` or `.`, so `_assets/`, `_data.json`, and `_next/` never get published. It also interprets `{{ ... }}` and `{% ... %}` in HTML as Liquid template syntax, which mangles or fails on pages containing framework templates or code samples.

The fix is one empty file at the publish root:

```bash
touch .nojekyll   # or docs/.nojekyll when the source path is /docs
git add -f .nojekyll && git commit -m "Disable Jekyll" && git push
```

`scripts/deploy.sh` does this automatically. Note the `-f` on `git add` — some `.gitignore` templates exclude dotfiles.

## The build says "errored"

```bash
gh api "repos/$OWNER/$REPO/pages/builds/latest" --jq '.error.message'
```

Almost always a Jekyll parse error on a file that was never meant to be Jekyll input. Add `.nojekyll` (above) and request a rebuild:

```bash
gh api --method POST "repos/$OWNER/$REPO/pages/builds"
```

Builds are limited to one at a time and roughly 10 per hour per repo.

## `gh repo create` fails

- **`Name already exists on this account`** — pick a different name, or push into the existing repo instead:
  ```bash
  git remote add origin "https://github.com/$OWNER/<existing-repo>.git"
  git push -u origin main
  ```
  Check what's there before pushing into it; `gh repo view $OWNER/<name>` is cheap.
- **`--source` requires the directory to be a git repository`** — run `git init` and make at least one commit first. `gh repo create --push` has nothing to push from an empty repo.
- **`could not determine the default branch`** — the branch has no commits. Commit, then retry.

## Enabling Pages fails

- **409 Conflict** — Pages is already on. Not an error; switch to `PUT` if you need to change the source.
- **404 immediately after `gh repo create`** — the repo is still provisioning. Sleep a few seconds and retry; `deploy.sh` retries six times.
- **403 / "upgrade" / "not available"** — Pages on a private repo requires GitHub Pro, Team, or Enterprise. Either upgrade or make it public:
  ```bash
  gh repo edit "$OWNER/$REPO" --visibility public --accept-visibility-change-consequences
  ```
  Worth saying out loud: a Pages site is publicly readable on the internet even when its repository is private. Private repos hide the source, not the site.
- **`HTTP 403: Resource not accessible by integration`** — the token lacks `repo` scope or admin rights on the repo. `gh auth refresh -s repo`.

## Changes pushed but the site is stale

1. Confirm the commit actually reached the published branch: `git log origin/main -1 --oneline`.
2. Confirm a build ran for it: `gh api "repos/$OWNER/$REPO/pages/builds/latest" --jq '.commit, .status'`.
3. If both look right, it's browser or CDN caching. Hard-reload, or check with a cache-busting query: `curl -sI "$URL?$(date +%s)"`. The Pages CDN typically holds assets for around 10 minutes.

## Custom domains

```bash
gh api --method PUT "repos/$OWNER/$REPO/pages" -f cname=example.com
```

This writes a `CNAME` file into the repo — don't delete it, and don't hand-edit it and set the API value to different things. DNS side: an apex domain needs A records pointing at GitHub's four Pages IPs (`185.199.108-111.153`); a subdomain needs a CNAME to `<owner>.github.io`. Certificate provisioning takes up to 24 hours, during which HTTPS may warn.

Remove a custom domain with `-F cname=null` (note `-F`, not `-f` — `-f` would send the literal string "null").

## HTTPS

```bash
gh api --method PUT "repos/$OWNER/$REPO/pages" -F https_enforced=true
```

On by default for `*.github.io`. It can only be enforced once a certificate exists, so on a brand-new custom domain this call may fail until provisioning completes.

## Turning a site off

```bash
gh api --method DELETE "repos/$OWNER/$REPO/pages"
```

Unpublishes the site; the repo and its contents are untouched. Confirm with the user first — the URL stops resolving immediately, and anything linking to it breaks.

## Useful one-liners

```bash
# Everything about the current Pages config
gh api "repos/$OWNER/$REPO/pages"

# Just the URL
gh api "repos/$OWNER/$REPO/pages" --jq .html_url

# Build history, most recent first
gh api "repos/$OWNER/$REPO/pages/builds" --jq '.[] | "\(.status)  \(.created_at)  \(.commit[0:7])"'

# Force a rebuild without a new commit
gh api --method POST "repos/$OWNER/$REPO/pages/builds"

# What the server actually returns
curl -sI "$(gh api "repos/$OWNER/$REPO/pages" --jq .html_url)"
```
