"""Check whether each Step's narrative exists in the DOM at load time
(hidden via CSS) or is rendered only when the user clicks that step.

Strategy:
 - Load the Solution page (URL path already includes /solutions).
 - Snapshot innerText (= visible text only).
 - Snapshot document.body.innerHTML (includes hidden nodes).
 - Look inside the full HTML for prose sentences typical of walkthrough steps
   (sentences ending with '.' and containing lowercase letters) that are NOT
   present in innerText — those are hidden step narratives.
 - Click the next-step button a few times and re-snapshot innerText to see
   whether new narratives appear on interaction.
"""

import os
import re
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


def probe(slug: str, url: str, p) -> None:
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
        page.wait_for_timeout(2000)

        # Click Solution tab to be sure
        for el in page.query_selector_all("a, button, [role=tab]"):
            try:
                if (el.inner_text() or "").strip() == "Solution":
                    el.click()
                    break
            except Exception:
                pass
        page.wait_for_timeout(2500)

        visible = page.evaluate("() => document.body.innerText")
        html = page.evaluate("() => document.body.innerHTML")

        # Save both for manual inspection
        with open(os.path.join(OUT, f"{slug}.step1.visible.txt"), "w", encoding="utf-8") as f:
            f.write(visible)
        with open(os.path.join(OUT, f"{slug}.step1.html.txt"), "w", encoding="utf-8") as f:
            f.write(html)

        # Current step indicator
        step_match = re.search(r"Step\s+(\d+)\s*/\s*(\d+)", visible)
        total_steps = int(step_match.group(2)) if step_match else 0
        print(f"[{slug}] total steps = {total_steps}")

        # Heuristic: all sentences in HTML that look like walkthrough prose.
        # Look between >...< tags for text with lowercase + period ending
        # (approximate — we just want to see if they exist hidden).
        prose_re = re.compile(r">\s*([A-Z][A-Za-z0-9 ,;:'()\-]{15,}[.?!])\s*<")
        hidden_candidates = set(prose_re.findall(html))
        visible_set = {s.strip() for s in visible.split("\n") if s.strip()}
        only_hidden = [s for s in hidden_candidates if s not in visible_set]
        print(f"[{slug}] prose-like sentences in HTML total: {len(hidden_candidates)}")
        print(f"[{slug}] prose-like sentences NOT visible: {len(only_hidden)}")
        for s in only_hidden[:15]:
            print(f"    HIDDEN: {s}")

        # Now try clicking a next-step control, if one exists, to confirm steps
        # are dynamic. Candidate selectors: buttons with ">", "Next", or chevron.
        clicked = 0
        for sel in [
            'button[aria-label="Next"]',
            'button[aria-label="next"]',
            '[data-testid*="next" i]',
            'button >> text=">"',
        ]:
            try:
                btn = page.query_selector(sel)
                if btn:
                    for _ in range(min(3, max(0, total_steps - 1))):
                        btn.click()
                        page.wait_for_timeout(500)
                        clicked += 1
                    break
            except Exception:
                continue
        if clicked:
            visible2 = page.evaluate("() => document.body.innerText")
            with open(
                os.path.join(OUT, f"{slug}.after-clicks.visible.txt"), "w", encoding="utf-8"
            ) as f:
                f.write(visible2)
            step_match2 = re.search(r"Step\s+(\d+)\s*/\s*(\d+)", visible2)
            if step_match2:
                print(
                    f"[{slug}] after {clicked} click(s): Step {step_match2.group(1)}/{step_match2.group(2)}"
                )
            # Which new prose appeared?
            new_lines = [
                ln.strip()
                for ln in visible2.split("\n")
                if ln.strip() and ln.strip() not in visible_set
            ]
            new_prose = [
                ln
                for ln in new_lines
                if ln.endswith((".", "?", "!")) and any(c.islower() for c in ln)
            ]
            print(f"[{slug}] new prose after clicks: {len(new_prose)}")
            for s in new_prose[:6]:
                print(f"    NEW: {s}")
        else:
            print(f"[{slug}] could not find a next-step control to click")
        print("-" * 60)
    finally:
        context.close()
        if browser is not None:
            browser.close()


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        for slug, url in URLS:
            probe(slug, url, p)


if __name__ == "__main__":
    main()
