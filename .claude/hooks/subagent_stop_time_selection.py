#!/usr/bin/env python3
"""SubagentStop hook for time-selection.

Parses the worker's last assistant message for the contract line:
    intermediate=I advanced=A top=T source=SRC problem-id=N

and runs `write_tsv.py --list-name X --problem-id N --intermediate I --advanced A --top T --source SRC`
where X is the active list name (read from .thoughts/time-estimatives/.active-list.yaml).

Safe to run for ALL SubagentStop events: exits 0 silently when the agent is
not a time-selection agent. On write_tsv failure, appends a WRITE_TSV_ERROR
line to the run's audit.log and returns a `block` decision so the parent
dispatcher fails fast.
"""

import datetime
import json
import os
import re
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.normpath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from lib.active_list import load_pair as _load_active_list  # noqa: E402


def log_err(msg):
    sys.stderr.write(f"[subagent_stop_time_selection] {msg}\n")


_CONTRACT_RE = re.compile(
    r"intermediate=(\d+)\s+advanced=(\d+)\s+top=(\d+)\s+source=(\S+)\s+problem-id=(\d+)"
)


def _parse_contract(msg):
    """Return (intermediate, advanced, top, source, problem_id) or None."""
    if not msg or not isinstance(msg, str):
        return None
    m = _CONTRACT_RE.search(msg)
    if not m:
        return None
    return {
        "intermediate": int(m.group(1)),
        "advanced": int(m.group(2)),
        "top": int(m.group(3)),
        "source": m.group(4),
        "problem_id": int(m.group(5)),
    }


def _emit_block(reason):
    """Write a JSON block decision to stdout."""
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.stdout.flush()


def _append_audit(work_folder, line):
    if not work_folder:
        return
    try:
        os.makedirs(work_folder, exist_ok=True)
        audit_path = os.path.join(work_folder, "audit.log")
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        log_err(f"failed to append audit log: {e}")


def main():
    try:
        raw = sys.stdin.read()
    except Exception as e:
        log_err(f"failed to read stdin: {e}")
        return 0

    if not raw.strip():
        return 0

    try:
        payload = json.loads(raw)
    except Exception as e:
        log_err(f"payload not valid JSON: {e}")
        return 0

    if not isinstance(payload, dict):
        return 0

    last_msg = payload.get("last_assistant_message") or ""
    parsed = _parse_contract(last_msg)
    if not parsed:
        log_err("could not parse contract line from last_assistant_message")
        return 0

    list_name, work_folder = _load_active_list()
    if not list_name:
        log_err("could not determine list-name from .active-list.yaml")
        return 0

    # Resolve write_tsv.py relative to this hook's location: hooks/ -> .claude/ -> scripts/
    here = os.path.dirname(os.path.abspath(__file__))
    claude_dir = os.path.dirname(here)
    write_tsv = os.path.join(claude_dir, "scripts", "write_tsv.py")

    cmd = [
        sys.executable,
        write_tsv,
        "--list-name",
        list_name,
        "--problem-id",
        str(parsed["problem_id"]),
        "--intermediate",
        str(parsed["intermediate"]),
        "--advanced",
        str(parsed["advanced"]),
        "--top",
        str(parsed["top"]),
        "--source",
        parsed["source"],
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        reason = f"write_tsv invocation failed: {e}"
        log_err(reason)
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _append_audit(
            work_folder,
            f"{ts}\tWRITE_TSV_ERROR\tp{parsed['problem_id']}\t{reason}\n",
        )
        _emit_block(f"write_tsv failed: {reason}")
        return 0

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip().replace("\n", " ")
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        _append_audit(
            work_folder,
            f"{ts}\tWRITE_TSV_ERROR\tp{parsed['problem_id']}\t{stderr}\n",
        )
        _emit_block(f"write_tsv failed: {stderr}")
        return 0

    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as e:
        log_err(f"unexpected error: {e}")
        rc = 0
    sys.exit(rc or 0)
