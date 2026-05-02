#!/usr/bin/env python3
"""Parse standard-solutions.md for all problems and write std-solution/ files."""

import os
import re
import sys

LIST_NAME = "uber"
BASE = f".thoughts/time-estimatives/{LIST_NAME}"


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


def parse_and_write(problem_id, start=None, end=None):
    pdir = f"{BASE}/p{problem_id}"
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


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    total = 0
    for pid in range(start, end + 1):
        count, msg = parse_and_write(pid)
        total += count
        print(f"p{pid}: {msg}")

    print(f"Total solutions written: {total}")


if __name__ == "__main__":
    main()
