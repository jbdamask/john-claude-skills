#!/usr/bin/env python3
"""Audit a static site directory before publishing it to GitHub Pages.

Checks the things that make a site render locally but break in production:
missing index.html, root-relative asset paths, references to files that do not
exist (including case-only mismatches, which macOS hides), Jekyll-excluded
paths, and files git or Pages will reject on size.

Usage:
    python3 preflight.py <site-dir> [--user-site] [--json]

--user-site   The repo is named <owner>.github.io, so the site is served from
              the domain root and root-relative paths are legitimate.

Exit status: 0 if nothing worse than a note was found, 1 if there are errors.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

# Attributes that can point at a local file we need to ship.
URL_ATTRS = {
    "src": {"img", "script", "iframe", "video", "audio", "source", "embed", "track", "input"},
    "href": {"link", "a"},
    "poster": {"video"},
    "data": {"object"},
}

MAX_BLOB_BYTES = 100 * 1024 * 1024  # git hard-rejects pushes above this
MAX_SITE_BYTES = 1024 * 1024 * 1024  # Pages published-site soft limit

CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.IGNORECASE)
SRCSET_SPLIT_RE = re.compile(r"\s*,\s*")


class RefCollector(HTMLParser):
    """Pull every candidate local-file reference out of an HTML document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, int]] = []
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line = self.getpos()[0]
        attrd = {k.lower(): (v or "") for k, v in attrs}
        for attr, tags in URL_ATTRS.items():
            if tag in tags and attrd.get(attr):
                self.refs.append((attrd[attr], line))
        # srcset carries several URLs, each optionally followed by a descriptor.
        for attr in ("srcset", "imagesrcset"):
            if attrd.get(attr):
                for candidate in SRCSET_SPLIT_RE.split(attrd[attr]):
                    url = candidate.strip().split()[0] if candidate.strip() else ""
                    if url:
                        self.refs.append((url, line))
        if tag == "style":
            self._in_style = True
        if attrd.get("style"):
            for m in CSS_URL_RE.finditer(attrd["style"]):
                self.refs.append((m.group(1), line))

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            line = self.getpos()[0]
            for m in CSS_URL_RE.finditer(data):
                self.refs.append((m.group(1), line))


def is_local(url: str) -> bool:
    """True when the reference points at a file we have to publish."""
    url = url.strip()
    if not url or url.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return False
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.netloc


def resolve_case_sensitively(root: Path, rel: str) -> tuple[bool, str | None]:
    """Resolve `rel` under `root` the way a case-sensitive server would.

    Returns (exists_exactly, actual_path_if_case_differs). Walking segment by
    segment is what lets us spot `assets/Logo.png` vs `assets/logo.png` on a
    case-insensitive local filesystem, where a plain exists() check lies.
    """
    current = root
    for part in Path(rel).parts:
        if part in (".", ""):
            continue
        if part == "..":
            current = current.parent
            continue
        try:
            entries = os.listdir(current)
        except (NotADirectoryError, FileNotFoundError, PermissionError):
            return False, None
        if part in entries:
            current = current / part
            continue
        matches = [e for e in entries if e.lower() == part.lower()]
        if matches:
            return False, str((current / matches[0]).relative_to(root))
        return False, None
    return current.exists(), None


def audit(site_dir: Path, user_site: bool) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    index = site_dir / "index.html"
    if not index.is_file():
        errors.append(
            "No index.html at the publish root. GitHub Pages serves index.html as the "
            "homepage; without it the site returns 404."
        )

    html_files = sorted(p for p in site_dir.rglob("*.htm*") if ".git" not in p.parts)
    if not html_files:
        errors.append(f"No HTML files found under {site_dir}.")

    jekyll_paths: set[str] = set()
    total_bytes = 0
    for path in site_dir.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        size = path.stat().st_size
        total_bytes += size
        if size > MAX_BLOB_BYTES:
            errors.append(
                f"{path.relative_to(site_dir)} is {size / 1e6:.0f} MB; git rejects "
                "individual files over 100 MB."
            )
        for part in path.relative_to(site_dir).parts:
            if part.startswith("_") or (part.startswith(".") and part != ".nojekyll"):
                jekyll_paths.add(str(path.relative_to(site_dir)))

    if total_bytes > MAX_SITE_BYTES:
        warnings.append(
            f"Site is {total_bytes / 1e9:.2f} GB; GitHub Pages publishes up to about 1 GB."
        )

    if jekyll_paths and not (site_dir / ".nojekyll").exists():
        sample = ", ".join(sorted(jekyll_paths)[:4])
        notes.append(
            f"{len(jekyll_paths)} path(s) start with '_' or '.' ({sample}). Jekyll skips "
            "these; deploy.sh adds a .nojekyll file, which fixes it."
        )

    for html in html_files:
        rel_html = html.relative_to(site_dir)
        try:
            text = html.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            warnings.append(f"Could not read {rel_html}: {exc}")
            continue
        collector = RefCollector()
        try:
            collector.feed(text)
        except Exception as exc:  # malformed HTML shouldn't abort the audit
            warnings.append(f"Could not fully parse {rel_html}: {exc}")

        seen: set[str] = set()
        for raw, line in collector.refs:
            url = raw.strip()
            if not is_local(url) or url in seen:
                continue
            seen.add(url)
            target = unquote(urlparse(url).path)
            if not target:
                continue

            if target.startswith("/"):
                if user_site:
                    notes.append(
                        f"{rel_html}:{line} uses the root-relative path '{url}'. Fine for a "
                        "user site served at the domain root."
                    )
                else:
                    errors.append(
                        f"{rel_html}:{line} references '{url}'. On a project site the leading "
                        f"'/' resolves to the account root, not your repo. Use "
                        f"'{target.lstrip('/')}' instead."
                    )
                lookup_root, lookup_rel = site_dir, target.lstrip("/")
            else:
                lookup_root, lookup_rel = site_dir, str(
                    (rel_html.parent / target).as_posix()
                )

            exists, cased = resolve_case_sensitively(lookup_root, lookup_rel)
            if cased is not None:
                errors.append(
                    f"{rel_html}:{line} references '{url}' but the file on disk is "
                    f"'{cased}'. GitHub Pages is case-sensitive even though macOS is not, "
                    "so this loads locally and 404s in production."
                )
            elif not exists:
                errors.append(f"{rel_html}:{line} references '{url}', which does not exist.")

    return {"errors": errors, "warnings": warnings, "notes": notes}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("site_dir")
    ap.add_argument(
        "--user-site",
        action="store_true",
        help="Repo is <owner>.github.io, so root-relative paths are valid.",
    )
    ap.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = ap.parse_args()

    site_dir = Path(args.site_dir).expanduser().resolve()
    if not site_dir.is_dir():
        print(f"error: {site_dir} is not a directory", file=sys.stderr)
        return 2

    result = audit(site_dir, args.user_site)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for label, items in (
            ("ERROR", result["errors"]),
            ("WARN", result["warnings"]),
            ("NOTE", result["notes"]),
        ):
            for item in items:
                print(f"{label}: {item}")
        if not any(result.values()):
            print("OK: site looks ready to publish.")
        else:
            print(
                f"\n{len(result['errors'])} error(s), {len(result['warnings'])} warning(s), "
                f"{len(result['notes'])} note(s)."
            )

    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
