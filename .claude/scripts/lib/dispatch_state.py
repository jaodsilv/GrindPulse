"""Shared in-flight counter helpers for agent_dispatch and subagent_stop_state_advance.

All read/modify/write of the counter file is serialized via lib.file_lock on a
sibling .lock file so concurrent SubagentStop / agent_dispatch hooks cannot
race. The lock primitive is reentrant-safe across processes (advisory OS lock
on a separate file descriptor).

Malformed counter contents (empty, non-int, partial write from a crashed
process) are logged to stderr with the file path and offending content, then
clamped to 0 so the dispatcher keeps making progress instead of wedging on a
ValueError.
"""

import sys
from pathlib import Path

from lib.file_lock import file_lock


def counter_path(work_folder):
    return Path(work_folder) / "in-flight.txt"


def _log_err(msg):
    print(f"[dispatch_state] {msg}", file=sys.stderr)


def _parse_counter(p):
    """Read and parse the counter file. On any parse/IO failure, log and return 0."""
    try:
        raw = p.read_text()
    except FileNotFoundError:
        return 0
    except OSError as e:
        _log_err(f"failed to read counter at {p}: {e!r}; defaulting to 0")
        return 0
    stripped = raw.strip()
    if not stripped:
        _log_err(f"counter at {p} is empty (raw={raw!r}); defaulting to 0")
        return 0
    try:
        return int(stripped)
    except ValueError:
        _log_err(f"counter at {p} has non-integer contents (raw={raw!r}); defaulting to 0")
        return 0


def read_counter(work_folder):
    """Read the in-flight counter under the dispatch lock.

    Returns 0 if the file is missing, empty, or malformed (with stderr log).
    """
    p = counter_path(work_folder)
    with file_lock(str(p)):
        return _parse_counter(p)


def write_counter(work_folder, n):
    """Write the in-flight counter under the dispatch lock, clamped to >= 0."""
    p = counter_path(work_folder)
    with file_lock(str(p)):
        try:
            p.write_text(str(max(0, n)))
        except OSError as e:
            _log_err(f"failed to write counter at {p} (n={n!r}): {e!r}")
            raise
