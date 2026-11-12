"""Shared settings for the hive tools and hooks: the repo root, hive/project.json, and where runtime files go.

Runtime files (logs, scratch folders) live outside the repo, under ~/.hive/<slug>/ (HIVE_HOME overrides ~/.hive).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "hive" / "project.json"


def config(root: Path = ROOT) -> dict:
    try:
        return json.loads((root / "hive" / "project.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def slug(cfg: dict | None = None) -> str:
    cfg = config() if cfg is None else cfg
    return cfg.get("slug") or re.sub(r"[^a-z0-9]+", "-", ROOT.name.lower()).strip("-")


def hive_home(cfg: dict | None = None) -> Path:
    base = Path(os.environ.get("HIVE_HOME") or Path.home() / ".hive")
    return base / slug(cfg)


def scratch_root(cfg: dict | None = None) -> Path:
    return hive_home(cfg) / "scratch"


def claude_projects_glob(root: Path = ROOT) -> str:
    """Where Claude Code stores this repo's transcripts (worktrees included)."""
    mangled = re.sub(r"[^A-Za-z0-9]", "-", str(root))
    return str(Path.home() / ".claude" / "projects" / (mangled + "*"))
