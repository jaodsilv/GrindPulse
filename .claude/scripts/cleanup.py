"""Phase 5 cleanup: append final RUN_COMPLETE line to audit.log and report count.

Usage:
  python .claude/scripts/cleanup.py --list-name X

Reads {root}/status.yaml via lib.status_io.read_status, counts the `complete`
entries (defensive against missing/None values and against both old
list-of-strings and new list-of-dicts shapes), appends a tab-separated line
to {root}/audit.log, and prints the result wrapped in <result>...</result>.
"""

import datetime
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from lib import status_io  # noqa: E402


def _parse_args(argv: list[str]) -> str:
    list_name = None
    for i, a in enumerate(argv):
        if a == "--list-name" and i + 1 < len(argv):
            list_name = argv[i + 1]
    if not list_name:
        active_path = os.path.join(".thoughts", "time-estimatives", ".active-list.yaml")
        try:
            import yaml

            with open(active_path, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            list_name = cfg.get("list-name")
        except Exception:
            pass
    if not list_name:
        print("--list-name is required (or .active-list.yaml must be present)", file=sys.stderr)
        sys.exit(1)
    return list_name


def _count_complete(status: dict) -> int:
    if not isinstance(status, dict):
        return 0
    complete = status.get("complete")
    if complete is None:
        return 0
    try:
        return len(complete)
    except TypeError:
        return 0


def main() -> None:
    list_name = _parse_args(sys.argv[1:])
    work_folder = f".thoughts/time-estimatives/{list_name}"

    status = status_io.read_status(work_folder)
    n = _count_complete(status)

    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    audit_path = os.path.join(work_folder, "audit.log")
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(f"{ts}\tRUN_COMPLETE\tcomplete={n}\n")

    print(f"<result>run complete: {n} problems updated</result>")


if __name__ == "__main__":
    main()
