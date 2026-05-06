"""Diagnostic: dump neetcode.io Solution-tab content for p7 and p10 so we can
see exactly what format the page is delivering and why _parse_solutions finds 0.

Writes:
  tools/debug/debug_out/{slug}.body.txt   # full innerText after Solution click
  tools/debug/debug_out/{slug}.pre-{i}.txt # each <pre> block
  tools/debug/debug_out/{slug}.summary.txt # numbered-heading / Intuition counts
"""

import os
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URLS = [
    (
        "optimal-account-balancing",
        "https://neetcode.io/problems/optimal-account-balancing/solutions",
    ),
    ("design-hit-counter", "https://neetcode.io/problems/design-hit-counter/solutions"),
]

_HERE = Path(__file__).resolve().parent
OUT = str(_HERE / "debug_out")
PROFILE = str(_HERE.parent.parent / ".claude" / "scripts" / ".neetcode-profile")


def dump(slug: str, url: str, p) -> None:
    has_auth = os.path.isdir(PROFILE)
    browser = None
    if has_auth:
        context = p.chromium.launch_persistent_context(PROFILE, headless=True)
    else:
        browser = p.chromium.launch(headless=True, channel="msedge")
        context = browser.new_context()
    try:
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        body0 = page.evaluate("() => document.body.innerText")
        if "Get Pro Access" in body0 and has_auth:
            print(f"[{slug}] AUTH EXPIRED — page still shows Get Pro Access")
        if "Get Pro Access" in body0 and len(body0.strip()) < 200:
            print(f"[{slug}] Pro-gated, short body")

        # Click Solution tab
        elements = page.query_selector_all("a, button, [role=tab]")
        clicked = False
        for el in elements:
            try:
                if (el.inner_text() or "").strip() == "Solution":
                    el.click()
                    clicked = True
                    break
            except Exception as e:
                # Debug scan: only one element needs to match; log and continue.
                print(
                    f"[{slug}] skipping element while searching Solution tab: "
                    f"{type(e).__name__}: {e}"
                )
                continue
        print(f"[{slug}] clicked Solution tab: {clicked}")
        page.wait_for_timeout(3500)

        body = page.evaluate("() => document.body.innerText")

        with open(os.path.join(OUT, f"{slug}.body.txt"), "w", encoding="utf-8") as f:
            f.write(body)

        pres = page.query_selector_all("pre")
        kept = 0
        for i, pre in enumerate(pres):
            try:
                t = pre.inner_text()
            except Exception as e:
                # Debug scan: detached <pre> elements raise transiently; log
                # and skip so the rest of the dump still completes.
                print(f"[{slug}] skipping <pre>[{i}]: {type(e).__name__}: {e}")
                continue
            with open(os.path.join(OUT, f"{slug}.pre-{i}.txt"), "w", encoding="utf-8") as f:
                f.write(t or "")
            if t and t.strip() and ("class Solution" in t or "def " in t or "public " in t):
                kept += 1

        lines = body.split("\n")
        numbered = [
            (i, ln.strip()) for i, ln in enumerate(lines) if re.match(r"^\d+\.\s+\S", ln.strip())
        ]
        intuitions = [i for i, ln in enumerate(lines) if ln.strip() == "Intuition"]
        algorithms = [i for i, ln in enumerate(lines) if ln.strip() == "Algorithm"]
        tsc = [i for i, ln in enumerate(lines) if ln.strip() == "Time & Space Complexity"]

        summary = [
            f"URL: {url}",
            f"body_len: {len(body)}",
            f"<pre> total: {len(pres)} ; with code heuristic: {kept}",
            f"numbered_headings: {len(numbered)}",
            *[f"  line {i}: {txt}" for i, txt in numbered[:20]],
            f"'Intuition' lines: {len(intuitions)} -> {intuitions[:10]}",
            f"'Algorithm' lines: {len(algorithms)} -> {algorithms[:10]}",
            f"'Time & Space Complexity' lines: {len(tsc)} -> {tsc[:10]}",
        ]
        with open(os.path.join(OUT, f"{slug}.summary.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(summary))
        print("\n".join(summary))
        print("-" * 60)
    finally:
        context.close()
        if browser is not None:
            browser.close()


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        for slug, url in URLS:
            dump(slug, url, p)


if __name__ == "__main__":
    sys.exit(main() or 0)
