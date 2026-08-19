#!/usr/bin/env python3
"""Prove a published GitHub Pages site actually serves.

Waits for the URL to return 200 (a fresh Pages build 404s for the first 30-90
seconds, so an immediate 404 usually means "not built yet", not "broken"), then
parses the served HTML and requests every local asset it references. Assets that
404 in production are the common failure this catches — usually a case-only
filename mismatch that a case-insensitive local filesystem hid.

Usage:
    python3 verify.py <url> [--timeout 180] [--json]

Exit status: 0 if the page and all its assets return 200, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from preflight import RefCollector, is_local  # noqa: E402

UA = {"User-Agent": "github-pages-deploy-verify/1.0"}


def fetch(url: str, method: str = "GET", timeout: int = 20):
    """Return (status, body_bytes). Status is 0 when the request never landed."""
    req = urllib.request.Request(url, method=method, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, (resp.read() if method == "GET" else b"")
    except urllib.error.HTTPError as exc:
        return exc.code, b""
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, b""


def wait_for_page(url: str, timeout: int) -> tuple[int, bytes, float]:
    deadline = time.time() + timeout
    delay = 5
    status, body = 0, b""
    started = time.time()
    while time.time() < deadline:
        status, body = fetch(url)
        if status == 200:
            return status, body, time.time() - started
        print(f"    {status or 'no response'} — waiting for the build ({delay}s)…", flush=True)
        time.sleep(delay)
        delay = min(delay + 5, 20)
    return status, body, time.time() - started


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--timeout", type=int, default=180, help="Seconds to wait for a 200.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    url = args.url if urlparse(args.url).scheme else f"https://{args.url}"

    print(f"==> fetching {url}")
    status, body, waited = wait_for_page(url, args.timeout)

    result: dict = {"url": url, "status": status, "waited_seconds": round(waited, 1), "assets": []}

    if status != 200:
        result["error"] = (
            f"{url} returned {status or 'no response'} after {waited:.0f}s. "
            "If the build only just started, wait and rerun. Otherwise check that "
            "index.html is at the publish root and that Pages points at the right "
            "branch and path."
        )
        print(json.dumps(result, indent=2) if args.json else f"FAIL: {result['error']}")
        return 1

    print(f"    200 OK after {waited:.0f}s")

    collector = RefCollector()
    try:
        collector.feed(body.decode("utf-8", errors="replace"))
    except Exception as exc:
        print(f"    note: could not fully parse the served HTML: {exc}")

    seen: set[str] = set()
    broken: list[dict] = []
    for raw, line in collector.refs:
        ref = raw.strip()
        if not is_local(ref) or ref in seen:
            continue
        seen.add(ref)
        target = urljoin(url, ref)
        code, _ = fetch(target, method="HEAD")
        if code in (405, 0):  # some CDNs dislike HEAD; fall back to GET
            code, _ = fetch(target)
        entry = {"ref": ref, "url": target, "status": code, "line": line}
        result["assets"].append(entry)
        if code != 200:
            broken.append(entry)
        print(f"    {code or 'ERR':>3} {ref}")

    result["checked"] = len(result["assets"])
    result["broken"] = broken

    if args.json:
        print(json.dumps(result, indent=2))
    elif broken:
        print(f"\nFAIL: {len(broken)} of {len(result['assets'])} referenced files do not load:")
        for entry in broken:
            print(f"  {entry['status'] or 'no response'}  {entry['ref']}  (line {entry['line']})")
        print(
            "\nMost often this is a case-only filename mismatch (Pages is case-sensitive, "
            "macOS is not) or a root-relative path that should be relative. Fix, commit, "
            "push, and rerun."
        )
    else:
        print(f"\nOK: {url} serves, and all {len(result['assets'])} referenced files load.")

    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
