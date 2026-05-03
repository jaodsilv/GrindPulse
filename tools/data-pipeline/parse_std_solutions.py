#!/usr/bin/env python3
"""Parse standard-solutions.md for all problems and write std-solution/ files."""

import argparse
import os
import re

DEFAULT_LIST_NAME = "uber"
DEFAULT_INPUT_DIR = ".thoughts/time-estimatives"
DEFAULT_START = 1
DEFAULT_END = 50


def get_time_complexity(sol):
    m = re.search(r"Time complexity.*?O\(([^)]+)\)", sol, re.IGNORECASE)
    if m:
        return f"O({m.group(1)})"
    return "unknown"


def complexity_order(tc):
    tc = tc.lower().replace(" ", "")
    if "o(1)" in tc:
        return 0
    if "o(logn)" in tc:
        return 1
    if tc == "o(n)":
        return 2
    if "nlogn" in tc or "o(nlogn)" in tc:
        return 3
    if "n^2" in tc or "o(n^2)" in tc:
        return 4
    if "n^3" in tc:
        return 5
    if "2^n" in tc:
        return 6
    return 2


def parse_and_write(problem_id, base):
    pdir = f"{base}/p{problem_id}"
    input_file = f"{pdir}/standard-solutions.md"
    output_dir = f"{pdir}/std-solution"
    status_file = f"{pdir}/status.std-solutions.yaml"

    if not os.path.exists(input_file):
        return 0, f"error: missing {input_file}"

    with open(input_file, encoding="utf-8") as f:
        content = f.read()

    parts = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    solutions = [p.strip() for p in parts if re.match(r"^## \d+", p.strip())]

    if not solutions:
        with open(status_file, "w", encoding="utf-8") as f:
            f.write("status: DONE\ncount: 0\n")
        return 0, "parsed 0 solutions"

    complexities = [get_time_complexity(s) for s in solutions]
    orders = [complexity_order(c) for c in complexities]
    best = min(orders)
    optimal = [i for i, o in enumerate(orders) if o == best]

    os.makedirs(output_dir, exist_ok=True)

    n = 0
    for idx in optimal:
        sol = solutions[idx]

        code_m = re.search(r"```python\n(.*?)\n```", sol, re.DOTALL)
        code = code_m.group(1) if code_m else ""

        md_path = f"{output_dir}/solution-{n}.md"
        py_path = f"{output_dir}/solution-{n}.py"

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(sol + "\n")
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(code + "\n")

        n += 1

    with open(status_file, "w", encoding="utf-8") as f:
        f.write(f"status: DONE\ncount: {n}\n")

    return n, f"parsed {n} solutions"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse standard-solutions.md for problems and write std-solution/ files.",
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
        "--start",
        type=int,
        default=DEFAULT_START,
        help=f"First problem id (inclusive, default: {DEFAULT_START})",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=DEFAULT_END,
        help=f"Last problem id (inclusive, default: {DEFAULT_END})",
    )
    parser.add_argument(
        "--problem-id",
        type=int,
        action="append",
        default=None,
        help=(
            "Specific problem id to process; may be passed multiple times. "
            "When provided, overrides --start/--end."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    base = f"{args.input_dir.rstrip('/')}/{args.list_name}"

    if args.problem_id:
        pids = list(args.problem_id)
    else:
        pids = list(range(args.start, args.end + 1))

    total = 0
    for pid in pids:
        count, msg = parse_and_write(pid, base)
        total += count
        print(f"p{pid}: {msg}")

    print(f"Total solutions written: {total}")


if __name__ == "__main__":
    main()
