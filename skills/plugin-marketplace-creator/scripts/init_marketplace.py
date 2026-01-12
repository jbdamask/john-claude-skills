#!/usr/bin/env python3
"""
Initialize a new Claude Code plugin marketplace.

Usage:
    python init_marketplace.py <marketplace-name> --path <output-directory>

Example:
    python init_marketplace.py my-team-plugins --path ./my-marketplace
"""

import argparse
import json
import os
import sys
import re

RESERVED_NAMES = {
    "claude-code-marketplace", "claude-code-plugins", "claude-plugins-official",
    "anthropic-marketplace", "anthropic-plugins", "agent-skills", "life-sciences"
}

def validate_name(name: str) -> tuple[bool, str]:
    if not name:
        return False, "Name cannot be empty"
    if not re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$', name):
        return False, "Name must be kebab-case (lowercase letters, numbers, hyphens)"
    if name in RESERVED_NAMES:
        return False, f"'{name}' is a reserved name"
    if '--' in name:
        return False, "Name cannot contain consecutive hyphens"
    return True, ""

def create_marketplace(name: str, output_path: str, owner_name: str = "", owner_email: str = "") -> None:
    os.makedirs(os.path.join(output_path, ".claude-plugin"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "plugins", "example-plugin", ".claude-plugin"), exist_ok=True)
    os.makedirs(os.path.join(output_path, "plugins", "example-plugin", "commands"), exist_ok=True)
    os.makedirs(os.path.join(output_path, ".github", "workflows"), exist_ok=True)
    
    # marketplace.json
    marketplace_json = {
        "name": name,
        "owner": {
            "name": owner_name or "Your Organization",
            "email": owner_email or "team@example.com"
        },
        "metadata": {
            "description": "A curated collection of Claude Code plugins",
            "version": "1.0.0"
        },
        "plugins": [{
            "name": "example-plugin",
            "source": "./plugins/example-plugin",
            "description": "An example plugin to demonstrate the structure",
            "version": "1.0.0",
            "author": {"name": owner_name or "Your Organization"},
            "category": "example",
            "keywords": ["example", "template"]
        }]
    }
    with open(os.path.join(output_path, ".claude-plugin", "marketplace.json"), "w") as f:
        json.dump(marketplace_json, f, indent=2)
    
    # plugin.json
    plugin_json = {
        "name": "example-plugin",
        "description": "An example plugin demonstrating the plugin structure",
        "version": "1.0.0",
        "author": {"name": owner_name or "Your Organization"}
    }
    with open(os.path.join(output_path, "plugins", "example-plugin", ".claude-plugin", "plugin.json"), "w") as f:
        json.dump(plugin_json, f, indent=2)
    
    # Example command
    command_content = """# Hello World

Say hello to demonstrate the plugin is working.

## Usage
Use `/example:hello` to run this command.

## Example
```
/example:hello World
```
Output: "Hello, World! The example plugin is working correctly."
"""
    with open(os.path.join(output_path, "plugins", "example-plugin", "commands", "hello.md"), "w") as f:
        f.write(command_content)
    
    # README.md
    readme_content = f"""# {name}

A Claude Code plugin marketplace.

## Installation

```
/plugin marketplace add owner/{name}
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| example-plugin | An example plugin |

## Usage

```
/plugin install plugin-name@{name}
```
"""
    with open(os.path.join(output_path, "README.md"), "w") as f:
        f.write(readme_content)
    
    # GitHub Actions workflow
    workflow_content = """name: Validate Marketplace

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate marketplace.json
        run: |
          python -c "
          import json
          with open('.claude-plugin/marketplace.json') as f:
              data = json.load(f)
          assert 'name' in data, 'Missing name'
          assert 'owner' in data, 'Missing owner'
          assert 'plugins' in data, 'Missing plugins'
          print('✅ Marketplace validation passed')
          "
"""
    with open(os.path.join(output_path, ".github", "workflows", "validate.yml"), "w") as f:
        f.write(workflow_content)
    
    # .gitignore
    with open(os.path.join(output_path, ".gitignore"), "w") as f:
        f.write(".DS_Store\nThumbs.db\n*.swp\n.vscode/\n.idea/\n__pycache__/\n*.pyc\n")
    
    print(f"✅ Marketplace '{name}' created at {output_path}")
    print(f"\nNext steps:")
    print(f"  1. cd {output_path}")
    print(f"  2. Edit .claude-plugin/marketplace.json")
    print(f"  3. git init && git add -A && git commit -m 'Initial'")
    print(f"  4. Push to GitHub")
    print(f"  5. /plugin marketplace add owner/{name}")

def main():
    parser = argparse.ArgumentParser(description="Initialize a Claude Code plugin marketplace")
    parser.add_argument("name", help="Marketplace name (kebab-case)")
    parser.add_argument("--path", required=True, help="Output directory")
    parser.add_argument("--owner-name", default="", help="Owner name")
    parser.add_argument("--owner-email", default="", help="Owner email")
    args = parser.parse_args()
    
    valid, error = validate_name(args.name)
    if not valid:
        print(f"❌ Invalid name: {error}", file=sys.stderr)
        sys.exit(1)
    
    if os.path.exists(args.path) and os.listdir(args.path):
        print(f"❌ Directory '{args.path}' exists and is not empty", file=sys.stderr)
        sys.exit(1)
    
    create_marketplace(args.name, args.path, args.owner_name, args.owner_email)

if __name__ == "__main__":
    main()
