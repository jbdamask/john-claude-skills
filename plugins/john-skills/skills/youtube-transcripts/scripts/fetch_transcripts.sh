#!/usr/bin/env bash
# Download YouTube auto-caption transcripts from a channel within a date range
# and write timestamped markdown.
#
# Usage:
#   fetch_transcripts.sh [--no-timestamps] [--chunk N] <channel_url> [start_YYYYMMDD] [end_YYYYMMDD] [max]
#
# Args:
#   --no-timestamps    optional; omit the [HH:MM:SS] prefixes (still markdown,
#                      still with frontmatter)
#   --chunk N          optional; group text into ~N-second paragraphs instead of
#                      one timestamped line per caption line
#   channel_url        e.g. https://www.youtube.com/@AIDailyBrief/videos
#   start              inclusive lower bound, YYYYMMDD (default: 7 days ago)
#   end                inclusive upper bound, YYYYMMDD (default: today)
#   max                optional cap on number of transcripts (default: no cap)

set -euo pipefail

STRIP=0
CHUNK=0
while [ "$#" -gt 0 ]; do
  case "${1:-}" in
    --no-timestamps) STRIP=1; shift ;;
    --keep-timestamps) shift ;;   # accepted for compatibility; now the default
    --chunk) CHUNK="${2:?--chunk needs a number of seconds}"; shift 2 ;;
    *) break ;;
  esac
done

case "$CHUNK" in
  ''|*[!0-9]*) echo "Error: --chunk must be a whole number of seconds" >&2; exit 1 ;;
esac

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 [--no-timestamps] [--chunk N] <channel_url> [start_YYYYMMDD] [end_YYYYMMDD] [max]" >&2
  exit 1
fi

URL="$1"
START="${2:-}"
END="${3:-}"
MAX="${4:-}"

# A missing date range would otherwise mean "the entire channel". Fall back to
# the last week instead -- a wrong guess costs a few files, not a back catalog.
DEFAULT_DAYS=7

days_ago() {
  date -v-"$1"d +%Y%m%d 2>/dev/null || date -d "$1 days ago" +%Y%m%d
}

if [ -z "$START" ] || [ -z "$END" ]; then
  [ -n "$START" ] || START="$(days_ago "$DEFAULT_DAYS")"
  [ -n "$END" ] || END="$(date +%Y%m%d)"
  echo ">> No date range given; defaulting to the last $DEFAULT_DAYS days ($START..$END)."
  echo ">> Pass explicit dates to widen it."
fi

for d in "$START" "$END"; do
  case "$d" in
    [0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]) : ;;
    *) echo "Error: dates must be YYYYMMDD (got '$d')" >&2; exit 1 ;;
  esac
done

if [ "$START" -gt "$END" ]; then
  echo "Error: start date $START is after end date $END" >&2
  exit 1
fi

# Normalize to the /videos tab so we get the channel's uploads newest-first.
case "$URL" in
  */videos) : ;;
  */) URL="${URL}videos" ;;
  *) URL="${URL}/videos" ;;
esac

for tool in yt-dlp ffmpeg; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Error: $tool not found on PATH" >&2; exit 1; }
done

MAX_ARG=()
if [ -n "$MAX" ]; then
  MAX_ARG=(--max-downloads "$MAX")
fi

echo ">> Fetching transcripts from $URL for $START..$END ${MAX:+(max $MAX)}"

# Snapshot everything already in this directory. Only files that appear after
# the fetch belong to this run, and only those get converted or deleted --
# whatever else is here is someone else's, whatever it happens to be named.
shopt -s nullglob dotglob
PRE=$'\n'
for f in *; do
  PRE="$PRE$f"$'\n'
done
shopt -u dotglob

is_ours() {
  case "$PRE" in
    *$'\n'"$1"$'\n'*) return 1 ;;
    *) return 0 ;;
  esac
}

# --break-match-filters stops the run once we pass below the start date
# (channel is newest-first), so we don't scan the whole back catalog.
# --max-downloads stops once the cap is hit. Both exit non-zero by design,
# so we tolerate those specific cases.
yt-dlp "$URL" \
  --break-match-filters "upload_date >= '$START'" \
  --match-filter "upload_date <= '$END'" \
  --lazy-playlist \
  --skip-download \
  --write-auto-subs \
  --sub-langs "en" \
  --sub-format ttml \
  --convert-subs srt \
  -o "%(upload_date)s - %(title)s [%(id)s].%(ext)s" \
  "${MAX_ARG[@]+"${MAX_ARG[@]}"}" || true

srts=()
skipped=0
for f in *; do
  if is_ours "$f"; then
    case "$f" in *.en.srt) srts+=("$f") ;; esac
  else
    skipped=$((skipped + 1))
  fi
done

if [ "$skipped" -gt 0 ]; then
  echo ">> Ignoring $skipped file(s) that were already in this directory."
fi

if [ "${#srts[@]}" -eq 0 ]; then
  echo ">> No transcripts matched that range." >&2
  exit 0
fi

AWK_PROG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/srt_to_md.awk"

if [ "$STRIP" -eq 1 ]; then
  echo ">> Converting ${#srts[@]} file(s) to .md (no timestamps)..."
else
  echo ">> Converting ${#srts[@]} file(s) to timestamped .md..."
fi

mds=()
for f in "${srts[@]}"; do
  base="${f%.en.srt}"
  date_part="${base%% - *}"
  title="${base#* - }"
  # yt-dlp appends " [VIDEOID]" via the -o template; peel it back off.
  vid="${title##*\[}"; vid="${vid%\]}"
  title="${title% \[*\]}"
  {
    printf -- '---\ntitle: %s\n' "$title"
    if [ "$date_part" != "$base" ]; then
      printf 'date: %s\n' "$date_part"
    fi
    printf 'video_id: %s\nurl: https://www.youtube.com/watch?v=%s\n' "$vid" "$vid"
    printf -- '---\n\n# %s\n\n' "$title"
    if [ "$STRIP" -eq 0 ]; then
      printf 'Link to any moment: `https://www.youtube.com/watch?v=%s&t=<seconds>s`\n\n' "$vid"
    fi
    awk -v chunk="$CHUNK" -v stamps="$((1 - STRIP))" -f "$AWK_PROG" "$f"
  } > "$base.md"
  mds+=("$base.md")
done

# Remove the intermediate .srt files, keep the readable .md
rm -f "${srts[@]}"

echo ">> Done. Transcripts:"
ls -1 "${mds[@]}"
