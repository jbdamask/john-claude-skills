#!/usr/bin/env python3
"""
Validate a Claude Code plugin marketplace.

Usage:
    python validate_marketplace.py <marketplace-path>
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

def validate_kebab_case(name: str) -> bool:
    return bool(re.match(r'^[a-z][a-z0-9-]*[a-z0-9]$|^[a-z]$', name)) and '--' not in name

def validate_marketplace(path: str) -> tuple[bool, list[str]]:
    errors = []
    
    marketplace_json_path = os.path.join(path, ".claude-plugin", "marketplace.json")
    if not os.path.exists(marketplace_json_path):
        return False, ["Missing .claude-plugin/marketplace.json"]
    
    try:
        with open(marketplace_json_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    # Required fields
    if "name" not in data:
        errors.append("Missing required field: 'name'")
    elif not validate_kebab_case(data["name"]):
        errors.append(f"'name' must be kebab-case: '{data['name']}'")
    elif data["name"] in RESERVED_NAMES:
        errors.append(f"'{data['name']}' is a reserved name")
    
    if "owner" not in data:
        errors.append("Missing required field: 'owner'")
    elif not isinstance(data["owner"], dict) or "name" not in data["owner"]:
        errors.append("'owner' must have 'name' field")
    
    if "plugins" not in data:
        errors.append("Missing required field: 'plugins'")
    elif not isinstance(data["plugins"], list):
        errors.append("'plugins' must be an array")
    else:
        seen = set()
        for i, plugin in enumerate(data["plugins"]):
            if "name" not in plugin:
                errors.append(f"plugins[{i}]: missing 'name'")
            elif not validate_kebab_case(plugin["name"]):
                errors.append(f"plugins[{i}]: name must be kebab-case")
            elif plugin["name"] in seen:
                errors.append(f"Duplicate plugin name: '{plugin['name']}'")
            else:
                seen.add(plugin["name"])
            
            if "source" not in plugin:
                errors.append(f"plugins[{i}]: missing 'source'")
            elif isinstance(plugin["source"], str) and plugin["source"].startswith("./"):
                full_path = os.path.join(path, plugin["source"])
                if not os.path.exists(full_path):
                    errors.append(f"plugins[{i}]: source path not found: {plugin['source']}")
                else:
                    # Validate plugin.json doesn't have invalid fields
                    plugin_json_path = os.path.join(full_path, ".claude-plugin", "plugin.json")
                    if os.path.exists(plugin_json_path):
                        with open(plugin_json_path) as pf:
                            pdata = json.load(pf)
                        invalid_fields = {"skills"} & set(pdata.keys())
                        if invalid_fields:
                            errors.append(f"plugins[{i}]: plugin.json has invalid fields: {invalid_fields}")
    
    return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(description="Validate a Claude Code plugin marketplace")
    parser.add_argument("path", help="Path to marketplace directory")
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"❌ Not a directory: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    valid, errors = validate_marketplace(args.path)
    
    for error in errors:
        print(f"❌ {error}")
    
    if valid:
        print("✅ Marketplace validation passed")
        sys.exit(0)
    else:
        print("\n❌ Validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
