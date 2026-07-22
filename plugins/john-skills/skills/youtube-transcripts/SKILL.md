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
date range and leaves one markdown file per video, with frontmatter linking it
back to the source video. Lines are timestamped by default; `--no-timestamps`
drops the times and leaves the prose.

## Requirements

`yt-dlp` and `ffmpeg` must be on PATH.

```bash
yt-dlp --version && ffmpeg -version | head -1
```

If missing on macOS: `brew install yt-dlp ffmpeg`.

## Parameters

- **channel_url** (required) — channel URL, e.g. `https://www.youtube.com/@AIDailyBrief/videos`. The `/videos` suffix is added automatically if absent.
- **start** — inclusive start date, `YYYYMMDD`. Defaults to 7 days ago.
- **end** — inclusive end date, `YYYYMMDD`. Defaults to today.
- **max** (optional) — cap on number of transcripts.
- **--no-timestamps** (optional flag, goes first) — omit the `[HH:MM:SS]` prefixes. Still markdown, still with the same frontmatter; only the per-line times go away.
- **--chunk N** (optional flag, goes first) — group the text into ~N-second paragraphs instead of one line per caption line. `--chunk 30` reads well as prose; the default is better for grepping and citing exact moments. Combines with `--no-timestamps` for plain paragraphs.

Timestamps are the default — don't pass a flag for them. Output is always `.md`,
and the intermediate `.srt` is never left behind.

Ask the user for the channel URL if it isn't given.

**If the request has no date range, ask for one before running.** An active
channel can have thousands of videos, and a request that doesn't mention dates
is far more likely to be an oversight than a request for the entire back
catalog. Offer the last 7 days as the default and let the user widen it. Only
skip the question when the user has already stated a range, said something like
"everything" or "all of it", or already declined to narrow it.

Convert natural-language ranges yourself ("July 2026" → `20260701` `20260731`,
"last month", "since May"). Look up today's date rather than assuming it.

The script applies the same 7-day default on its own if dates are omitted, so a
forgotten range can't turn into a full-catalog download — but ask first rather
than relying on that.

## Usage

```bash
scripts/fetch_transcripts.sh [--no-timestamps] [--chunk N] <channel_url> [start_YYYYMMDD] [end_YYYYMMDD] [max]
```

Omitting the dates fetches the last 7 days and says so.

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

Example — prose without timestamps:

```bash
scripts/fetch_transcripts.sh --no-timestamps "https://www.youtube.com/@AIDailyBrief/videos" 20260701 20260731
```

Output lands in the current directory as `YYYYMMDD - Title [VIDEOID].md`. The
video ID is kept in the filename so a transcript can always be traced back to
its source, and every file carries it in YAML frontmatter regardless of mode:

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

With `--chunk 30`, one paragraph per 30 seconds instead of one line per caption
line. With `--no-timestamps`, the same file minus the `[HH:MM:SS]` prefixes and
the deep-link hint — the frontmatter is unchanged.

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
