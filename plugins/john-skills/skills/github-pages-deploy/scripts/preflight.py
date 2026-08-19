#!/usr/bin/env python3
"""Audit a static site before publishing it to GitHub Pages.

Catches the things that render fine locally and break once the site is live:
a missing index.html, root-relative asset paths, references to files that do
not exist, and case-only filename mismatches that a case-insensitive macOS
filesystem hides from you.

Usage:
    python3 preflight.py <site-dir>

Exit status: 0 if clean, 1 if there are errors.
"""

from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

# Attributes that can point at a local file we need to ship.
URL_ATTRS = {
    "src": {"img", "script", "iframe", "video", "audio", "source", "embed", "track"},
    "href": {"link", "a"},
    "poster": {"video"},
}

MAX_BLOB_BYTES = 100 * 1024 * 1024  # git hard-rejects pushes above this
CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.IGNORECASE)


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
        if attrd.get("srcset"):
            for candidate in attrd["srcset"].split(","):
                parts = candidate.split()
                if parts:
                    self.refs.append((parts[0], line))
        if attrd.get("style"):
            self.refs += [(m.group(1), line) for m in CSS_URL_RE.finditer(attrd["style"])]
        if tag == "style":
            self._in_style = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            line = self.getpos()[0]
            self.refs += [(m.group(1), line) for m in CSS_URL_RE.finditer(data)]


def is_local(url: str) -> bool:
    """True when the reference points at a file we have to publish."""
    url = url.strip()
    if not url or url.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return False
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.netloc


def resolve_case_sensitively(root: Path, rel: str) -> tuple[bool, str | None]:
    """Resolve `rel` under `root` the way a case-sensitive server would.

    Returns (exists_exactly, actual_path_if_only_the_case_differs). Walking
    segment by segment against real directory listings is what catches
    `assets/Logo.png` vs `assets/logo.png`, where a plain exists() check lies
    on macOS.
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


def audit(site_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []

    if not (site_dir / "index.html").is_file():
        errors.append(
            "No index.html at the site root. Pages serves index.html as the homepage; "
            "without it the whole site returns 404."
        )

    html_files = sorted(p for p in site_dir.rglob("*.htm*") if ".git" not in p.parts)
    if not html_files:
        errors.append(f"No HTML files found under {site_dir}.")

    jekyll_paths: set[str] = set()
    for path in site_dir.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(site_dir)
        if path.stat().st_size > MAX_BLOB_BYTES:
            errors.append(f"{rel} is over 100 MB; git will reject the push.")
        if any(p.startswith("_") or (p.startswith(".") and p != ".nojekyll") for p in rel.parts):
            jekyll_paths.add(str(rel))

    if jekyll_paths and not (site_dir / ".nojekyll").exists():
        sample = ", ".join(sorted(jekyll_paths)[:3])
        notes.append(
            f"{len(jekyll_paths)} path(s) start with '_' or '.' ({sample}). Jekyll skips "
            "these; deploy.sh writes a .nojekyll file, which fixes it."
        )

    for html in html_files:
        rel_html = html.relative_to(site_dir)
        collector = RefCollector()
        try:
            collector.feed(html.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:  # malformed HTML shouldn't abort the audit
            notes.append(f"Could not fully parse {rel_html}: {exc}")

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
                errors.append(
                    f"{rel_html}:{line} references '{url}'. The leading '/' resolves to "
                    f"the account root, not your repo's path, so it 404s once published. "
                    f"Use '{target.lstrip('/')}' instead."
                )
                lookup = target.lstrip("/")
            else:
                lookup = (rel_html.parent / target).as_posix()

            exists, cased = resolve_case_sensitively(site_dir, lookup)
            if cased is not None:
                errors.append(
                    f"{rel_html}:{line} references '{url}' but the file on disk is "
                    f"'{cased}'. Pages is case-sensitive even though macOS is not, so "
                    "this loads locally and 404s in production."
                )
            elif not exists:
                errors.append(f"{rel_html}:{line} references '{url}', which does not exist.")

    return errors, notes


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(sys.argv) == 2 else 2

    site_dir = Path(sys.argv[1]).expanduser().resolve()
    if not site_dir.is_dir():
        print(f"error: {site_dir} is not a directory", file=sys.stderr)
        return 2

    errors, notes = audit(site_dir)
    for item in errors:
        print(f"ERROR: {item}")
    for item in notes:
        print(f"NOTE: {item}")
    if not errors and not notes:
        print("OK: site looks ready to publish.")
    elif errors:
        print(f"\n{len(errors)} problem(s) that would break the published site.")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
