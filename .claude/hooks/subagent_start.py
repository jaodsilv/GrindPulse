#!/usr/bin/env python3
"""SubagentStart hook: deliver the work-item XML claimed by agent_dispatch.py to the
spawned worker subagent's session via additionalContext.

The PreToolUse(Agent) hook (agent_dispatch.py) claims a work item from the queue and
writes the rendered <work-item> XML to <work-folder>/pending-claims/<subagent_type>.yaml.
This hook pops the oldest entry from that FIFO and emits it as additionalContext for
the SubagentStart event so the worker's session sees it.
"""

import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.normpath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)


def _detect_subagent_type(payload):
    for key in ("subagent_type", "agent_type", "name"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _load_work_folder():
    path = os.path.join(".thoughts", "time-estimatives", ".active-list.yaml")
    try:
        import yaml
    except ImportError:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        return None
    if not isinstance(cfg, dict):
        return None
    list_name = cfg.get("list-name")
    work_folder = cfg.get("work-folder")
    if not work_folder and list_name:
        work_folder = os.path.join(".thoughts", "time-estimatives", list_name)
    return os.path.abspath(work_folder) if work_folder else None


def _pop_pending_claim(work_folder, subagent_type):
    try:
        import yaml
        from filelock import FileLock
    except ImportError:
        return None

    pending_path = os.path.join(work_folder, "pending-claims", f"{subagent_type}.yaml")
    lock_path = os.path.join(work_folder, ".dispatch.lock")

    try:
        with FileLock(lock_path):
            if not os.path.exists(pending_path):
                return None
            with open(pending_path, encoding="utf-8") as f:
                try:
                    items = yaml.safe_load(f) or []
                except Exception:
                    return None
            if not isinstance(items, list) or not items:
                return None
            head = items[0]
            rest = items[1:]
            with open(pending_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(rest, f, sort_keys=False)
            return head if isinstance(head, str) else None
    except Exception:
        return None


def emit_additional_context(context):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0

    subagent_type = _detect_subagent_type(payload)
    if subagent_type is None:
        return 0

    work_folder = _load_work_folder()
    if work_folder is None:
        return 0

    xml = _pop_pending_claim(work_folder, subagent_type)
    if xml:
        emit_additional_context(xml)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except Exception:
        sys.exit(0)
