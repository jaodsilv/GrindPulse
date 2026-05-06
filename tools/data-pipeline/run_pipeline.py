import glob
import os
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python run_pipeline.py <company>")
    print("Example: python run_pipeline.py uber")
    exit(1)

company = sys.argv[1].lower()
scripts_dir = os.path.dirname(__file__)
base_dir = os.path.join(scripts_dir, "..", "..", "..", ".thoughts", "raw-html")
raw_dir = os.path.join(scripts_dir, "..", "..", "..", "raw")

html_files = sorted(glob.glob(os.path.join(base_dir, f"{company}-problems-*.html")))
if not html_files:
    print(f"No HTML files found matching {company}-problems-*.html in {base_dir}")
    exit(1)

md_files = []
print("\n=== extract_html_to_md.py ===")
for html_path in html_files:
    num = os.path.basename(html_path).split("-")[-1].replace(".html", "")
    md_path = os.path.join(base_dir, f"{company}-problems-converted-{num}.md")
    md_files.append(md_path)
    result = subprocess.run(
        [sys.executable, os.path.join(scripts_dir, "extract_html_to_md.py"), html_path, md_path]
    )
    if result.returncode != 0:
        print(f"FAILED at extract_html_to_md.py for {html_path}, aborting.")
        exit(1)

tsv_path = os.path.join(raw_dir, f"{company}.tsv")
neetcode_path = os.path.join(raw_dir, "neetcode250.tsv")
remaining_path = os.path.join(raw_dir, f"{company}_remaining.tsv")

print("\n=== merge_md_to_tsv.py ===")
result = subprocess.run(
    [sys.executable, os.path.join(scripts_dir, "merge_md_to_tsv.py"), tsv_path, *md_files]
)
if result.returncode != 0:
    print("FAILED at merge_md_to_tsv.py, aborting.")
    exit(1)

print("\n=== fill_from_reference.py ===")
result = subprocess.run(
    [
        sys.executable,
        os.path.join(scripts_dir, "fill_from_reference.py"),
        tsv_path,
        neetcode_path,
        tsv_path,
    ]
)
if result.returncode != 0:
    print("FAILED at fill_from_reference.py, aborting.")
    exit(1)

print("\n=== extract_remaining_zeros.py ===")
result = subprocess.run(
    [
        sys.executable,
        os.path.join(scripts_dir, "extract_remaining_zeros.py"),
        tsv_path,
        remaining_path,
    ]
)
if result.returncode != 0:
    print("FAILED at extract_remaining_zeros.py, aborting.")
    exit(1)

print("\nDone.")
