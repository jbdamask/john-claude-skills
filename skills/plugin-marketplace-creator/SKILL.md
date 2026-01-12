---
name: plugin-marketplace-creator
description: Create and configure Claude Code plugin marketplaces hosted on GitHub. Use this skill when users want to set up a new plugin marketplace repository, add plugins to an existing marketplace, configure team distribution settings, or troubleshoot marketplace issues. Triggers include "create a plugin marketplace", "set up a marketplace on GitHub", "add plugins to my marketplace", "configure marketplace for my team", or "distribute Claude Code plugins".
---

# Plugin Marketplace Creator

Create Claude Code plugin marketplaces—catalogs that distribute plugins to teams and communities via GitHub.

## Quick Start

1. Run `scripts/init_marketplace.py <name> --path <output-dir>` to scaffold
2. Edit `.claude-plugin/marketplace.json` to add plugins
3. Push to GitHub
4. Users install via `/plugin marketplace add owner/repo`

## Marketplace Structure

```
marketplace-repo/
├── .claude-plugin/
│   └── marketplace.json    # Required: marketplace definition
├── plugins/                 # Optional: local plugins
│   └── my-plugin/
│       └── .claude-plugin/
│           └── plugin.json
└── README.md
```

## Marketplace JSON Schema

### Required Fields

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Team Name",
    "email": "team@example.com"
  },
  "plugins": []
}
```

### Optional Metadata

```json
{
  "metadata": {
    "description": "Brief description",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  }
}
```

### Reserved Names (cannot use)

`claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `life-sciences`

## Plugin Entry Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Kebab-case identifier |
| `source` | string\|object | Yes | Where to fetch plugin |
| `description` | string | No | Brief description |
| `version` | string | No | Semantic version |
| `author` | object | No | `{name, email}` |
| `category` | string | No | For organization |
| `keywords` | array | No | Search tags |
| `strict` | boolean | No | Require plugin.json (default: true) |

### Source Types

**Local path:**
```json
{"source": "./plugins/my-plugin"}
```

**GitHub:**
```json
{"source": {"source": "github", "repo": "owner/repo"}}
```

**Git URL:**
```json
{"source": {"source": "url", "url": "https://gitlab.com/team/plugin.git"}}
```

## Complete Example

```json
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@company.com"
  },
  "metadata": {
    "description": "Internal development tools",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "code-formatter",
      "source": "./plugins/formatter",
      "description": "Auto-format code on save",
      "version": "1.0.0",
      "category": "development"
    },
    {
      "name": "deploy-tools",
      "source": {"source": "github", "repo": "company/deploy-plugin"},
      "description": "Deployment automation",
      "category": "devops"
    }
  ]
}
```

## Team Configuration

Add to project's `.claude/settings.json` for automatic installation:

```json
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {"source": "github", "repo": "org/claude-plugins"}
    }
  },
  "enabledPlugins": {
    "code-formatter@team-tools": true
  }
}
```

## Scripts

- **init_marketplace.py** - Create new marketplace with proper structure
- **validate_marketplace.py** - Validate marketplace.json and plugin sources
- **add_plugin.py** - Add plugin entries to existing marketplace

## Workflow

### Creating a New Marketplace

```bash
# 1. Initialize
python scripts/init_marketplace.py my-marketplace --path ./output

# 2. Validate
python scripts/validate_marketplace.py ./output

# 3. Push to GitHub
cd output && git init && git add -A && git commit -m "Initial"
# Create repo on GitHub and push

# 4. Test in Claude Code
# /plugin marketplace add owner/my-marketplace
```

### Adding Plugins

```bash
# Add local plugin
python scripts/add_plugin.py ./marketplace --name my-plugin --source ./plugins/my-plugin

# Add GitHub plugin  
python scripts/add_plugin.py ./marketplace --name external --source github:org/repo
```

## Troubleshooting

**Marketplace not loading**: Verify `.claude-plugin/marketplace.json` exists at repo root.

**Plugin install fails**: Check source is accessible. For private repos, ensure authentication.

**Team can't see marketplace**: Verify `extraKnownMarketplaces` in `.claude/settings.json`.

## References

- `references/plugin-schema.md` - Complete plugin.json schema
- `references/examples.md` - Additional marketplace examples
