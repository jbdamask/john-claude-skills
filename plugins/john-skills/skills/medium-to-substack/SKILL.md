---
name: medium-to-substack
description: Downloads one of the user's own Medium posts (full text plus images) and reformats it into a page they can paste straight into a new Substack post, with the title and subtitle split out for Substack's separate fields. Use when the user gives a medium.com link to their own post and says things like "move this to Substack", "cross-post my Medium post to Substack", "download this Medium post for Substack", or "make this Medium post pasteable into Substack". Only for posts the user wrote; stop if the byline is someone else.
---

# Medium to Substack

Turns one of the user's own Medium posts into:

- `post-for-substack.html`: a page to open in Chrome. It shows the Substack title and subtitle, and has a **Copy body** button that copies the formatted body (headings, bold and italic text, links, lists, code, images, captions) for pasting into the Substack editor.
- `post.md`: a plain Markdown backup that points to local images. It isn't for pasting, because Substack doesn't convert pasted Markdown.
- `images/01.jpeg`, `02.png`, and so on: every image in the order it appears, for manual upload if Substack doesn't import one.

## Ownership check (required)

Only use this skill on posts the user wrote. If you don't know the user's Medium name or handle, ask for it, unless the post URL is under their own `@handle` and they've said it's theirs. After extracting, compare the returned `author` with that name. If the post is by anyone else, stop and tell the user that this skill only cross-posts their own work. Don't build output for another writer's post.

## Steps

1. **Pick an output folder.** Use `<cwd>/substack/` unless the user names another location. If that folder already has files in it, use `substack-<post-slug>/` instead of overwriting them.

2. **Open the post in Chrome.** Medium returns a Cloudflare 403 to curl, and posts that aren't in the user's RSS feed (`https://medium.com/feed/@<handle>`) can't be fetched that way either, so go straight to the browser. Load the claude-in-chrome tools in one ToolSearch call: `tabs_context_mcp`, `navigate`, `javascript_tool`, `tabs_close_mcp`. Then navigate a new tab to the post URL. Drop tracking params such as `?sharedUserId=` from the URL.

3. **Extract the post.** Read `scripts/extract.js` and run its contents with `javascript_tool` in that tab. The script saves `~/Downloads/medium-<postid>.json` and returns `{file, author, title, blocks, images}`.
   - Run the ownership check on `author` now.
   - Don't try to return the article JSON through `javascript_tool`. The tool's output filter blocks it, because it contains URLs with query strings. That's why the script saves a file instead.
   - If `blocks` is very small, the page may be behind a paywall or still loading. Wait a moment and run the script again.

4. **Build the output.** Run:
   ```bash
   python3 -I <skill-dir>/scripts/build.py ~/Downloads/medium-<postid>.json <outdir>
   ```
   The script:
   - takes out Medium's "Listen / Share / More / Follow" buttons
   - moves the title and subtitle out of the body
   - removes query strings (tracking) from links and image URLs
   - bolds a "TL;DR" label
   - downloads the images

   It prints `{title, subtitle, images, outdir}`.

5. **Proofread.** Read `post.md`, then list for the user anything that needs a look:
   - typos and grammar slips
   - links to Medium-only pages, such as `medium.com/u/...` profile mentions, which mean less on Substack
   - inconsistent links, such as the same project linked to two different repos
   - embeds that became bare links

   **Don't change the wording on your own.** List the issues and fix them only after the user agrees. Apply each fix to both `post-for-substack.html` and `post.md`.

6. **Open and hand off.** Open the page with `open -a "Google Chrome" <outdir>/post-for-substack.html`, close the Medium tab, and tell the user:
   - the Substack title and subtitle to type into their own fields
   - to click **Copy body** on the page, then press Cmd+V in the Substack post body. If the button reports a fallback, the body is selected instead, so press Cmd+C first.
   - that Substack normally re-hosts images when you paste. Any image that doesn't appear can be uploaded from `images/`.
   - that `post.md` is only a backup and isn't meant for pasting
   - that they can delete `~/Downloads/medium-<postid>.json`

## Notes

- Images point to `miro.medium.com` in the HTML so the paste brings them along. The local copies are the fallback.
- YouTube, gist, and other embeds become a plain link. Paste that URL into Substack on its own line to turn it into an embed.
