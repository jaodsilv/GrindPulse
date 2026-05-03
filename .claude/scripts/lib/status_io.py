"""Helpers for reading/writing the per-path / per-phase status.yaml.

All mutating helpers:
  - acquire an exclusive file lock on `{work_folder}/status.yaml`
  - read-modify-write atomically (write to `.tmp`, then `os.replace`)

Schema (top-level keys):

    phase0-fetcher:
      state: waiting | ongoing | complete
      waiting: [{name, id, problem-folder}, ...]
      ongoing: [{name, id, problem-folder}, ...]

    standard-solutions-path:
      phase1-producer:        {waiting: [...], ongoing: [...]}
      phase2-explanator:      {waiting: [...], ongoing: [...]}
      phase3-time-estimator:  {waiting: [...], ongoing: [...]}
      phase4-criticizer:      {waiting: [...], ongoing: [...]}

    ai-solutions-path:                # only if ai_path flag is on
      phase1-producer:        {waiting: [...], ongoing: [...]}
      phase3-time-estimator:  {waiting: [...], ongoing: [...]}
      phase4-criticizer:      {waiting: [...], ongoing: [...]}

    community-times-path:             # only if community_path flag is on
      phase1-producer:        {waiting: [...], ongoing: [...]}
      phase4-criticizer:      {waiting: [...], ongoing: [...]}

    phase5-time-selection:
      waiting: [...]
      ongoing: [...]

    complete: [{name, id, problem-folder, times: {intermediate, advanced, top}}, ...]
"""

from __future__ import annotations

import os
import sys
from typing import Any

import yaml

from .file_lock import file_lock

STATUS_FILENAME = "status.yaml"


def _status_path(work_folder: str) -> str:
    return os.path.join(work_folder, STATUS_FILENAME)


def _atomic_write_yaml(path: str, data: dict) -> None:
    """Write `data` as YAML to `path` via a sibling .tmp + os.replace."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    os.replace(tmp, path)


def _empty_phase() -> dict:
    return {"waiting": [], "ongoing": []}


def _build_skeleton(problems: list[dict], flags: dict) -> dict:
    """Build the new top-level schema. `problems` items must be dicts with
    `name`, `id`, `problem-folder` keys (folder may be empty before fetch).
    """
    waiting_entries = [
        {
            "name": p["name"],
            "id": p["id"],
            "problem-folder": p.get("problem-folder", ""),
        }
        for p in problems
    ]

    data: dict[str, Any] = {
        "phase0-fetcher": {
            "state": "waiting",
            "waiting": waiting_entries,
            "ongoing": [],
        },
        "standard-solutions-path": {
            "phase1-producer": _empty_phase(),
            "phase2-explanator": _empty_phase(),
            "phase3-time-estimator": _empty_phase(),
            "phase4-criticizer": _empty_phase(),
        },
    }

    if flags.get("ai_path"):
        data["ai-solutions-path"] = {
            "phase1-producer": _empty_phase(),
            "phase3-time-estimator": _empty_phase(),
            "phase4-criticizer": _empty_phase(),
        }

    if flags.get("community_path"):
        data["community-times-path"] = {
            "phase1-producer": _empty_phase(),
            "phase4-criticizer": _empty_phase(),
        }

    data["phase5-time-selection"] = _empty_phase()
    data["complete"] = []

    return data


def read_status(work_folder: str) -> dict:
    """Return the parsed status.yaml dict (empty dict if file missing/empty)."""
    path = _status_path(work_folder)
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
    except OSError as e:
        # Permission/IO error other than missing-file: log so the caller can
        # see why the status appears reset. Still return {} to keep the
        # documented contract (best-effort UX mirror).
        print(
            f"warning: could not read {path}: {e}; treating as empty status",
            file=sys.stderr,
        )
        return {}


def init_status(work_folder: str, problems: list[dict], flags: dict) -> None:
    """Write the initial top-level skeleton to `{work_folder}/status.yaml`.

    Args:
        work_folder: directory where status.yaml lives
        problems: list of dicts with keys `name`, `id`, optional `problem-folder`
        flags: dict that may contain `ai_path` and/or `community_path` truthy
    """
    os.makedirs(work_folder, exist_ok=True)
    path = _status_path(work_folder)
    with file_lock(path):
        data = _build_skeleton(problems, flags)
        _atomic_write_yaml(path, data)


def _resolve_phase_node(data: dict, phase: str) -> dict:
    """Return the dict that owns the `waiting`/`ongoing` lists for `phase`.

    `phase` may be a top-level key (e.g. "phase0-fetcher",
    "phase4-time-selection") or a "path/phase" form like
    "standard-solutions-path/phase2-time-estimator".
    """
    if "/" in phase:
        path_key, _, phase_key = phase.partition("/")
        if path_key not in data or not isinstance(data[path_key], dict):
            raise KeyError(f"path bucket missing in status.yaml: {path_key}")
        bucket = data[path_key]
        if phase_key not in bucket or not isinstance(bucket[phase_key], dict):
            raise KeyError(f"phase missing under {path_key}: {phase_key}")
        return bucket[phase_key]

    if phase not in data or not isinstance(data[phase], dict):
        raise KeyError(f"phase missing in status.yaml: {phase}")
    return data[phase]


def _make_entry(name: str, problem_id: Any, problem_folder: str) -> dict:
    return {"name": name, "id": problem_id, "problem-folder": problem_folder}


def _remove_entry_by_name(entries: list, name: str) -> None:
    for i, e in enumerate(list(entries)):
        if isinstance(e, dict) and e.get("name") == name:
            entries.pop(i)
            return


def _has_entry_by_name(entries: list, name: str) -> bool:
    return any(isinstance(e, dict) and e.get("name") == name for e in entries)


def move_to_phase(
    work_folder: str,
    name: str,
    problem_id: Any,
    problem_folder: str,
    from_phase: str | None,
    to_phase: str | None,
) -> None:
    """Move a problem entry between waiting/ongoing lists across phases.

    Either `from_phase` or `to_phase` may be None (e.g. initial seeding into a
    waiting list, or marking the source phase done with no destination).

    Phase keys are either top-level ("phase0-fetcher", "phase4-time-selection")
    or "<path>/<phase>" (e.g. "standard-solutions-path/phase1-producer").

    By convention this helper:
      - removes the entry from BOTH `waiting` and `ongoing` of `from_phase`
      - appends a fresh entry to the `waiting` list of `to_phase`
        (a worker promotes waiting->ongoing separately)
    """
    path = _status_path(work_folder)
    with file_lock(path):
        data = read_status(work_folder)
        if not data:
            raise RuntimeError(f"status.yaml missing or empty at {path}")

        if from_phase is not None:
            src = _resolve_phase_node(data, from_phase)
            _remove_entry_by_name(src.get("waiting", []), name)
            _remove_entry_by_name(src.get("ongoing", []), name)

        if to_phase is not None:
            dst = _resolve_phase_node(data, to_phase)
            dst.setdefault("waiting", [])
            dst.setdefault("ongoing", [])
            if not _has_entry_by_name(dst["waiting"], name) and not _has_entry_by_name(
                dst["ongoing"], name
            ):
                dst["waiting"].append(_make_entry(name, problem_id, problem_folder))

        _atomic_write_yaml(path, data)


def claim_work_item(work_folder: str, phase: str, name: str) -> None:
    """Move `name` from phase.waiting → phase.ongoing under file lock. No-op if not found or already ongoing."""
    path = _status_path(work_folder)
    with file_lock(path):
        data = read_status(work_folder)
        if not data:
            return
        try:
            node = _resolve_phase_node(data, phase)
        except KeyError as e:
            print(
                f"warning: claim_work_item: phase {phase!r} not found in "
                f"status.yaml ({e}); leaving {name!r} unclaimed",
                file=sys.stderr,
            )
            return
        waiting = node.setdefault("waiting", [])
        ongoing = node.setdefault("ongoing", [])
        if _has_entry_by_name(ongoing, name):
            return
        entry = next((e for e in waiting if isinstance(e, dict) and e.get("name") == name), None)
        if entry is None:
            return
        waiting.remove(entry)
        ongoing.append(entry)
        _atomic_write_yaml(path, data)


def release_work_item(
    work_folder: str,
    from_phase: str | None,
    to_phase: str | None,
    name: str,
) -> None:
    """Move `name` from from_phase.ongoing → to_phase.waiting under file lock."""
    path = _status_path(work_folder)
    with file_lock(path):
        data = read_status(work_folder)
        if not data:
            return
        entry = None
        if from_phase is not None:
            try:
                src = _resolve_phase_node(data, from_phase)
            except KeyError as e:
                print(
                    f"warning: release_work_item: source phase {from_phase!r} "
                    f"not found in status.yaml ({e}); leaving {name!r} in place",
                    file=sys.stderr,
                )
                return
            ongoing = src.get("ongoing", [])
            for e in list(ongoing):
                if isinstance(e, dict) and e.get("name") == name:
                    entry = e
                    ongoing.remove(e)
                    break
        if to_phase is not None and entry is not None:
            try:
                dst = _resolve_phase_node(data, to_phase)
            except KeyError as e:
                # The destination phase may legitimately not exist when an
                # optional path (ai/community) is disabled. Log so a typo in
                # the caller's `to_phase` is still visible.
                print(
                    f"warning: release_work_item: destination phase {to_phase!r} "
                    f"not found in status.yaml ({e}); leaving {name!r} unfiled",
                    file=sys.stderr,
                )
            else:
                dst.setdefault("waiting", [])
                if not _has_entry_by_name(dst["waiting"], name):
                    dst["waiting"].append(entry)
        _atomic_write_yaml(path, data)


def set_fetcher_state(work_folder: str, state: str) -> None:
    """Set phase0-fetcher.state under file lock."""
    path = _status_path(work_folder)
    with file_lock(path):
        data = read_status(work_folder)
        if not data or "phase0-fetcher" not in data:
            return
        data["phase0-fetcher"]["state"] = state
        _atomic_write_yaml(path, data)


def mark_complete(
    work_folder: str,
    name: str,
    problem_id: Any,
    times: dict,
) -> None:
    """Move a problem entry from `phase4-time-selection.ongoing` (or any
    ongoing list it happens to live in) into `complete[]` with a `times`
    dict of {intermediate, advanced, top}.

    `times` must be a dict containing integer values for the three keys.
    Missing fields default to 0.
    """
    path = _status_path(work_folder)
    intermediate = int(times.get("intermediate", 0))
    advanced = int(times.get("advanced", 0))
    top = int(times.get("top", 0))

    with file_lock(path):
        data = read_status(work_folder)
        if not data:
            raise RuntimeError(f"status.yaml missing or empty at {path}")

        problem_folder = ""

        # Sweep every phase node we know about and remove the entry; capture
        # `problem-folder` from whichever entry we encounter first.
        def _sweep(node: dict) -> None:
            nonlocal problem_folder
            for bucket_key in ("waiting", "ongoing"):
                bucket = node.get(bucket_key)
                if not isinstance(bucket, list):
                    continue
                for e in bucket:
                    if isinstance(e, dict) and e.get("name") == name:
                        if not problem_folder:
                            problem_folder = e.get("problem-folder", "") or ""
                        break
                _remove_entry_by_name(bucket, name)

        for top_key, value in list(data.items()):
            if top_key == "complete":
                continue
            if not isinstance(value, dict):
                continue
            # phase0-fetcher / phase4-time-selection have waiting/ongoing directly
            if "waiting" in value or "ongoing" in value:
                _sweep(value)
                continue
            # path buckets have nested phase dicts
            for _phase_key, phase_node in value.items():
                if isinstance(phase_node, dict):
                    _sweep(phase_node)

        complete = data.setdefault("complete", [])
        if not _has_entry_by_name(complete, name):
            complete.append(
                {
                    "name": name,
                    "id": problem_id,
                    "problem-folder": problem_folder,
                    "times": {
                        "intermediate": intermediate,
                        "advanced": advanced,
                        "top": top,
                    },
                }
            )

        _atomic_write_yaml(path, data)
