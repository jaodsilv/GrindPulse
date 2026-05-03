"""Atomic TSV mutation + audit log + status.yaml update.

Usage:
  python write_tsv.py --list-name X --problem-id N --intermediate I --advanced A --top T --source SRC
"""
# ruff: noqa: E402

import datetime
import os
import shutil
import sys

import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from lib import status_io  # type: ignore[import-not-found]
from lib.active_list import load as _load_active_list  # type: ignore[import-not-found]


def main() -> None:
    args = sys.argv[1:]
    params: dict[str, str] = {}
    for i, a in enumerate(args):
        if a.startswith("--") and i + 1 < len(args):
            params[a[2:]] = args[i + 1]

    list_name = params["list-name"]
    problem_id = int(params["problem-id"])
    intermediate = int(params["intermediate"])
    advanced = int(params["advanced"])
    top = int(params["top"])
    source = params.get("source", "std-0")

    root = f".thoughts/time-estimatives/{list_name}"
    pdir = os.path.join(root, f"p{problem_id}")

    with open(os.path.join(pdir, "metadata.yaml"), encoding="utf-8") as f:
        metadata = yaml.safe_load(f)
    problem_name: str = metadata["problem-name"]

    config = _load_active_list()
    if not config or "list-path" not in config:
        print("ERROR: .active-list.yaml missing or has no list-path", file=sys.stderr)
        sys.exit(1)
    list_path: str = config["list-path"]

    with open(list_path, encoding="utf-8") as f:
        lines = f.readlines()

    updated = False
    new_lines = [lines[0]]
    for idx, line in enumerate(lines[1:], start=2):
        stripped = line.rstrip("\n")
        if not stripped:
            new_lines.append(line)
            continue
        cols = stripped.split("\t")
        try:
            if len(cols) >= 5 and cols[0].strip() == problem_name:
                cols[2] = str(intermediate)
                cols[3] = str(advanced)
                cols[4] = str(top)
                new_lines.append("\t".join(cols) + "\n")
                updated = True
            else:
                new_lines.append(line)
        except (KeyError, IndexError) as e:
            raise KeyError(f"missing field {e!s} while writing {list_path} row {idx}") from e

    if not updated:
        print(f"ERROR: problem {problem_name!r} not found in {list_path}", file=sys.stderr)
        sys.exit(1)

    # Called only once per pipeline run (at the end), so concurrent writers cannot occur and no file lock is needed.
    tmp = list_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    shutil.move(tmp, list_path)

    audit_path = os.path.join(root, "audit.log")
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(
            f"{ts}\t{problem_name}\tp{problem_id}\t{intermediate}\t{advanced}\t{top}\t{source}\n"
        )

    status_io.mark_complete(
        root,
        problem_name,
        problem_id,
        times={"intermediate": intermediate, "advanced": advanced, "top": top},
    )

    print(f"Updated {problem_name}: intermediate={intermediate}, advanced={advanced}, top={top}")


if __name__ == "__main__":
    main()
