"""Tests for data_parser.py error handling."""

import pytest

from data_parser import parse_tsv_files
from exceptions import (
    DataFileEmptyError,
    DataFileNotFoundError,
    TSVParseError,
    ValidationError,
)


class TestRawFolderValidation:
    """Tests for raw folder validation."""

    def test_missing_raw_folder_raises_error(self, temp_dir):
        """Should raise DataFileNotFoundError when raw/ doesn't exist."""
        with pytest.raises(DataFileNotFoundError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        message = str(exc_info.value).lower()
        assert "raw" in message
        assert "not found" in message

    def test_missing_raw_folder_includes_suggestion(self, temp_dir):
        """Should include helpful suggestion for missing raw folder."""
        with pytest.raises(DataFileNotFoundError) as exc_info:
            parse_tsv_files(temp_dir / "nonexistent")

        assert "suggestion" in str(exc_info.value).lower()

    def test_empty_raw_folder_raises_error(self, temp_dir):
        """Should raise DataFileEmptyError when raw/ has no TSV files."""
        raw_dir = temp_dir / "raw"
        raw_dir.mkdir()

        with pytest.raises(DataFileEmptyError) as exc_info:
            parse_tsv_files(raw_dir)

        message = str(exc_info.value).lower()
        assert "no tsv files" in message

    def test_raw_folder_with_non_tsv_files(self, temp_dir):
        """Should raise error when raw/ has files but no TSV files."""
        raw_dir = temp_dir / "raw"
        raw_dir.mkdir()
        (raw_dir / "readme.txt").write_text("not a tsv")

        with pytest.raises(DataFileEmptyError) as exc_info:
            parse_tsv_files(raw_dir)

        assert "no tsv files" in str(exc_info.value).lower()


class TestTSVFileReading:
    """Tests for TSV file reading."""

    def test_empty_tsv_file_raises_error(self, temp_dir, create_tsv_file, empty_tsv_content):
        """Should raise DataFileEmptyError for empty TSV files."""
        create_tsv_file("test.tsv", empty_tsv_content)

        with pytest.raises(DataFileEmptyError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        assert "empty" in str(exc_info.value).lower()

    def test_whitespace_only_file_raises_error(
        self, temp_dir, create_tsv_file, whitespace_only_tsv_content
    ):
        """Should raise DataFileEmptyError for whitespace-only files."""
        create_tsv_file("test.tsv", whitespace_only_tsv_content)

        with pytest.raises(DataFileEmptyError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        assert "empty" in str(exc_info.value).lower()

    def test_header_only_tsv_raises_error(self, temp_dir, create_tsv_file, header_only_tsv_content):
        """Should raise TSVParseError for TSV with only header."""
        create_tsv_file("test.tsv", header_only_tsv_content)

        with pytest.raises(TSVParseError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        message = str(exc_info.value).lower()
        assert "header" in message or "data row" in message


class TestTSVRowParsing:
    """Tests for TSV row parsing and validation."""

    def test_malformed_row_raises_error(self, temp_dir, create_tsv_file, malformed_tsv_content):
        """Should raise TSVParseError for rows with insufficient columns."""
        create_tsv_file("test.tsv", malformed_tsv_content)

        with pytest.raises(TSVParseError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        message = str(exc_info.value).lower()
        assert "columns" in message

    def test_malformed_row_includes_line_number(
        self, temp_dir, create_tsv_file, malformed_tsv_content
    ):
        """Should include line number in TSVParseError for malformed rows."""
        create_tsv_file("test.tsv", malformed_tsv_content)

        with pytest.raises(TSVParseError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        assert exc_info.value.line_number is not None
        assert "line" in str(exc_info.value).lower()

    def test_empty_problem_name_raises_error(
        self, temp_dir, create_tsv_file, empty_name_tsv_content
    ):
        """Should raise TSVParseError when problem name is empty."""
        create_tsv_file("test.tsv", empty_name_tsv_content)

        with pytest.raises(TSVParseError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        message = str(exc_info.value).lower()
        assert "name" in message
        assert "empty" in message

    def test_skips_completely_empty_rows(self, temp_dir, create_tsv_file):
        """Should silently skip completely empty rows."""
        content = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table

3Sum\tMedium\t55\t40\t28\tTwo Pointers"""
        create_tsv_file("test.tsv", content)

        result = parse_tsv_files(temp_dir / "raw")

        assert len(result["data"]["test"]) == 2

    def test_skips_whitespace_only_rows(self, temp_dir, create_tsv_file):
        """Should silently skip rows with only whitespace/tabs."""
        content = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table
\t\t\t\t\t
3Sum\tMedium\t55\t40\t28\tTwo Pointers"""
        create_tsv_file("test.tsv", content)

        result = parse_tsv_files(temp_dir / "raw")

        assert len(result["data"]["test"]) == 2


class TestSuccessfulParsing:
    """Tests for successful parsing scenarios."""

    def test_valid_tsv_parses_correctly(self, temp_dir, create_tsv_file, valid_tsv_content):
        """Should correctly parse valid TSV content."""
        create_tsv_file("blind75.tsv", valid_tsv_content)

        result = parse_tsv_files(temp_dir / "raw")

        assert "blind75" in result["file_list"]
        assert len(result["data"]["blind75"]) == 2
        assert result["data"]["blind75"][0]["name"] == "Two Sum"
        assert result["data"]["blind75"][0]["difficulty"] == "Easy"
        assert result["data"]["blind75"][0]["pattern"] == "Hash Table"

    def test_multiple_tsv_files(self, temp_dir, create_tsv_file, valid_tsv_content):
        """Should parse multiple TSV files."""
        create_tsv_file("blind75.tsv", valid_tsv_content)
        create_tsv_file("neetcode150.tsv", valid_tsv_content)

        result = parse_tsv_files(temp_dir / "raw")

        assert len(result["file_list"]) == 2
        assert "blind75" in result["file_list"]
        assert "neetcode150" in result["file_list"]

    def test_duplicate_detection(self, temp_dir, create_tsv_file):
        """Should detect problems appearing in multiple files."""
        content1 = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table"""
        content2 = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table
3Sum\tMedium\t55\t40\t28\tTwo Pointers"""

        create_tsv_file("blind75.tsv", content1)
        create_tsv_file("neetcode150.tsv", content2)

        result = parse_tsv_files(temp_dir / "raw")

        assert "Two Sum" in result["duplicate_map"]
        assert len(result["duplicate_map"]["Two Sum"]) == 2

    def test_no_duplicates_when_unique(self, temp_dir, create_tsv_file):
        """Should have empty duplicate_map when all problems unique."""
        content1 = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table"""
        content2 = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
3Sum\tMedium\t55\t40\t28\tTwo Pointers"""

        create_tsv_file("blind75.tsv", content1)
        create_tsv_file("neetcode150.tsv", content2)

        result = parse_tsv_files(temp_dir / "raw")

        assert result["duplicate_map"] == {}

    def test_default_values_for_empty_fields(self, temp_dir, create_tsv_file):
        """Should use default values for empty optional fields."""
        content = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\t\t\t\t\t"""
        create_tsv_file("test.tsv", content)

        result = parse_tsv_files(temp_dir / "raw")

        problem = result["data"]["test"][0]
        assert problem["name"] == "Two Sum"
        assert problem["difficulty"] == "Unknown"
        assert problem["intermediate_time"] == "0"
        assert problem["advanced_time"] == "0"
        assert problem["top_time"] == "0"
        assert problem["pattern"] == "Unknown"

    def test_problem_has_all_expected_fields(self, temp_dir, create_tsv_file, valid_tsv_content):
        """Should include all expected fields in parsed problem."""
        create_tsv_file("test.tsv", valid_tsv_content)

        result = parse_tsv_files(temp_dir / "raw")

        problem = result["data"]["test"][0]
        expected_fields = [
            "name",
            "difficulty",
            "intermediate_time",
            "advanced_time",
            "top_time",
            "pattern",
            "solved",
            "time_to_solve",
            "comments",
            "solved_date",
        ]
        for field in expected_fields:
            assert field in problem

    def test_result_structure(self, temp_dir, create_tsv_file, valid_tsv_content):
        """Should return dict with expected keys."""
        create_tsv_file("test.tsv", valid_tsv_content)

        result = parse_tsv_files(temp_dir / "raw")

        assert "data" in result
        assert "duplicate_map" in result
        assert "file_list" in result
        assert isinstance(result["data"], dict)
        assert isinstance(result["duplicate_map"], dict)
        assert isinstance(result["file_list"], list)


class TestValidationErrors:
    """Tests for validation errors after parsing."""

    def test_all_empty_data_rows_raises_error(self, temp_dir, create_tsv_file):
        """Should raise ValidationError if all data rows are empty."""
        # Header + only whitespace rows
        content = """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern

\t\t\t\t\t
"""
        create_tsv_file("test.tsv", content)

        with pytest.raises(ValidationError) as exc_info:
            parse_tsv_files(temp_dir / "raw")

        assert "no problems parsed" in str(exc_info.value).lower()
