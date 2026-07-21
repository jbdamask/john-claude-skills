---
name: repo-security-review
description: Security audit for GitHub repositories before installation. Use when user wants to check if a repo/app is safe to install, review install scripts for malicious code, verify an open source project isn't collecting data, or audit dependencies for suspicious packages. Triggers on phrases like "is this safe to install", "check this repo", "review this script", "audit this code", "is this sketchy".
---

# Repo Security Review

Perform security audits on GitHub repositories to identify data exfiltration, malicious code, or suspicious behavior before installation.

## Workflow

### 1. Gather Repository Info
- Fetch the main page to understand what the project does
- Locate the GitHub repository URL
- Identify install scripts (install.sh, setup.py, Makefile, etc.)

### 2. Review Install Scripts
Fetch and analyze all install scripts for:
- **URLs contacted** - Should only be official sources (GitHub releases, package registries)
- **Commands executed** - Look for curl/wget to unknown hosts, eval of remote code
- **File system access** - Unexpected writes outside install directory
- **Environment variables** - Harvesting of secrets, API keys, credentials

### 3. Audit Source Code
Examine main application code for:
- **Network calls** - All HTTP/HTTPS requests and their destinations
- **Data collection** - Any telemetry, analytics, or phone-home behavior
- **File access** - Reading sensitive files (~/.ssh, ~/.aws, credentials)
- **Obfuscated code** - Base64 encoded strings, eval(), exec()

### 4. Check Dependencies
Review dependency files (package.json, go.mod, requirements.txt, Cargo.toml):
- Look for analytics/telemetry packages
- Check for typosquatted package names
- Verify packages are from reputable sources

### 5. Provide Assessment
Summarize findings with:
- **Overall verdict** (Safe / Caution / Unsafe)
- **Network activity** - All external endpoints contacted
- **Data storage** - Where data is stored (local vs remote)
- **Red flags found** - Any suspicious patterns
- **Recommendation** - Install as-is, build from source, or avoid

## Red Flags Reference

See [references/red-flags.md](references/red-flags.md) for comprehensive list of suspicious patterns.

## Key Suspicious Patterns (Quick Reference)

**Install scripts:**
- `curl | bash` from non-official URLs
- Hidden file creation (dotfiles outside expected locations)
- Modification of shell profiles to inject code
- Download and execute without verification

**Source code:**
- Hardcoded IPs or non-GitHub/official URLs
- Base64 encoded payloads
- Reading SSH keys, AWS credentials, browser data
- Sending data to analytics endpoints
- Obfuscated variable names

**Dependencies:**
- `analytics`, `telemetry`, `tracking` packages
- Misspelled package names (typosquatting)
- Packages with very few downloads/stars
- Dependencies from personal GitHub repos

## Output Format

```
## Security Review Summary: [Project Name]

### [Status Emoji] Install Script - [CLEAN/SUSPICIOUS/DANGEROUS]
[Findings]

### [Status Emoji] Application Code - [CLEAN/SUSPICIOUS/DANGEROUS]
[Findings]

### [Status Emoji] Dependencies - [CLEAN/SUSPICIOUS/DANGEROUS]
[Findings]

### Assessment
[Overall verdict and recommendation]
```

Use checkmarks for clean, warning signs for suspicious, X for dangerous.
