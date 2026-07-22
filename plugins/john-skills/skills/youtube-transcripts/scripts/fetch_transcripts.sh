#!/usr/bin/env bash
# Download YouTube auto-caption transcripts from a channel within a date range,
# strip timestamps, and write clean .txt files.
#
# Usage:
#   fetch_transcripts.sh [--keep-timestamps] [--chunk N] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]
#
# Args:
#   --keep-timestamps  optional; keep timestamps, writing deduped .md instead of
#                      plain .txt
#   --chunk N          optional; with --keep-timestamps, group text into ~N-second
#                      paragraphs instead of one timestamped line per caption line
#   channel_url        e.g. https://www.youtube.com/@AIDailyBrief/videos
#   start              inclusive lower bound, YYYYMMDD
#   end                inclusive upper bound, YYYYMMDD
#   max                optional cap on number of transcripts (default: no cap)

set -euo pipefail

STRIP=1
CHUNK=0
while [ "$#" -gt 0 ]; do
  case "${1:-}" in
    --keep-timestamps) STRIP=0; shift ;;
    --chunk) CHUNK="${2:?--chunk needs a number of seconds}"; shift 2 ;;
    *) break ;;
  esac
done

case "$CHUNK" in
  ''|*[!0-9]*) echo "Error: --chunk must be a whole number of seconds" >&2; exit 1 ;;
esac

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 [--keep-timestamps] [--chunk N] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]" >&2
  exit 1
fi

URL="$1"
START="$2"
END="$3"
MAX="${4:-}"

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

shopt -s nullglob
srts=(*.en.srt)
if [ "${#srts[@]}" -eq 0 ]; then
  echo ">> No transcripts matched that range." >&2
  exit 0
fi

if [ "$STRIP" -eq 0 ]; then
  AWK_PROG="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/srt_to_md.awk"
  echo ">> Converting ${#srts[@]} file(s) to timestamped .md..."
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
      printf 'Link to any moment: `https://www.youtube.com/watch?v=%s&t=<seconds>s`\n\n' "$vid"
      awk -v chunk="$CHUNK" -f "$AWK_PROG" "$f"
    } > "$base.md"
    mds+=("$base.md")
  done

  # Remove the intermediate .srt files, keep the readable .md
  rm -f "${srts[@]}"

  echo ">> Done. Timestamped transcripts:"
  ls -1 "${mds[@]}"
  exit 0
fi

echo ">> Stripping timestamps from ${#srts[@]} file(s)..."
for f in "${srts[@]}"; do
  sed -E '/^[0-9]+$/d; /-->/d; s/<[^>]*>//g; /^[[:space:]]*$/d' "$f" > "${f%.srt}.txt"
done

# Remove the intermediate .srt files, keep the clean .txt
rm -f "${srts[@]}"

echo ">> Done. Clean transcripts:"
ls -1 *.en.txt
