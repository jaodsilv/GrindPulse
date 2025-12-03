#!/usr/bin/env python3
"""
Data Parser Sub-Agent
Reads and parses all TSV files dynamically from problems-tracker/raw/
"""

import os
import csv
import json
from pathlib import Path
from collections import defaultdict

def parse_tsv_files(raw_folder):
    """Parse all TSV files in the raw folder"""

    # Find all TSV files
    tsv_files = list(Path(raw_folder).glob("*.tsv"))

    all_data = {}
    all_problems = defaultdict(list)  # For duplicate detection

    for tsv_file in tsv_files:
        file_key = tsv_file.stem  # e.g., "blind75"
        problems = []

        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')

            for idx, row in enumerate(reader):
                if idx == 0 or len(row) < 6:  # Skip header row and malformed rows
                    continue

                problem = {
                    "name": row[0].strip(),
                    "difficulty": row[1].strip(),
                    "intermediate_time": row[2].strip(),
                    "advanced_time": row[3].strip(),
                    "top_time": row[4].strip(),
                    "pattern": row[5].strip(),
                    # These columns will be added by the tracker
                    "solved": False,
                    "time_to_solve": "",
                    "comments": "",
                    "solved_date": ""
                }

                problems.append(problem)

                # Track for duplicate detection
                all_problems[problem["name"]].append(file_key)

        all_data[file_key] = problems

    # Build duplicate mapping (only include problems that appear in multiple files)
    duplicate_map = {
        name: files for name, files in all_problems.items()
        if len(files) > 1
    }

    return {
        "data": all_data,
        "duplicate_map": duplicate_map,
        "file_list": [f.stem for f in tsv_files]
    }

if __name__ == "__main__":
    raw_folder = Path(__file__).parent / "raw"
    result = parse_tsv_files(raw_folder)
    print(json.dumps(result, indent=2))
