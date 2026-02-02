#!/usr/bin/env python3
"""Semantic search over checkpoints using cosine similarity."""

import argparse
import json
import math
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

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def generate_embedding(text: str) -> list[float]:
    """Generate embedding using FastEmbed."""
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        embeddings = list(model.embed([text]))
        return embeddings[0].tolist()
    except ImportError:
        print("Error: fastembed not installed. Run: pip install fastembed", file=sys.stderr)
        sys.exit(1)

def search_checkpoints(query: str, top_n: int = 5) -> list[dict]:
    """Search checkpoints by semantic similarity."""
    checkpoint_dir = get_project_checkpoint_dir()
    index = load_index(checkpoint_dir)

    if not index["checkpoints"]:
        return []

    # Generate query embedding
    query_embedding = generate_embedding(query)

    # Score all checkpoints
    results = []
    for checkpoint in index["checkpoints"]:
        if not checkpoint.get("embedding"):
            continue
        score = cosine_similarity(query_embedding, checkpoint["embedding"])
        results.append({
            "timestamp": checkpoint["timestamp"],
            "filename": checkpoint["filename"],
            "status": checkpoint["status"],
            "summary": checkpoint["summary"],
            "score": score
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]

def read_checkpoint_content(filename: str) -> str:
    """Read the full content of a checkpoint file."""
    checkpoint_dir = get_project_checkpoint_dir()
    filepath = checkpoint_dir / "checkpoints" / filename
    if filepath.exists():
        with open(filepath) as f:
            return f.read()
    return ""

def main():
    parser = argparse.ArgumentParser(description="Search checkpoints semantically")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-n", "--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--full", action="store_true", help="Show full checkpoint content for top result")
    args = parser.parse_args()

    if not args.query:
        # Read from stdin if no query provided
        args.query = sys.stdin.read().strip()

    if not args.query:
        print("Error: No search query provided", file=sys.stderr)
        sys.exit(1)

    results = search_checkpoints(args.query, args.top)

    if not results:
        print("No checkpoints found.")
        return

    output = {"results": results}

    if args.full and results:
        output["top_result_content"] = read_checkpoint_content(results[0]["filename"])

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
