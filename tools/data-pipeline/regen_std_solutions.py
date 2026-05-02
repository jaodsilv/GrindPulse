"""Regenerate standard-solutions.md for a set of problem folders using the
updated fetch_problem._fetch_problem_content. Does NOT touch metadata.yaml,
problem.md, status files, or any std-solution/community/ai-solution outputs."""

import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude" / "scripts"))

from fetch_problem import _fetch_problem_content  # noqa: E402

TARGETS = [
    ".thoughts/time-estimatives/veryshortlist2/p7",
    ".thoughts/time-estimatives/veryshortlist2/p9",
    ".thoughts/time-estimatives/veryshortlist2/p10",
]


def main():
    for folder in TARGETS:
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
