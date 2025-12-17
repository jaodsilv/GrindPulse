#!/usr/bin/env python3
"""
Data Parser Sub-Agent
Reads and parses all TSV files dynamically from GrindPulse/raw/
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

from exceptions import (
    DataFileEmptyError,
    DataFileNotFoundError,
    FileIOError,
    TSVParseError,
    ValidationError,
)


def parse_tsv_files(raw_folder):
    """Parse all TSV files in the raw folder.

    Args:
        raw_folder: Path to the folder containing TSV files

    Returns:
        dict with keys: data, duplicate_map, file_list

    Raises:
        DataFileNotFoundError: If raw folder doesn't exist
        DataFileEmptyError: If no TSV files found or file is empty
        FileIOError: If file cannot be read (permissions, etc.)
        TSVParseError: If TSV content is malformed
        ValidationError: If no problems parsed from any file
    """
    raw_path = Path(raw_folder)

    # Validate raw folder exists
    if not raw_path.exists():
        raise DataFileNotFoundError(
            "Raw data folder not found",
            file_path=str(raw_path),
            suggestion="Create the 'raw/' directory with TSV problem files",
        )

    # Find all TSV files
    tsv_files = list(raw_path.glob("*.tsv"))

    # Validate at least one TSV file exists
    if not tsv_files:
        raise DataFileEmptyError(
            "No TSV files found in raw folder",
            file_path=str(raw_path),
            suggestion="Add at least one .tsv file (e.g., blind75.tsv) to the raw/ directory",
        )

    all_data = {}
    all_problems = defaultdict(list)  # For duplicate detection

    for tsv_file in tsv_files:
        file_key = tsv_file.stem  # e.g., "blind75"
        problems = []

        # File read with error handling
        try:
            with open(tsv_file, encoding="utf-8") as f:
                content = f.read()
        except PermissionError as err:
            raise FileIOError(
                "Permission denied reading TSV file",
                file_path=str(tsv_file),
                suggestion="Check file permissions and ensure file is not locked",
            ) from err
        except UnicodeDecodeError as e:
            raise TSVParseError(
                f"File encoding error: {e}",
                file_path=str(tsv_file),
                suggestion="Ensure file is saved with UTF-8 encoding",
            ) from e

        # Validate file is not empty
        if not content.strip():
            raise DataFileEmptyError(
                "TSV file is empty",
                file_path=str(tsv_file),
                suggestion="Add header row and problem data to the file",
            )

        # Parse TSV content
        try:
            reader = csv.reader(content.splitlines(), delimiter="\t")
            rows = list(reader)
        except csv.Error as e:
            raise TSVParseError(
                f"CSV parsing error: {e}",
                file_path=str(tsv_file),
                suggestion="Check for malformed tab-separated values",
            ) from e

        # Validate header row exists and at least one data row
        if len(rows) < 2:
            raise TSVParseError(
                "TSV file must have header row and at least one data row",
                file_path=str(tsv_file),
                suggestion="Add header: Problem Name, Difficulty, Intermediate Max time, ...",
            )

        # Parse data rows with validation
        for idx, row in enumerate(rows):
            if idx == 0:  # Skip header
                continue

            line_number = idx + 1  # 1-indexed for user display

            # Skip completely empty rows silently
            if not row or all(cell.strip() == "" for cell in row):
                continue

            # Validate minimum columns
            if len(row) < 6:
                raise TSVParseError(
                    f"Row has {len(row)} columns, expected at least 6",
                    file_path=str(tsv_file),
                    line_number=line_number,
                    suggestion="Ensure row has: Name, Difficulty, IntermediateTime, AdvancedTime, TopTime, Pattern",
                )

            # Validate required fields are not empty
            if not row[0].strip():
                raise TSVParseError(
                    "Problem name is empty",
                    file_path=str(tsv_file),
                    line_number=line_number,
                    suggestion="Add a problem name in the first column",
                )

            problem = {
                "name": row[0].strip(),
                "difficulty": row[1].strip() or "Unknown",
                "intermediate_time": row[2].strip() or "0",
                "advanced_time": row[3].strip() or "0",
                "top_time": row[4].strip() or "0",
                "pattern": row[5].strip() or "Unknown",
                # These columns will be added by the tracker
                "solved": False,
                "time_to_solve": "",
                "comments": "",
                "solved_date": "",
            }

            problems.append(problem)

            # Track for duplicate detection
            all_problems[problem["name"]].append(file_key)

        all_data[file_key] = problems

    # Final validation
    total_problems = sum(len(probs) for probs in all_data.values())
    if total_problems == 0:
        raise ValidationError(
            "No problems parsed from any TSV file",
            suggestion="Check that TSV files contain data rows after the header",
        )

    # Build duplicate mapping (only include problems that appear in multiple files)
    duplicate_map = {name: files for name, files in all_problems.items() if len(files) > 1}

    return {
        "data": all_data,
        "duplicate_map": duplicate_map,
        "file_list": [f.stem for f in tsv_files],
    }


if __name__ == "__main__":
    raw_folder = Path(__file__).parent / "raw"
    result = parse_tsv_files(raw_folder)
    print(json.dumps(result, indent=2))
