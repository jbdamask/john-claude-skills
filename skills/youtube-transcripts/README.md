# YouTube Channel Transcripts

Download transcripts for a YouTube channel's videos within a date range. The skill grabs English auto-captions and, by default, strips timestamps and the duplicate scroll-in lines to leave one readable `.txt` per video. Stripping is optional — pass `--keep-timestamps` to keep the raw `.srt` instead.

## What it does

- Walks a channel's uploads (newest-first) and pulls only the videos whose upload date falls inside your range — it does **not** scan the whole back catalog.
- Downloads English auto-captions and converts them to SRT.
- **By default**, strips timestamp lines, index numbers, and repeated scrolling-caption lines, writing one clean `YYYYMMDD - Title.en.txt` per video.
- **With `--keep-timestamps`**, skips the stripping and leaves the raw `YYYYMMDD - Title.en.srt` (timestamps and index lines intact) instead.
- Output lands in the current directory.

## Prerequisites

- **`yt-dlp`** and **`ffmpeg`** must be installed and on your `PATH`.

  Check:

  ```bash
  yt-dlp --version && ffmpeg -version | head -1
  ```

  Install on macOS:

  ```bash
  brew install yt-dlp ffmpeg
  ```

- A `bash` shell (the script uses `set -euo pipefail`, arrays, and `shopt`).
- Network access to YouTube. Videos without English auto-captions are silently skipped.

> Tip: keep `yt-dlp` current (`brew upgrade yt-dlp`) — YouTube changes break older versions.

## How to use

Ask for transcripts in natural language, e.g.:

- "download transcripts for all AI Daily Brief videos from July 2026"
- "get the captions from this channel for last month"
- "pull transcripts between two dates"

The skill needs three things and will ask for any that are missing:

- **channel_url** — e.g. `https://www.youtube.com/@AIDailyBrief/videos` (the `/videos` suffix is added automatically).
- **start** — inclusive start date, `YYYYMMDD`.
- **end** — inclusive end date, `YYYYMMDD`.

Optional:

- **max** — cap on the number of transcripts.
- **`--keep-timestamps`** — keep raw `.srt` files (timestamps + index lines) instead of stripping to plain `.txt`. Goes first.

## Running the script directly

```bash
scripts/fetch_transcripts.sh [--keep-timestamps] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]
```

All July 2026 videos from AI Daily Brief:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

At most 5 transcripts:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731 5
```

Keep raw `.srt` with timestamps:

```bash
scripts/fetch_transcripts.sh --keep-timestamps "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

## What's an `.srt` file?

`.srt` (SubRip Subtitle) is the plain-text file format subtitles ship in. It's just numbered caption blocks — an index, a start/end timestamp, and the line of text — like this:

```
1
00:00:01,000 --> 00:00:04,000
Welcome back to the show.

2
00:00:04,200 --> 00:00:07,500
Today we're talking about AI.
```

Any text editor opens it. This skill's default (stripped `.txt`) throws away the numbers and timestamps and keeps only the words, which is what you want for reading or feeding into another tool. Use `--keep-timestamps` when you actually need to know *when* something was said — e.g. clipping video or linking to a moment.

## Notes

- `yt-dlp` exits non-zero when `--break-match-filters` or `--max-downloads` trips; the script treats those as normal completion.
- Duplicate-line removal is global within each file — adjacent scroll-in repeats are the target, but a genuinely repeated phrase elsewhere gets collapsed too. That's fine for reading.

See [`SKILL.md`](./SKILL.md) for the full parameter reference and internals.
