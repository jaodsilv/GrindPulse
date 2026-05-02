#!/usr/bin/env python3
"""Phase-0 fetch loop driver.

Idempotent: re-running continues from disk state (remaining.yaml / next-id.txt)
because fetch_problem.py is itself idempotent. No in-memory state is carried
across iterations of this script.

Reads `.thoughts/time-estimatives/.active-list.yaml` for:
  - `list-name` (required)
  - `fetch-delay-seconds` (optional, default 7)

For each iteration, runs `python .claude/scripts/fetch_problem.py` as a
subprocess, streams its stdout, and dispatches on the terminal `<result>` token:

  - problem_fetched -> increment K, sleep, continue
  - empty_list      -> touch {root}/.fetch-complete, emit fetch_complete + count, exit 0
  - fetch_error     -> re-emit child output verbatim, exit 1
  - unrecognized    -> emit fetch_error with diagnostic, exit 1

Must be invoked from the repo root because fetch_problem.py uses paths
relative to `.thoughts/`.
"""

import os
import re
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
try:
    from lib import status_io as _status_io
except ImportError:
    _status_io = None


ACTIVE_LIST_PATH = ".thoughts/time-estimatives/.active-list.yaml"
FETCH_PROBLEM_SCRIPT = ".claude/scripts/fetch_problem.py"
DEFAULT_FETCH_DELAY_SECONDS = 7

RESULT_RE = re.compile(r"<result>([^<]+)</result>")


def load_active_list():
    """Parse `.active-list.yaml` minimally without requiring PyYAML.

    Returns (list_name, fetch_delay_seconds).
    """
    if not os.path.isfile(ACTIVE_LIST_PATH):
        emit_fetch_error(f"active list yaml not found at {ACTIVE_LIST_PATH}")
        sys.exit(1)

    list_name = None
    fetch_delay = DEFAULT_FETCH_DELAY_SECONDS

    with open(ACTIVE_LIST_PATH, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key == "list-name":
                list_name = value
            elif key == "fetch-delay-seconds":
                try:
                    fetch_delay = int(value)
                except ValueError:
                    pass

    if not list_name:
        emit_fetch_error(f"`list-name` missing from {ACTIVE_LIST_PATH}")
        sys.exit(1)

    return list_name, fetch_delay


def emit_fetch_error(message):
    print("<result>fetch_error</result>")
    print(f"<error-message>{message}</error-message>")


def find_last_result_token(output):
    """Return the last `<result>...</result>` token value, or None."""
    matches = RESULT_RE.findall(output)
    if not matches:
        return None
    return matches[-1].strip()


def run_fetch_problem():
    """Run fetch_problem.py once, streaming stdout and capturing it.

    Returns the captured combined output (stdout+stderr).
    """
    proc = subprocess.Popen(
        [sys.executable, FETCH_PROBLEM_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
    )

    captured_lines = []
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        captured_lines.append(line)
    proc.wait()

    return "".join(captured_lines)


def main():
    list_name, fetch_delay_seconds = load_active_list()
    root = f".thoughts/time-estimatives/{list_name}/"
    fetch_complete_path = os.path.join(root, ".fetch-complete")

    fetched_count = 0
    skipped_count = 0

    while True:
        output = run_fetch_problem()
        token = find_last_result_token(output)

        if token == "problem_fetched":
            fetched_count += 1
            time.sleep(fetch_delay_seconds)
            continue

        if token == "problem_skipped":
            skipped_count += 1
            continue

        if token == "empty_list":
            os.makedirs(root, exist_ok=True)
            open(fetch_complete_path, "w").close()
            if _status_io is not None:
                try:
                    _status_io.set_fetcher_state(
                        os.path.abspath(root.rstrip("/\\").rstrip(os.sep)), "complete"
                    )
                except Exception:
                    pass
            print("<result>fetch_complete</result>")
            print(f"<count>{fetched_count}</count>")
            print(f"<skipped>{skipped_count}</skipped>")
            sys.exit(0)

        if token == "fetch_error":
            sys.exit(1)

        emit_fetch_error("unrecognized fetch_problem.py output")
        sys.exit(1)


if __name__ == "__main__":
    main()
