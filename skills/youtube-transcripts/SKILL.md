---
name: youtube-transcripts
description: >
  Download clean text transcripts (auto-captions, timestamps stripped) for
  videos from a YouTube channel within a date range. Use when the user wants
  to grab transcripts/subtitles/captions from a channel, e.g. "download
  transcripts for all AI Daily Brief videos from July 2026", "get the captions
  from this channel for last month", "pull transcripts between two dates".
  Requires yt-dlp and ffmpeg installed.
---

# YouTube Channel Transcripts

Downloads English auto-caption transcripts for a channel's videos in a given
date range, converts them to plain text with timestamps and duplicate scroll
lines removed, and leaves one `.txt` per video.

## Requirements

`yt-dlp` and `ffmpeg` must be on PATH.

```bash
yt-dlp --version && ffmpeg -version | head -1
```

If missing on macOS: `brew install yt-dlp ffmpeg`.

## Parameters

- **channel_url** (required) — channel URL, e.g. `https://www.youtube.com/@AIDailyBrief/videos`. The `/videos` suffix is added automatically if absent.
- **start** (required) — inclusive start date, `YYYYMMDD`.
- **end** (required) — inclusive end date, `YYYYMMDD`.
- **max** (optional) — cap on number of transcripts.
- **--keep-timestamps** (optional flag, goes first) — keep raw `.srt` files with timestamps and index lines instead of stripping to plain `.txt`. Default is to strip.

Ask the user for any of the three required values that aren't given. Convert
natural-language ranges yourself ("July 2026" → `20260701` `20260731`).

## Usage

```bash
scripts/fetch_transcripts.sh [--keep-timestamps] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]
```

Example — all July 2026 videos from AI Daily Brief:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Example — at most 5 transcripts:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731 5
```

Example — keep timestamps (raw `.srt`):

```bash
scripts/fetch_transcripts.sh --keep-timestamps "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Output is `YYYYMMDD - Title.en.txt` (stripped) or `YYYYMMDD - Title.en.srt` (with `--keep-timestamps`) in the current directory.

## How it works

- Channels list newest-first, so the script uses `--break-match-filters` on the
  start date to stop walking the catalog once it passes below the range —
  it does not scan all videos.
- `--sub-langs en` (not `en.*`) avoids downloading both `en` and `en-orig`,
  which are duplicates on most channels.
- Timestamp lines, index numbers, and the repeated scroll-in caption lines are
  stripped; only readable text remains.

## Notes

- `yt-dlp` exits non-zero when `--break-match-filters` or `--max-downloads`
  trips; the script treats those as normal completion.
- If a video has no English auto-captions it's silently skipped.
- The duplicate-line removal is global within a file. Adjacent repeats from
  scrolling captions are the target; a genuinely repeated phrase elsewhere
  gets collapsed too, which is fine for reading.
