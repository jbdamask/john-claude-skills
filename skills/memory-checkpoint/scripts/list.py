#!/usr/bin/env python3
"""List recent checkpoints with timestamps and status."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Setup and use skill venv
SKILL_DIR = Path(__file__).parent.parent
VENV_PYTHON = SKILL_DIR / ".venv" / "bin" / "python3"
SETUP_SCRIPT = SKILL_DIR / "scripts" / "setup.sh"

if not VENV_PYTHON.exists() and SETUP_SCRIPT.exists():
    print("Setting up venv (first run)...", file=sys.stderr)
    subprocess.run(["bash", str(SETUP_SCRIPT)], check=True)

if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON)] + sys.argv)

def get_project_checkpoint_dir() -> Path:
    """Get the checkpoint directory for the current project."""
    cwd = Path.cwd()
    return cwd / ".claude" / "checkpoints"

def load_index(checkpoint_dir: Path) -> dict:
    """Load the checkpoint index."""
    index_path = checkpoint_dir / "index.json"
    if not index_path.exists():
        return {"checkpoints": []}
    with open(index_path) as f:
        return json.load(f)

def list_checkpoints(limit: int = 10, status_filter: str | None = None) -> list[dict]:
    """List recent checkpoints."""
    checkpoint_dir = get_project_checkpoint_dir()
    index = load_index(checkpoint_dir)

    checkpoints = index.get("checkpoints", [])

    # Filter by status if specified
    if status_filter:
        checkpoints = [c for c in checkpoints if c.get("status") == status_filter]

    # Sort by timestamp descending (most recent first)
    checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Return limited results without embeddings
    results = []
    for c in checkpoints[:limit]:
        results.append({
            "timestamp": c.get("timestamp"),
            "filename": c.get("filename"),
            "status": c.get("status"),
            "summary": c.get("summary"),
            "auto": c.get("auto", False)
        })
    return results

def read_checkpoint_content(filename: str) -> str:
    """Read the full content of a checkpoint file."""
    checkpoint_dir = get_project_checkpoint_dir()
    filepath = checkpoint_dir / "checkpoints" / filename
    if filepath.exists():
        with open(filepath) as f:
            return f.read()
    return ""

def main():
    parser = argparse.ArgumentParser(description="List recent checkpoints")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Number of checkpoints to list (default: 10)")
    parser.add_argument("--status", type=str, help="Filter by status (IN_PROGRESS, BLOCKED, DECISION_NEEDED)")
    parser.add_argument("--latest", action="store_true", help="Show full content of most recent checkpoint")
    args = parser.parse_args()

    checkpoints = list_checkpoints(args.limit, args.status)

    if not checkpoints:
        print("No checkpoints found.")
        return

    output = {"checkpoints": checkpoints, "total": len(checkpoints)}

    if args.latest and checkpoints:
        output["latest_content"] = read_checkpoint_content(checkpoints[0]["filename"])

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
