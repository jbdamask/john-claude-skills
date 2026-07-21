# Authoritative MCP Sources

When scanning an MCP, check these authoritative sources for current security advisories, best practices, and ecosystem updates. These are maintained by the official governing bodies and standards organizations.

## Primary Sources (Always Check)

### 1. Model Context Protocol Official Site
**URL**: `https://modelcontextprotocol.io`

- **Specification**: `/specification/` - Current protocol spec with security requirements
- **Security Best Practices**: `/specification/draft/basic/security_best_practices` - Official security guidance
- **Blog**: `blog.modelcontextprotocol.io` - Announcements and updates

**What to look for**: Latest spec version, security updates, breaking changes

### 2. Agentic AI Foundation (AAIF) / Linux Foundation
**URL**: `https://www.linuxfoundation.org/projects/agentic-ai-foundation`

MCP is governed by the AAIF under the Linux Foundation (as of December 2025). This is the authoritative source for:
- Governance decisions
- Security advisories
- Certified/vetted implementations

**What to look for**: Official security bulletins, governance announcements

### 3. OWASP MCP Top 10
**URL**: `https://owasp.org/www-project-mcp-top-10/`

The OWASP MCP Top 10 is a living document that tracks the most critical MCP security risks. The categories are stable, but specific guidance evolves.

**What to look for**: Updated vulnerability descriptions, new attack vectors, mitigation guidance

## Secondary Sources (Check When Relevant)

### Official SDK Repositories
- **TypeScript SDK**: `https://github.com/modelcontextprotocol/typescript-sdk`
- **Python SDK**: `https://github.com/modelcontextprotocol/python-sdk`

Check these for:
- Security-related commits
- Dependency updates
- Known issues

### MCP Server Registry (When Available)
The ecosystem is developing registries of vetted MCP servers. Check if the MCP under review is listed in any official registry.

## How to Use These Sources

When scanning an MCP:

1. **Check the spec version** - Is the MCP built against a current spec version?
2. **Look for security advisories** - Has the AAIF or MCP blog posted any relevant warnings?
3. **Verify OWASP alignment** - Does the MCP address the current Top 10 categories?
4. **Check for CVEs** - Search the MCP name in security databases if concerned

## What NOT to Trust

- Random blog posts without official backing
- Social media claims about MCP security
- Outdated documentation (check dates)
- Self-proclaimed "security audits" without verifiable credentials

## Keeping Current

The AI ecosystem moves fast. When in doubt:
1. Fetch the latest from the official spec site
2. Check the AAIF/Linux Foundation for announcements
3. Review the MCP's own changelog for recent security updates
