# MCP Security Checklist

Use this checklist when analyzing MCP server source code. Items are grouped by severity.

## Critical Findings (Recommend: Don't Install)

### Hardcoded Secrets
- API keys, tokens, passwords in source code
- Look for: `apiKey`, `secret`, `password`, `token`, `bearer`, `authorization`
- Check: `.env.example` files that contain real values

### Dangerous Command Execution
- `eval()`, `exec()`, `child_process.exec()` with user input
- Shell command construction without sanitization
- `subprocess.run(shell=True)` with untrusted input

### Data Exfiltration Patterns
- HTTP calls to unknown/hardcoded external endpoints
- WebSocket connections to third-party servers
- Data being sent to URLs not related to the MCP's stated purpose

### File System Abuse
- Access to paths outside expected scope (e.g., `~/.ssh`, `/etc/passwd`)
- Ability to read/write arbitrary files
- No path traversal protection (`../` patterns)

## High Severity (Recommend: Proceed with Caution)

### Missing Input Validation
- User input passed directly to database queries
- No schema validation on tool inputs
- Missing type checking on parameters

### Overly Permissive Scopes
- Requests for more permissions than needed
- `*` or `all` in scope requests
- Access to entire file system when only one directory needed

### Token/Auth Issues
- Long-lived tokens without rotation
- Tokens stored in plaintext
- Missing token validation
- Token passthrough (forwarding unvalidated tokens)

### Missing Authentication
- No auth on sensitive operations
- Weak session management
- Predictable session IDs

## Medium Severity (Note in Report)

### Error Handling
- Errors expose sensitive information
- Stack traces visible to users
- Missing error boundaries

### Logging Gaps
- No audit logging for sensitive operations
- Sensitive data logged in plaintext
- Missing request/response logging

### Network Security
- HTTP instead of HTTPS
- Missing certificate validation
- No rate limiting

### Session Management
- Sessions don't expire
- No session binding to user
- Missing CSRF protection

## Low Severity (Mention if Relevant)

### Code Quality
- No tests
- Missing documentation
- Outdated dependencies with known vulnerabilities

### Best Practices
- Missing license file
- No SECURITY.md or security policy
- No contribution guidelines

---

## MCP-Specific Checks

These are foundational MCP patterns that indicate quality and security.

### Tool Annotations
Well-built MCPs annotate their tools with behavioral hints:
- `readOnlyHint` - Tool only reads data, doesn't modify
- `destructiveHint` - Tool can delete or permanently modify data
- `idempotentHint` - Running multiple times has same effect as once
- `openWorldHint` - Tool interacts with external systems

**What to check**:
- Are tools annotated? (Missing = less trustworthy)
- Do annotations match actual behavior? (Mislabeled = red flag)
- Are destructive tools clearly marked?

### Transport Security
MCPs use different transports with different security implications:

**stdio (local)**:
- Should not log sensitive data to stdout
- Appropriate for single-user, local-only use

**Streamable HTTP (remote)**:
- Should validate Origin headers
- Should enable DNS rebinding protection
- Should bind to 127.0.0.1 for local servers
- Should use HTTPS for remote deployment

**What to check**:
- Does the transport match the use case?
- Are appropriate protections in place?

### Spec Compliance
- What MCP spec version does it target?
- Is it using deprecated patterns?
- Does it follow current SDK conventions?

### Ecosystem Standing
- Is the MCP from a known, reputable source?
- Is it listed in any official registry?
- Check [authoritative-sources.md](authoritative-sources.md) for current advisories

## OWASP MCP Top 10 Reference

When analyzing, check for these specific vulnerabilities:

| ID | Name | What to Look For |
|----|------|------------------|
| MCP01 | Token Mismanagement | Hardcoded creds, long-lived tokens, secrets in logs |
| MCP02 | Privilege Escalation | Scope creep, permission accumulation over time |
| MCP03 | Tool Poisoning | Tool descriptions with hidden instructions |
| MCP04 | Supply Chain | Suspicious dependencies, typosquatting packages |
| MCP05 | Command Injection | Unsanitized input in shell commands |
| MCP06 | Prompt Injection | Untrusted data in prompts to LLM |
| MCP07 | Auth Gaps | Missing or weak authentication |
| MCP08 | No Audit Trail | Missing logging, no telemetry |
| MCP09 | Shadow Servers | Unauthorized MCP deployments |
| MCP10 | Context Leakage | Shared context between users/sessions |

## MCP Trust Principles to Verify

From the official specification:
- Does the MCP respect user consent for data access?
- Does it give users control over shared data?
- Are tool descriptions honest about what tools do?
- Does it protect data privacy appropriately?

## Plain Language Translations

Use these when explaining findings to non-technical users:

| Technical Finding | Plain Language |
|-------------------|----------------|
| Hardcoded API key | "The developer left a password visible in the code - like writing your PIN on your debit card" |
| Command injection | "An attacker could trick this tool into running harmful commands on your computer" |
| Data exfiltration | "This tool sends your information to an external server you didn't authorize" |
| Missing auth | "Anyone who finds this tool could use it - there's no lock on the door" |
| Overly permissive | "This tool asks to access everything when it only needs access to one folder - like giving a plumber keys to your whole house" |
| Token passthrough | "This tool forwards your credentials without checking them - like a guard who lets anyone through with a badge, real or fake" |
| No audit logging | "There's no record of what this tool does - like a store with no security cameras" |
