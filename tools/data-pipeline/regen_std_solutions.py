"""Regenerate standard-solutions.md for a set of problem folders using the
updated fetch_problem._fetch_problem_content. Does NOT touch metadata.yaml,
problem.md, status files, or any std-solution/community/ai-solution outputs."""

import argparse
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude" / "scripts"))

from fetch_problem import _fetch_problem_content  # noqa: E402

DEFAULT_LIST_NAME = "veryshortlist2"
DEFAULT_INPUT_DIR = ".thoughts/time-estimatives"
DEFAULT_PROBLEM_IDS = [7, 9, 10]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate standard-solutions.md for a set of problem folders "
            "from each problem's metadata.yaml link."
        ),
    )
    parser.add_argument(
        "--list-name",
        default=DEFAULT_LIST_NAME,
        help=f"Problem list name under the input dir (default: {DEFAULT_LIST_NAME})",
    )
    parser.add_argument(
        "--input-dir",
        default=DEFAULT_INPUT_DIR,
        help=(f"Root directory containing the list folder (default: {DEFAULT_INPUT_DIR})"),
    )
    parser.add_argument(
        "--problem-id",
        type=int,
        action="append",
        default=None,
        help=(
            "Problem id under the list (e.g. 7 -> p7). May be passed multiple "
            f"times. Default: {DEFAULT_PROBLEM_IDS}"
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help=(
            "Explicit folder path to a problem directory. May be passed "
            "multiple times. When provided, overrides --list-name/--problem-id."
        ),
    )
    return parser.parse_args(argv)


def resolve_targets(args):
    if args.target:
        return list(args.target)
    base = f"{args.input_dir.rstrip('/')}/{args.list_name}"
    pids = args.problem_id if args.problem_id else DEFAULT_PROBLEM_IDS
    return [f"{base}/p{pid}" for pid in pids]


def main(argv=None):
    args = parse_args(argv)
    targets = resolve_targets(args)

    for folder in targets:
        meta_path = os.path.join(folder, "metadata.yaml")
        if not os.path.isfile(meta_path):
            print(f"[skip] no metadata.yaml at {folder}")
            continue
        with open(meta_path, encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
        link = meta.get("link", "")
        name = meta.get("problem-name", folder)
        print(f"=== {name} ({folder}) ===")
        if not link:
            print("  no link in metadata; skipping")
            continue
        _, solutions_md, status = _fetch_problem_content(link)
        print(f"  status={status}, len={len(solutions_md)}")
        if not solutions_md:
            print("  empty solutions_md; not overwriting")
            continue
        out_path = os.path.join(folder, "standard-solutions.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(solutions_md)
        print(f"  wrote {out_path}")


if __name__ == "__main__":
    main()
