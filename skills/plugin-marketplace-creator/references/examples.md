# Marketplace Examples

## Team Internal Marketplace

```json
{
  "name": "acme-tools",
  "owner": {"name": "ACME Engineering", "email": "eng@acme.com"},
  "metadata": {"description": "Internal dev tools", "version": "1.0.0"},
  "plugins": [
    {
      "name": "acme-deploy",
      "source": "./plugins/deploy",
      "description": "Deploy to ACME infrastructure",
      "category": "devops"
    },
    {
      "name": "code-standards",
      "source": {"source": "github", "repo": "acme/standards"},
      "description": "Enforce coding standards",
      "category": "quality"
    }
  ]
}
```

## Open Source Marketplace

```json
{
  "name": "awesome-plugins",
  "owner": {"name": "Community", "email": "maintainers@example.com"},
  "plugins": [
    {
      "name": "git-workflow",
      "source": {"source": "github", "repo": "user/git-workflow"},
      "description": "Enhanced git commands",
      "keywords": ["git", "workflow"]
    },
    {
      "name": "test-generator",
      "source": {"source": "url", "url": "https://gitlab.com/org/test-gen.git"},
      "description": "Auto-generate tests"
    }
  ]
}
```

## Minimal Marketplace

```json
{
  "name": "my-plugins",
  "owner": {"name": "Developer"},
  "plugins": [
    {"name": "helper", "source": "./plugins/helper", "description": "Helper tool"}
  ]
}
```

## Team Settings (`.claude/settings.json`)

```json
{
  "extraKnownMarketplaces": {
    "team-tools": {
      "source": {"source": "github", "repo": "org/plugins"}
    }
  },
  "enabledPlugins": {
    "deploy@team-tools": true,
    "formatter@team-tools": true
  }
}
```
