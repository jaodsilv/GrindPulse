import re
import sys
import urllib.parse

args = sys.argv[1:]
pattern_only = False
add_problems = False
if "--problem-pattern-only" in args:
    args.remove("--problem-pattern-only")
    pattern_only = True
if "--add-problems" in args:
    args.remove("--add-problems")
    add_problems = True

if len(args) < 3:
    print(
        "Usage: python fill_from_reference.py [--problem-pattern-only] [--add-problems] <input_tsv> <reference_tsv> <output_tsv>"
    )
    print("  --problem-pattern-only  Only fill the Pattern column, skip time columns")
    print("  --add-problems          Append reference rows whose slug is missing from the input")
    print(
        "Example: python fill_from_reference.py raw/uber.tsv raw/neetcode250.tsv raw/uber_filled.tsv"
    )
    exit(1)

input_path = args[0]
reference_path = args[1]
output_path = args[2]


def extract_slug(url):
    match = re.search(r"/problems/([^/?]+)", url)
    return match.group(1) if match else None


def rewrite_list_query(url, canonical):
    parts = urllib.parse.urlsplit(url)
    query_pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    found = False
    new_pairs = []
    for k, v in query_pairs:
        if k == "list":
            new_pairs.append((k, canonical))
            found = True
        else:
            new_pairs.append((k, v))
    if not found:
        new_pairs.append(("list", canonical))
    new_query = urllib.parse.urlencode(new_pairs)
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, new_query, parts.fragment)
    )


reference = {}
reference_rows_in_order = []
with open(reference_path, encoding="utf-8") as f:
    header = f.readline()
    for line in f:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 7:
            continue
        slug = extract_slug(cols[6])
        if slug:
            reference[slug] = {
                "intermediate": cols[2],
                "advanced": cols[3],
                "top": cols[4],
                "pattern": cols[5],
            }
            reference_rows_in_order.append((slug, cols))

matched = 0
total = 0
rows = []
seen_slugs = set()
list_values_seen = []

with open(input_path, encoding="utf-8") as f:
    header = f.readline()
    for line in f:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 7:
            rows.append(line.rstrip("\n"))
            continue
        total += 1
        slug = extract_slug(cols[6])
        if slug:
            seen_slugs.add(slug)
        if slug and slug in reference:
            data = reference[slug]
            if not pattern_only:
                cols[2] = data["intermediate"]
                cols[3] = data["advanced"]
                cols[4] = data["top"]
            cols[5] = data["pattern"]
            matched += 1
        parts = urllib.parse.urlsplit(cols[6])
        for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True):
            if k == "list" and v and v not in list_values_seen:
                list_values_seen.append(v)
        rows.append("\t".join(cols))

canonical_list = list_values_seen[0] if list_values_seen else None
if add_problems:
    if canonical_list is None:
        print(
            "Warning: input has no '?list=...' query string; appended rows will use reference URLs verbatim"
        )
    elif len(list_values_seen) > 1:
        print(
            f"Warning: input has multiple '?list=' values {list_values_seen}; using first '{canonical_list}'"
        )

added = 0
with open(output_path, "w", encoding="utf-8") as f:
    f.write(header)
    for row in rows:
        f.write(row + "\n")
    if add_problems:
        for slug, ref_cols in reference_rows_in_order:
            if slug in seen_slugs:
                continue
            link = ref_cols[6]
            if canonical_list is not None:
                link = rewrite_list_query(link, canonical_list)
            if pattern_only:
                out_cols = [ref_cols[0], ref_cols[1], "0", "0", "0", ref_cols[5], link]
            else:
                out_cols = list(ref_cols[:6]) + [link]
            f.write("\t".join(out_cols) + "\n")
            added += 1

print(f"Matched: {matched}/{total}")
print(f"Remaining: {total - matched}")
if add_problems:
    print(f"Added: {added}")
