"""Disk walker for the subagent-mode process-list pipeline.

Usage:
  python list_work.py <subcommand> --list-name X [--ai-path] [--community-path]
  python list_work.py select-discover --pdir <path>

Subcommands:
  parse-needed      Problems with standard-solutions.md but no std-solution/ dir
  solve-needed      Problems with no ai-solution/ dir (requires --ai-path)
  solve-easy-needed     solve-needed filtered to nominal-difficulty == Easy
  solve-medium-needed   solve-needed filtered to nominal-difficulty == Medium
  solve-hard-needed     solve-needed filtered to nominal-difficulty == Hard
  community-needed  Problems with no community/ dir (requires --community-path)
  explain-needed    Std solutions missing Intuition/Algorithm/Complexity writeup
  analyze-needed    Solutions without a time-evaluation file
  analyze-easy-needed     analyze-needed filtered to nominal-difficulty == Easy
  analyze-medium-needed   analyze-needed filtered to nominal-difficulty == Medium
  analyze-hard-needed     analyze-needed filtered to nominal-difficulty == Hard
  critique-needed   Analyses without a critique file
  critique-easy-needed    critique-needed filtered to nominal-difficulty == Easy
  critique-medium-needed  critique-needed filtered to nominal-difficulty == Medium
  critique-hard-needed    critique-needed filtered to nominal-difficulty == Hard
  tiebreak-needed   Re-emit entries from <root>/queues/tiebreak.yaml (or [])
  select-discover   Discover paired (eval + critique) sources for one problem dir

Output: YAML list to stdout. Each item has at minimum {problem-id: N}.
        Some items also carry {source: str} and {pair-type: str}.
        For select-discover, each item is {name, eval, critique} with paths
        relative to --pdir.
"""

import os
import re
import sys

import yaml


def _dir_has_nonempty_file(path: str) -> bool:
    """True iff path is a directory containing at least one file of size > 0."""
    if not os.path.isdir(path):
        return False
    try:
        for entry in os.scandir(path):
            if entry.is_file() and entry.stat().st_size > 0:
                return True
    except OSError:
        return False
    return False


def _problem_dirs(root: str) -> list[tuple[int, str]]:
    """Return sorted list of (problem_id, abs_path) for p{N} dirs in root."""
    result = []
    try:
        entries = os.listdir(root)
    except FileNotFoundError:
        return result
    for entry in entries:
        m = re.match(r"^p(\d+)$", entry)
        if m:
            result.append((int(m.group(1)), os.path.join(root, entry)))
    result.sort(key=lambda x: x[0])
    return result


def _has_writeup(md_path: str) -> bool:
    """Return True if the solution .md has all three writeup sections."""
    try:
        with open(md_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return False
    return "### Intuition" in content and "### Algorithm" in content and "### Complexity" in content


def _problem_difficulty(pdir: str) -> str | None:
    """Return Easy/Medium/Hard from pdir/metadata.yaml, or None on missing/parse-error."""
    meta_path = os.path.join(pdir, "metadata.yaml")
    try:
        with open(meta_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    val = data.get("nominal-difficulty")
    if val in ("Easy", "Medium", "Hard"):
        return val
    return None


def _filter_items_by_tier(root: str, items: list[dict], tier: str) -> list[dict]:
    """Drop items whose problem-id's metadata.yaml difficulty != tier (None drops too)."""
    cache: dict[int, str | None] = {}
    out = []
    for it in items:
        pid = it.get("problem-id")
        if not isinstance(pid, int):
            continue
        if pid not in cache:
            cache[pid] = _problem_difficulty(os.path.join(root, f"p{pid}"))
        if cache[pid] == tier:
            out.append(it)
    return out


def cmd_parse_needed(root: str) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        has_src = os.path.isfile(os.path.join(pdir, "standard-solutions.md"))
        has_parsed = _dir_has_nonempty_file(os.path.join(pdir, "std-solution"))
        if has_src and not has_parsed:
            items.append({"problem-id": pid})
    return items


def cmd_solve_needed(root: str) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        if not _dir_has_nonempty_file(os.path.join(pdir, "ai-solution")):
            items.append({"problem-id": pid})
    return items


def cmd_community_needed(root: str) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        if not _dir_has_nonempty_file(os.path.join(pdir, "community")):
            items.append({"problem-id": pid})
    return items


def cmd_explain_needed(root: str) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        std_dir = os.path.join(pdir, "std-solution")
        if not os.path.isdir(std_dir):
            continue
        for fname in sorted(os.listdir(std_dir)):
            m = re.match(r"^solution-(\d+)\.md$", fname)
            if not m:
                continue
            n = m.group(1)
            if not _has_writeup(os.path.join(std_dir, fname)):
                items.append({"problem-id": pid, "source": f"std-{n}"})
    return items


def cmd_analyze_needed(root: str, ai: bool) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        std_dir = os.path.join(pdir, "std-solution")
        if os.path.isdir(std_dir):
            for fname in sorted(os.listdir(std_dir)):
                m = re.match(r"^solution-(\d+)\.md$", fname)
                if not m:
                    continue
                n = m.group(1)
                if not os.path.isfile(os.path.join(std_dir, f"time-evaluation-{n}.md")):
                    items.append({"problem-id": pid, "source": f"std-{n}"})
        if ai:
            ai_dir = os.path.join(pdir, "ai-solution")
            if os.path.isdir(ai_dir):
                sol = os.path.join(ai_dir, "solution.md")
                ev = os.path.join(ai_dir, "time-evaluation.md")
                if os.path.isfile(sol) and not os.path.isfile(ev):
                    items.append({"problem-id": pid, "source": "ai"})
    return items


def cmd_critique_needed(root: str, ai: bool, comm: bool) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        std_dir = os.path.join(pdir, "std-solution")
        if os.path.isdir(std_dir):
            for fname in sorted(os.listdir(std_dir)):
                m = re.match(r"^time-evaluation-(\d+)\.md$", fname)
                if not m:
                    continue
                n = m.group(1)
                if not os.path.isfile(os.path.join(std_dir, f"critique-{n}.md")):
                    items.append({"problem-id": pid, "source": f"std-{n}", "pair-type": "paired"})
        if ai:
            ai_dir = os.path.join(pdir, "ai-solution")
            if os.path.isdir(ai_dir):
                ev = os.path.join(ai_dir, "time-evaluation.md")
                cr = os.path.join(ai_dir, "critique.md")
                if os.path.isfile(ev) and not os.path.isfile(cr):
                    items.append({"problem-id": pid, "source": "ai", "pair-type": "paired"})
        if comm:
            comm_dir = os.path.join(pdir, "community")
            if os.path.isdir(comm_dir):
                for fname in sorted(os.listdir(comm_dir)):
                    m = re.match(r"^estimative-(\d+)\.md$", fname)
                    if not m:
                        continue
                    n = m.group(1)
                    if not os.path.isfile(os.path.join(comm_dir, f"critique-{n}.md")):
                        items.append(
                            {
                                "problem-id": pid,
                                "source": f"community-{n}",
                                "pair-type": "standalone",
                            }
                        )
    return items


def cmd_select_needed(root: str, ai: bool, comm: bool) -> list[dict]:
    items = []
    for pid, pdir in _problem_dirs(root):
        if os.path.isfile(os.path.join(pdir, "selected-times.md")):
            continue
        has_work = False
        all_critiqued = True

        std_dir = os.path.join(pdir, "std-solution")
        if os.path.isdir(std_dir):
            for fname in sorted(os.listdir(std_dir)):
                m = re.match(r"^time-evaluation-(\d+)\.md$", fname)
                if not m:
                    continue
                n = m.group(1)
                has_work = True
                if not os.path.isfile(os.path.join(std_dir, f"critique-{n}.md")):
                    all_critiqued = False

        if ai:
            ai_dir = os.path.join(pdir, "ai-solution")
            if os.path.isdir(ai_dir) and os.path.isfile(os.path.join(ai_dir, "time-evaluation.md")):
                has_work = True
                if not os.path.isfile(os.path.join(ai_dir, "critique.md")):
                    all_critiqued = False

        if comm:
            comm_dir = os.path.join(pdir, "community")
            if os.path.isdir(comm_dir):
                for fname in sorted(os.listdir(comm_dir)):
                    m = re.match(r"^estimative-(\d+)\.md$", fname)
                    if not m:
                        continue
                    n = m.group(1)
                    has_work = True
                    if not os.path.isfile(os.path.join(comm_dir, f"critique-{n}.md")):
                        all_critiqued = False

        if has_work and all_critiqued:
            items.append({"problem-id": pid})
    return items


def cmd_select_discover(pdir: str) -> list[dict]:
    """Walk pdir to discover paired (eval + critique) source files.

    Returns a list of {name, eval, critique} dicts with paths relative to pdir.
    Returns empty list if no sources found or pdir does not exist.
    """
    items = []

    std_dir = os.path.join(pdir, "std-solution")
    if os.path.isdir(std_dir):
        for fname in sorted(os.listdir(std_dir)):
            m = re.match(r"^critique-(\d+)\.md$", fname)
            if not m:
                continue
            n = m.group(1)
            eval_named = f"time-evaluation-{n}.md"
            eval_path = os.path.join(std_dir, eval_named)
            if os.path.isfile(eval_path):
                items.append(
                    {
                        "name": f"std-{n}",
                        "eval": f"std-solution/{eval_named}",
                        "critique": f"std-solution/{fname}",
                    }
                )
            elif n == "1":
                eval_fallback = os.path.join(std_dir, "time-evaluation.md")
                if os.path.isfile(eval_fallback):
                    items.append(
                        {
                            "name": f"std-{n}",
                            "eval": "std-solution/time-evaluation.md",
                            "critique": f"std-solution/{fname}",
                        }
                    )

    ai_dir = os.path.join(pdir, "ai-solution")
    if os.path.isdir(ai_dir):
        ev = os.path.join(ai_dir, "time-evaluation.md")
        cr = os.path.join(ai_dir, "critique.md")
        if os.path.isfile(ev) and os.path.isfile(cr):
            items.append(
                {
                    "name": "ai",
                    "eval": "ai-solution/time-evaluation.md",
                    "critique": "ai-solution/critique.md",
                }
            )

    comm_dir = os.path.join(pdir, "community")
    if os.path.isdir(comm_dir):
        for fname in sorted(os.listdir(comm_dir)):
            m = re.match(r"^critique-(\d+)\.md$", fname)
            if not m:
                continue
            n = m.group(1)
            est_named = f"estimative-{n}.md"
            est_path = os.path.join(comm_dir, est_named)
            if os.path.isfile(est_path):
                items.append(
                    {
                        "name": f"community-{n}",
                        "eval": f"community/{est_named}",
                        "critique": f"community/{fname}",
                    }
                )

    return items


def cmd_solve_needed_tier(root: str, tier: str) -> list[dict]:
    return _filter_items_by_tier(root, cmd_solve_needed(root), tier)


def cmd_analyze_needed_tier(root: str, ai: bool, tier: str) -> list[dict]:
    return _filter_items_by_tier(root, cmd_analyze_needed(root, ai), tier)


def cmd_critique_needed_tier(root: str, ai: bool, comm: bool, tier: str) -> list[dict]:
    return _filter_items_by_tier(root, cmd_critique_needed(root, ai, comm), tier)


def cmd_tiebreak_needed(root: str) -> list[dict]:
    """Re-emit entries from <root>/queues/tiebreak.yaml. Empty list if missing/empty.

    Idempotent: never writes the file. time_selection.py is responsible for
    producing queues/tiebreak.yaml; this verb only lets the dispatch hook
    materialize a queue file from it via the standard code path.
    """
    path = os.path.join(root, "queues", "tiebreak.yaml")
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        return []
    if not isinstance(data, list):
        return []
    return data


_COMMANDS = {
    "parse-needed": lambda r, *_: cmd_parse_needed(r),
    "solve-needed": lambda r, *_: cmd_solve_needed(r),
    "solve-easy-needed": lambda r, *_: cmd_solve_needed_tier(r, "Easy"),
    "solve-medium-needed": lambda r, *_: cmd_solve_needed_tier(r, "Medium"),
    "solve-hard-needed": lambda r, *_: cmd_solve_needed_tier(r, "Hard"),
    "community-needed": lambda r, *_: cmd_community_needed(r),
    "explain-needed": lambda r, *_: cmd_explain_needed(r),
    "analyze-needed": lambda r, ai, *_: cmd_analyze_needed(r, ai),
    "analyze-easy-needed": lambda r, ai, *_: cmd_analyze_needed_tier(r, ai, "Easy"),
    "analyze-medium-needed": lambda r, ai, *_: cmd_analyze_needed_tier(r, ai, "Medium"),
    "analyze-hard-needed": lambda r, ai, *_: cmd_analyze_needed_tier(r, ai, "Hard"),
    "critique-needed": cmd_critique_needed,
    "critique-easy-needed": lambda r, ai, comm: cmd_critique_needed_tier(r, ai, comm, "Easy"),
    "critique-medium-needed": lambda r, ai, comm: cmd_critique_needed_tier(r, ai, comm, "Medium"),
    "critique-hard-needed": lambda r, ai, comm: cmd_critique_needed_tier(r, ai, comm, "Hard"),
    "tiebreak-needed": lambda r, *_: cmd_tiebreak_needed(r),
}


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(
            "Usage: list_work.py <subcommand> --list-name X [--ai-path] [--community-path]",
            file=sys.stderr,
        )
        sys.exit(1)

    subcommand = args[0]

    if subcommand == "select-discover":
        pdir = None
        for i, a in enumerate(args):
            if a == "--pdir" and i + 1 < len(args):
                pdir = args[i + 1]
        if not pdir:
            print("--pdir is required for select-discover", file=sys.stderr)
            sys.exit(1)
        items = cmd_select_discover(pdir)
        if not items:
            print("[]")
        else:
            print(yaml.dump(items, default_flow_style=False, allow_unicode=True), end="")
        return

    if subcommand not in _COMMANDS:
        valid = list(_COMMANDS.keys()) + ["select-discover"]
        print(f"Unknown subcommand: {subcommand!r}. Valid: {', '.join(valid)}", file=sys.stderr)
        sys.exit(1)

    list_name = None
    for i, a in enumerate(args):
        if a == "--list-name" and i + 1 < len(args):
            list_name = args[i + 1]

    if not list_name:
        print("--list-name is required", file=sys.stderr)
        sys.exit(1)

    ai_path = "--ai-path" in args
    community_path = "--community-path" in args

    root = f".thoughts/time-estimatives/{list_name}"
    items = _COMMANDS[subcommand](root, ai_path, community_path)
    print(yaml.dump(items, default_flow_style=False, allow_unicode=True), end="")


if __name__ == "__main__":
    main()
