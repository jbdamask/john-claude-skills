# YouTube Channel Transcripts

Download transcripts for a YouTube channel's videos within a date range. You get one markdown file per video, timestamped and linked back to the source.

## What it does

- Walks a channel's uploads and pulls only the videos whose upload date falls inside your range — it does **not** scan the whole back catalog.
- Writes one `YYYYMMDD - Title [VIDEOID].md` per video into the current directory.
- Leaves any files that were already in that directory untouched.

Each file looks like this:

```markdown
---
title: Is Kimi K3 Really Fable Class
date: 20260721
video_id: lmQqiWQF_8I
url: https://www.youtube.com/watch?v=lmQqiWQF_8I
---

# Is Kimi K3 Really Fable Class

Link to any moment: `https://www.youtube.com/watch?v=lmQqiWQF_8I&t=<seconds>s`

[00:00:00] Today on the AI Daily Brief, did we
[00:00:02] actually just get a fable level open
```

To link a quote, convert its `[HH:MM:SS]` to seconds and append `&t=<seconds>s` to the frontmatter `url`.

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
- Network access to YouTube. Videos without English auto-captions are skipped.

> Tip: keep `yt-dlp` current (`brew upgrade yt-dlp`) — YouTube changes break older versions.

## How to use

Ask for transcripts in natural language, e.g.:

- "download transcripts for all AI Daily Brief videos from July 2026"
- "get the captions from this channel for last month"
- "pull transcripts between two dates"

- **channel_url** — e.g. `https://www.youtube.com/@AIDailyBrief/videos` (the `/videos` suffix is added automatically). You'll be asked for this if you don't give it.
- **start** and **end** — inclusive date bounds, `YYYYMMDD`. If your request doesn't mention a date range you'll be asked for one, since a busy channel can hold thousands of videos. The default is the last 7 days.

Optional:

- **max** — cap on the number of transcripts.
- **`--no-timestamps`** — leave out the `[HH:MM:SS]` prefixes. Goes first.
- **`--chunk N`** — group the text into ~N-second paragraphs rather than one line per caption line. Reads better as prose; harder to cite a precise moment from. Goes first.

## Running the script directly

```bash
scripts/fetch_transcripts.sh [--no-timestamps] [--chunk N] <channel_url> [start_YYYYMMDD] [end_YYYYMMDD] [max]
```

Last 7 days (the dates are optional):

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos"
```

All July 2026 videos from AI Daily Brief:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

At most 5 transcripts:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731 5
```

Prose in 30-second paragraphs, no timestamps:

```bash
scripts/fetch_transcripts.sh --no-timestamps --chunk 30 "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

## Notes

- **Tested only on macOS.** The script has been exercised on Mac (including its default Bash 3.2) and not yet on Linux or Windows/WSL. It should work on any POSIX-ish `bash`, but treat non-Mac use as untested.
- Transcripts come from YouTube's automatic captions, so expect the occasional misheard word — proper nouns especially.
- `yt-dlp` exits non-zero when it stops early at a date boundary or download cap; the script treats those as normal completion.

See [`SKILL.md`](./SKILL.md) for the full parameter reference and internals.
