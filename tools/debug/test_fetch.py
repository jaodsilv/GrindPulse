"""Test harness for _fetch_problem_content without touching remaining.yaml."""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude" / "scripts"))
from fetch_problem import _fetch_problem_content  # noqa: E402

_PROFILE_PATH = os.path.join(".claude", "scripts", ".neetcode-profile")
if os.path.isdir(_PROFILE_PATH):
    print(f"[auth] profile found at {_PROFILE_PATH} — tests will run AUTHENTICATED.")
else:
    print(f"[auth] no profile found at {_PROFILE_PATH} — tests will run UNAUTHENTICATED.")


CASES = [
    ("two-integer-sum", "non-pro / expected ok"),
    ("random-pick-with-weight", "non-pro / expected ok"),
    ("boundary-of-binary-tree", "pro-gated / expected pro_gated"),
]


def run_case(slug: str, note: str):
    link = f"https://neetcode.io/problems/{slug}"
    print(f"\n{'=' * 70}")
    print(f"CASE: {slug}  ({note})")
    print("=" * 70)
    try:
        problem_md, solutions_md, status = _fetch_problem_content(link)
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print(f"status = {status!r}")
    print(f"problem_md length = {len(problem_md)}")
    print(f"solutions_md length = {len(solutions_md)}")
    print("\n--- problem_md (first 800 chars) ---")
    print(problem_md[:800])
    print("\n--- problem_md (last 300 chars) ---")
    print(problem_md[-300:])
    print("\n--- solutions_md (first 1200 chars) ---")
    print(solutions_md[:1200])
    print("\n--- solutions_md (last 800 chars) ---")
    print(solutions_md[-800:])


def main():
    wanted = sys.argv[1:]
    cases = [c for c in CASES if not wanted or c[0] in wanted]
    for slug, note in cases:
        run_case(slug, note)

    # Simulated error case (bogus slug): we pass a garbage slug that will load
    # the site but yield essentially empty content; also test a bad URL scheme.
    print(f"\n{'=' * 70}")
    print("CASE: bogus URL (expected exception to propagate)")
    print("=" * 70)
    try:
        r = _fetch_problem_content("https://nonexistent.invalid.tld/problems/whatever")
        print(f"(no exception) returned: status={r[2]!r}, lens=({len(r[0])}, {len(r[1])})")
    except Exception as e:
        print(f"EXCEPTION (expected): {type(e).__name__}: {str(e).splitlines()[0]}")


if __name__ == "__main__":
    main()
