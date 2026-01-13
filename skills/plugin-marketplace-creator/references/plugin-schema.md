# Plugin JSON Schema Reference

## Minimal Plugin

```json
{
  "name": "my-plugin",
  "description": "Brief description"
}
```

## Complete Schema

```json
{
  "name": "my-plugin",
  "description": "Description",
  "version": "1.0.0",
  "author": {"name": "Name", "email": "email@example.com"},
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/org/repo",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "commands": ["./commands/"],
  "agents": ["./agents/"],
  "hooks": "./hooks.json",
  "mcpServers": "./mcp.json"
}
```

## Component Fields

### Commands
Markdown files defining slash commands:
```
commands/
├── format.md      -> /plugin:format
└── deploy.md      -> /plugin:deploy
```

### Agents
Specialized sub-agents in markdown:
```
agents/
└── reviewer.md
```

### Hooks
Event handlers (PreToolUse, PostToolUse, Notification, Stop):
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh"}]
    }]
  }
}
```

### MCP Servers
```json
{
  "mcpServers": {
    "my-server": {
      "command": "${CLAUDE_PLUGIN_ROOT}/server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"]
    }
  }
}
```

## Environment Variables

- `${CLAUDE_PLUGIN_ROOT}` - Absolute path to plugin installation

## Invalid Fields

These fields are NOT valid in plugin.json:
- `skills` - Skills are auto-discovered from the `skills/` directory
