"""Tests for the custom exception hierarchy."""

from exceptions import (
    DataFileEmptyError,
    DataFileNotFoundError,
    FileIOError,
    GeneratorError,
    GrindPulseError,
    JSONParseError,
    ParseError,
    TSVParseError,
    ValidationError,
)


class TestGrindPulseError:
    """Tests for base exception class."""

    def test_basic_message(self):
        """Should create exception with just a message."""
        err = GrindPulseError("Something went wrong")
        assert "Something went wrong" in str(err)

    def test_with_file_path(self):
        """Should include file path in message."""
        err = GrindPulseError("Failed", file_path="/path/to/file.txt")
        message = str(err)
        assert "Failed" in message
        assert "/path/to/file.txt" in message
        assert "File:" in message

    def test_with_suggestion(self):
        """Should include suggestion in message."""
        err = GrindPulseError("Failed", suggestion="Try this instead")
        message = str(err)
        assert "Failed" in message
        assert "Try this instead" in message
        assert "Suggestion:" in message

    def test_with_all_context(self):
        """Should include all context in message."""
        err = GrindPulseError(
            "Failed to read",
            file_path="/path/file.txt",
            suggestion="Check permissions",
        )
        message = str(err)
        assert "Failed to read" in message
        assert "/path/file.txt" in message
        assert "Check permissions" in message

    def test_attributes_stored(self):
        """Should store file_path and suggestion as attributes."""
        err = GrindPulseError(
            "Error",
            file_path="/test/path",
            suggestion="Fix it",
        )
        assert err.file_path == "/test/path"
        assert err.suggestion == "Fix it"

    def test_none_attributes(self):
        """Should handle None attributes gracefully."""
        err = GrindPulseError("Error")
        assert err.file_path is None
        assert err.suggestion is None


class TestFileIOError:
    """Tests for FileIOError."""

    def test_inherits_from_grindpulse_error(self):
        """Should inherit from GrindPulseError."""
        err = FileIOError("IO failed")
        assert isinstance(err, GrindPulseError)

    def test_with_file_path(self):
        """Should accept file_path parameter."""
        err = FileIOError("Cannot read", file_path="/test.txt")
        assert "/test.txt" in str(err)


class TestDataFileNotFoundError:
    """Tests for DataFileNotFoundError."""

    def test_inherits_from_file_io_error(self):
        """Should inherit from FileIOError."""
        err = DataFileNotFoundError("Not found")
        assert isinstance(err, FileIOError)
        assert isinstance(err, GrindPulseError)

    def test_typical_usage(self):
        """Should work with typical missing file scenario."""
        err = DataFileNotFoundError(
            "parsed_data.json not found",
            file_path="/project/parsed_data.json",
            suggestion="Run data_parser.py first",
        )
        message = str(err)
        assert "parsed_data.json not found" in message
        assert "/project/parsed_data.json" in message
        assert "Run data_parser.py first" in message


class TestDataFileEmptyError:
    """Tests for DataFileEmptyError."""

    def test_inherits_from_file_io_error(self):
        """Should inherit from FileIOError."""
        err = DataFileEmptyError("File is empty")
        assert isinstance(err, FileIOError)

    def test_typical_usage(self):
        """Should work with typical empty file scenario."""
        err = DataFileEmptyError(
            "TSV file is empty",
            file_path="/raw/blind75.tsv",
            suggestion="Add problem data",
        )
        assert "TSV file is empty" in str(err)


class TestParseError:
    """Tests for ParseError base class."""

    def test_inherits_from_grindpulse_error(self):
        """Should inherit from GrindPulseError."""
        err = ParseError("Parse failed")
        assert isinstance(err, GrindPulseError)


class TestJSONParseError:
    """Tests for JSONParseError."""

    def test_inherits_from_parse_error(self):
        """Should inherit from ParseError."""
        err = JSONParseError("Invalid JSON")
        assert isinstance(err, ParseError)
        assert isinstance(err, GrindPulseError)

    def test_typical_usage(self):
        """Should work with typical JSON error scenario."""
        err = JSONParseError(
            "Invalid JSON: Expecting property name",
            file_path="/config.json",
            suggestion="Check JSON syntax",
        )
        message = str(err)
        assert "Invalid JSON" in message
        assert "/config.json" in message


class TestTSVParseError:
    """Tests for TSVParseError."""

    def test_inherits_from_parse_error(self):
        """Should inherit from ParseError."""
        err = TSVParseError("Invalid row", file_path="/test.tsv")
        assert isinstance(err, ParseError)

    def test_with_line_number(self):
        """Should include line number in message."""
        err = TSVParseError(
            "Invalid row",
            file_path="/data/test.tsv",
            line_number=42,
        )
        message = str(err)
        assert "line 42" in message
        assert "Invalid row" in message

    def test_without_line_number(self):
        """Should work without line number."""
        err = TSVParseError("Invalid format", file_path="/data/test.tsv")
        assert "line" not in str(err)

    def test_line_number_attribute(self):
        """Should store line_number as attribute."""
        err = TSVParseError("Error", file_path="/test.tsv", line_number=10)
        assert err.line_number == 10

    def test_with_all_parameters(self):
        """Should work with all parameters."""
        err = TSVParseError(
            "Missing columns",
            file_path="/raw/problems.tsv",
            line_number=5,
            suggestion="Add missing columns",
        )
        message = str(err)
        assert "Missing columns" in message
        assert "line 5" in message
        assert "/raw/problems.tsv" in message
        assert "Add missing columns" in message


class TestGeneratorError:
    """Tests for GeneratorError."""

    def test_wraps_original_error(self):
        """Should wrap and expose original error."""
        original = ValueError("bad input")
        err = GeneratorError("html_generator", original)
        assert err.original_error is original
        assert err.generator_name == "html_generator"

    def test_message_includes_generator_name(self):
        """Should include generator name in message."""
        original = TypeError("wrong type")
        err = GeneratorError("css_generator", original)
        message = str(err)
        assert "css_generator" in message
        assert "wrong type" in message

    def test_includes_suggestion(self):
        """Should include default suggestion."""
        err = GeneratorError("test_gen", Exception("error"))
        assert "Suggestion:" in str(err)

    def test_inherits_from_grindpulse_error(self):
        """Should inherit from GrindPulseError."""
        err = GeneratorError("gen", Exception())
        assert isinstance(err, GrindPulseError)


class TestValidationError:
    """Tests for ValidationError."""

    def test_inherits_from_grindpulse_error(self):
        """Should inherit from GrindPulseError."""
        err = ValidationError("Validation failed")
        assert isinstance(err, GrindPulseError)

    def test_typical_usage(self):
        """Should work with typical validation scenario."""
        err = ValidationError(
            "No problems parsed",
            suggestion="Check TSV files have data rows",
        )
        message = str(err)
        assert "No problems parsed" in message
        assert "Check TSV files" in message


class TestExceptionHierarchy:
    """Tests for exception class inheritance."""

    def test_file_io_inherits_from_base(self):
        """FileIOError should inherit from GrindPulseError."""
        assert issubclass(FileIOError, GrindPulseError)

    def test_parse_error_inherits_from_base(self):
        """ParseError should inherit from GrindPulseError."""
        assert issubclass(ParseError, GrindPulseError)

    def test_data_file_not_found_inherits_from_file_io(self):
        """DataFileNotFoundError should inherit from FileIOError."""
        assert issubclass(DataFileNotFoundError, FileIOError)

    def test_data_file_empty_inherits_from_file_io(self):
        """DataFileEmptyError should inherit from FileIOError."""
        assert issubclass(DataFileEmptyError, FileIOError)

    def test_json_parse_inherits_from_parse(self):
        """JSONParseError should inherit from ParseError."""
        assert issubclass(JSONParseError, ParseError)

    def test_tsv_parse_inherits_from_parse(self):
        """TSVParseError should inherit from ParseError."""
        assert issubclass(TSVParseError, ParseError)

    def test_generator_error_inherits_from_base(self):
        """GeneratorError should inherit from GrindPulseError."""
        assert issubclass(GeneratorError, GrindPulseError)

    def test_validation_error_inherits_from_base(self):
        """ValidationError should inherit from GrindPulseError."""
        assert issubclass(ValidationError, GrindPulseError)

    def test_can_catch_all_with_base(self):
        """Should be able to catch all errors with GrindPulseError."""
        errors = [
            FileIOError("test"),
            DataFileNotFoundError("test"),
            DataFileEmptyError("test"),
            ParseError("test"),
            JSONParseError("test"),
            TSVParseError("test", file_path="/test"),
            GeneratorError("test", Exception()),
            ValidationError("test"),
        ]
        for err in errors:
            try:
                raise err
            except GrindPulseError:
                pass  # Should catch all
