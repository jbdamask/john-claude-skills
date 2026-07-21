#!/usr/bin/env python3
"""Stop a cost-tracking session: extract entries, calculate costs, write summary."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

# Load pricing from external resource file
PRICING_FILE = os.path.join(os.path.dirname(__file__), "..", "resources", "pricing.json")
with open(PRICING_FILE) as _f:
    _pricing_data = json.load(_f)
PRICING = _pricing_data["models"]
PRICING_META = _pricing_data["_meta"]


def resolve_model(model_id):
    """Resolve a model ID (possibly with snapshot date) to a pricing key."""
    if not model_id:
        return None
    if model_id in PRICING:
        return model_id
    # Strip snapshot suffix: claude-sonnet-4-6-20260101 -> claude-sonnet-4-6
    for base in PRICING:
        if model_id.startswith(base):
            return base
    return None


def calc_cost(usage, model_key):
    """Calculate cost for a single entry's usage."""
    prices = PRICING.get(model_key)
    if not prices:
        return None

    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)
    cache_creation_tokens = usage.get("cache_creation_input_tokens", 0)
    cache_read_tokens = usage.get("cache_read_input_tokens", 0)

    # Split cache writes into 5m and 1h using the cache_creation sub-object
    cache_creation_detail = usage.get("cache_creation", {})
    cache_1h = cache_creation_detail.get("ephemeral_1h_input_tokens", 0)
    cache_5m = cache_creation_detail.get("ephemeral_5m_input_tokens", 0)

    # If no detail breakdown, assume all cache writes are 5m (conservative fallback)
    if cache_creation_tokens > 0 and cache_1h == 0 and cache_5m == 0:
        cache_5m = cache_creation_tokens

    mtok = 1_000_000
    input_cost = input_tokens / mtok * prices["input"]
    output_cost = output_tokens / mtok * prices["output"]
    cache_write_5m_cost = cache_5m / mtok * prices["cache_write_5m"]
    cache_write_1h_cost = cache_1h / mtok * prices["cache_write_1h"]
    cache_read_cost = cache_read_tokens / mtok * prices["cache_read"]

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "cache_write_5m_cost": cache_write_5m_cost,
        "cache_write_1h_cost": cache_write_1h_cost,
        "cache_read_cost": cache_read_cost,
        "total_cost": input_cost + output_cost + cache_write_5m_cost + cache_write_1h_cost + cache_read_cost,
    }


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

    # Aggregate totals per model
    totals_by_model = {}
    for entry in entries:
        model_key = resolve_model(entry["model"])
        if not model_key:
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
        prices = PRICING.get(model_key)
        if not prices:
            cost_breakdown[model_key] = {"error": "unknown model, cannot calculate cost", **t}
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
        "pricing_source": PRICING_META["source"],
        "pricing_date": PRICING_META["updated"],
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
