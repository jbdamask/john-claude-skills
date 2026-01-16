# License Guide for MCP Assessment

## Quick Reference

| License | Commercial Use | Modification | Distribution | Patent Grant | Copyleft |
|---------|---------------|--------------|--------------|--------------|----------|
| MIT | Yes | Yes | Yes | No | No |
| Apache 2.0 | Yes | Yes | Yes | Yes | No |
| BSD 2/3-Clause | Yes | Yes | Yes | No | No |
| ISC | Yes | Yes | Yes | No | No |
| GPL v3 | Yes* | Yes | Yes* | Yes | Strong |
| LGPL v3 | Yes | Yes | Yes* | Yes | Weak |
| AGPL v3 | Yes* | Yes | Yes* | Yes | Network |
| MPL 2.0 | Yes | Yes | Yes | Yes | File-level |
| Unlicense | Yes | Yes | Yes | No | No |
| CC0 | Yes | Yes | Yes | No | No |

*With conditions

## License Categories

### Permissive (Low Risk)
**MIT, Apache 2.0, BSD, ISC**
- Can use for any purpose including commercial
- Must include license notice
- No requirement to share modifications
- **Plain language**: "Use it however you want, just give credit"

### Copyleft (Medium Risk)
**GPL, LGPL, AGPL**
- Must share source code if you distribute
- Modifications must use same license
- **Plain language**: "If you share it, you must share your changes too"

### Network Copyleft (Higher Risk)
**AGPL**
- Even network use (SaaS) triggers sharing requirement
- **Plain language**: "Even if users access it over the internet, you must share code"

## Common Concerns by Use Case

### Using MCP for Internal Company Use
- **MIT/Apache/BSD**: Safe, just keep the license file
- **GPL/LGPL**: Safe for internal use, no distribution
- **AGPL**: Caution - may require source sharing even for internal SaaS

### Using MCP in a Commercial Product
- **MIT/Apache/BSD**: Safe, include attribution
- **GPL**: Risky - may require open-sourcing your product
- **LGPL**: Usually safe if MCP is a separate component
- **AGPL**: High risk for any networked application

### Modifying the MCP
- **MIT/Apache/BSD**: Can keep modifications private
- **GPL/LGPL/AGPL**: Must share modifications under same license

## Red Flags

### No License File
- **Risk**: Legally, you have NO permission to use the code
- **Plain language**: "Without a license, the author owns all rights and hasn't given permission to use it"
- **Recommendation**: Contact author or avoid

### "All Rights Reserved" or Custom Licenses
- **Risk**: May have unexpected restrictions
- **Plain language**: "The author has special rules that may limit how you can use this"
- **Recommendation**: Review carefully or consult legal

### Multiple/Conflicting Licenses
- **Risk**: Unclear which terms apply
- **Plain language**: "It's like having two contracts that say different things"
- **Recommendation**: Use the most restrictive interpretation

### License in README Only
- **Risk**: May not be legally binding
- **Plain language**: "Mentioning a license isn't the same as properly including one"
- **Recommendation**: Request proper LICENSE file

## Plain Language Explanations

Use these when explaining to users:

| Situation | Plain Language |
|-----------|----------------|
| MIT License | "Free to use for anything. Just keep the copyright notice." |
| Apache 2.0 | "Free to use. Includes patent protection. Keep the notice." |
| GPL | "Free to use, but if you share it, you must also share your code." |
| AGPL | "Like GPL, but even using it on a website counts as sharing." |
| No License | "The author hasn't given permission to use this. Legally risky." |
| Custom License | "Has special rules. Worth reading carefully or asking a lawyer." |

## What to Report

### Low Concern
- MIT, Apache 2.0, BSD, ISC, Unlicense, CC0
- "This MCP uses a permissive license. You can use it freely for personal or commercial purposes. Just keep the license notice."

### Medium Concern
- LGPL, MPL
- "This MCP has some sharing requirements if you modify and distribute it. Fine for most internal use."

### High Concern
- GPL, AGPL
- "This MCP requires you to share your source code if you distribute it or (for AGPL) provide it as a network service."

### Red Flag
- No license, unclear license, custom restrictive license
- "This MCP doesn't have clear licensing. Using it could expose you to legal risk."
