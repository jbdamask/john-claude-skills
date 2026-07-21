#!/usr/bin/env bash
#
# clone-repos.sh — Clone a set of git repositories into a root directory.
#
# Usage:
#   clone-repos.sh [-n NUM] [-f FILE] ROOT_DIR [REPO_URL ...]
#
#   ROOT_DIR   Required. Repos are cloned as subdirectories beneath it
#              (created if it doesn't exist).
#   REPO_URL   Zero or more git URLs to clone.
#   -f FILE    Read additional repo URLs from FILE, one per line
#              (# comments and blank lines ignored).
#   -n NUM     Clone at most NUM repos. Default: 5
#              (or set the CLONE_REPO_LIMIT environment variable).
#   -h         Show this help.
#
# Examples:
#   clone-repos.sh ~/clients/acme https://github.com/acme/api.git
#   clone-repos.sh -n 10 ~/clients/acme -f repos.txt
#   CLONE_REPO_LIMIT=3 clone-repos.sh ~/clients/acme -f repos.txt

set -euo pipefail

DEFAULT_LIMIT="${CLONE_REPO_LIMIT:-5}"
limit="$DEFAULT_LIMIT"
repo_file=""

usage() {
  sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
}

while getopts ":n:f:h" opt; do
  case "$opt" in
    n) limit="$OPTARG" ;;
    f) repo_file="$OPTARG" ;;
    h) usage; exit 0 ;;
    :) echo "Error: -$OPTARG requires an argument" >&2; exit 1 ;;
    \?) echo "Error: unknown option -$OPTARG" >&2; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

# Validate the limit is a positive integer.
if ! [[ "$limit" =~ ^[0-9]+$ ]] || [ "$limit" -lt 1 ]; then
  echo "Error: -n must be a positive integer (got '$limit')" >&2
  exit 1
fi

# ROOT_DIR is required.
if [ "$#" -lt 1 ]; then
  echo "Error: ROOT_DIR is required" >&2
  usage
  exit 1
fi
root_dir="$1"
shift

# Collect repo URLs: positional args first, then any from -f FILE.
repos=("$@")
if [ -n "$repo_file" ]; then
  if [ ! -f "$repo_file" ]; then
    echo "Error: repo file not found: $repo_file" >&2
    exit 1
  fi
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%%#*}"                 # strip inline/full-line comments
    line="$(echo "$line" | xargs)"     # trim surrounding whitespace
    [ -n "$line" ] && repos+=("$line")
  done < "$repo_file"
fi

if [ "${#repos[@]}" -eq 0 ]; then
  echo "Error: no repositories given (pass URLs as arguments or via -f FILE)" >&2
  exit 1
fi

command -v git >/dev/null 2>&1 || { echo "Error: git is not installed" >&2; exit 1; }

mkdir -p "$root_dir"

cloned=0; skipped=0; failed=0; count=0

for url in "${repos[@]}"; do
  if [ "$count" -ge "$limit" ]; then
    echo "Reached limit of $limit repo(s); $(( ${#repos[@]} - count )) remaining not cloned."
    break
  fi
  count=$((count + 1))

  name="$(basename "$url")"; name="${name%.git}"
  dest="$root_dir/$name"

  if [ -d "$dest/.git" ]; then
    echo "[$count/$limit] skip: $name already present at $dest"
    skipped=$((skipped + 1))
    continue
  fi

  echo "[$count/$limit] cloning $url -> $dest"
  if git clone "$url" "$dest"; then
    cloned=$((cloned + 1))
  else
    echo "  ! failed to clone $url" >&2
    failed=$((failed + 1))
  fi
done

echo
echo "Done. cloned=$cloned skipped=$skipped failed=$failed (limit=$limit)"
[ "$failed" -eq 0 ]
