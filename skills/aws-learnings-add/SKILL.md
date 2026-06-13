---
name: aws-learnings-add
description: "Contribute a new lesson to the AWS Learnings library (the llms.txt-format library at github.com/jbdamask/aws-learnings-library). Use this whenever you've just debugged, fixed, or discovered a non-obvious AWS gotcha — CloudFormation, CDK, Lambda, API Gateway, IAM, S3, CloudFront, EC2, EventBridge, SQS, Secrets Manager, SSM — and want to capture it for next time. Triggers on phrases like 'add an AWS learning', 'save this AWS lesson', 'capture this gotcha', 'add this to the learnings library', or after solving a tricky AWS deployment problem worth remembering. This skill WRITES files (a new lesson file + an updated index) and prepares a pull request; it is the write companion to the read-only 'aws-learnings' skill."
---

# AWS Learnings — Add a Lesson

## Overview

The AWS Learnings library is a collection of hard-won AWS deployment lessons, published in [llms.txt](https://llmstxt.org/) format so coding agents can fetch just the lessons relevant to a task. It lives at:

**Repo:** https://github.com/jbdamask/aws-learnings-library

Structure:
- `llms.txt` — the index: grouped by AWS service, one bullet per lesson (link + one-line summary).
- `lessons/<service>-<NNN>-<SS>.md` — one self-contained lesson per file, each with YAML frontmatter + body. (`SS` is a two-digit seconds suffix added at creation time to avoid collisions between concurrent contributors; the original curated lessons predate this and use the plain `<service>-<NNN>.md` form.)

This skill adds a new lesson: it writes the new `lessons/<id>.md` file, inserts a matching entry into `llms.txt`, commits the change on a branch, and then tells the user how to open a pull request. **The library is the source of truth and changes land via PR** — so this skill never pushes to `main` or merges; it stops at "here's how to open the PR."

## Why a PR, and how the handoff degrades gracefully

The library is the source of truth and changes land via PR — so this skill never pushes to `main` or merges; it prepares the change on a branch and opens (or hands off) a PR.

Anyone on any machine should be able to contribute, so the skill adapts to the available tooling:
- **If the GitHub CLI (`gh`) is installed and authenticated, the skill submits the PR automatically** — push the branch and `gh pr create`, then report the PR URL.
- **If `gh` is absent or not authenticated, it falls back to plain `git`** (clone, branch, commit, push) and hands the user a ready-to-click GitHub compare URL to open the PR in the browser.

Everything up to step 7 is identical either way; only the final handoff differs. The skill must never *depend* on `gh` — it's an accelerator when present, not a requirement.

## Workflow

### 1. Locate (or obtain) a local clone of the library

The lesson files must be written into a working copy of the repo.

1. Check whether the current project already *is* the library: look for `llms.txt` + a `lessons/` directory with a git remote pointing at `aws-learnings-library`.
2. Otherwise, search common locations (e.g. `~/code`, `~/projects`, `~/src`, `~/git`, the current directory's siblings) for a clone:
   ```bash
   find ~ -maxdepth 4 -type d -name aws-learnings-library 2>/dev/null
   ```
3. If no clone is found, offer to make one in a sensible spot (don't assume `gh`):
   ```bash
   git clone https://github.com/jbdamask/aws-learnings-library.git
   ```
   If the user can't or won't clone, you can still help by drafting the lesson file content and the index entry as text for them to paste in manually — but the clean path is a local clone.

Set `LIB=<path to the clone>` for the rest of the workflow.

### 2. Draft the lesson from the current context

The most valuable lessons are **generalized** from a specific incident — strip the project-specific names, keep the transferable insight. Most often you'll be invoked right after solving a problem, so pull the material from the current conversation. Capture:

- **Problem** — the observable symptom (the error message, the wrong behavior). Lead with what the user would actually see, so future readers recognize their situation.
- **Root Cause** — *why* it happened. This is the heart of the lesson; explain the underlying AWS behavior, not just the fix.
- **Solution** — the concrete fix, with a minimal code/YAML/CLI snippet. Use placeholder names (`myapp-*`, `your-prefix-*`), not the originating project's real identifiers.
- **Key Insight** (optional) — the one-sentence takeaway that generalizes beyond this case.

Keep it tight and faithful to the existing lessons' voice — look at a couple of files in `$LIB/lessons/` for the house style before writing.

### 3. Pick the service and the lesson ID

Lesson IDs have the form `<service>-<NNN>-<SS>`:
- `<service>` — the prefix for the lesson's **primary** service.
- `<NNN>` — a zero-padded 3-digit sequence number, one higher than the current max for that prefix.
- `<SS>` — the **two-digit seconds** of the current time (`date +%S`, e.g. `42`).

The seconds suffix exists to **prevent ID collisions when several people contribute concurrently**: two contributors who independently grab the same next sequence number (e.g. both compute `apigw-006`) will almost always be running at different wall-clock seconds, so their files and index entries won't clash. It's a cheap guard, not a guarantee — but it makes same-number collisions vanishingly unlikely without any central coordination.

Existing service prefixes:

`apigw`, `lambda`, `iam`, `s3`, `cloudfront`, `cfn` (CloudFormation), `secrets`, `frontend`, `ec2`, `eventbridge`, `sqs`, `spot`

If the lesson is about a genuinely new service not in the list, coin a short, lowercase, obvious prefix (e.g. `dynamodb`, `stepfunctions`, `cognito`).

Compute the ID:
```bash
PREFIX=apigw   # the chosen service prefix
# highest existing sequence number for this prefix (tolerates the -SS suffix on newer files)
MAX=$(ls "$LIB/lessons/" | grep -E "^${PREFIX}-[0-9]{3}" | sed -E "s/^${PREFIX}-([0-9]+).*/\1/" | sort -n | tail -1)
NEXT=$(printf '%03d' $(( ${MAX:-0} + 1 )))   # 001 if no files exist yet for a new prefix
SS=$(date +%S)                                # two-digit seconds, 00–59
ID="${PREFIX}-${NEXT}-${SS}"                  # e.g. apigw-006-42
echo "$ID"
```

### 4. Write the lesson file

Create `$LIB/lessons/<id>.md` using this exact frontmatter shape (it's what makes the library machine-readable and lets the index be regenerated):

```markdown
---
id: apigw-006-42
title: Short Imperative Title of the Lesson
services: [API Gateway]
summary: One sentence — the gotcha and the fix, dense enough to decide relevance from the index alone.
---

# Short Imperative Title of the Lesson

**Problem:** ...

**Root Cause:** ...

**Solution:** ...
\```yaml
# minimal, generalized snippet
\```

**Key Insight:** ...   # optional
```

Notes:
- `services` is a list of human-readable service names (e.g. `[API Gateway, Lambda]`), used for cross-referencing.
- `summary` is reused verbatim (or near-verbatim) as the index bullet's description — write it once, well.
- The H1 should match `title`.

### 5. Add the entry to the index (`llms.txt`)

Insert a bullet under the matching `## <Service>` heading in `$LIB/llms.txt`, in the same format as the existing entries. The link must be the **fully-qualified raw URL** so an agent can fetch it directly:

```
- [Short link text](https://raw.githubusercontent.com/jbdamask/aws-learnings-library/main/lessons/<id>.md): <summary>.
```

- Append within the existing section (rough numeric/topical order is fine).
- If the lesson introduces a **new** service prefix, add a new `## <Service>` section. Place it sensibly among the existing headings.
- Don't disturb the `# AWS Learnings` title or the `>` blockquote intro at the top.

### 6. Commit on a branch (never on `main`)

```bash
cd "$LIB"
git checkout -b add-lesson-<id>
git add llms.txt "lessons/<id>.md"
git commit -m "Add lesson <id>: <title>"
```

Per the user's global preferences, do **not** attribute the commit to Claude/Anthropic.

### 7. Open the PR — automatically via `gh` if it's available, otherwise hand off to the browser

First detect whether the GitHub CLI is installed **and** authenticated:
```bash
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "gh-ready"
fi
```

**If `gh` is ready → submit the PR for the user.** Push the branch and create the PR directly; no manual step required:
```bash
git push -u origin add-lesson-<id>
gh pr create \
  --base main \
  --title "Add lesson <id>: <title>" \
  --body "Adds lesson \`<id>\` (<title>) to the AWS Learnings library, plus its index entry in llms.txt."
```
`gh pr create` prints the PR URL on success — surface that URL to the user so they can track it. (If `gh auth status` showed an account without push access to `jbdamask/aws-learnings-library`, `gh` will offer to fork and open the PR from the fork — let it; that's the correct behavior for outside contributors.)

**If `gh` is not installed or not authenticated → fall back to the browser path.** Push the branch, then hand the user a ready-to-click compare URL:
```bash
git push -u origin add-lesson-<id>
```
> Open a pull request here:
> https://github.com/jbdamask/aws-learnings-library/compare/main...add-lesson-<id>?expand=1

If the user lacks push access (and has no `gh` to auto-fork), they'll need to fork the repo first, push the branch to their fork, and open the PR from there — explain that briefly.

Either way, end by summarizing what was added: the new lesson id/title, the file path, the index section it landed under, and the PR URL (or the compare URL the user should open).

## Guardrails

- **One lesson per invocation, one lesson per file.** If the user describes several distinct gotchas, create several files (and several index entries), each with its own id.
- **Never merge or push to `main`.** Stop at the PR. The library owner reviews contributions.
- **Generalize.** Replace real account IDs, bucket names, ARNs, and project names with placeholders before writing. Never paste secrets, tokens, or credentials into a lesson.
- **Match the house style.** Read an existing lesson or two first; keep the Problem / Root Cause / Solution / Key Insight rhythm.
