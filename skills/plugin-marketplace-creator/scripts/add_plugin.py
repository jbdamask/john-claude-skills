#!/usr/bin/env python3
"""
Add a plugin to a Claude Code marketplace.

Usage:
    python add_plugin.py <marketplace-path> --name <plugin-name> --source <source>

Examples:
    python add_plugin.py ./marketplace --name my-plugin --source ./plugins/my-plugin
    python add_plugin.py ./marketplace --name deploy --source github:company/deploy
"""

import argparse
import json
import os
import sys
import re

def validate_kebab_case(name: str) -> bool:
    return bool(re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$', name)) and '--' not in name

def parse_source(source_str: str):
    if source_str.startswith("github:"):
        return {"source": "github", "repo": source_str[7:]}
    elif source_str.startswith("git:") or source_str.startswith("https://"):
        url = source_str[4:] if source_str.startswith("git:") else source_str
        return {"source": "url", "url": url}
    return source_str

def add_plugin(marketplace_path: str, name: str, source: str, 
               description: str = None, version: str = None, category: str = None):
    
    json_path = os.path.join(marketplace_path, ".claude-plugin", "marketplace.json")
    if not os.path.exists(json_path):
        print(f"❌ Marketplace not found at {marketplace_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(json_path) as f:
        data = json.load(f)
    
    existing = [p.get("name") for p in data.get("plugins", [])]
    if name in existing:
        print(f"❌ Plugin '{name}' already exists", file=sys.stderr)
        sys.exit(1)
    
    plugin = {"name": name, "source": parse_source(source)}
    if description:
        plugin["description"] = description
    if version:
        plugin["version"] = version
    if category:
        plugin["category"] = category
    
    data.setdefault("plugins", []).append(plugin)
    
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added plugin '{name}'")
    print(json.dumps(plugin, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Add a plugin to a marketplace")
    parser.add_argument("marketplace_path", help="Path to marketplace")
    parser.add_argument("--name", required=True, help="Plugin name (kebab-case)")
    parser.add_argument("--source", required=True, help="Source: ./path, github:owner/repo, or URL")
    parser.add_argument("--description", help="Plugin description")
    parser.add_argument("--version", help="Plugin version")
    parser.add_argument("--category", help="Plugin category")
    args = parser.parse_args()
    
    if not validate_kebab_case(args.name):
        print(f"❌ Name must be kebab-case", file=sys.stderr)
        sys.exit(1)
    
    add_plugin(args.marketplace_path, args.name, args.source, 
               args.description, args.version, args.category)

if __name__ == "__main__":
    main()
