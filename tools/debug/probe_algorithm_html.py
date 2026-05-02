"""Inspect the DOM around the 'Algorithm' section of each approach on a
multi-approach Solution page (p9: interval-list-intersections). Goal: find a
stable query that yields per-approach Algorithm HTML we can render to markdown
preserving bullets / nested lists.

Writes tools/debug/debug_out/ill.solution.html (full HTML), and prints:
  - list of all headings found with text
  - outerHTML of any container whose previous sibling is <h?>Algorithm</h?>
  - any <ol>/<ul> that appear between 'Algorithm' and 'Time & Space Complexity'
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "https://neetcode.io/problems/interval-list-intersections/solutions"
_HERE = Path(__file__).resolve().parent
OUT = str(_HERE / "debug_out")
PROFILE = str(_HERE.parent.parent / ".claude" / "scripts" / ".neetcode-profile")


def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        has_auth = os.path.isdir(PROFILE)
        browser = None
        if has_auth:
            context = p.chromium.launch_persistent_context(PROFILE, headless=True)
        else:
            browser = p.chromium.launch(headless=True, channel="msedge")
            context = browser.new_context()
        try:
            page = context.new_page()
            page.goto(URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1500)
            for el in page.query_selector_all("a, button, [role=tab]"):
                try:
                    if (el.inner_text() or "").strip() == "Solution":
                        el.click()
                        break
                except Exception:
                    pass
            page.wait_for_timeout(3500)

            html = page.evaluate("() => document.body.innerHTML")
            with open(os.path.join(OUT, "ill.solution.html"), "w", encoding="utf-8") as f:
                f.write(html)

            # Enumerate all heading-like elements with their text
            headings = page.evaluate(
                """
                () => {
                    const hs = Array.from(document.querySelectorAll(
                        'h1, h2, h3, h4, h5, strong, [class*=heading i], [class*=title i]'
                    ));
                    return hs.map(h => ({
                        tag: h.tagName,
                        cls: h.className || '',
                        text: (h.innerText || '').trim(),
                    })).filter(x => x.text);
                }
                """
            )
            print(f"headings found: {len(headings)}")
            for h in headings:
                if (
                    h["text"] in ("Algorithm", "Intuition", "Time & Space Complexity")
                    or "Interval List Intersections" in h["text"]
                ):
                    print(f"  {h['tag']:8s} cls={h['cls'][:60]!r:70s} text={h['text'][:80]!r}")

            # For each "Algorithm" heading, grab the next sibling's outerHTML
            algo_siblings = page.evaluate(
                """
                () => {
                    const out = [];
                    const all = Array.from(document.querySelectorAll('*'));
                    for (const el of all) {
                        if ((el.innerText || '').trim() !== 'Algorithm') continue;
                        if (el.children.length > 0) continue; // only leaf matches
                        // walk siblings collecting HTML until we hit 'Time & Space Complexity'
                        const parts = [];
                        let node = el.parentElement;
                        if (!node) continue;
                        let sib = node.nextElementSibling;
                        while (sib && (sib.innerText || '').trim() !== 'Time & Space Complexity') {
                            parts.push(sib.outerHTML);
                            sib = sib.nextElementSibling;
                            if (parts.length > 20) break;
                        }
                        out.push({
                            parentTag: node.tagName,
                            algorithmOwnTag: el.tagName,
                            siblingsHTML: parts.slice(0, 3),
                        });
                    }
                    return out;
                }
                """
            )
            print(f"\nAlgorithm-sibling candidates: {len(algo_siblings)}")
            for i, a in enumerate(algo_siblings):
                print(f"  [{i}] algo tag={a['algorithmOwnTag']} parent={a['parentTag']}")
                for j, h in enumerate(a["siblingsHTML"]):
                    snippet = h[:400].replace("\n", "\\n")
                    print(f"     sibling[{j}]: {snippet}")
        finally:
            context.close()
            if browser is not None:
                browser.close()


if __name__ == "__main__":
    main()
