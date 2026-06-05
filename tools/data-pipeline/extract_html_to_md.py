import os
import re
import sys

if len(sys.argv) < 3:
    print("Usage: python extract_html_to_md.py <input_html> <output_md>")
    print(
        "Example: python extract_html_to_md.py raw-html/uber-problems-1.html raw-html/uber-problems-converted-1.md"
    )
    exit(1)

html_path = sys.argv[1]
out_path = sys.argv[2]

DIFF_MAP = {
    "is-success": "Easy",
    "is-warning": "Medium",
    "is-danger": "Hard",
}

with open(html_path, encoding="utf-8") as f:
    html = f.read()

rows = re.findall(r"(<tr\b[^>]*>)(.*?)</tr>", html, re.DOTALL)

problems = []
for tr_tag, tr_body in rows:
    link_match = re.search(
        r'<a[^>]*class="table-text text-color"[^>]*href="([^"]*)"[^>]*>\s*(.*?)\s*</a>',
        tr_body,
        re.DOTALL,
    )
    if not link_match:
        continue

    href = link_match.group(1).replace("&amp;", "&")
    name = re.sub(r"<[^>]+>", "", link_match.group(2)).strip()
    full_link = "https://neetcode.io" + href

    diff_match = re.search(r'class="button table-button (is-\w+)"', tr_body)
    difficulty = DIFF_MAP.get(diff_match.group(1), "Unknown") if diff_match else "Unknown"

    completed = "completed" in tr_tag

    problems.append((name, full_link, difficulty, completed))

os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    basename = os.path.basename(html_path)
    f.write(f"# {basename}\n\n")
    f.write("| Status | Problem | Difficulty |\n")
    f.write("|--------|---------|------------|\n")
    for name, link, diff, completed in problems:
        status = "Done" if completed else ""
        f.write(f"| {status} | [{name}]({link}) | {diff} |\n")

print(f"Wrote {len(problems)} problems to {out_path}")
