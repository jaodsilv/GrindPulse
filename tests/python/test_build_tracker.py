"""Tests for build_tracker.py error handling."""

import json
from unittest.mock import MagicMock, patch

import pytest

from build_tracker import (
    load_firebase_config,
    load_parsed_data,
    main,
    run_generator,
    write_output,
)
from exceptions import (
    DataFileNotFoundError,
    FileIOError,
    GeneratorError,
    JSONParseError,
)


class TestLoadParsedData:
    """Tests for load_parsed_data function."""

    def test_missing_file_raises_error(self, temp_dir, monkeypatch):
        """Should raise DataFileNotFoundError when parsed_data.json missing."""
        # Change to temp_dir so __file__ resolution finds nothing
        monkeypatch.chdir(temp_dir)

        # Patch the module's __file__ attribute
        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(DataFileNotFoundError) as exc_info:
                load_parsed_data()

            assert "parsed_data.json" in str(exc_info.value)
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_empty_file_raises_error(self, temp_dir, monkeypatch):
        """Should raise DataFileNotFoundError when file is empty."""
        (temp_dir / "parsed_data.json").write_text("")

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(DataFileNotFoundError) as exc_info:
                load_parsed_data()

            assert "empty" in str(exc_info.value).lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_whitespace_only_file_raises_error(self, temp_dir, monkeypatch):
        """Should raise DataFileNotFoundError when file has only whitespace."""
        (temp_dir / "parsed_data.json").write_text("   \n\t  ")

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(DataFileNotFoundError) as exc_info:
                load_parsed_data()

            assert "empty" in str(exc_info.value).lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_invalid_json_raises_error(self, temp_dir, monkeypatch):
        """Should raise JSONParseError for malformed JSON."""
        (temp_dir / "parsed_data.json").write_text("{invalid json")

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(JSONParseError) as exc_info:
                load_parsed_data()

            assert "invalid json" in str(exc_info.value).lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_missing_required_keys_raises_error(self, temp_dir, monkeypatch):
        """Should raise JSONParseError when required keys missing."""
        (temp_dir / "parsed_data.json").write_text(json.dumps({"data": {}}))

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(JSONParseError) as exc_info:
                load_parsed_data()

            message = str(exc_info.value).lower()
            assert "missing" in message
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_missing_some_keys_lists_them(self, temp_dir, monkeypatch):
        """Should list missing keys in error message."""
        (temp_dir / "parsed_data.json").write_text(json.dumps({"data": {}, "file_list": []}))

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(JSONParseError) as exc_info:
                load_parsed_data()

            assert "duplicate_map" in str(exc_info.value)
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_valid_file_loads_correctly(self, temp_dir, valid_parsed_data, monkeypatch):
        """Should load valid parsed_data.json correctly."""
        (temp_dir / "parsed_data.json").write_text(json.dumps(valid_parsed_data))

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            result = load_parsed_data()

            assert result["file_list"] == ["blind75"]
            assert "blind75" in result["data"]
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)


class TestLoadFirebaseConfig:
    """Tests for load_firebase_config function."""

    def test_missing_file_returns_none(self, temp_dir, monkeypatch, capsys):
        """Should return None when firebase_config.json doesn't exist."""
        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            result = load_firebase_config()

            assert result is None
            captured = capsys.readouterr()
            assert "not found" in captured.out.lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_empty_file_returns_none(self, temp_dir, monkeypatch, capsys):
        """Should return None for empty config file."""
        (temp_dir / "firebase_config.json").write_text("")

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            result = load_firebase_config()

            assert result is None
            captured = capsys.readouterr()
            assert "empty" in captured.out.lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_invalid_json_raises_error(self, temp_dir, monkeypatch):
        """Should raise JSONParseError for invalid JSON."""
        (temp_dir / "firebase_config.json").write_text("{bad json")

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(JSONParseError) as exc_info:
                load_firebase_config()

            assert "firebase_config.json" in str(exc_info.value)
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_valid_config_loads_correctly(self, temp_dir, monkeypatch, capsys):
        """Should load valid firebase config."""
        config = {"apiKey": "test-key", "projectId": "test-project"}
        (temp_dir / "firebase_config.json").write_text(json.dumps(config))

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            result = load_firebase_config()

            assert result["apiKey"] == "test-key"
            captured = capsys.readouterr()
            assert "loaded" in captured.out.lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)


class TestRunGenerator:
    """Tests for run_generator wrapper function."""

    def test_successful_generator_returns_result(self):
        """Should return generator result on success."""

        def mock_generator(x):
            return x * 2

        result = run_generator("test_gen", mock_generator, 5)
        assert result == 10

    def test_generator_with_kwargs(self):
        """Should pass kwargs to generator."""

        def mock_generator(a, b=10):
            return a + b

        result = run_generator("test_gen", mock_generator, 5, b=20)
        assert result == 25

    def test_failed_generator_raises_generator_error(self):
        """Should wrap exceptions in GeneratorError."""

        def failing_generator():
            raise ValueError("bad input")

        with pytest.raises(GeneratorError) as exc_info:
            run_generator("failing_gen", failing_generator)

        assert "failing_gen" in str(exc_info.value)
        assert "bad input" in str(exc_info.value)

    def test_generator_error_preserves_original(self):
        """Should preserve original exception in GeneratorError."""
        original = TypeError("wrong type")

        def failing_generator():
            raise original

        with pytest.raises(GeneratorError) as exc_info:
            run_generator("test_gen", failing_generator)

        assert exc_info.value.original_error is original


class TestWriteOutput:
    """Tests for write_output function."""

    def test_successful_write(self, temp_dir):
        """Should write content to file successfully."""
        output_path = temp_dir / "test.html"

        write_output("<html></html>", output_path)

        assert output_path.exists()
        assert output_path.read_text() == "<html></html>"

    def test_overwrites_existing_file(self, temp_dir):
        """Should overwrite existing file."""
        output_path = temp_dir / "test.html"
        output_path.write_text("old content")

        write_output("new content", output_path)

        assert output_path.read_text() == "new content"

    def test_permission_error_raises_file_io_error(self, temp_dir):
        """Should raise FileIOError on permission denied."""
        output_path = temp_dir / "readonly.html"

        with patch("builtins.open", side_effect=PermissionError("denied")):
            with pytest.raises(FileIOError) as exc_info:
                write_output("<html></html>", output_path)

            assert "permission" in str(exc_info.value).lower()

    def test_os_error_raises_file_io_error(self, temp_dir):
        """Should raise FileIOError on OS error (disk full, etc)."""
        output_path = temp_dir / "test.html"

        with patch("builtins.open", side_effect=OSError("No space left")):
            with pytest.raises(FileIOError) as exc_info:
                write_output("<html></html>", output_path)

            assert "no space left" in str(exc_info.value).lower()


class TestMainFunction:
    """Tests for main entry point."""

    def test_returns_one_on_grindpulse_error(self, temp_dir, monkeypatch, capsys):
        """Should return 1 on GrindPulseError."""
        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            exit_code = main()

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "error" in captured.err.lower()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_returns_one_on_unexpected_error(self, monkeypatch, capsys):
        """Should return 1 on unexpected exception."""
        with patch("build_tracker.load_parsed_data", side_effect=RuntimeError("unexpected")):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "unexpected" in captured.err.lower()

    def test_returns_130_on_keyboard_interrupt(self, monkeypatch, capsys):
        """Should return 130 on KeyboardInterrupt."""
        with patch("build_tracker.load_parsed_data", side_effect=KeyboardInterrupt):
            exit_code = main()

        assert exit_code == 130
        captured = capsys.readouterr()
        assert "interrupted" in captured.err.lower()

    def test_error_message_goes_to_stderr(self, temp_dir, monkeypatch, capsys):
        """Should print error messages to stderr."""
        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            main()
            captured = capsys.readouterr()
            assert captured.err  # Something was written to stderr
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_returns_zero_on_success(self, temp_dir, valid_parsed_data, monkeypatch):
        """Should return 0 on successful build."""
        # Write parsed_data.json
        (temp_dir / "parsed_data.json").write_text(json.dumps(valid_parsed_data))

        import build_tracker

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        # Mock all generators
        mock_html = MagicMock(return_value="{CSS_PLACEHOLDER}{DATA_PLACEHOLDER}{JS_PLACEHOLDER}")
        mock_css = MagicMock(return_value="/* CSS */")
        mock_js = MagicMock(return_value="// JS")

        try:
            with (
                patch.object(build_tracker, "generate_html_structure", mock_html),
                patch.object(build_tracker, "generate_css", mock_css),
                patch.object(build_tracker, "generate_js_awareness", mock_js),
                patch.object(build_tracker, "generate_js_settings", mock_js),
                patch.object(build_tracker, "generate_js_config_sync", mock_js),
                patch.object(build_tracker, "generate_js_import_export", mock_js),
                patch.object(build_tracker, "generate_js_conflict_dialog", mock_js),
                patch.object(build_tracker, "generate_js_shared", mock_js),
                patch.object(build_tracker, "generate_js_firebase", mock_js),
                patch.object(build_tracker, "generate_js_core", mock_js),
                patch.object(build_tracker, "generate_js_sync", mock_js),
            ):
                exit_code = main()

            assert exit_code == 0
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)


class TestBuildTrackerIntegration:
    """Integration-style tests for build_tracker function."""

    def test_propagates_load_errors(self, temp_dir, monkeypatch):
        """Should propagate errors from load_parsed_data."""
        import build_tracker
        from build_tracker import build_tracker as build_tracker_func

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with pytest.raises(DataFileNotFoundError):
                build_tracker_func()
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)

    def test_propagates_generator_errors(self, temp_dir, valid_parsed_data, monkeypatch):
        """Should propagate errors from generators."""
        (temp_dir / "parsed_data.json").write_text(json.dumps(valid_parsed_data))

        import build_tracker
        from build_tracker import build_tracker as build_tracker_func

        original_file = build_tracker.__file__
        monkeypatch.setattr(build_tracker, "__file__", str(temp_dir / "build_tracker.py"))

        try:
            with patch.object(
                build_tracker, "generate_html_structure", side_effect=Exception("generator failed")
            ):
                with pytest.raises(GeneratorError) as exc_info:
                    build_tracker_func()

                assert "html_generator" in str(exc_info.value)
        finally:
            monkeypatch.setattr(build_tracker, "__file__", original_file)
