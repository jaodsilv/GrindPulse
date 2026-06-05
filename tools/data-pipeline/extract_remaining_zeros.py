import sys

if len(sys.argv) < 3:
    print("Usage: python extract_remaining_zeros.py <input_tsv> <output_tsv>")
    print("Example: python extract_remaining_zeros.py raw/uber.tsv raw/uber_remaining.tsv")
    exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

remaining = []

with open(input_path, encoding="utf-8") as f:
    header = f.readline()
    for line in f:
        cols = line.rstrip("\n").split("\t")
        if len(cols) >= 3 and cols[2] == "0":
            remaining.append(line.rstrip("\n"))

with open(output_path, "w", encoding="utf-8") as f:
    f.write(header)
    for row in remaining:
        f.write(row + "\n")

print(f"Extracted {len(remaining)} problems with 0 times to {output_path}")
