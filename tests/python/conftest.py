"""Pytest fixtures for GrindPulse Python tests."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def valid_tsv_content():
    """Valid TSV file content with header and data rows."""
    return """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy\t25\t15\t8\tHash Table
3Sum\tMedium\t55\t40\t28\tTwo Pointers + Sorting"""


@pytest.fixture
def empty_tsv_content():
    """Empty TSV file content."""
    return ""


@pytest.fixture
def whitespace_only_tsv_content():
    """TSV file with only whitespace."""
    return "   \n\t\n  "


@pytest.fixture
def header_only_tsv_content():
    """TSV with only header row."""
    return "Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern"


@pytest.fixture
def malformed_tsv_content():
    """TSV with malformed rows (missing columns)."""
    return """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
Two Sum\tEasy"""


@pytest.fixture
def empty_name_tsv_content():
    """TSV with empty problem name."""
    return """Problem Name\tDifficulty\tIntermediate Max time\tAdvanced Max time\tTop of the crop max time\tProblem Pattern
\tEasy\t25\t15\t8\tHash Table"""


@pytest.fixture
def valid_parsed_data():
    """Valid parsed_data.json structure."""
    return {
        "data": {
            "blind75": [
                {
                    "name": "Two Sum",
                    "difficulty": "Easy",
                    "intermediate_time": "25",
                    "advanced_time": "15",
                    "top_time": "8",
                    "pattern": "Hash Table",
                    "solved": False,
                    "time_to_solve": "",
                    "comments": "",
                    "solved_date": "",
                }
            ]
        },
        "duplicate_map": {},
        "file_list": ["blind75"],
    }


@pytest.fixture
def create_tsv_file(temp_dir):
    """Factory fixture to create TSV files in raw/ subdirectory."""

    def _create(filename: str, content: str):
        raw_dir = temp_dir / "raw"
        raw_dir.mkdir(exist_ok=True)
        file_path = raw_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create


@pytest.fixture
def create_json_file(temp_dir):
    """Factory fixture to create JSON files."""

    def _create(filename: str, data):
        file_path = temp_dir / filename
        if isinstance(data, dict):
            file_path.write_text(json.dumps(data), encoding="utf-8")
        else:
            # Allow writing raw string content (for invalid JSON tests)
            file_path.write_text(data, encoding="utf-8")
        return file_path

    return _create


@pytest.fixture
def mock_generators(monkeypatch):
    """Mock all generator functions to return minimal valid content."""
    from unittest.mock import MagicMock

    # Create mock functions that return valid strings
    mock_html = MagicMock(return_value="{CSS_PLACEHOLDER}{DATA_PLACEHOLDER}{JS_PLACEHOLDER}")
    mock_css = MagicMock(return_value="/* CSS */")
    mock_js = MagicMock(return_value="// JS")

    # Patch all generators
    import build_tracker

    monkeypatch.setattr(build_tracker, "generate_html_structure", mock_html)
    monkeypatch.setattr(build_tracker, "generate_css", mock_css)
    monkeypatch.setattr(build_tracker, "generate_js_awareness", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_settings", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_config_sync", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_import_export", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_conflict_dialog", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_shared", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_firebase", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_core", mock_js)
    monkeypatch.setattr(build_tracker, "generate_js_sync", mock_js)

    return {
        "html": mock_html,
        "css": mock_css,
        "js": mock_js,
    }
