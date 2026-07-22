---
name: youtube-transcripts
description: >
  Download transcripts (auto-captions) for videos from a YouTube channel within
  a date range, as timestamped markdown linked back to the source video. Use
  when the user wants to grab transcripts/subtitles/captions from a channel,
  e.g. "download transcripts for all AI Daily Brief videos from July 2026",
  "get the captions from this channel for last month", "pull transcripts
  between two dates". Requires yt-dlp and ffmpeg installed.
---

# YouTube Channel Transcripts

Downloads English auto-caption transcripts for a channel's videos in a given
date range and leaves one readable file per video: timestamped markdown `.md`
by default, or plain `.txt` with `--no-timestamps`.

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
- **--no-timestamps** (optional flag, goes first) — drop the timestamps and frontmatter, writing plain `.txt` instead of `.md`. Only worth it when the text is headed somewhere that can't use them.
- **--chunk N** (optional flag, goes first) — group the text into ~N-second paragraphs instead of one timestamped line per caption line. `--chunk 30` reads well as prose; the default (one line per caption line) is better for grepping and citing exact moments. Ignored with `--no-timestamps`.

Timestamped markdown is the default — don't pass a flag for it. The raw `.srt`
is always post-processed and never left behind either way.

Ask the user for any of the three required values that aren't given. Convert
natural-language ranges yourself ("July 2026" → `20260701` `20260731`).

## Usage

```bash
scripts/fetch_transcripts.sh [--no-timestamps] [--chunk N] <channel_url> <start_YYYYMMDD> <end_YYYYMMDD> [max]
```

Example — all July 2026 videos from AI Daily Brief, as timestamped markdown:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Example — at most 5 transcripts:

```bash
scripts/fetch_transcripts.sh "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731 5
```

Example — timestamps grouped into 30-second paragraphs:

```bash
scripts/fetch_transcripts.sh --chunk 30 "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Example — plain text, no timestamps:

```bash
scripts/fetch_transcripts.sh --no-timestamps "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Output lands in the current directory as `YYYYMMDD - Title [VIDEOID].md`, or
`YYYYMMDD - Title [VIDEOID].en.txt` with `--no-timestamps`. The video ID is kept
in the filename so a transcript can always be traced back to its source; the
`.md` also carries it in YAML frontmatter:

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

or, with `--chunk 30`, one timestamped paragraph per 30 seconds.

To deep-link a quote, convert its `[HH:MM:SS]` to seconds and append
`&t=<seconds>s` to the `url` from the frontmatter — no lookup or web search
needed.

## How it works

- Channels list newest-first, so the script uses `--break-match-filters` on the
  start date to stop walking the catalog once it passes below the range —
  it does not scan all videos.
- `--sub-langs en` (not `en.*`) avoids downloading both `en` and `en-orig`,
  which are duplicates on most channels.
- `--sub-format ttml` is what keeps the output clean. YouTube serves auto-captions
  in several formats; the default `vtt`/`srt` ones are a rolling two-line window
  where each cue repeats the previous line above the new one (interleaved with
  10 ms "hold" cues), so every phrase lands in the file about twice. `ttml` has
  one entry per phrase with no repetition, and `--convert-subs srt` turns it into
  a plain SRT. Requesting the right format beats deduplicating afterward — a
  transcript is allowed to contain genuinely repeated lines.
- The ttml → srt conversion wraps each line in `<font …>` styling tags; both
  output paths strip them.
- `scripts/srt_to_md.awk` does the `.md` formatting: it drops index and timestamp
  lines and re-tags each caption line with its start time as `[HH:MM:SS]`.

## Notes

- `yt-dlp` exits non-zero when `--break-match-filters` or `--max-downloads`
  trips; the script treats those as normal completion.
- If a video has no English auto-captions it's silently skipped.
- The script takes a snapshot of the directory before fetching, and only files
  that appear afterward are converted or cleaned up. Anything already present is
  counted, reported, and left untouched, whatever it's named — so running twice
  in the same directory can't mangle or delete the first run's output.
- This skill is YouTube-only by design. `--sub-format ttml` relies on YouTube
  offering that format, which it does for every video and language; other sites
  may not, in which case the fetch would find no matching subtitle format.
