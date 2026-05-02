"""UserPromptSubmit gate for the /process-list skill."""

import json
import os
import shutil
import sys

import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS = os.path.normpath(os.path.join(_HERE, "..", "scripts"))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
from lib import status_io  # type: ignore[import-not-found]  # noqa: E402


def _parse_positive_int(flag: str, parts: list[str]) -> tuple[int | None, str | None]:
    """Return (value, error_msg). value=None + error=None means 'not present'."""
    if flag not in parts:
        return None, None
    idx = parts.index(flag)
    if idx + 1 >= len(parts):
        return None, f"{flag} requires a value"
    try:
        n = int(parts[idx + 1])
    except ValueError:
        return None, f"{flag} must be a positive integer (got {parts[idx + 1]!r})"
    if n < 1:
        return None, f"{flag} must be >= 1"
    return n, None


def _parse_phases(parts: list[str]) -> tuple[int, int, str | None]:
    """Return (start_phase, end_phase, error_msg). Defaults to (0, 6, None)."""
    flag = "--phases"
    if flag not in parts:
        return 0, 7, None
    idx = parts.index(flag)
    if idx + 1 >= len(parts):
        return 0, 7, f"{flag} requires a value"
    spec = parts[idx + 1]

    def _to_int(s: str, ctx: str) -> int | str:
        """Return the parsed int, or an error-message string on failure."""
        try:
            return int(s)
        except ValueError:
            return f"{flag} {ctx} must be an integer (got {s!r})"

    if ":" in spec:
        left, _, right = spec.partition(":")
        if left == "" and right == "":
            return 0, 6, f"{flag} value must not be bare ':'"
        if left == "":
            start = 0
            end_parsed = _to_int(right, "end")
            if isinstance(end_parsed, str):
                return 0, 6, end_parsed
            end = end_parsed
        elif right == "":
            start_parsed = _to_int(left, "start")
            if isinstance(start_parsed, str):
                return 0, 6, start_parsed
            start = start_parsed
            end = 7
        else:
            start_parsed = _to_int(left, "start")
            if isinstance(start_parsed, str):
                return 0, 6, start_parsed
            start = start_parsed
            end_parsed = _to_int(right, "end")
            if isinstance(end_parsed, str):
                return 0, 6, end_parsed
            end = end_parsed
    else:
        n_parsed = _to_int(spec, "value")
        if isinstance(n_parsed, str):
            return 0, 6, n_parsed
        start = n_parsed
        end = n_parsed + 1

    if not (0 <= start < end <= 7):
        return (
            0,
            7,
            (f"{flag} out of bounds: need 0 <= start < end <= 7, got start={start} end={end}"),
        )
    return start, end, None


def main() -> None:
    payload = json.load(sys.stdin)
    prompt = payload.get("prompt", "").strip()

    if not prompt.startswith("/process-list"):
        sys.exit(0)

    parts = prompt.split()
    if len(parts) < 2:
        json.dump(
            {
                "decision": "block",
                "reason": (
                    "Usage: /process-list <path> [--fresh] "
                    "[--concurrency N] [--parallelism N] "
                    "[--fetch-delay-seconds N] [--ai-path] [--community-path] "
                    "[--phases <spec>]"
                ),
            },
            sys.stdout,
        )
        sys.exit(0)

    list_path = parts[1]
    fresh = "--fresh" in parts
    ai_path = "--ai-path" in parts
    community_path = "--community-path" in parts

    _pool_flags: list[tuple[str, int]] = [
        ("--parallelism", 10),
        ("--fetch-delay-seconds", 7),
    ]
    pool_sizes: dict[str, int] = {}
    explicit_flags: set[str] = set()
    for flag, default in _pool_flags:
        val, err = _parse_positive_int(flag, parts)
        if err:
            json.dump({"decision": "block", "reason": err}, sys.stdout)
            sys.exit(0)
        key = flag.lstrip("-")
        if val is not None:
            pool_sizes[key] = val
            explicit_flags.add(flag)
        else:
            pool_sizes[key] = default

    concurrency, err = _parse_positive_int("--concurrency", parts)
    if err:
        json.dump({"decision": "block", "reason": err}, sys.stdout)
        sys.exit(0)

    start_phase, end_phase, err = _parse_phases(parts)
    if err:
        json.dump({"decision": "block", "reason": err}, sys.stdout)
        sys.exit(0)
    if concurrency is not None and "--parallelism" not in explicit_flags:
        pool_sizes["parallelism"] = concurrency

    if not os.path.isfile(list_path):
        json.dump(
            {"decision": "block", "reason": f"File not found: {list_path}"},
            sys.stdout,
        )
        sys.exit(0)

    list_name = os.path.splitext(os.path.basename(list_path))[0]

    with open(list_path, encoding="utf-8") as f:
        lines = f.readlines()

    if len(lines) < 2:
        json.dump(
            {"decision": "block", "reason": "TSV file has no data rows."},
            sys.stdout,
        )
        sys.exit(0)

    problems = []
    waiting = []
    for line in lines[1:]:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        cols = line_stripped.split("\t")
        if len(cols) < 7:
            continue

        name = cols[0].strip()
        difficulty = cols[1].strip()
        pattern = cols[5].strip()
        link = cols[6].strip()

        if not fresh:
            try:
                t2 = int(cols[2].strip() or "0")
                t3 = int(cols[3].strip() or "0")
                t4 = int(cols[4].strip() or "0")
            except ValueError:
                t2 = t3 = t4 = 0
            if t2 > 0 and t3 > 0 and t4 > 0:
                continue

        problems.append(
            {
                "problem-name": name,
                "link": link,
                "nominal-difficulty": difficulty,
                "problem-pattern": pattern,
            }
        )
        waiting.append(name)

    if not problems:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "All problems in the list already have time estimates. Nothing to process.",
                },
            },
            sys.stdout,
        )
        sys.exit(0)

    bkp_path = list_path + ".bkp"
    if not os.path.isfile(bkp_path):
        shutil.copy2(list_path, bkp_path)

    work_folder = f".thoughts/time-estimatives/{list_name}"
    os.makedirs(work_folder, exist_ok=True)

    remaining_data = {"problems": problems}
    with open(os.path.join(work_folder, "remaining.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(remaining_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    status_problems = [
        {"name": name, "id": idx + 1, "problem-folder": ""} for idx, name in enumerate(waiting)
    ]
    status_io.init_status(
        work_folder,
        status_problems,
        {"ai_path": ai_path, "community_path": community_path},
    )

    next_id_path = os.path.join(work_folder, "next-id.txt")
    if fresh:
        with open(next_id_path, "w", encoding="utf-8") as f:
            f.write("1")
    elif not os.path.isfile(next_id_path):
        with open(next_id_path, "w", encoding="utf-8") as f:
            f.write("1")

    active_dir = ".thoughts/time-estimatives"
    os.makedirs(active_dir, exist_ok=True)
    active_data: dict[str, object] = {
        "work-folder": work_folder,
        "list-path": list_path,
        "list-name": list_name,
        "ai-path": ai_path,
        "community-path": community_path,
        "fresh": fresh,
        "parallelism": pool_sizes["parallelism"],
        **pool_sizes,
    }
    with open(os.path.join(active_dir, ".active-list.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(active_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    context = (
        f"<list-path>{list_path}</list-path>\n"
        f"<work-folder>{work_folder}</work-folder>\n"
        f"<list-name>{list_name}</list-name>\n"
        f"<problem-count>{len(problems)}</problem-count>\n"
        f"<parallelism>{pool_sizes['parallelism']}</parallelism>\n"
        f"<fetch-delay-seconds>{pool_sizes['fetch-delay-seconds']}</fetch-delay-seconds>\n"
        f"<ai-path>{str(ai_path).lower()}</ai-path>\n"
        f"<community-path>{str(community_path).lower()}</community-path>\n"
        f"<start-phase>{start_phase}</start-phase>\n"
        f"<end-phase>{end_phase}</end-phase>"
    )
    json.dump(
        {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}},
        sys.stdout,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
