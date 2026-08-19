#!/usr/bin/env bash
# Stand up a new static site on GitHub Pages: audit, push, enable, verify.
#
# Safe to rerun — later runs just commit and push the changes, then recheck the
# live site. That's the update path.
#
# Usage:
#   deploy.sh --dir <site-dir> [--repo <name>] [--private] [--force]
#             [--message "commit message"]

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="."
REPO_NAME=""
VISIBILITY="--public"
COMMIT_MSG=""
FORCE=0

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
say() { printf '==> %s\n' "$*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)     SITE_DIR="${2:?--dir needs a value}"; shift 2 ;;
    --repo)    REPO_NAME="${2:?--repo needs a value}"; shift 2 ;;
    --private) VISIBILITY="--private"; shift ;;
    --public)  VISIBILITY="--public"; shift ;;
    --message) COMMIT_MSG="${2:?--message needs a value}"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *)         die "unknown argument: $1" ;;
  esac
done

command -v git >/dev/null || die "git is not installed."
command -v gh  >/dev/null || die "gh (GitHub CLI) is not installed: https://cli.github.com"
gh auth status >/dev/null 2>&1 ||
  die "gh is not authenticated. Run 'gh auth login' yourself — it needs a browser."

[[ -d "$SITE_DIR" ]] || die "$SITE_DIR is not a directory."
cd "$SITE_DIR"
SITE_DIR="$PWD"

[[ -f index.html ]] ||
  die "no index.html in $SITE_DIR — Pages would serve a 404 for the whole site."

# --- audit -------------------------------------------------------------------

say "auditing the site"
if ! python3 "$HERE/preflight.py" .; then
  [[ "$FORCE" -eq 1 ]] ||
    die "the audit found problems that would break the published site. Fix them, or rerun with --force to publish anyway."
  say "publishing despite the audit (--force)"
fi

# Jekyll runs by default and skips _* and .* paths, and mangles {{ }} in HTML.
[[ -f .nojekyll ]] || { touch .nojekyll; say "wrote .nojekyll (disables Jekyll)"; }

# --- commit ------------------------------------------------------------------

if [[ -z "$(git rev-parse --show-toplevel 2>/dev/null || true)" ]]; then
  say "initializing git repository"
  git init -q
  git branch -M main
  : "${COMMIT_MSG:=Initial site}"
else
  : "${COMMIT_MSG:=Update site}"
fi

git add -A
if git rev-parse HEAD >/dev/null 2>&1 && git diff --cached --quiet; then
  say "nothing new to commit"
else
  git commit -q -m "$COMMIT_MSG"
  say "committed: $COMMIT_MSG"
fi

# --- create or push ----------------------------------------------------------

OWNER="$(gh api user --jq .login)"

if [[ -z "$(git remote get-url origin 2>/dev/null || true)" ]]; then
  : "${REPO_NAME:=$(basename "$SITE_DIR")}"
  gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1 &&
    die "$OWNER/$REPO_NAME already exists. Pick a different --repo name."
  say "creating $OWNER/$REPO_NAME ($VISIBILITY)"
  gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push
else
  REPO_NAME="$(gh repo view --json name --jq .name)"
  OWNER="$(gh repo view --json owner --jq .owner.login)"
  say "pushing to $OWNER/$REPO_NAME"
  git push -q -u origin main
fi

SLUG="$OWNER/$REPO_NAME"

# --- enable Pages ------------------------------------------------------------

if gh api "repos/$SLUG/pages" >/dev/null 2>&1; then
  say "Pages already enabled"
else
  say "enabling GitHub Pages"
  # The endpoint 404s for a few seconds after repo creation while GitHub
  # finishes provisioning, so retry instead of treating it as fatal.
  for attempt in 1 2 3 4 5 6; do
    if OUT="$(gh api --method POST "repos/$SLUG/pages" \
                -f 'source[branch]=main' -f 'source[path]=/' 2>&1)"; then
      break
    fi
    grep -q '409' <<<"$OUT" && { say "Pages was already enabled"; break; }
    if [[ $attempt -eq 6 ]]; then
      grep -qi 'upgrade\|not available\|payment' <<<"$OUT" &&
        die "GitHub refused to enable Pages: $OUT
Pages on a private repo needs a paid plan. Make it public:
  gh repo edit $SLUG --visibility public --accept-visibility-change-consequences"
      die "could not enable Pages: $OUT"
    fi
    sleep 5
  done
fi

# --- wait, then prove it serves ----------------------------------------------

say "waiting for the Pages build"
for _ in $(seq 1 40); do
  STATUS="$(gh api "repos/$SLUG/pages/builds/latest" --jq .status 2>/dev/null || echo "")"
  case "$STATUS" in
    built)   say "build succeeded"; break ;;
    errored) die "Pages build failed: $(gh api "repos/$SLUG/pages/builds/latest" --jq '.error.message // "no message"')" ;;
    *)       sleep 6 ;;
  esac
done

URL="$(gh api "repos/$SLUG/pages" --jq .html_url)"
printf '\nrepo: https://github.com/%s\nsite: %s\n\n' "$SLUG" "$URL"

python3 "$HERE/verify.py" "$URL"
