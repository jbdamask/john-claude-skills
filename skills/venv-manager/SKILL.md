---
name: venv-manager
description: Manage Python virtual environments in a consistent, organized way. Use when a skill needs Python packages installed, or when the user wants to create a venv following standard conventions. Provides the authoritative convention for venv location and naming that other skills should follow.
---

# Venv Manager

Provides standardized conventions and commands for managing Python virtual environments. Other skills that need Python packages should reference this skill to ensure consistent organization.

## Convention

All virtual environments are stored in a standard location with consistent naming:

```
~/.venvs/<package-name>/
```

**Examples:**
- `~/.venvs/gitingest/`
- `~/.venvs/myproject/`

## When to Use

- Another skill needs a Python package installed
- User wants to create a venv following standard conventions
- User asks about venv organization or where venvs are stored

## Workflow

### 1. Check if Venv Already Exists

Before creating, check if the venv already exists:

```bash
ls ~/.venvs/<name>/bin/python 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
```

### 2. Create a New Venv

```bash
python3 -m venv ~/.venvs/<name>
```

### 3. Install Packages

Install one or more packages into the venv:

```bash
~/.venvs/<name>/bin/pip install <package1> <package2> ...
```

### 4. Run Commands in the Venv

To run a command using the venv's Python or installed packages:

```bash
~/.venvs/<name>/bin/<command> <args>
```

Or activate first (less preferred):

```bash
source ~/.venvs/<name>/bin/activate
<command> <args>
deactivate
```

## Complete Example

Creating a venv for gitingest:

```bash
# Check if exists
ls ~/.venvs/gitingest/bin/python 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"

# Create venv (if NOT_FOUND)
python3 -m venv ~/.venvs/gitingest

# Install package
~/.venvs/gitingest/bin/pip install gitingest

# Verify installation
~/.venvs/gitingest/bin/gitingest --version

# Use it
~/.venvs/gitingest/bin/gitingest https://github.com/owner/repo -o output.txt
```

## For Other Skills

If you're a skill that needs Python packages:

1. Ask the user how they want to install the package
2. If user chooses "create a venv for me", follow the conventions in this skill
3. Use `~/.venvs/<package-name>/` as the location
4. Run commands via `~/.venvs/<package-name>/bin/<command>`

## Listing Existing Venvs

To see what venvs exist:

```bash
ls -1 ~/.venvs/
```

## Removing a Venv

To remove a venv (requires user confirmation):

```bash
rm -rf ~/.venvs/<name>
```

**Always confirm with user before deleting.**
