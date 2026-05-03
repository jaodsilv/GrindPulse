"""Helpers for reading `.thoughts/time-estimatives/.active-list.yaml`.

This is the single source of truth for the small set of pipeline scripts and
hooks that need to discover the active run's `list-name` / `work-folder`
(plus a handful of optional flags such as `ai-path`, `community-path`,
`parallelism`, `list-path`, `fresh`).

The file is *written* in exactly one place (`process_list_hook.py`); every
other consumer is expected to *read* it via the helpers here.

Two shapes are exposed because callers want either:
  - the full config dict (e.g. fetch_problem.py needs `list-path`,
    agent_dispatch.py needs `ai-path` / `community-path` / `parallelism`)
  - just the (`list-name`, `work-folder`) pair (the SubagentStop hooks).

Behavior:
  - Returns None / (None, None) on missing file, missing PyYAML, YAML parse
    failure, or non-dict content.
  - Logs a single line to stderr on each failure mode so callers can be quiet
    pass-throughs.

Note: `fetch_loop.py` deliberately hand-parses this file without depending on
PyYAML and so does NOT use this module — see its docstring for rationale.
"""

from __future__ import annotations

import os
import sys

ACTIVE_LIST_PATH = os.path.join(".thoughts", "time-estimatives", ".active-list.yaml")


def _log_err(msg: str) -> None:
    sys.stderr.write(f"[lib.active_list] {msg}\n")


def load() -> dict | None:
    """Return the parsed `.active-list.yaml` dict, or None on any failure.

    Failure modes (each logs once to stderr and returns None):
      - PyYAML not installed
      - file missing or unreadable
      - YAML parse error
      - top-level value is not a dict
    """
    try:
        import yaml
    except ImportError as e:
        _log_err(f"PyYAML not installed; cannot read {ACTIVE_LIST_PATH}: {e}")
        return None
    try:
        with open(ACTIVE_LIST_PATH, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except OSError as e:
        _log_err(f"failed to read {ACTIVE_LIST_PATH}: {e}")
        return None
    except yaml.YAMLError as e:
        _log_err(f"YAML parse error in {ACTIVE_LIST_PATH}: {e}")
        return None
    if cfg is None:
        return {}
    if not isinstance(cfg, dict):
        _log_err(f"{ACTIVE_LIST_PATH} did not contain a top-level mapping")
        return None
    return cfg


def load_pair() -> tuple[str | None, str | None]:
    """Return (list_name, work_folder) from `.active-list.yaml`.

    Returns (None, None) on failure (see `load`) or when neither field is
    available. If `work-folder` is absent but `list-name` is set, the
    canonical default `.thoughts/time-estimatives/<list-name>` is returned.
    """
    cfg = load()
    if not cfg:
        return None, None
    list_name = cfg.get("list-name") or cfg.get("name")
    work_folder = cfg.get("work-folder")
    if not work_folder and list_name:
        work_folder = os.path.join(".thoughts", "time-estimatives", list_name)
    return list_name, work_folder
