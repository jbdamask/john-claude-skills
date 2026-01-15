---
name: gitingest
description: Convert any Git repository into a text file optimized for LLM consumption using GitIngest. Use when the user wants to ingest a repo, create a text digest of a codebase, prepare a repository for LLM analysis, or needs to convert a GitHub URL to a readable text file.
---

# GitIngest

Convert any Git repository into a prompt-friendly text file for LLM consumption. GitIngest extracts the structure and contents of a repository into a single text file that can be easily processed by language models.

## When to Use

- User wants to analyze an entire codebase with an LLM
- User needs a text representation of a repository
- User mentions "ingest", "digest", or converting a repo to text
- User wants to prepare code for LLM context

## Prerequisites

GitIngest must be installed in a virtual environment. Never install directly to the host system.

### Setup Virtual Environment

Create a dedicated venv for gitingest (one-time setup):

```bash
python3 -m venv ~/.venvs/gitingest
source ~/.venvs/gitingest/bin/activate
pip install gitingest
deactivate
```

### Running GitIngest

Always activate the venv before running:

```bash
source ~/.venvs/gitingest/bin/activate
gitingest <args>
deactivate
```

Or run directly without activating:

```bash
~/.venvs/gitingest/bin/gitingest <args>
```

### Check Installation

```bash
~/.venvs/gitingest/bin/gitingest --version
```

If the venv doesn't exist, create it using the setup steps above.

## Workflow

### 1. Identify the Target

Determine what the user wants to ingest:
- **Local directory:** A path on the filesystem
- **GitHub URL:** A repository URL like `https://github.com/owner/repo`
- **Current directory:** If unspecified, confirm with user

### 2. Run GitIngest

Use the venv binary directly (recommended) or activate the venv first.

**For a local directory:**
```bash
~/.venvs/gitingest/bin/gitingest /path/to/repository -o output.txt
```

**For a GitHub repository:**
```bash
~/.venvs/gitingest/bin/gitingest https://github.com/owner/repo -o output.txt
```

**For the current directory:**
```bash
~/.venvs/gitingest/bin/gitingest . -o output.txt
```

### 3. Common Options

| Option | Description |
|--------|-------------|
| `-o <file>` | Output to specified file (use `-` for stdout) |
| `-t <token>` | GitHub token for private repos |
| `--include-gitignored` | Include files normally ignored by .gitignore |
| `--include-submodules` | Process git submodules |

**Private repositories:** If the user needs to ingest a private repo, they must provide a GitHub token:
```bash
~/.venvs/gitingest/bin/gitingest https://github.com/owner/private-repo -t <GITHUB_TOKEN> -o output.txt
```

Or set the environment variable:
```bash
export GITHUB_TOKEN=<token>
~/.venvs/gitingest/bin/gitingest https://github.com/owner/private-repo -o output.txt
```

### 4. Output

GitIngest produces a text file containing:
- Repository structure (directory tree)
- File contents with clear delimiters
- Token count estimate (useful for LLM context limits)

After running, confirm success and report:
- Output file location
- Approximate size/token count if available
- Any warnings or skipped files

## Example Usage

**User:** "Ingest the FastAPI repository"

```bash
~/.venvs/gitingest/bin/gitingest https://github.com/tiangolo/fastapi -o fastapi-digest.txt
```

**User:** "Create a text file of this project for Claude"

```bash
~/.venvs/gitingest/bin/gitingest . -o project-digest.txt
```

**User:** "I need to analyze a private repo"

```bash
# User must provide token
~/.venvs/gitingest/bin/gitingest https://github.com/owner/private-repo -t ghp_xxxx -o output.txt
```

## Tips

- Output files can be large for big repositories - warn user about potential size
- Token counts help users understand if the output will fit in LLM context windows
- For very large repos, consider suggesting the user focus on specific subdirectories
- The output is optimized for LLM consumption but is also human-readable

## Reference

- **GitHub:** https://github.com/coderamp-labs/gitingest
- **Web interface:** Replace "hub" with "ingest" in any GitHub URL (e.g., `gitingest.com/owner/repo`)
