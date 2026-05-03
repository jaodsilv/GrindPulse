#!/usr/bin/env python3
"""SubagentStop hook: advances status.yaml phase state after each pipeline worker completes.

Routing (standard path vs AI path vs community path):
  solutions-parser        → standard phase1-producer → standard phase2-explanator
  coding-challenge-solver → ai phase1-producer       → ai phase3-time-estimator  (skips phase2)
  community-time-finder   → community phase1-producer → community phase4-criticizer (skips phases 2+3)
  code-explanator         → standard phase2-explanator → standard phase3-time-estimator
  solution-analyzer (ai)  → ai phase3-time-estimator  → ai phase4-criticizer
  solution-analyzer (std) → standard phase3-time-estimator → standard phase4-criticizer
  justification-criticizer → appropriate phase4-criticizer → phase5-time-selection

Safe to run for ALL SubagentStop events — exits 0 silently for unrecognized agents.
"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.normpath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from lib.active_list import load_pair as _load_active_list  # noqa: E402


def log_err(msg):
    sys.stderr.write(f"[subagent_stop_state_advance] {msg}\n")


# Recognized worker agent-type substrings, in priority order. Order matters because
# some agent names may contain overlapping substrings; we check the most specific first.
_RECOGNIZED_WORKERS = (
    "solutions-parser",
    "coding-challenge-solver",
    "community-time-finder",
    "code-explanator",
    "solution-analyzer",
    "justification-criticizer",
    "time-selection",
)


def _detect_worker(payload):
    """Return the worker-type string if this SubagentStop is for a recognized
    pipeline worker, else None.
    """
    for key in ("agent_type", "subagent_type", "name"):
        val = payload.get(key)
        if not isinstance(val, str):
            continue
        for worker in _RECOGNIZED_WORKERS:
            if worker in val:
                return worker
    return None


def _iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


_PROBLEM_ID_RE = re.compile(r"<problem-id>\s*(\d+)\s*</problem-id>")
_SOURCE_RE = re.compile(r"<source>\s*([^<\s]+)\s*</source>")


def _scan_transcript(transcript_path):
    """Scan the transcript JSONL file for <problem-id>N</problem-id> and
    <source>S</source> tags. Returns (problem_id, source) or (None, None).
    """
    if not transcript_path or not os.path.isfile(transcript_path):
        return None, None
    problem_id = None
    source = None
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    # Transcripts are JSONL; non-JSON lines (banners, blanks)
                    # are expected and skipped silently to avoid spamming
                    # stderr per pipeline run. The narrowed exception ensures
                    # only true parse errors are swallowed.
                    continue
                for s in _iter_strings(rec):
                    if problem_id is None:
                        m = _PROBLEM_ID_RE.search(s)
                        if m:
                            problem_id = m.group(1).strip()
                    if source is None:
                        m = _SOURCE_RE.search(s)
                        if m:
                            source = m.group(1).strip()
                    if problem_id is not None and source is not None:
                        return problem_id, source
    except Exception as e:
        log_err(f"failed to scan transcript {transcript_path}: {e}")
    return problem_id, source


def _read_problem_name(work_folder, problem_id):
    """Read {work_folder}/p{problem_id}/metadata.yaml and return problem-name, or None."""
    meta_path = os.path.join(work_folder, f"p{problem_id}", "metadata.yaml")
    if not os.path.isfile(meta_path):
        log_err(f"metadata.yaml not found at {meta_path}")
        return None
    try:
        import yaml
    except ImportError:
        log_err("PyYAML not installed; cannot read metadata.yaml")
        return None
    try:
        with open(meta_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        log_err(f"failed to read {meta_path}: {e}")
        return None
    if not isinstance(data, dict):
        return None
    name = data.get("problem-name")
    if not isinstance(name, str) or not name.strip():
        return None
    return name.strip()


def _route(worker, source):
    """Return (from_phase, to_phase) for a recognized worker + optional source.

    `source` is the value parsed from <source>...</source> in the transcript;
    may be None for workers where source is not relevant.
    """
    src = (source or "").strip().lower()

    if worker == "solutions-parser":
        return (
            "standard-solutions-path/phase1-producer",
            "standard-solutions-path/phase2-explanator",
        )

    if worker == "coding-challenge-solver":
        return (
            "ai-solutions-path/phase1-producer",
            "ai-solutions-path/phase3-time-estimator",
        )

    if worker == "community-time-finder":
        return (
            "community-times-path/phase1-producer",
            "community-times-path/phase4-criticizer",
        )

    if worker == "code-explanator":
        return (
            "standard-solutions-path/phase2-explanator",
            "standard-solutions-path/phase3-time-estimator",
        )

    if worker == "solution-analyzer":
        if src == "ai":
            return (
                "ai-solutions-path/phase3-time-estimator",
                "ai-solutions-path/phase4-criticizer",
            )
        # std or std-N (or any non-ai value) → standard path
        return (
            "standard-solutions-path/phase3-time-estimator",
            "standard-solutions-path/phase4-criticizer",
        )

    if worker == "justification-criticizer":
        if src.startswith("community"):
            return (
                "community-times-path/phase4-criticizer",
                "phase5-time-selection",
            )
        if src == "ai":
            return (
                "ai-solutions-path/phase4-criticizer",
                "phase5-time-selection",
            )
        # std or std-N (or any non-ai/non-community value) → standard path
        return (
            "standard-solutions-path/phase4-criticizer",
            "phase5-time-selection",
        )

    if worker == "time-selection":
        return ("phase5-time-selection", None)

    return None, None


def _atomic_decrement_counter(work_folder):
    """Atomically decrement the in-flight counter under .dispatch.lock.

    Uses lib.file_lock to coordinate with concurrent stop hooks. If the counter
    file is missing or malformed, logs clearly and clamps to 0 (never below).
    Returns True iff a decrement was successfully written, False on any failure.
    """
    try:
        from lib.dispatch_state import counter_path, write_counter
        from lib.file_lock import file_lock
    except Exception as e:
        log_err(f"failed to import counter helpers: {e}")
        return False

    cpath = counter_path(work_folder)
    try:
        with file_lock(os.path.join(work_folder, ".dispatch.lock")):
            current = 0
            if os.path.isfile(cpath):
                try:
                    current = int(cpath.read_text().strip())
                except Exception as e:
                    log_err(
                        f"in-flight counter at {cpath} is malformed ({e!r}); "
                        f"clamping to 0 before decrement"
                    )
                    current = 0
            if current <= 0:
                log_err(
                    f"in-flight counter at {cpath} is {current}; "
                    f"clamping to 0 (possible drift or double-stop)"
                )
                write_counter(work_folder, 0)
            else:
                write_counter(work_folder, current - 1)
    except Exception as e:
        log_err(f"failed to decrement in-flight counter: {e}")
        return False
    return True


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

    worker = _detect_worker(payload)
    if worker is None:
        return 0

    # From this point on, this stop event corresponds to an in-flight worker that
    # agent_dispatch previously incremented for. We MUST decrement exactly once,
    # regardless of whether transcript scanning, metadata loading, routing, or
    # status_io updates succeed. Use try/finally with a guard so we never
    # double-decrement if an inner step also tries.
    decremented = False
    try:
        transcript_path = payload.get("agent_transcript_path") or payload.get("transcript_path")
        problem_id, source = _scan_transcript(transcript_path)
        if problem_id is None:
            log_err(f"could not find <problem-id> in transcript for worker {worker!r}")
            return 0

        _, work_folder = _load_active_list()
        if not work_folder:
            log_err("could not determine work-folder from .active-list.yaml")
            return 0

        if _atomic_decrement_counter(work_folder):
            decremented = True

        problem_name = _read_problem_name(work_folder, problem_id)
        if not problem_name:
            log_err(f"could not read problem-name from metadata.yaml for p{problem_id}")
            return 0

        from_phase, to_phase = _route(worker, source)
        if from_phase is None:
            log_err(f"no routing for worker={worker!r} source={source!r}")
            return 0
        if to_phase is None:
            return 0

        try:
            from lib import status_io  # type: ignore[import-not-found]
        except Exception as e:
            log_err(f"failed to import status_io: {e}")
            return 0

        try:
            status_io.release_work_item(work_folder, from_phase, to_phase, problem_name)
        except Exception as e:
            log_err(
                f"release_work_item failed (worker={worker} source={source} "
                f"name={problem_name!r} from={from_phase} to={to_phase}): {e}"
            )
            return 0

        return 0
    finally:
        if not decremented:
            # We failed before reaching the in-line decrement (e.g. transcript
            # scan or .active-list.yaml load failed). Best-effort: try to load
            # work_folder again and decrement, so a missing transcript tag does
            # not leak the in-flight slot until the dispatcher times out.
            try:
                _, wf = _load_active_list()
                if wf:
                    _atomic_decrement_counter(wf)
            except Exception as e:
                log_err(f"final-fallback counter decrement failed: {e}")


if __name__ == "__main__":
    try:
        rc = main()
    except Exception as e:
        log_err(f"unexpected error: {e}")
        rc = 0
    sys.exit(rc or 0)
