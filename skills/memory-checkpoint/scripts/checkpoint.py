#!/usr/bin/env python3
"""Create a checkpoint with semantic embedding for later retrieval."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
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
    # Default to current directory's .claude/checkpoints
    cwd = Path.cwd()
    checkpoint_dir = cwd / ".claude" / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    (checkpoint_dir / "checkpoints").mkdir(exist_ok=True)
    return checkpoint_dir

def load_index(checkpoint_dir: Path) -> dict:
    """Load or create the checkpoint index."""
    index_path = checkpoint_dir / "index.json"
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return {"checkpoints": []}

def save_index(checkpoint_dir: Path, index: dict) -> None:
    """Save the checkpoint index."""
    index_path = checkpoint_dir / "index.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)

def generate_embedding(text: str) -> list[float]:
    """Generate embedding using FastEmbed."""
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()
    except ImportError:
        print("Warning: fastembed not installed. Run: pip install fastembed", file=sys.stderr)
        return []

def create_checkpoint(content: str, auto: bool = False) -> dict:
    """Create a checkpoint file and add to index."""
    checkpoint_dir = get_project_checkpoint_dir()

    # Generate timestamp
    timestamp = datetime.now()
    filename = timestamp.strftime("%Y-%m-%dT%H-%M-%S") + ".md"
    filepath = checkpoint_dir / "checkpoints" / filename

    # Write checkpoint content
    with open(filepath, "w") as f:
        f.write(content)

    # Extract summary for index (first non-empty line after # Checkpoint)
    lines = content.split("\n")
    summary = ""
    status = "UNKNOWN"
    for line in lines:
        if line.startswith("## Status:"):
            status = line.replace("## Status:", "").strip()
        elif line.startswith("## Current Task"):
            # Next non-empty line is the task
            idx = lines.index(line)
            for next_line in lines[idx+1:]:
                if next_line.strip():
                    summary = next_line.strip()
                    break
            break

    # Generate embedding from content
    embedding = generate_embedding(content)

    # Update index
    index = load_index(checkpoint_dir)
    entry = {
        "timestamp": timestamp.isoformat(),
        "filename": filename,
        "status": status,
        "summary": summary[:200],
        "auto": auto,
        "embedding": embedding
    }
    index["checkpoints"].append(entry)
    save_index(checkpoint_dir, index)

    return {
        "filepath": str(filepath),
        "timestamp": timestamp.isoformat(),
        "status": status,
        "summary": summary,
        "has_embedding": bool(embedding)
    }

def main():
    parser = argparse.ArgumentParser(description="Create a session checkpoint")
    parser.add_argument("--auto", action="store_true", help="Mark as auto-generated (e.g., from hook)")
    parser.add_argument("--content", type=str, help="Checkpoint content (reads from stdin if not provided)")
    args = parser.parse_args()

    if args.content:
        content = args.content
    else:
        # Read from stdin
        content = sys.stdin.read()

    if not content.strip():
        print("Error: No checkpoint content provided", file=sys.stderr)
        sys.exit(1)

    result = create_checkpoint(content, auto=args.auto)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
