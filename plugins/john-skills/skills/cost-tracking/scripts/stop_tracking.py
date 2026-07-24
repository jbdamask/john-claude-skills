#!/usr/bin/env python3
"""Stop a cost-tracking session: extract entries, calculate costs, write summary."""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

# -------------------------------------------------------------------------- #
# Live pricing — fetched from Anthropic's published pricing page at run time,
# with the version-controlled resources/pricing.json as an explicit offline
# fallback. A model we can't price is reported as an ERROR — never silently
# mapped to another model's rate. (The old resolve_model prefix-match sent
# `claude-opus-4-8` to the legacy `claude-opus-4` row and 3x-overcharged.)
# -------------------------------------------------------------------------- #

PRICING_URL = "https://platform.claude.com/docs/en/about-claude/pricing.md"
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FALLBACK_FILE = os.path.join(_SCRIPT_DIR, "..", "resources", "pricing.json")
_CACHE_PATH = os.path.join(_SCRIPT_DIR, ".pricing_cache.json")
_CACHE_TTL_HOURS = 24
_FAMILIES = ("opus", "sonnet", "haiku", "fable", "mythos")


def _price(cell):
    m = re.search(r"\$([0-9]+(?:\.[0-9]+)?)", cell)
    return float(m.group(1)) if m else None


def _parse_date(s):
    try:
        return datetime.strptime(s.strip().title(), "%B %d, %Y").date()
    except ValueError:
        return None


def _norm_id(model_id):
    """API model id -> normalized key. claude-opus-4-8 -> 'opus 4.8';
    claude-haiku-4-5-20251001 -> 'haiku 4.5' (8-digit snapshot dropped)."""
    if not model_id:
        return None
    s = model_id.lower()
    s = s[len("claude-"):] if s.startswith("claude-") else s
    parts = s.split("-")
    if not parts or parts[0] not in _FAMILIES:
        return None
    nums = [p for p in parts[1:] if p.isdigit() and len(p) != 8]
    return f"{parts[0]} {'.'.join(nums)}".strip()


def _row_key_window(name):
    """Table model-name cell -> (normalized_key, window). window is
    ('until', date) / ('from', date) / None, capturing intro-vs-standard rows."""
    low = name.lower()
    m = re.search(r"\b(opus|sonnet|haiku|fable|mythos)\s+([0-9]+(?:\.[0-9]+)?)", low)
    if not m:
        return None, None
    key = f"{m.group(1)} {m.group(2)}"
    window = None
    dm = re.search(r"through\s+([a-z]+\s+\d+,\s*\d{4})", low)
    if dm:
        window = ("until", _parse_date(dm.group(1)))
    dm = re.search(r"starting\s+([a-z]+\s+\d+,\s*\d{4})", low)
    if dm:
        window = ("from", _parse_date(dm.group(1)))
    return key, window


def _parse_pricing_md(md):
    """Parse the '## Model pricing' pipe-table into {key: [ {prices, window} ]}."""
    start = md.find("## Model pricing")
    if start == -1:
        return {}
    region = md[start: md.find("\n## ", start + 1)]
    table = {}
    for line in region.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        if cells[1].lower().startswith("base input") or set(cells[0]) <= set("-: "):
            continue  # header row / separator row
        key, window = _row_key_window(cells[0])
        if not key:
            continue
        prices = {
            "input": _price(cells[1]),
            "cache_write_5m": _price(cells[2]),
            "cache_write_1h": _price(cells[3]),
            "cache_read": _price(cells[4]),
            "output": _price(cells[5]),
        }
        if None in prices.values():
            continue
        table.setdefault(key, []).append({"prices": prices, "window": window})
    return table


def _serialize(table):
    return {k: [{"prices": r["prices"],
                 "window": ([r["window"][0], r["window"][1].isoformat()]
                            if r["window"] and r["window"][1] else None)}
                for r in rows] for k, rows in table.items()}


def _deserialize(obj):
    table = {}
    for k, rows in obj.items():
        table[k] = [{"prices": r["prices"],
                     "window": ((r["window"][0], datetime.fromisoformat(r["window"][1]).date())
                                if r.get("window") else None)}
                    for r in rows]
    return table


def _bundled_table():
    """resources/pricing.json (offline fallback), normalized into the live-table
    key space so it can't prefix-match the wrong model."""
    try:
        with open(_FALLBACK_FILE) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}, None
    table = {}
    for mid, prices in data.get("models", {}).items():
        key = _norm_id(mid)
        if key:
            table.setdefault(key, []).append({"prices": prices, "window": None})
    return table, data.get("_meta", {}).get("updated")


def load_pricing_table():
    """Return (table, source_note). Fresh 24h cache -> live fetch -> stale cache
    -> bundled resources/pricing.json (loud) -> None. Never silently substitutes
    one model's price for another."""
    try:
        age_h = (datetime.now().timestamp() - os.stat(_CACHE_PATH).st_mtime) / 3600
        if age_h < _CACHE_TTL_HOURS:
            with open(_CACHE_PATH) as f:
                cached = json.load(f)
            return _deserialize(cached["table"]), f"cached {cached['fetched_at'][:19]}Z"
    except (OSError, KeyError, ValueError):
        pass
    try:
        req = urllib.request.Request(PRICING_URL, headers={"User-Agent": "cost-tracking/2.0"})
        md = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        table = _parse_pricing_md(md)
        if not table:
            raise ValueError("no pricing rows parsed from page")
        fetched_at = datetime.now(timezone.utc).isoformat()
        try:
            with open(_CACHE_PATH, "w") as f:
                json.dump({"fetched_at": fetched_at, "table": _serialize(table)}, f)
        except OSError:
            pass
        return table, f"live: {PRICING_URL}"
    except Exception as e:  # network or parse failure
        try:
            with open(_CACHE_PATH) as f:
                cached = json.load(f)
            print(f"  ⚠️  Could not fetch live prices ({type(e).__name__}: {e}); "
                  f"using STALE cache from {cached['fetched_at'][:19]}Z — verify manually.",
                  file=sys.stderr)
            return _deserialize(cached["table"]), f"STALE cache {cached['fetched_at'][:19]}Z"
        except (OSError, KeyError, ValueError):
            table, updated = _bundled_table()
            if table:
                print(f"  ⚠️  Could not fetch live prices ({type(e).__name__}: {e}); "
                      f"using bundled resources/pricing.json (updated {updated}) — may be stale.",
                      file=sys.stderr)
                return table, f"bundled resources/pricing.json (updated {updated})"
            print(f"  ⚠️  No live prices, no cache, no bundled fallback "
                  f"({type(e).__name__}: {e}). Token counts shown; cost cannot be computed.",
                  file=sys.stderr)
            return None, f"UNAVAILABLE ({type(e).__name__})"


def get_prices(table, model_id, as_of):
    """Prices for a model as of a date, or None if it can't be priced."""
    if table is None:
        return None
    rows = table.get(_norm_id(model_id))
    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]["prices"]
    # Multiple rows (e.g. intro vs standard) — pick the one in effect at as_of.
    for r in rows:
        w = r["window"]
        if not w or w[1] is None:
            continue
        if (w[0] == "until" and as_of <= w[1]) or (w[0] == "from" and as_of >= w[1]):
            return r["prices"]
    return rows[0]["prices"]


def main():
    parser = argparse.ArgumentParser(description="Stop cost tracking and calculate costs")
    parser.add_argument("tracking_id", help="Tracking session ID")
    parser.add_argument("cost_tracking_dir", help="Directory for cost tracking data")
    args = parser.parse_args()

    tracking_dir = os.path.join(args.cost_tracking_dir, args.tracking_id)
    metadata_path = os.path.join(tracking_dir, "metadata.json")

    if not os.path.exists(metadata_path):
        print(f"Error: Tracking session not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)

    with open(metadata_path) as f:
        metadata = json.load(f)

    session_jsonl = metadata["session_jsonl"]
    start_line = metadata["start_line"]

    if not os.path.exists(session_jsonl):
        print(f"Error: Session file not found: {session_jsonl}", file=sys.stderr)
        sys.exit(1)

    # Read entries from start_line onwards
    entries = []
    with open(session_jsonl) as f:
        for i, line in enumerate(f):
            if i < start_line:
                continue
            try:
                obj = json.loads(line)
                usage = obj.get("message", {}).get("usage", {})
                if not usage or not usage.get("output_tokens"):
                    continue
                model = obj.get("message", {}).get("model", "")
                timestamp = obj.get("timestamp", "")
                entries.append({
                    "timestamp": timestamp,
                    "model": model,
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                    "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
                    "cache_creation": usage.get("cache_creation", {}),
                })
            except (json.JSONDecodeError, KeyError):
                continue

    # Write tokens JSONL
    tokens_path = os.path.join(tracking_dir, "tokens.jsonl")
    with open(tokens_path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    # Live prices, as of the run's date (handles intro-vs-standard rows).
    stamps = [e["timestamp"][:10] for e in entries if e.get("timestamp")]
    try:
        as_of = datetime.fromisoformat(max(stamps)).date() if stamps else datetime.now().date()
    except ValueError:
        as_of = datetime.now().date()
    pricing_table, pricing_source = load_pricing_table()

    # Aggregate totals per model
    totals_by_model = {}
    for entry in entries:
        model_key = entry["model"] or "unknown"

        if model_key not in totals_by_model:
            totals_by_model[model_key] = {
                "input_tokens": 0, "output_tokens": 0,
                "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0,
                "cache_5m_tokens": 0, "cache_1h_tokens": 0,
                "entries": 0,
            }
        t = totals_by_model[model_key]
        t["input_tokens"] += entry["input_tokens"]
        t["output_tokens"] += entry["output_tokens"]
        t["cache_creation_input_tokens"] += entry["cache_creation_input_tokens"]
        t["cache_read_input_tokens"] += entry["cache_read_input_tokens"]
        cc = entry.get("cache_creation", {})
        t["cache_1h_tokens"] += cc.get("ephemeral_1h_input_tokens", 0)
        t["cache_5m_tokens"] += cc.get("ephemeral_5m_input_tokens", 0)
        t["entries"] += 1

    # Calculate costs
    grand_total = 0
    cost_breakdown = {}
    for model_key, t in totals_by_model.items():
        prices = get_prices(pricing_table, model_key, as_of)
        if not prices:
            cost_breakdown[model_key] = {
                "error": f"could not price '{model_key}' from {pricing_source} "
                         f"— not silently substituting another model's rate", **t}
            continue
        mtok = 1_000_000
        cache_5m = t["cache_5m_tokens"]
        cache_1h = t["cache_1h_tokens"]
        if t["cache_creation_input_tokens"] > 0 and cache_5m == 0 and cache_1h == 0:
            cache_5m = t["cache_creation_input_tokens"]

        costs = {
            "input": t["input_tokens"] / mtok * prices["input"],
            "output": t["output_tokens"] / mtok * prices["output"],
            "cache_write_5m": cache_5m / mtok * prices["cache_write_5m"],
            "cache_write_1h": cache_1h / mtok * prices["cache_write_1h"],
            "cache_read": t["cache_read_input_tokens"] / mtok * prices["cache_read"],
        }
        costs["total"] = sum(costs.values())
        grand_total += costs["total"]
        cost_breakdown[model_key] = {"tokens": t, "costs": costs}

    # Write summary
    summary = {
        "tracking_id": args.tracking_id,
        "start_time": metadata["start_time"],
        "stop_time": datetime.now(timezone.utc).isoformat(),
        "total_entries": len(entries),
        "cost_breakdown": cost_breakdown,
        "grand_total_usd": round(grand_total, 6),
        "pricing_source": pricing_source,
        "priced_as_of": as_of.isoformat(),
    }

    summary_path = os.path.join(tracking_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Print report
    print(f"\n{'='*60}")
    print(f"  Cost Tracking Report: {args.tracking_id}")
    print(f"{'='*60}")
    print(f"  Period: {metadata['start_time'][:19]} -> {summary['stop_time'][:19]}")
    print(f"  API calls tracked: {len(entries)}")
    print(f"  Prices: {pricing_source}  (as of {as_of.isoformat()})")
    print()

    for model_key, data in cost_breakdown.items():
        if "error" in data:
            print(f"  {model_key}: {data['error']}")
            continue
        t = data["tokens"]
        c = data["costs"]
        print(f"  Model: {model_key}")
        print(f"  {'─'*50}")
        print(f"  {'Token Type':<28} {'Tokens':>10}  {'Cost':>10}")
        print(f"  {'─'*50}")
        print(f"  {'Base input':<28} {t['input_tokens']:>10,}  ${c['input']:.4f}")
        print(f"  {'Output':<28} {t['output_tokens']:>10,}  ${c['output']:.4f}")
        print(f"  {'Cache writes (5m)':<28} {t['cache_5m_tokens']:>10,}  ${c['cache_write_5m']:.4f}")
        print(f"  {'Cache writes (1h)':<28} {t['cache_1h_tokens']:>10,}  ${c['cache_write_1h']:.4f}")
        print(f"  {'Cache reads':<28} {t['cache_read_input_tokens']:>10,}  ${c['cache_read']:.4f}")
        print(f"  {'─'*50}")
        print(f"  {'Subtotal':<28} {'':>10}  ${c['total']:.4f}")
        print()

    print(f"  {'='*50}")
    print(f"  {'GRAND TOTAL':<28} {'':>10}  ${grand_total:.4f}")
    print(f"  {'='*50}")
    print(f"\n  Files: {tracking_dir}/")
    print(f"    tokens.jsonl  — per-entry token log")
    print(f"    summary.json  — full cost breakdown")


if __name__ == "__main__":
    main()
