#!/usr/bin/env python3
"""PreToolUse(Agent) hook: gates dispatcher subagents and claims work items for worker subagents."""

import json
import os
import re
import subprocess
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.normpath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
try:
    from lib import status_io as _status_io
except ImportError:
    _status_io = None

try:
    from lib.dispatch_state import read_counter, write_counter
except ImportError:
    from pathlib import Path as _Path

    def read_counter(work_folder):
        p = _Path(work_folder) / "in-flight.txt"
        return int(p.read_text().strip()) if p.exists() else 0

    def write_counter(work_folder, n):
        (_Path(work_folder) / "in-flight.txt").write_text(str(max(0, n)))


def write_pending_claim(work_folder, subagent_type, xml):
    """Append a work-item XML string to the per-subagent_type FIFO under .dispatch.lock.

    Caller must already hold .dispatch.lock.
    """
    try:
        import yaml
    except ImportError:
        raise

    pending_dir = os.path.join(work_folder, "pending-claims")
    os.makedirs(pending_dir, exist_ok=True)
    pending_path = os.path.join(pending_dir, f"{subagent_type}.yaml")

    existing = []
    if os.path.exists(pending_path):
        with open(pending_path, encoding="utf-8") as f:
            try:
                existing = yaml.safe_load(f) or []
            except Exception:
                existing = []
        if not isinstance(existing, list):
            existing = []
    existing.append(xml)
    with open(pending_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(existing, f, sort_keys=False)


DISPATCHER_SUBAGENTS = {
    "phase-1-produce-dispatcher",
    "phase-2-explain-dispatcher",
    "phase-3-analyze-dispatcher",
    "phase-4-critique-dispatcher",
    "phase-5-select-dispatcher",
}

WORKER_QUEUE_MAP = {
    "solutions-parser": "parse.yaml",
    "coding-challenge-solver-easy": "solve-easy.yaml",
    "coding-challenge-solver-medium": "solve-medium.yaml",
    "coding-challenge-solver-hard": "solve-hard.yaml",
    "community-time-finder": "community.yaml",
    "code-explanator": "explain.yaml",
    "solution-analyzer-easy": "analyze-easy.yaml",
    "solution-analyzer-medium": "analyze-medium.yaml",
    "solution-analyzer-hard": "analyze-hard.yaml",
    "justification-criticizer-easy": "critique-easy.yaml",
    "justification-criticizer-medium": "critique-medium.yaml",
    "justification-criticizer-hard": "critique-hard.yaml",
    "time-selection-tiebreak": "tiebreak.yaml",
}


def _normalize_worker_type(subagent_type):
    """Strip tier suffix from a worker subagent_type to get its base name.

    Returns the bare worker name used by phase routing (`coding-challenge-solver`,
    `solution-analyzer`, `justification-criticizer`, `time-selection`). Workers
    without a tier suffix (`solutions-parser`, `community-time-finder`,
    `code-explanator`) are returned unchanged.
    """
    if not isinstance(subagent_type, str):
        return subagent_type
    for suffix in ("-easy", "-medium", "-hard", "-tiebreak"):
        if subagent_type.endswith(suffix):
            return subagent_type[: -len(suffix)]
    return subagent_type


def emit_deny(reason):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


def emit_allow_with_context(context):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


def emit_implicit_allow():
    # No output, exit 0 → harness treats as implicit allow.
    return


def parse_flag(prompt, flag):
    """Extract a `--flag VALUE` argument from the prompt string. Returns value or None."""
    if not prompt:
        return None
    pattern = re.compile(r"--" + re.escape(flag) + r"(?:\s+|=)([^\s]+)")
    m = pattern.search(prompt)
    if m:
        return m.group(1)
    return None


def _load_active_list():
    """Return config dict from .active-list.yaml, or None on failure."""
    path = os.path.join(".thoughts", "time-estimatives", ".active-list.yaml")
    try:
        import yaml
    except ImportError:
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return None


def run_list_work(args):
    """Run `python .claude/scripts/list_work.py <args>` and return (stdout, stderr, returncode)."""
    cmd = ["python", ".claude/scripts/list_work.py"] + args
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    return proc.stdout, proc.stderr, proc.returncode


def yaml_is_empty(text):
    """Return True if YAML output represents an empty list (or no items)."""
    try:
        import yaml
    except ImportError:
        # Fallback: treat empty/whitespace or "[]" as empty
        stripped = (text or "").strip()
        if not stripped:
            return True
        if stripped in ("[]", "null", "~"):
            return True
        return False

    try:
        data = yaml.safe_load(text)
    except Exception as e:
        raise RuntimeError(f"YAML parse error: {e}") from e

    if data is None:
        return True
    if isinstance(data, list):
        return len(data) == 0
    if isinstance(data, dict):
        return len(data) == 0
    return False


def yaml_item_count(text):
    """Return the number of items in a YAML list output, or 0 if empty/null."""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML package not installed") from None

    try:
        data = yaml.safe_load(text)
    except Exception as e:
        raise RuntimeError(f"YAML parse error: {e}") from e

    if data is None:
        return 0
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        return len(data)
    return 0


def materialize_queue(verb, list_name, queue_path, extra_args=None):
    """Run list_work.py <verb> for list_name, write YAML to queue_path, return item count.

    Raises RuntimeError on failure.
    """
    args = [verb, "--list-name", list_name]
    if extra_args:
        args.extend(extra_args)
    stdout, stderr, rc = run_list_work(args)
    if rc != 0:
        raise RuntimeError(stderr.strip() or f"list_work.py {verb} exited {rc}")

    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, "w", encoding="utf-8") as f:
        f.write(stdout)

    return yaml_item_count(stdout)


def _seed_phase_status(work_folder, queue_path, phase_key):
    """Best-effort: seed status.yaml waiting list from materialized queue."""
    if _status_io is None:
        return
    try:
        import yaml

        with open(queue_path, encoding="utf-8") as f:
            items = yaml.safe_load(f) or []
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            problem_id = item.get("problem-id")
            if problem_id is None:
                continue
            problem_folder = item.get("problem-folder") or f"p{problem_id}"
            pdir = os.path.join(work_folder, problem_folder)
            meta_path = os.path.join(pdir, "metadata.yaml")
            try:
                with open(meta_path, encoding="utf-8") as f:
                    meta = yaml.safe_load(f) or {}
                name = meta.get("problem-name") or meta.get("name") or f"p{problem_id}"
            except Exception:
                name = f"p{problem_id}"
            try:
                _status_io.move_to_phase(
                    work_folder,
                    name,
                    problem_id,
                    problem_folder,
                    from_phase=None,
                    to_phase=phase_key,
                )
            except Exception:
                pass
    except Exception:
        pass


def handle_dispatcher(subagent_type):
    cfg = _load_active_list()
    if not cfg:
        emit_deny("cannot read .active-list.yaml; start a run with /process-list first")
        return

    list_name = cfg.get("list-name")
    if not list_name:
        emit_deny(".active-list.yaml missing list-name")
        return

    work_folder = cfg.get("work-folder") or f".thoughts/time-estimatives/{list_name}"
    work_folder_abs = os.path.abspath(work_folder)
    root = work_folder_abs
    if not os.path.isdir(root):
        emit_deny(f"work folder not found: {root}")
        return

    queues_dir = os.path.join(work_folder_abs, "queues")
    has_ai = bool(cfg.get("ai-path"))
    has_community = bool(cfg.get("community-path"))

    if subagent_type == "phase-1-produce-dispatcher":
        if not os.path.exists(os.path.join(root, ".fetch-complete")):
            emit_deny("phase-1: .fetch-complete missing; run phase 0 first")
            return

        materializations: list = [
            ("parse-needed", "parse.yaml", [], "standard-solutions-path/phase1-producer")
        ]
        if has_ai:
            materializations.append(
                ("solve-needed", "solve.yaml", ["--ai-path"], "ai-solutions-path/phase1-producer")
            )
        if has_community:
            materializations.append(
                (
                    "community-needed",
                    "community.yaml",
                    ["--community-path"],
                    "community-times-path/phase1-producer",
                )
            )

        total = 0
        queue_paths = []
        for verb, fname, extra, phase_key in materializations:
            qp = os.path.join(queues_dir, fname)
            try:
                count = materialize_queue(verb, list_name, qp, extra)
            except RuntimeError as e:
                emit_deny(str(e))
                return
            total += count
            queue_paths.append(qp)
            if count > 0:
                _seed_phase_status(work_folder_abs, qp, phase_key)

        emit_implicit_allow()
        return

    if subagent_type == "phase-2-explain-dispatcher":
        qp = os.path.join(queues_dir, "explain.yaml")
        try:
            count = materialize_queue("explain-needed", list_name, qp)
        except RuntimeError as e:
            emit_deny(str(e))
            return

        if count > 0:
            _seed_phase_status(work_folder_abs, qp, "standard-solutions-path/phase2-explanator")
        emit_implicit_allow()
        return

    if subagent_type == "phase-3-analyze-dispatcher":
        extra = ["--ai-path"] if has_ai else None
        qp = os.path.join(queues_dir, "analyze.yaml")
        try:
            count = materialize_queue("analyze-needed", list_name, qp, extra)
        except RuntimeError as e:
            emit_deny(str(e))
            return

        if count > 0:
            try:
                import yaml

                with open(qp, encoding="utf-8") as f:
                    items = yaml.safe_load(f) or []
                for item in items if isinstance(items, list) else []:
                    source = item.get("source", "") if isinstance(item, dict) else ""
                    phase_key = (
                        "ai-solutions-path/phase3-time-estimator"
                        if source == "ai"
                        else "standard-solutions-path/phase3-time-estimator"
                    )
                    problem_id = item.get("problem-id") if isinstance(item, dict) else None
                    if problem_id is None:
                        continue
                    problem_folder = item.get("problem-folder") or f"p{problem_id}"
                    pdir = os.path.join(work_folder_abs, problem_folder)
                    meta_path = os.path.join(pdir, "metadata.yaml")
                    try:
                        with open(meta_path, encoding="utf-8") as f2:
                            meta = yaml.safe_load(f2) or {}
                        name = meta.get("problem-name") or f"p{problem_id}"
                    except Exception:
                        name = f"p{problem_id}"
                    if _status_io:
                        try:
                            _status_io.move_to_phase(
                                work_folder_abs,
                                name,
                                problem_id,
                                problem_folder,
                                from_phase=None,
                                to_phase=phase_key,
                            )
                        except Exception:
                            pass
            except Exception:
                pass

        emit_implicit_allow()
        return

    if subagent_type == "phase-4-critique-dispatcher":
        extra = []
        if has_ai:
            extra.append("--ai-path")
        if has_community:
            extra.append("--community-path")
        qp = os.path.join(queues_dir, "critique.yaml")
        try:
            count = materialize_queue("critique-needed", list_name, qp, extra or None)
        except RuntimeError as e:
            emit_deny(str(e))
            return

        if count > 0:
            try:
                import yaml

                with open(qp, encoding="utf-8") as f:
                    items = yaml.safe_load(f) or []
                for item in items if isinstance(items, list) else []:
                    if not isinstance(item, dict):
                        continue
                    source = item.get("source", "")
                    if source.startswith("community"):
                        phase_key = "community-times-path/phase4-criticizer"
                    elif source == "ai":
                        phase_key = "ai-solutions-path/phase4-criticizer"
                    else:
                        phase_key = "standard-solutions-path/phase4-criticizer"
                    problem_id = item.get("problem-id")
                    if problem_id is None:
                        continue
                    problem_folder = item.get("problem-folder") or f"p{problem_id}"
                    pdir = os.path.join(work_folder_abs, problem_folder)
                    meta_path = os.path.join(pdir, "metadata.yaml")
                    try:
                        with open(meta_path, encoding="utf-8") as f2:
                            meta = yaml.safe_load(f2) or {}
                        name = meta.get("problem-name") or f"p{problem_id}"
                    except Exception:
                        name = f"p{problem_id}"
                    if _status_io:
                        try:
                            _status_io.move_to_phase(
                                work_folder_abs,
                                name,
                                problem_id,
                                problem_folder,
                                from_phase=None,
                                to_phase=phase_key,
                            )
                        except Exception:
                            pass
            except Exception:
                pass

        emit_implicit_allow()
        return

    if subagent_type == "phase-5-select-dispatcher":
        extra = []
        if has_ai:
            extra.append("--ai-path")
        if has_community:
            extra.append("--community-path")
        qp = os.path.join(queues_dir, "select.yaml")
        try:
            count = materialize_queue("select-needed", list_name, qp, extra or None)
        except RuntimeError as e:
            emit_deny(str(e))
            return

        if count > 0:
            _seed_phase_status(work_folder_abs, qp, "phase5-time-selection")
        emit_implicit_allow()
        return


def handle_worker(subagent_type):
    queue_file = WORKER_QUEUE_MAP[subagent_type]

    cfg = _load_active_list()
    if not cfg:
        emit_deny("cannot read .active-list.yaml; start a run with /process-list first")
        return

    list_name = cfg.get("list-name")
    if not list_name:
        emit_deny(".active-list.yaml missing list-name")
        return

    work_folder = cfg.get("work-folder") or f".thoughts/time-estimatives/{list_name}"
    work_folder_abs = os.path.abspath(work_folder)
    parallelism = int(cfg.get("parallelism", 10))

    queue_path = os.path.join(work_folder_abs, "queues", queue_file)

    try:
        from filelock import FileLock
    except ImportError:
        emit_deny(
            "filelock package not installed; run `pip install -r .claude/scripts/requirements.txt`"
        )
        return

    try:
        import yaml
    except ImportError:
        emit_deny("PyYAML package not installed")
        return

    lock = FileLock(os.path.join(work_folder_abs, ".dispatch.lock"))
    try:
        with lock:
            if not os.path.exists(queue_path):
                emit_deny("queue empty")
                return

            with open(queue_path, encoding="utf-8") as f:
                raw = f.read()

            try:
                data = yaml.safe_load(raw)
            except Exception as e:
                emit_deny(f"YAML parse error in {queue_path}: {e}")
                return

            if not data or not isinstance(data, list) or len(data) == 0:
                emit_deny("queue empty")
                return

            in_flight = read_counter(work_folder_abs)
            if in_flight >= parallelism:
                emit_deny(
                    "maximum in-flight subagents running; "
                    "wait for any agent to finish before spawning more"
                )
                return

            item = data[0]
            remaining = data[1:]

            with open(queue_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(remaining, f, sort_keys=False)
            write_counter(work_folder_abs, in_flight + 1)
    except Exception as e:
        emit_deny(f"queue claim failed: {e}")
        return

    if not isinstance(item, dict) or "problem-id" not in item:
        emit_deny(f"malformed work item in {queue_path}: {item!r}")
        return

    problem_id = item["problem-id"]
    problem_folder = item.get("problem-folder") or f"p{problem_id}"
    pdir = os.path.join(work_folder_abs, problem_folder)

    # Best-effort: advance status.yaml waiting→ongoing for this worker
    if _status_io:
        try:
            meta_path = os.path.join(pdir, "metadata.yaml")
            with open(meta_path, encoding="utf-8") as f:
                meta = yaml.safe_load(f) or {}
            problem_name = meta.get("problem-name") or f"p{problem_id}"
            source = item.get("source", "")
            worker_kind = _normalize_worker_type(subagent_type)
            if worker_kind == "solutions-parser":
                phase_key = "standard-solutions-path/phase1-producer"
            elif worker_kind == "coding-challenge-solver":
                phase_key = "ai-solutions-path/phase1-producer"
            elif worker_kind == "community-time-finder":
                phase_key = "community-times-path/phase1-producer"
            elif worker_kind == "code-explanator":
                phase_key = "standard-solutions-path/phase2-explanator"
            elif worker_kind == "solution-analyzer":
                phase_key = (
                    "ai-solutions-path/phase3-time-estimator"
                    if source == "ai"
                    else "standard-solutions-path/phase3-time-estimator"
                )
            elif worker_kind == "justification-criticizer":
                if source.startswith("community"):
                    phase_key = "community-times-path/phase4-criticizer"
                elif source == "ai":
                    phase_key = "ai-solutions-path/phase4-criticizer"
                else:
                    phase_key = "standard-solutions-path/phase4-criticizer"
            elif worker_kind == "time-selection":
                phase_key = "phase5-time-selection"
            else:
                phase_key = None
            if phase_key:
                _status_io.claim_work_item(work_folder_abs, phase_key, problem_name)
        except Exception:
            pass

    parts = ["<work-item>"]
    parts.append(f"  <list-name>{list_name}</list-name>")
    parts.append(f"  <problem-id>{problem_id}</problem-id>")
    if "source" in item:
        parts.append(f"  <source>{item['source']}</source>")
    if "pair-type" in item:
        parts.append(f"  <pair-type>{item['pair-type']}</pair-type>")

    worker_kind = _normalize_worker_type(subagent_type)
    if worker_kind in ("solution-analyzer", "justification-criticizer"):
        try:
            extra_lines = _build_path_context(worker_kind, item, list_name, work_folder_abs)
        except RuntimeError as e:
            emit_deny(str(e))
            return
        parts.extend(extra_lines)
    elif subagent_type == "time-selection-tiebreak":
        try:
            extra_lines = _build_tiebreak_context(item, list_name, work_folder_abs)
        except RuntimeError as e:
            emit_deny(str(e))
            return
        parts.extend(extra_lines)
    elif worker_kind == "community-time-finder":
        try:
            extra_lines = _build_community_context(item, list_name, work_folder_abs)
        except RuntimeError as e:
            emit_deny(str(e))
            return
        parts.extend(extra_lines)
    elif worker_kind == "coding-challenge-solver":
        parts.append(f"  <pdir>{pdir}</pdir>")
        parts.append(f"  <problem-md-path>{os.path.join(pdir, 'problem.md')}</problem-md-path>")

    parts.append("</work-item>")
    context = "\n".join(parts)

    try:
        with FileLock(os.path.join(work_folder_abs, ".dispatch.lock")):
            write_pending_claim(work_folder_abs, subagent_type, context)
    except Exception as e:
        emit_deny(f"failed to write pending claim: {e}")
        return
    emit_implicit_allow()


def _build_select_context(item, list_name, work_folder=None):
    """Resolve pdir, run select-discover, read metadata, and return XML lines for time-selection.

    Returns a list of indented XML element strings to splice into the <work-item> block.
    Raises RuntimeError on missing/malformed inputs.
    """
    if work_folder is None:
        work_folder = f".thoughts/time-estimatives/{list_name}"
    problem_folder = item.get("problem-folder") or f"p{item['problem-id']}"
    pdir = f"{work_folder}/{problem_folder}"

    hooks_dir = os.path.dirname(os.path.abspath(__file__))
    list_work_script = os.path.normpath(os.path.join(hooks_dir, "..", "scripts", "list_work.py"))

    try:
        proc = subprocess.run(
            ["python", list_work_script, "select-discover", "--pdir", pdir],
            capture_output=True,
            text=True,
        )
    except Exception as e:
        raise RuntimeError(f"failed to invoke list_work.py select-discover: {e}") from e

    if proc.returncode != 0:
        raise RuntimeError(
            (proc.stderr or "").strip() or f"list_work.py select-discover exited {proc.returncode}"
        )

    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML package not installed") from None

    try:
        sources = yaml.safe_load(proc.stdout) or []
    except Exception as e:
        raise RuntimeError(f"failed to parse select-discover output: {e}") from e

    if not isinstance(sources, list):
        raise RuntimeError(f"select-discover did not return a list: {sources!r}")

    metadata_path = os.path.join(pdir, "metadata.yaml")
    if not os.path.isfile(metadata_path):
        raise RuntimeError(
            f"metadata.yaml missing for problem-id {item['problem-id']}: {metadata_path}"
        )

    try:
        with open(metadata_path, encoding="utf-8") as f:
            metadata = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(f"failed to read {metadata_path}: {e}") from e

    problem_name = metadata.get("problem-name") or metadata.get("name") or ""
    difficulty = metadata.get("nominal-difficulty") or metadata.get("difficulty") or ""
    pattern = metadata.get("problem-pattern") or metadata.get("pattern") or ""

    lines = [
        f"  <problem-name>{problem_name}</problem-name>",
        f"  <difficulty>{difficulty}</difficulty>",
        f"  <pattern>{pattern}</pattern>",
    ]

    if not sources:
        lines.append("  <sources/>")
    else:
        lines.append("  <sources>")
        for src in sources:
            if not isinstance(src, dict):
                continue
            name = src.get("name", "")
            ev = src.get("eval", "")
            cr = src.get("critique", "")
            lines.append(f'    <source name="{name}" eval="{ev}" critique="{cr}"/>')
        lines.append("  </sources>")

    return lines


def _build_tiebreak_context(item, list_name, work_folder=None):
    """Resolve pdir, read metadata, and return XML lines for time-selection-tiebreak.

    Returns a list of indented XML element strings to splice into the <work-item>
    block: `<pdir>`, `<problem-name>`, `<difficulty>`, `<pattern>`, and one
    `<candidate-source>` per candidate listed in the queue entry.
    Raises RuntimeError on missing/malformed inputs.
    """
    if work_folder is None:
        work_folder = f".thoughts/time-estimatives/{list_name}"
    problem_folder = item.get("problem-folder") or f"p{item['problem-id']}"
    pdir = f"{work_folder}/{problem_folder}"

    metadata_path = os.path.join(pdir, "metadata.yaml")
    if not os.path.isfile(metadata_path):
        raise RuntimeError(
            f"metadata.yaml missing for problem-id {item['problem-id']}: {metadata_path}"
        )

    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML package not installed") from None

    try:
        with open(metadata_path, encoding="utf-8") as f:
            metadata = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(f"failed to read {metadata_path}: {e}") from e

    problem_name = metadata.get("problem-name", "")
    difficulty = metadata.get("nominal-difficulty") or metadata.get("difficulty") or ""
    pattern = metadata.get("problem-pattern") or metadata.get("pattern") or ""

    candidates = item.get("candidate-sources") or []
    if not isinstance(candidates, list) or not candidates:
        raise RuntimeError(
            f"tiebreak queue entry for p{item['problem-id']} missing candidate-sources list"
        )

    lines = [
        f"  <pdir>{pdir}</pdir>",
        f"  <problem-name>{problem_name}</problem-name>",
        f"  <difficulty>{difficulty}</difficulty>",
        f"  <pattern>{pattern}</pattern>",
    ]
    for cand in candidates:
        lines.append(f"  <candidate-source>{cand}</candidate-source>")
    return lines


def _build_community_context(item, list_name, work_folder=None):
    """Resolve pdir and read metadata for the community-time-finder.

    Returns a list of indented XML element strings to splice into the <work-item> block.
    Raises RuntimeError on missing/malformed inputs.
    """
    if work_folder is None:
        work_folder = f".thoughts/time-estimatives/{list_name}"
    problem_folder = item.get("problem-folder") or f"p{item['problem-id']}"
    pdir = f"{work_folder}/{problem_folder}"

    metadata_path = os.path.join(pdir, "metadata.yaml")
    if not os.path.isfile(metadata_path):
        raise RuntimeError(
            f"metadata.yaml missing for problem-id {item['problem-id']}: {metadata_path}"
        )

    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML package not installed") from None

    try:
        with open(metadata_path, encoding="utf-8") as f:
            metadata = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(f"failed to read {metadata_path}: {e}") from e

    problem_name = metadata.get("problem-name") or metadata.get("name") or ""
    difficulty = metadata.get("nominal-difficulty") or metadata.get("difficulty") or ""
    pattern = metadata.get("problem-pattern") or metadata.get("pattern") or ""

    return [
        f"  <pdir>{pdir}</pdir>",
        f"  <problem-name>{problem_name}</problem-name>",
        f"  <difficulty>{difficulty}</difficulty>",
        f"  <pattern>{pattern}</pattern>",
    ]


def _build_path_context(subagent_type, item, list_name, work_folder=None):
    """Resolve pdir, read metadata, and return XML lines for analyzer/criticizer paths.

    Returns a list of indented XML element strings to splice into the <work-item> block.
    Raises RuntimeError on missing/malformed inputs.
    """
    if work_folder is None:
        work_folder = f".thoughts/time-estimatives/{list_name}"
    problem_folder = item.get("problem-folder") or f"p{item['problem-id']}"
    pdir = f"{work_folder}/{problem_folder}"

    metadata_path = os.path.join(pdir, "metadata.yaml")
    if not os.path.isfile(metadata_path):
        raise RuntimeError(
            f"metadata.yaml missing for problem-id {item['problem-id']}: {metadata_path}"
        )

    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML package not installed") from None

    try:
        with open(metadata_path, encoding="utf-8") as f:
            metadata = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(f"failed to read {metadata_path}: {e}") from e

    problem_name = metadata.get("problem-name", "")
    difficulty = metadata.get("nominal-difficulty") or metadata.get("difficulty") or ""
    pattern = metadata.get("problem-pattern") or metadata.get("pattern") or ""

    source = item.get("source", "")
    lines = [
        f"  <problem-name>{problem_name}</problem-name>",
        f"  <difficulty>{difficulty}</difficulty>",
        f"  <pattern>{pattern}</pattern>",
    ]

    worker_kind = _normalize_worker_type(subagent_type)
    if worker_kind == "solution-analyzer":
        sol_md, sol_py, analysis_path = _resolve_analyzer_paths(pdir, source)
        lines.append(f"  <solution-md>{sol_md}</solution-md>")
        lines.append(f"  <solution-py>{sol_py}</solution-py>")
        lines.append(f"  <analysis-path>{analysis_path}</analysis-path>")
        lines.append(f"  <output-path>{analysis_path}</output-path>")
    else:
        pair_type = item.get("pair-type", "")
        sol_md, sol_py, analysis_or_estimative, critique_path = _resolve_criticizer_paths(
            pdir, source, pair_type
        )
        if sol_md is not None:
            lines.append(f"  <solution-md>{sol_md}</solution-md>")
        if sol_py is not None:
            lines.append(f"  <solution-py>{sol_py}</solution-py>")
        lines.append(f"  <analysis-or-estimative>{analysis_or_estimative}</analysis-or-estimative>")
        lines.append(f"  <critique-path>{critique_path}</critique-path>")

    return lines


def _resolve_analyzer_paths(pdir, source):
    """Return (solution-md, solution-py, analysis-path) for the solution-analyzer."""
    if source == "ai":
        return (
            f"{pdir}/ai-solution/solution.md",
            f"{pdir}/ai-solution/solution.py",
            f"{pdir}/ai-solution/time-evaluation.md",
        )
    if source == "std":
        return (
            f"{pdir}/std-solution/solution.md",
            f"{pdir}/std-solution/solution.py",
            f"{pdir}/std-solution/time-evaluation.md",
        )
    if source.startswith("std-"):
        n = source[len("std-") :]
        return (
            f"{pdir}/std-solution/solution-{n}.md",
            f"{pdir}/std-solution/solution-{n}.py",
            f"{pdir}/std-solution/time-evaluation-{n}.md",
        )
    raise RuntimeError(f"unrecognized source for solution-analyzer: {source!r}")


def _resolve_criticizer_paths(pdir, source, pair_type):
    """Return (solution-md, solution-py, analysis-or-estimative, critique-path) for the criticizer.

    solution-md/solution-py may be None for community (standalone) sources.
    """
    if source.startswith("community-"):
        n = source[len("community-") :]
        return (
            None,
            None,
            f"{pdir}/community/estimative-{n}.md",
            f"{pdir}/community/critique-{n}.md",
        )
    if source == "community":
        return (
            None,
            None,
            f"{pdir}/community/estimative.md",
            f"{pdir}/community/critique.md",
        )
    if source == "ai":
        sol_md = f"{pdir}/ai-solution/solution.md"
        sol_py = f"{pdir}/ai-solution/solution.py"
        analysis = f"{pdir}/ai-solution/time-evaluation.md"
        if pair_type == "standalone":
            critique = f"{pdir}/ai-solution/critique-standalone.md"
        else:
            critique = f"{pdir}/ai-solution/critique.md"
        return (sol_md, sol_py, analysis, critique)
    if source == "std":
        sol_md = f"{pdir}/std-solution/solution.md"
        sol_py = f"{pdir}/std-solution/solution.py"
        analysis = f"{pdir}/std-solution/time-evaluation.md"
        if pair_type == "standalone":
            critique = f"{pdir}/std-solution/critique-standalone.md"
        else:
            critique = f"{pdir}/std-solution/critique.md"
        return (sol_md, sol_py, analysis, critique)
    if source.startswith("std-"):
        n = source[len("std-") :]
        sol_md = f"{pdir}/std-solution/solution-{n}.md"
        sol_py = f"{pdir}/std-solution/solution-{n}.py"
        analysis = f"{pdir}/std-solution/time-evaluation-{n}.md"
        critique = f"{pdir}/std-solution/critique-{n}.md"
        return (sol_md, sol_py, analysis, critique)
    raise RuntimeError(f"unrecognized source for justification-criticizer: {source!r}")


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            # No input → implicit allow.
            return
        try:
            payload = json.loads(raw)
        except Exception as e:
            emit_deny(f"hook payload not valid JSON: {e}")
            return

        tool_input = payload.get("tool_input") or {}
        subagent_type = tool_input.get("subagent_type")
        if not subagent_type:
            # Not an Agent invocation we recognize → implicit allow.
            return

        if subagent_type in DISPATCHER_SUBAGENTS:
            handle_dispatcher(subagent_type)
            return

        if subagent_type in WORKER_QUEUE_MAP:
            handle_worker(subagent_type)
            return

        # Branch B3: any other subagent_type → implicit allow.
        return
    except Exception as e:
        emit_deny(f"agent_dispatch hook crashed: {e}\n{traceback.format_exc()}")
        return


if __name__ == "__main__":
    main()
    sys.exit(0)
