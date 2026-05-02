"""CLI helper for appending a pool-observation line to a JSONL log.

Used by the analysis-controller agent on every path_complete handler run
to record a single observation of pool state for manual pool-size tuning.
The helper exists because LLM agents have no wall clock; the timestamp
MUST come from a real clock, not from the model.

The helper:
- Computes `ts` as `YYYY-MM-DDTHH:MM:SSZ` from `datetime.now(timezone.utc)`.
- Appends one JSON line to the target file, creating parent dirs if missing.
- Is best-effort: any I/O failure prints to stderr and exits non-zero, but
  the controller spec says log failures MUST NOT block completion tracking,
  so callers should ignore a non-zero exit.

Usage:
    python tools/ops/append_pool_observation.py \
        --log-path <path> \
        --thread-id <id> \
        --task <task> \
        --queue-size <N> \
        --idle-pool-members <I> \
        --busy-pool-members <B> \
        --total-pool-members <T>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log-path", required=True, help="Path to the pool-observations.jsonl file."
    )
    parser.add_argument(
        "--thread-id", required=True, help="Thread id that triggered the observation."
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task name (e.g., std-solution, ai-solution, community-times).",
    )
    parser.add_argument(
        "--queue-size", required=True, type=int, help="Current depth of the relevant pool queue."
    )
    parser.add_argument(
        "--idle-pool-members",
        required=True,
        type=int,
        help="Number of idle pool members for this task.",
    )
    parser.add_argument(
        "--busy-pool-members",
        required=True,
        type=int,
        help="Number of busy pool members for this task.",
    )
    parser.add_argument(
        "--total-pool-members", required=True, type=int, help="Total pool members for this task."
    )
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    record = {
        "ts": ts,
        "thread-id": args.thread_id,
        "task": args.task,
        "queue-size": args.queue_size,
        "idle-pool-members": args.idle_pool_members,
        "busy-pool-members": args.busy_pool_members,
        "total-pool-members": args.total_pool_members,
    }

    try:
        parent = os.path.dirname(args.log_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"append_pool_observation: failed to append: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
