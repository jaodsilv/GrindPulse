import re
import sys

if len(sys.argv) < 3:
    print("Usage: python merge_md_to_tsv.py <output_tsv> <input_md1> [input_md2 ...]")
    print("Example: python merge_md_to_tsv.py raw/uber.tsv converted-1.md converted-2.md")
    exit(1)

out_path = sys.argv[1]
md_files = sys.argv[2:]

seen = set()
problems = []

for md_path in md_files:
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            match = re.match(r"\|\s*(Done)?\s*\|\s*\[(.+?)\]\((.+?)\)\s*\|\s*(\w+)\s*\|", line)
            if not match:
                continue
            name = match.group(2).strip()
            link = match.group(3).strip()
            difficulty = match.group(4).strip()

            if name in seen:
                continue
            seen.add(name)
            problems.append((name, difficulty, link))

HEADER = "Problem Name\tDifficulty\tIntermediate Max Time\tAdvanced Max Time\tTop of the Crop Max Time\tProblem Pattern\tLink"

with open(out_path, "w", encoding="utf-8") as f:
    f.write(HEADER + "\n")
    for name, difficulty, link in problems:
        f.write(f"{name}\t{difficulty}\t0\t0\t0\tN/A\t{link}\n")

print(f"Wrote {len(problems)} unique problems to {out_path}")
