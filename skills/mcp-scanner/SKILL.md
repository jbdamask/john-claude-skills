---
name: mcp-scanner
description: Help users evaluate whether an MCP (Model Context Protocol) tool is safe and right for them before installing it. Use when a user wants to check, scan, review, or assess a third-party MCP server from GitHub, npm, or any repository URL. Provides plain-language assessments that anyone can understand, with technical details available on request.
---

# MCP Scanner

Evaluate MCP servers for safety, functionality, and legal compliance before installation.

## Communication Style

**Always default to plain language.** The user may not be technical. Use everyday analogies to explain security concepts. Only provide technical details (OWASP codes, code snippets, severity levels) when the user explicitly asks for them.

## Workflow

### Step 1: Understand What the User Wants

Before scanning, ask:
1. "What are you hoping this MCP will do for you?"
2. "Do you have any specific concerns about it?"

This helps you assess whether the MCP actually meets their needs.

### Step 2: Get the URL

Ask the user for the URL to the MCP. Accept:
- GitHub repository URLs
- npm package URLs
- PyPI package URLs
- Direct links to source files

### Step 3: Fetch Source Code

Use WebFetch to retrieve key files. See [url-patterns.md](references/url-patterns.md) for URL conversion patterns.

Fetch in this order:
1. **README.md** - Understand what the MCP claims to do
2. **LICENSE** - Check legal terms
3. **package.json** or **pyproject.toml** - Dependencies and entry point
4. **Main source file** - The actual code (index.ts, server.py, etc.)
5. **Tool definition files** - Where tools are registered

### Step 4: Analyze

#### A. Functionality Check
- Does the MCP do what the user needs?
- What tools/capabilities does it provide?
- Are there limitations or missing features?
- What setup is required?

#### B. Security Analysis
Review against [security-checklist.md](references/security-checklist.md). Look for:
- Critical: Hardcoded secrets, command injection, data exfiltration
- High: Missing auth, overly permissive scopes, token issues
- Medium: Missing logging, error handling
- Low: Missing docs, tests
- MCP-Specific: Tool annotations, transport security, spec compliance

#### C. Legal/License Check
Review against [license-guide.md](references/license-guide.md). Check:
- Is there a license file?
- What type of license?
- Any commercial use restrictions?

#### D. Current Advisories (Optional)
For high-stakes decisions, check [authoritative-sources.md](references/authoritative-sources.md) for:
- Known security advisories from AAIF/Linux Foundation
- Current OWASP MCP Top 10 guidance
- Whether the MCP is in any official registry

### Step 5: Deliver Report

**Always use the Plain Language Report first.**

---

## Report Template (Plain Language - Always Show This)

```
## MCP Assessment: [Name]

### The Bottom Line
[One sentence verdict: Safe to use / Proceed with caution / Don't install this]

### What This Tool Does
[2-3 sentences in plain English. What problem does it solve? How does it work?]

### Will It Work For You?
[Based on what they told you they want]
[Yes / No / Partially] - [Brief explanation]

### Should You Be Concerned?
[Plain language summary. Use analogies from the checklist.]
[If concerns exist, explain in everyday terms]
[If no concerns, say so clearly]

### My Recommendation
[Clear, actionable advice]

---
*Want the technical details? Just ask and I'll provide the full security analysis.*
```

---

## Technical Report (Only When Requested)

If user asks for details, provide:

```
### Detailed Security Findings

| Severity | Finding | Location |
|----------|---------|----------|
| [CRITICAL/HIGH/MEDIUM/LOW] | [Description] | [File:line] |

### OWASP MCP Top 10 Check
- MCP01 Token Mismanagement: [Pass/Fail/N/A]
- MCP02 Privilege Escalation: [Pass/Fail/N/A]
- [Continue for all 10...]

### License Details
- License Type: [Name]
- Commercial Use: [Yes/No/Conditional]
- Modification Allowed: [Yes/No/Conditional]
- Distribution Requirements: [Description]

### Dependencies of Concern
[List any suspicious or outdated dependencies]

### Code Snippets
[Relevant code showing concerns]
```

---

## Verdict Criteria

### Safe to Use
- No critical or high severity findings
- Clear, permissive license (MIT, Apache, BSD)
- Does what user needs
- Active maintenance (recent commits, responses to issues)

### Proceed with Caution
- Has medium severity findings OR
- Copyleft license (GPL, LGPL) OR
- Partially meets user needs OR
- Limited maintenance OR
- Missing documentation

### Don't Install This
- Any critical severity finding OR
- No license file OR
- Evidence of malicious intent OR
- Abandoned with known vulnerabilities OR
- Does not do what user needs

---

## Example Analogies

Use these to explain technical concepts:

| Concept | Analogy |
|---------|---------|
| Hardcoded credentials | "Like writing your PIN on your debit card" |
| Command injection | "Letting someone send commands to your computer through a text field" |
| Data exfiltration | "This tool might be sending your information somewhere without asking" |
| Overly permissive access | "Like giving the plumber keys to your whole house when they only need the bathroom" |
| No license | "The author hasn't said you can use this - legally risky" |
| Missing audit logs | "No record of what this tool does - like a store with no security cameras" |
| Token passthrough | "Like a security guard who waves through anyone with a badge, real or fake" |

---

## What If I Can't Access the Code?

If the repository is private or returns 404:
- Inform the user you cannot access the source code
- Explain that without code review, you cannot verify safety
- Suggest they contact the author or find an alternative with public source code

---

## Staying Current

The MCP ecosystem evolves rapidly. This skill uses foundational security principles that don't change, but specific advisories and best practices do.

**For high-stakes decisions**, use WebFetch to check:
1. `https://modelcontextprotocol.io/specification/draft/basic/security_best_practices` - Latest official guidance
2. `https://owasp.org/www-project-mcp-top-10/` - Current vulnerability categories

**What stays stable** (hardcoded in this skill):
- Core security patterns (injection, exfiltration, auth gaps)
- License compatibility principles
- MCP Trust Principles (consent, control, privacy)
- Tool annotation expectations

**What changes** (check authoritative sources):
- Specific CVEs and advisories
- New attack vectors
- Ecosystem registries and certifications
- Governance updates

See [authoritative-sources.md](references/authoritative-sources.md) for the full list of trusted sources.
