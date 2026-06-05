"""Shared in-flight counter helpers for agent_dispatch and subagent_stop_state_advance.

Concurrency contract: callers MUST hold the dispatch lock
(`file_lock(<work_folder>/.dispatch.lock)`) for the duration of any
read-modify-write sequence on the counter. read_counter/write_counter
deliberately do NOT take a second lock of their own — doing so would be
redundant with the caller's dispatch lock and only adds I/O. The hooks in
`.claude/hooks/agent_dispatch.py` and `.claude/hooks/subagent_stop_state_advance.py`
already enter the dispatch lock before invoking these helpers.

Malformed counter contents (empty, non-int, partial write from a crashed
process) are logged to stderr with the file path and offending content, then
clamped to 0 so the dispatcher keeps making progress instead of wedging on a
ValueError.
"""

import sys
from pathlib import Path


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
    """Read the in-flight counter. Caller must hold the dispatch lock.

    Returns 0 if the file is missing, empty, or malformed (with stderr log).
    """
    return _parse_counter(counter_path(work_folder))


def write_counter(work_folder, n):
    """Write the in-flight counter, clamped to >= 0. Caller must hold the dispatch lock."""
    p = counter_path(work_folder)
    try:
        p.write_text(str(max(0, n)))
    except OSError as e:
        _log_err(f"failed to write counter at {p} (n={n!r}): {e!r}")
        raise
