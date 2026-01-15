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

## Required Package

This skill requires the `gitingest` Python package.

## Workflow

### 1. Check if GitIngest is Available

First, check if gitingest is already installed and accessible:

```bash
which gitingest || echo "NOT_FOUND"
```

Also check common venv locations:
```bash
ls ~/.venvs/gitingest/bin/gitingest 2>/dev/null || echo "NOT_IN_VENVS"
```

### 2. If Not Installed, Ask User

If gitingest is not found, ask the user how they'd like to install it:

**Ask:** "The `gitingest` package is required but not installed. How would you like to install it?"

**Options:**
- **Specify path** - User provides path to existing venv or installation
- **Create a venv for me** - Convenience option: look up the venv-manager skill by name/description and use it to create a venv and install the package

If user chooses the convenience option, discover and invoke a venv-manager skill to handle the installation. Do not hardcode venv paths - let the venv-manager skill decide the organization.

### 3. Identify the Target

Once gitingest is available, determine what the user wants to ingest:
- **Local directory:** A path on the filesystem
- **GitHub URL:** A repository URL like `https://github.com/owner/repo`
- **Current directory:** If unspecified, confirm with user

### 4. Run GitIngest

Run gitingest using the path determined in steps 1-2. Examples use `<gitingest>` as placeholder for the actual path:

**For a local directory:**
```bash
<gitingest> /path/to/repository -o output.txt
```

**For a GitHub repository:**
```bash
<gitingest> https://github.com/owner/repo -o output.txt
```

**For the current directory:**
```bash
<gitingest> . -o output.txt
```

### 5. Common Options

| Option | Description |
|--------|-------------|
| `-o <file>` | Output to specified file (use `-` for stdout) |
| `-t <token>` | GitHub token for private repos |
| `--include-gitignored` | Include files normally ignored by .gitignore |
| `--include-submodules` | Process git submodules |

**Private repositories:** If the user needs to ingest a private repo, they must provide a GitHub token:
```bash
<gitingest> https://github.com/owner/private-repo -t <GITHUB_TOKEN> -o output.txt
```

Or set the environment variable:
```bash
export GITHUB_TOKEN=<token>
<gitingest> https://github.com/owner/private-repo -o output.txt
```

### 6. Output

GitIngest produces a text file containing:
- Repository structure (directory tree)
- File contents with clear delimiters
- Token count estimate (useful for LLM context limits)

After running, confirm success and report:
- Output file location
- Approximate size/token count if available
- Any warnings or skipped files

## Tips

- Output files can be large for big repositories - warn user about potential size
- Token counts help users understand if the output will fit in LLM context windows
- For very large repos, consider suggesting the user focus on specific subdirectories
- The output is optimized for LLM consumption but is also human-readable

## Reference

- **GitHub:** https://github.com/coderamp-labs/gitingest
- **Web interface:** Replace "hub" with "ingest" in any GitHub URL (e.g., `gitingest.com/owner/repo`)
