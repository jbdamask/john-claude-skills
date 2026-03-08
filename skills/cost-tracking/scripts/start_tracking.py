#!/usr/bin/env python3
"""Start a cost-tracking session by recording current position in the session JSONL."""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone


def count_lines(filepath):
    count = 0
    with open(filepath, "r") as f:
        for _ in f:
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Start cost tracking")
    parser.add_argument("session_jsonl", help="Path to the current session JSONL file")
    parser.add_argument("cost_tracking_dir", help="Directory for cost tracking data")
    args = parser.parse_args()

    if not os.path.exists(args.session_jsonl):
        print(f"Error: Session file not found: {args.session_jsonl}", file=sys.stderr)
        sys.exit(1)

    tracking_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    start_line = count_lines(args.session_jsonl)

    tracking_dir = os.path.join(args.cost_tracking_dir, tracking_id)
    os.makedirs(tracking_dir, exist_ok=True)

    metadata = {
        "tracking_id": tracking_id,
        "session_jsonl": args.session_jsonl,
        "start_line": start_line,
        "start_time": datetime.now(timezone.utc).isoformat(),
    }

    metadata_path = os.path.join(tracking_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(json.dumps({"tracking_id": tracking_id, "metadata_path": metadata_path, "start_line": start_line}))


if __name__ == "__main__":
    main()
