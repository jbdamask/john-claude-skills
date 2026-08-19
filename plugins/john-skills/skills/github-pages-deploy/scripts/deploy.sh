#!/usr/bin/env bash
# Publish a static site directory to GitHub Pages, idempotently.
#
# Safe to rerun: it detects whether the directory is already a repo, already has
# an origin, and whether Pages is already enabled, and only does the missing
# parts. Rerunning after a fix or for a routine content update is the intended
# way to use it.
#
# Usage:
#   deploy.sh --dir <site-dir> [--repo <name>] [--private] [--branch main]
#             [--path / | /docs] [--message "commit message"] [--no-wait]

set -euo pipefail

SITE_DIR="."
REPO_NAME=""
VISIBILITY="--public"
BRANCH="main"
PAGES_PATH="/"
COMMIT_MSG=""
WAIT_FOR_BUILD=1

die() { printf 'error: %s\n' "$*" >&2; exit 1; }
say() { printf '==> %s\n' "$*"; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir)     SITE_DIR="${2:?--dir needs a value}"; shift 2 ;;
    --repo)    REPO_NAME="${2:?--repo needs a value}"; shift 2 ;;
    --private) VISIBILITY="--private"; shift ;;
    --public)  VISIBILITY="--public"; shift ;;
    --branch)  BRANCH="${2:?--branch needs a value}"; shift 2 ;;
    --path)    PAGES_PATH="${2:?--path needs a value}"; shift 2 ;;
    --message) COMMIT_MSG="${2:?--message needs a value}"; shift 2 ;;
    --no-wait) WAIT_FOR_BUILD=0; shift ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *)         die "unknown argument: $1" ;;
  esac
done

[[ "$PAGES_PATH" == "/" || "$PAGES_PATH" == "/docs" ]] ||
  die "--path must be / or /docs; GitHub only publishes those two from a branch. See the 'Publishing from a subdirectory' section of SKILL.md."

# --- prerequisites -----------------------------------------------------------

command -v git >/dev/null || die "git is not installed."
command -v gh  >/dev/null || die "gh (GitHub CLI) is not installed: https://cli.github.com"
gh auth status >/dev/null 2>&1 ||
  die "gh is not authenticated. Run 'gh auth login' (it needs a browser, so run it yourself)."

[[ -d "$SITE_DIR" ]] || die "$SITE_DIR is not a directory."
cd "$SITE_DIR"
SITE_DIR="$PWD"

# --- repo state detection ----------------------------------------------------

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
ORIGIN_URL=""
[[ -n "$REPO_ROOT" ]] && ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"

if [[ -n "$REPO_ROOT" && "$REPO_ROOT" != "$SITE_DIR" ]]; then
  die "$SITE_DIR is inside the repo at $REPO_ROOT, not its root. GitHub publishes only / or /docs from a branch — move the site to the repo root or to docs/, or give it its own repo. See SKILL.md."
fi

# The publish root is what Pages actually serves; .nojekyll and index.html
# belong there, not necessarily at the repo root.
PUBLISH_ROOT="$SITE_DIR"
[[ "$PAGES_PATH" == "/docs" ]] && PUBLISH_ROOT="$SITE_DIR/docs"

[[ -f "$PUBLISH_ROOT/index.html" ]] ||
  die "no index.html in $PUBLISH_ROOT — Pages would serve a 404 for the whole site."

# Jekyll (on by default) skips paths starting with _ or . and rewrites {{ }} as
# Liquid. .nojekyll turns it off, which is what you want for a plain static site.
if [[ ! -f "$PUBLISH_ROOT/.nojekyll" ]]; then
  touch "$PUBLISH_ROOT/.nojekyll"
  say "wrote .nojekyll (disables Jekyll processing)"
fi

# --- commit ------------------------------------------------------------------

if [[ -z "$REPO_ROOT" ]]; then
  say "initializing git repository"
  git init -q
  git checkout -q -b "$BRANCH" 2>/dev/null || git branch -M "$BRANCH"
  : "${COMMIT_MSG:=Initial site}"
else
  CURRENT_BRANCH="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo "")"
  if [[ -z "$CURRENT_BRANCH" ]]; then
    git checkout -q -b "$BRANCH"
  elif [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    say "note: on branch '$CURRENT_BRANCH' but publishing '$BRANCH'; switching"
    git checkout -q "$BRANCH" 2>/dev/null || git branch -M "$BRANCH"
  fi
  : "${COMMIT_MSG:=Update site}"
fi

git add -A
if git diff --cached --quiet 2>/dev/null && git rev-parse HEAD >/dev/null 2>&1; then
  say "nothing to commit; working tree matches HEAD"
else
  git commit -q -m "$COMMIT_MSG"
  say "committed: $COMMIT_MSG"
fi

# --- push / create -----------------------------------------------------------

OWNER="$(gh api user --jq .login)"

if [[ -z "$ORIGIN_URL" ]]; then
  : "${REPO_NAME:=$(basename "$SITE_DIR")}"
  if gh repo view "$OWNER/$REPO_NAME" >/dev/null 2>&1; then
    die "$OWNER/$REPO_NAME already exists but this directory has no origin. Pass a different --repo, or add the remote yourself with 'git remote add origin' and rerun."
  fi
  say "creating $OWNER/$REPO_NAME ($VISIBILITY)"
  gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push
else
  say "pushing to existing origin: $ORIGIN_URL"
  git push -u origin "$BRANCH"
  REPO_NAME="$(gh repo view --json name --jq .name)"
  OWNER="$(gh repo view --json owner --jq .owner.login)"
fi

SLUG="$OWNER/$REPO_NAME"

# --- enable Pages ------------------------------------------------------------

PAGES_ENABLED=0
gh api "repos/$SLUG/pages" >/dev/null 2>&1 && PAGES_ENABLED=1

if [[ "$PAGES_ENABLED" -eq 0 ]]; then
  say "enabling GitHub Pages on $BRANCH $PAGES_PATH"
  # Right after repo creation the Pages endpoint can 404 for a few seconds while
  # the repo finishes provisioning, so retry rather than treating it as fatal.
  for attempt in 1 2 3 4 5 6; do
    if OUT="$(gh api --method POST "repos/$SLUG/pages" \
                -f "source[branch]=$BRANCH" -f "source[path]=$PAGES_PATH" 2>&1)"; then
      break
    fi
    if grep -q '409' <<<"$OUT"; then
      say "Pages was already enabled"
      break
    fi
    if [[ $attempt -eq 6 ]]; then
      if grep -qi 'upgrade\|not available\|payment' <<<"$OUT"; then
        die "GitHub refused to enable Pages: $OUT
Pages on a private repository requires a paid plan (Pro, Team, or Enterprise). Make the repo public with 'gh repo edit $SLUG --visibility public --accept-visibility-change-consequences' or upgrade the account."
      fi
      die "could not enable Pages after 6 attempts: $OUT"
    fi
    sleep 5
  done
else
  HAVE_BRANCH="$(gh api "repos/$SLUG/pages" --jq '.source.branch // ""')"
  HAVE_PATH="$(gh api "repos/$SLUG/pages" --jq '.source.path // ""')"
  if [[ "$HAVE_BRANCH" != "$BRANCH" || "$HAVE_PATH" != "$PAGES_PATH" ]]; then
    say "Pages points at $HAVE_BRANCH $HAVE_PATH; updating to $BRANCH $PAGES_PATH"
    gh api --method PUT "repos/$SLUG/pages" \
      -f "source[branch]=$BRANCH" -f "source[path]=$PAGES_PATH" >/dev/null
  else
    say "Pages already enabled on $BRANCH $PAGES_PATH"
  fi
fi

URL="$(gh api "repos/$SLUG/pages" --jq .html_url)"

# --- wait for the build ------------------------------------------------------

if [[ "$WAIT_FOR_BUILD" -eq 1 ]]; then
  say "waiting for the Pages build"
  for _ in $(seq 1 40); do
    STATUS="$(gh api "repos/$SLUG/pages/builds/latest" --jq .status 2>/dev/null || echo "")"
    case "$STATUS" in
      built)   say "build succeeded"; break ;;
      errored) die "Pages build failed: $(gh api "repos/$SLUG/pages/builds/latest" --jq '.error.message // "no message"')" ;;
      *)       sleep 6 ;;
    esac
  done
fi

printf '\nrepo: https://github.com/%s\nsite: %s\n' "$SLUG" "$URL"
printf '\nVerify it actually serves: python3 "%s/verify.py" "%s"\n' \
  "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" "$URL"
