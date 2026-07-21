#!/usr/bin/env bash
# Download YouTube auto-caption transcripts from a channel within a date range,
# strip timestamps, and write clean .txt files.
#
# Usage:
#   fetch_transcripts.sh [--keep-timestamps] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]
#
# Args:
#   --keep-timestamps  optional; keep raw .srt (timestamps + index lines) instead
#                      of stripping to plain .txt
#   channel_url        e.g. https://www.youtube.com/@AIDailyBrief/videos
#   start              inclusive lower bound, YYYYMMDD
#   end                inclusive upper bound, YYYYMMDD
#   max                optional cap on number of transcripts (default: no cap)

set -euo pipefail

STRIP=1
if [ "${1:-}" = "--keep-timestamps" ]; then
  STRIP=0
  shift
fi

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 [--keep-timestamps] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]" >&2
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
  --convert-subs srt \
  -o "%(upload_date)s - %(title)s.%(ext)s" \
  "${MAX_ARG[@]+"${MAX_ARG[@]}"}" || true

shopt -s nullglob
srts=(*.en.srt)
if [ "${#srts[@]}" -eq 0 ]; then
  echo ">> No transcripts matched that range." >&2
  exit 0
fi

if [ "$STRIP" -eq 0 ]; then
  echo ">> Done. Keeping raw .srt (timestamps intact):"
  ls -1 "${srts[@]}"
  exit 0
fi

echo ">> Stripping timestamps from ${#srts[@]} file(s)..."
for f in "${srts[@]}"; do
  sed -E '/^[0-9]+$/d; /-->/d; /^[[:space:]]*$/d' "$f" \
    | awk '!seen[$0]++' > "${f%.srt}.txt"
done

# Remove the intermediate .srt files, keep the clean .txt
rm -f "${srts[@]}"

echo ">> Done. Clean transcripts:"
ls -1 *.en.txt
