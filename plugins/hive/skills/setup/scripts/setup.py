#!/usr/bin/env python3
"""Install, or update, the hive agent team in a git repository.

  setup.py [--repo PATH] [--answers FILE.json] [--name ...] [--user ...] [--fast-tests ...] [--spend ...]
           [--lead ...] [--no-github] [--no-commit] [--skip-plugin-check]

The team needs Beads (bd): every task is a bead, and the agents, the spawn gate and the planner all read it.
It also needs the gh command and the beads-planner plugin, 0.2.0 or later. Without bd the setup stops before
changing anything.

Two layers. The general layer (template/general: rule files, role briefs, tools, hooks, tests) is the same in
every repo; each run writes it fresh and reports what changed. The project layer (template/project: vision,
project rules, product test, principles, checklist, glossary, settings) is written once from the answers and
never overwritten. A second run needs no answers: it reads hive/project.json.

Answers (flags, or keys in the answers file): name, user (who the product is for and what it is for), fast_tests
(the project's fast test command), spend (money caps), lead (the lead's bd actor name), labels (true/false:
create the GitHub labels now; --no-github means false).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
GENERAL = HERE / "template" / "general"
PROJECT = HERE / "template" / "project"
HOOKS = HERE / "template" / "settings-hooks.json"
VERSION = "0.1.0"
MANIFEST = "hive/general-files.json"
RENDERED = {".md", ".json"}
SLOT = re.compile(r"\{\{(\w+)\}\}")
LABELS = [
    ("drafting", "fbca04", "A spec is being written"),
    ("pending_approval", "0e8a16", "The brief is ready for the owner to read"),
    ("approved_spec", "1d76db", "The owner approved the spec: build it"),
    ("proposal", "c5def5", "An idea from the team; remove the label to make it a request"),
    ("in_progress", "5319e7", "Being built or fixed"),
    ("bug", "d73a4a", "Something is broken"),
]
BEADS_REQUIRED = """\
This team requires Beads, the bd task tracker (https://github.com/steveyegge/beads).
Every task is a bead, and the agents, the spawn gate and the planner all read it.
It also needs the gh command (https://cli.github.com) and the beads-planner plugin, 0.2.0 or later."""
NO_BD = """\
STOP: bd (Beads) is not installed, so nothing was changed.
Beads is required: every task the team does is a bead, and the agents, the spawn gate and the planner all read it.
Install it, then run the setup again:
  brew install beads          (or: npm install -g @beads/bd)
Project page: https://github.com/steveyegge/beads"""
CLAUDE_START = "<!-- hive:start (managed by /hive:setup; edit outside these markers) -->"
CLAUDE_END = "<!-- hive:end -->"
CLAUDE_BLOCK = """## The team
This repo is run by an agent team: one lead, started with `HIVE_ROLE=lead claude`, and one-shot agents that each do one bead. It requires Beads (`bd`). Start at hive/README.md; this project's own rules are in hive/PROJECT.md."""


def sh(args: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"{' '.join(args)} failed: {(r.stderr or r.stdout).strip()}")
    return r


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"


# ---- prerequisites ----

def planner_version() -> str | None:
    path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    try:
        plugins = json.loads(path.read_text(encoding="utf-8")).get("plugins", {})
    except (OSError, ValueError):
        return None
    versions = [e.get("version", "") for k, v in plugins.items() if k.split("@")[0] == "beads-planner"
                for e in (v if isinstance(v, list) else [v])]
    return max(versions, key=lambda s: tuple(int(x) for x in re.findall(r"\d+", s)), default=None)


def at_least(version: str | None, want: str) -> bool:
    if not version:
        return False
    return tuple(int(x) for x in re.findall(r"\d+", version)[:3]) >= tuple(int(x) for x in want.split("."))


def prerequisites(repo: Path, a) -> Path:
    if shutil.which("bd") is None:
        print(NO_BD)
        raise SystemExit(3)
    r = sh(["git", "rev-parse", "--show-toplevel"], repo)
    if r.returncode != 0:
        print(f"STOP: {repo} is not inside a git repository, so nothing was changed. Run `git init` first.")
        raise SystemExit(3)
    if shutil.which("gh") is None and not a.no_github:
        print("STOP: the gh command is not installed, so nothing was changed. The team works on GitHub issues: "
              "install it from https://cli.github.com, or run with --no-github to skip the labels for now.")
        raise SystemExit(3)
    if not a.skip_plugin_check and not at_least(planner_version(), "0.2.0"):
        print(f"STOP: the beads-planner plugin 0.2.0 or later is not installed (found: {planner_version()}), so "
              "nothing was changed. The lead uses it to turn an approved spec into beads. Install it with: "
              "claude plugin install beads-planner@john-claude-skills")
        raise SystemExit(3)
    return Path(r.stdout.strip())


# ---- answers ----

def answers(root: Path, a) -> tuple[dict, bool]:
    """(the project's settings, whether they already existed)."""
    cfg_path = root / "hive" / "project.json"
    if cfg_path.is_file():
        return json.loads(cfg_path.read_text(encoding="utf-8")), True
    given = json.loads(Path(a.answers).read_text(encoding="utf-8")) if a.answers else {}
    for key in ("name", "user", "fast_tests", "spend", "lead"):
        if getattr(a, key, None):
            given[key] = getattr(a, key)
    missing = [k for k in ("name", "user", "fast_tests") if not given.get(k)]
    if missing:
        print("STOP: these answers are needed for a first install, so nothing was changed: " + ", ".join(missing))
        raise SystemExit(2)
    owner = sh(["git", "config", "user.name"], root).stdout.strip() or "the owner"
    branch = sh(["git", "symbolic-ref", "--short", "HEAD"], root).stdout.strip() or "main"
    cfg = {
        "name": given["name"],
        "slug": slugify(given["name"]),
        "owner": given.get("owner") or owner.split()[0],
        "lead": given.get("lead") or "lead",
        "user": given["user"].strip(),
        "fast_tests": given["fast_tests"],
        "spend": given.get("spend") or "No pay-per-use API spend without the owner's yes; the cap is $0",
        "main_branch": branch,
        "remote": "origin",
        "flow_since": dt.date.today().isoformat(),
        "shared_tree_may_edit": ["hive/", "docs/", ".beads/", "*.md"],
        "labels": bool(given.get("labels", True)) and not a.no_github,
    }
    return cfg, False


def render(text: str, values: dict, as_json: bool) -> str:
    def fill(m):
        key = m.group(1)
        if key not in values:
            raise SystemExit(f"template slot {{{{{key}}}}} has no value")
        v = str(values[key])
        return json.dumps(v)[1:-1] if as_json else v
    return SLOT.sub(fill, text)


def values(cfg: dict) -> dict:
    v = {k: cfg.get(k, "") for k in ("name", "slug", "owner", "lead", "user", "fast_tests", "spend")}
    v["version"] = VERSION
    return v


def template_files(base: Path) -> list[Path]:
    return sorted(p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts)


def content(src: Path, vals: dict) -> str:
    text = src.read_text(encoding="utf-8")
    if src.suffix in RENDERED or src.name == "VERSION":
        text = render(text, vals, src.suffix == ".json")
    return text


# ---- the layers ----

def write_project(root: Path, cfg: dict, report: dict) -> None:
    vals = values(cfg)
    cfg_path = root / "hive" / "project.json"
    if not cfg_path.is_file():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
        report["project_created"].append("hive/project.json")
    else:
        report["project_kept"].append("hive/project.json")
    for src in template_files(PROJECT):
        rel = src.relative_to(PROJECT).as_posix()
        dest = root / rel
        if dest.exists():
            report["project_kept"].append(rel)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content(src, vals), encoding="utf-8")
        report["project_created"].append(rel)


def write_general(root: Path, cfg: dict, report: dict) -> None:
    vals = values(cfg)
    man_path = root / MANIFEST
    old = json.loads(man_path.read_text(encoding="utf-8")) if man_path.is_file() else {"version": None, "files": {}}
    report["from_version"] = old.get("version")
    new_files = {}
    for src in template_files(GENERAL):
        rel = src.relative_to(GENERAL).as_posix()
        dest = root / rel
        text = content(src, vals)
        new_files[rel] = sha(text)
        if dest.is_file():
            current = dest.read_text(encoding="utf-8")
            if current == text:
                report["unchanged"].append(rel)
                continue
            edited = rel in old["files"] and sha(current) != old["files"][rel]
            report["local_edits_replaced" if edited else "updated"].append(rel)
        else:
            report["added"].append(rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        if src.stat().st_mode & 0o111 or rel.startswith(("hive/tools/", "hive/hooks/")) and rel.endswith(".py"):
            dest.chmod(0o755)
    report["dropped"] = sorted(set(old["files"]) - set(new_files))
    man_path.write_text(json.dumps({"version": VERSION, "files": new_files}, indent=1, sort_keys=True) + "\n",
                        encoding="utf-8")


def ours(cmd: str) -> bool:
    return "/hive/hooks/" in cmd or "/hive/tools/" in cmd or "bd prime" in cmd


def write_settings(root: Path, report: dict) -> None:
    path = root / ".claude" / "settings.json"
    settings = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    before = json.dumps(settings, indent=2)
    hooks = settings.setdefault("hooks", {})
    for event, groups in list(hooks.items()):
        kept = []
        for g in groups:
            g = {**g, "hooks": [h for h in g.get("hooks", []) if not ours(h.get("command", ""))]}
            if g["hooks"]:
                kept.append(g)
        hooks[event] = kept
    for event, groups in json.loads(HOOKS.read_text(encoding="utf-8")).items():
        hooks.setdefault(event, []).extend(groups)
    for event in [e for e, g in hooks.items() if not g]:
        del hooks[event]
    after = json.dumps(settings, indent=2)
    if after != before:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(after + "\n", encoding="utf-8")
        report["updated" if before != "{}" else "added"].append(".claude/settings.json")
    else:
        report["unchanged"].append(".claude/settings.json")


def write_claude_md(root: Path, report: dict) -> None:
    path = root / "CLAUDE.md"
    block = f"{CLAUDE_START}\n{CLAUDE_BLOCK}\n{CLAUDE_END}"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if CLAUDE_START in text and CLAUDE_END in text:
        new = text[:text.index(CLAUDE_START)] + block + text[text.index(CLAUDE_END) + len(CLAUDE_END):]
    else:
        new = (text.rstrip("\n") + "\n\n" if text.strip() else "") + block + "\n"
    if new != text:
        path.write_text(new, encoding="utf-8")
        report["updated" if text else "added"].append("CLAUDE.md (the hive block only)")


# ---- main ----

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--answers")
    ap.add_argument("--name")
    ap.add_argument("--user")
    ap.add_argument("--fast-tests", dest="fast_tests")
    ap.add_argument("--spend")
    ap.add_argument("--lead")
    ap.add_argument("--no-github", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    ap.add_argument("--skip-plugin-check", action="store_true")
    a = ap.parse_args(argv)

    print(f"hive setup {VERSION}: installs the agent team (lead, one-shot agents, roles, hooks, tests) under hive/.")
    print(BEADS_REQUIRED + "\n")
    root = prerequisites(Path(a.repo).resolve(), a)
    cfg, existed = answers(root, a)
    report = {k: [] for k in ("added", "updated", "local_edits_replaced", "unchanged", "project_created",
                              "project_kept")}

    if not (root / ".beads").is_dir() or not any(p.name != "PLANNING.md" for p in (root / ".beads").iterdir()):
        r = sh(["bd", "init", "--non-interactive", "--init-if-missing", "--skip-agents", "--skip-hooks", "-q",
                "--prefix", cfg["slug"]], root)
        if r.returncode != 0:
            print("STOP: bd init failed: " + (r.stderr or r.stdout).strip())
            return 3
        print("bd init: a new Beads tracker in .beads/")

    write_project(root, cfg, report)
    write_general(root, cfg, report)
    write_settings(root, report)
    write_claude_md(root, report)
    for tool in ("roles.py", "brief.py"):
        r = sh([sys.executable, f"hive/tools/{tool}", "build"], root)
        if r.returncode != 0:
            print(f"STOP: hive/tools/{tool} build failed:\n{r.stdout}{r.stderr}")
            return 1

    if report["from_version"] == VERSION:
        print(f"The general layer {VERSION} is already installed; bringing every team file back to it.")
    elif report["from_version"]:
        print(f"Updating the general layer from {report['from_version']} to {VERSION}.")
    else:
        print(f"Installing the general layer {VERSION}.")
    for key, label in (("added", "added"), ("updated", "updated"),
                       ("local_edits_replaced", "updated; local edits replaced (see git diff)"),
                       ("project_created", "project file created"), ("project_kept", "project file kept as is")):
        for rel in report[key]:
            print(f"  {label}: {rel}")
    print(f"  unchanged: {len(report['unchanged'])} general files")
    for rel in report.get("dropped", []):
        print(f"  no longer part of the general layer (left in place; delete it if unused): {rel}")

    t = subprocess.run([sys.executable, "-m", "unittest", "discover", "-q", "-s", "hive/tests"], cwd=root,
                       capture_output=True, text=True)
    tail = (t.stdout + t.stderr).strip().splitlines()[-3:]
    print("hive/tests: " + " | ".join(tail))
    if t.returncode != 0:
        print("STOP: the team's tests fail; nothing was committed. Full output: "
              "python3 -m unittest discover -s hive/tests")
        print(t.stdout + t.stderr)
        return 1

    if cfg.get("labels") and not a.no_github:
        for name, color, desc in LABELS:
            r = sh(["gh", "label", "create", name, "--color", color, "--description", desc, "--force"], root)
            print(f"  label {name}: " + ("ok" if r.returncode == 0 else "failed: " + r.stderr.strip()[:120]))
    else:
        print("GitHub labels: skipped. Create them later with the setup, or by hand: "
              + ", ".join(n for n, _, _ in LABELS))

    if not a.no_commit:
        paths = ["hive", ".beads", ".claude/settings.json", ".claude/agents", "CLAUDE.md"]
        sh(["git", "add", "--", *[p for p in paths if (root / p).exists()]], root, check=True)
        if sh(["git", "diff", "--cached", "--quiet"], root).returncode != 0:
            old = report["from_version"]
            msg = (f"Update the hive team layer {old} -> {VERSION}" if old and old != VERSION
                   else f"Update the hive team layer {VERSION}" if old else f"Install the hive team layer {VERSION}")
            sh(["git", "commit", "-q", "-m", msg], root, check=True)
            print("committed: " + sh(["git", "log", "-1", "--format=%h %s"], root).stdout.strip())
        else:
            print("nothing to commit: the repo already matches")

    print("\nNext:")
    print("  1. Start the lead in this repo:  HIVE_ROLE=lead claude")
    print("  2. Open a GitHub issue with one sentence on what you want to see. The lead takes it from there.")
    if not existed:
        print("  Then rewrite the drafts in hive/VISION.md, hive/PROJECT.md, hive/PRINCIPLES.md and "
              "hive/strategy/PRODUCT-TEST.md in your own words.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
