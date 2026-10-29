# Medium to Substack

Cross-post one of your own Medium posts to Substack. You get a page you can open in Chrome and copy from, with the post body formatted the way Substack's editor expects when you paste.

## What it does

- Opens the post in Chrome (Medium blocks direct downloads) and saves the article as JSON.
- Checks the byline and stops if the post isn't yours.
- Builds three things in `./substack/`:
  - `post-for-substack.html`: shows the Substack title and subtitle, and has a **Copy body** button
  - `post.md`: a Markdown backup (Substack doesn't convert pasted Markdown, so don't paste this)
  - `images/`: every image, numbered in the order it appears
- Takes out Medium's "Listen / Share / More" buttons and the tracking parameters on links.
- Lists typos and Medium-only links for you to review. It doesn't change your wording unless you say so.

## Usage

```
/medium-to-substack https://medium.com/@you/your-post-id
```

Then in Substack:

1. Type the title and subtitle into their own fields.
2. On the open page, click **Copy body**.
3. Press Cmd+V in the Substack post body.

Substack normally re-hosts the images when you paste. Upload any that don't appear from `images/`.

## Requirements

- Chrome with the Claude in Chrome extension
- Python 3 (standard library only)
