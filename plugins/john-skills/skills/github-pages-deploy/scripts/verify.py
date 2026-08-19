#!/usr/bin/env python3
"""Prove a published GitHub Pages site actually serves.

Waits for the URL to return 200 — a fresh build 404s for the first 30-90
seconds, so an immediate 404 usually means "not built yet" rather than
"broken" — then requests every local file the served page references. Assets
that 404 in production are the common failure, usually a case-only filename
mismatch that the local filesystem hid.

Usage:
    python3 verify.py <url> [timeout-seconds]

Exit status: 0 if the page and all its assets return 200, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from preflight import RefCollector, is_local  # noqa: E402

UA = {"User-Agent": "github-pages-deploy-verify/1.0"}


def fetch(url: str, method: str = "GET") -> tuple[int, bytes]:
    """Return (status, body). Status is 0 when the request never landed."""
    req = urllib.request.Request(url, method=method, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, (resp.read() if method == "GET" else b"")
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, b""


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    url = sys.argv[1] if urlparse(sys.argv[1]).scheme else f"https://{sys.argv[1]}"
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 180

    print(f"==> fetching {url}")
    deadline, delay, started = time.time() + timeout, 5, time.time()
    status, body = 0, b""
    while time.time() < deadline:
        status, body = fetch(url)
        if status == 200:
            break
        print(f"    {status or 'no response'} — waiting for the build ({delay}s)…", flush=True)
        time.sleep(delay)
        delay = min(delay + 5, 20)
    waited = time.time() - started

    if status != 200:
        print(
            f"FAIL: {url} returned {status or 'no response'} after {waited:.0f}s.\n"
            "If the build only just started, wait and rerun. Otherwise check that "
            "index.html is at the repo root and that Pages points at main and /."
        )
        return 1

    print(f"    200 OK after {waited:.0f}s")

    collector = RefCollector()
    try:
        collector.feed(body.decode("utf-8", errors="replace"))
    except Exception as exc:
        print(f"    note: could not fully parse the served HTML: {exc}")

    seen: set[str] = set()
    broken: list[tuple[str, int, int]] = []
    checked = 0
    for raw, line in collector.refs:
        ref = raw.strip()
        if not is_local(ref) or ref in seen:
            continue
        seen.add(ref)
        target = urljoin(url, ref)
        code, _ = fetch(target, method="HEAD")
        if code in (405, 0):  # some servers dislike HEAD; fall back to GET
            code, _ = fetch(target)
        checked += 1
        print(f"    {code or 'ERR':>3} {ref}")
        if code != 200:
            broken.append((ref, code, line))

    if broken:
        print(f"\nFAIL: {len(broken)} of {checked} referenced files do not load:")
        for ref, code, line in broken:
            print(f"  {code or 'no response'}  {ref}  (line {line})")
        print(
            "\nUsually a case-only filename mismatch (Pages is case-sensitive, macOS is "
            "not) or a root-relative path that should be relative. Fix, then rerun deploy.sh."
        )
        return 1

    print(f"\nOK: {url} serves, and all {checked} referenced files load.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
