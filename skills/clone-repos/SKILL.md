---
name: clone-repos
description: "Bulk-clone a set of git repositories into a single root directory using the bundled clone-repos.sh script. Use this whenever the user wants to clone several repos at once, pull down all the repos for a project or engineering estate, lay multiple repositories out side-by-side under one folder, or set up a local working tree of many repos (e.g. as the first step before reading, documenting, or doing an architecture review across a codebase). Trigger on phrases like 'clone these repos', 'clone all the repos', 'bulk clone', 'clone a bunch of repositories into a folder', or when the user hands over a list of git URLs and a destination directory."
---

# clone-repos

Clone many git repositories into one root directory in a single step, using the
bundled `assets/clone-repos.sh`. Each repo lands as a subdirectory beneath the root.

## When to use this

Reach for this whenever the user needs more than one repo cloned into a common
location — for example, pulling down every service in a project, or staging a
client's repos before an architecture/documentation pass. If the user only wants a
single repo cloned, a plain `git clone` is simpler and you don't need this skill.

## What you need from the user

Two things — ask for whatever is missing:

1. **A destination (root) directory** — where the repos should land. The script
   creates it if it doesn't exist.
2. **The repository URLs** — either as a list in the conversation, or a path to a
   file with one URL per line.

If the user mentions a maximum number of repos, note it — the script defaults to
cloning at most **5** and that cap is raised with `-n`.

## How to run it

The script lives at `assets/clone-repos.sh` relative to this skill's directory.
Resolve that absolute path, ensure it's executable, then invoke it with the Bash
tool. The general form:

```
<skill-dir>/assets/clone-repos.sh [-n NUM] [-f FILE] ROOT_DIR [REPO_URL ...]
```

| Option / arg | Meaning |
|--------------|---------|
| `ROOT_DIR`   | Required. Root directory the repos are cloned beneath (created if missing). |
| `REPO_URL …` | Zero or more git URLs to clone. |
| `-f FILE`    | Read repo URLs from a file, one per line (`#` comments and blanks ignored). |
| `-n NUM`     | Clone at most `NUM` repos. **Default 5.** Also settable via `CLONE_REPO_LIMIT`. |
| `-h`         | Print help. |

URLs passed on the command line and via `-f FILE` are combined; the `-n` limit
applies to the total.

**Important:** the default cap is 5. If the user supplies more than 5 URLs (or asks
for "all of them"), pass `-n` with a number at least as large as the count —
otherwise the extras are silently left unclone­d (the script reports how many it
skipped). When in doubt, set `-n` to the number of URLs you were given.

## Examples

**A few URLs given inline, into a fresh folder:**

```bash
/path/to/skill/assets/clone-repos.sh -n 3 ~/clients/acme \
  https://github.com/acme/api.git \
  https://github.com/acme/web.git \
  https://github.com/acme/common.git
```

**A list the user keeps in a file:**

```bash
/path/to/skill/assets/clone-repos.sh -n 20 ~/clients/acme -f ~/acme-repos.txt
```

**Override the cap with the environment variable instead of `-n`:**

```bash
CLONE_REPO_LIMIT=50 /path/to/skill/assets/clone-repos.sh ~/clients/acme -f repos.txt
```

## After running

The script is safe to re-run — it skips any repo already cloned (detected by a
`.git` directory at the destination) and prints a final `cloned / skipped / failed`
summary. Relay that summary to the user, and if any clone **failed** (non-zero exit),
surface which URL failed rather than reporting success. Common causes: a private repo
the user isn't authenticated for, or a typo'd URL.
