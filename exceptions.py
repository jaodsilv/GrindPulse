#!/usr/bin/env python3
"""
Custom Exception Hierarchy for GrindPulse Build Pipeline

Provides clear, actionable error messages for common failure modes.
"""


class GrindPulseError(Exception):
    """Base exception for all GrindPulse build errors."""

    def __init__(
        self, message: str, file_path: str | None = None, suggestion: str | None = None
    ) -> None:
        self.file_path = file_path
        self.suggestion = suggestion
        full_message = message
        if file_path:
            full_message = f"{message}\n  File: {file_path}"
        if suggestion:
            full_message = f"{full_message}\n  Suggestion: {suggestion}"
        super().__init__(full_message)


class FileIOError(GrindPulseError):
    """Raised when file read/write operations fail."""

    pass


class DataFileNotFoundError(FileIOError):
    """Raised when a required data file is missing."""

    pass


class DataFileEmptyError(FileIOError):
    """Raised when a data file exists but is empty."""

    pass


class ParseError(GrindPulseError):
    """Base class for parsing errors."""

    pass


class JSONParseError(ParseError):
    """Raised when JSON parsing fails."""

    pass


class TSVParseError(ParseError):
    """Raised when TSV parsing fails."""

    def __init__(
        self,
        message: str,
        file_path: str,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.line_number = line_number
        if line_number:
            message = f"{message} (line {line_number})"
        super().__init__(message, file_path, suggestion)


class GeneratorError(GrindPulseError):
    """Raised when a generator function fails."""

    def __init__(self, generator_name: str, original_error: Exception) -> None:
        self.generator_name = generator_name
        self.original_error = original_error
        message = f"Generator '{generator_name}' failed: {original_error}"
        suggestion = "Check generator function implementation and input data"
        super().__init__(message, suggestion=suggestion)


class ValidationError(GrindPulseError):
    """Raised when data validation fails."""

    pass
