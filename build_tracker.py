#!/usr/bin/env python3
"""
Final Integration Script
Assembles all components into tracker.html
"""

import json
import sys
from pathlib import Path

from exceptions import (
    DataFileNotFoundError,
    FileIOError,
    GeneratorError,
    GrindPulseError,
    JSONParseError,
)

# Import sub-agent generators
sys.path.insert(0, str(Path(__file__).parent))
from css_generator import generate_css
from html_generator import generate_html_structure
from js_awareness_generator import generate_js_awareness
from js_config_sync_generator import generate_js_config_sync
from js_conflict_dialog_generator import generate_js_conflict_dialog
from js_core_generator import generate_js_core
from js_firebase_generator import generate_js_firebase
from js_import_export_generator import generate_js_import_export
from js_settings_generator import generate_js_settings
from js_shared_generator import generate_js_shared
from js_sync_generator import generate_js_sync


def load_parsed_data() -> dict:
    """Load and validate parsed_data.json.

    Returns:
        Parsed data dictionary with keys: data, duplicate_map, file_list

    Raises:
        DataFileNotFoundError: If file is missing or empty
        FileIOError: If file cannot be read (permission denied, I/O error)
        JSONParseError: If JSON is invalid or missing required keys
    """
    parsed_data_path = Path(__file__).parent / "parsed_data.json"

    if not parsed_data_path.exists():
        raise DataFileNotFoundError(
            "parsed_data.json not found",
            file_path=str(parsed_data_path),
            suggestion="Run data_parser.py first to generate parsed_data.json",
        )

    try:
        with open(parsed_data_path, encoding="utf-8") as f:
            content = f.read()
    except PermissionError as err:
        raise FileIOError(
            "Permission denied reading parsed_data.json",
            file_path=str(parsed_data_path),
            suggestion="Check file permissions",
        ) from err
    except OSError as err:
        raise FileIOError(
            f"I/O error reading parsed_data.json: {err}",
            file_path=str(parsed_data_path),
            suggestion="Check file accessibility and system resources",
        ) from err

    if not content.strip():
        raise DataFileNotFoundError(
            "parsed_data.json is empty",
            file_path=str(parsed_data_path),
            suggestion="Regenerate by running data_parser.py",
        )

    try:
        parsed_data = json.loads(content)
    except json.JSONDecodeError as e:
        raise JSONParseError(
            f"Invalid JSON in parsed_data.json: {e}",
            file_path=str(parsed_data_path),
            suggestion="Regenerate by running data_parser.py",
        ) from e

    # Validate expected structure
    required_keys = ["data", "duplicate_map", "file_list"]
    missing = [k for k in required_keys if k not in parsed_data]
    if missing:
        raise JSONParseError(
            f"parsed_data.json missing required keys: {missing}",
            file_path=str(parsed_data_path),
            suggestion="Regenerate by running data_parser.py",
        )

    return parsed_data


def load_firebase_config() -> dict | None:
    """Load Firebase config if it exists.

    This function implements graceful degradation for optional Firebase cloud sync:
    - Missing file: Returns None (feature not configured - normal case)
    - Permission error: Prints warning, returns None (user sees warning, app continues offline)
    - Empty file: Prints warning, returns None (likely incomplete setup)
    - Invalid JSON: Raises error (user intended to configure but config is broken)

    This behavior is intentional: Firebase is an optional enhancement, not a required
    feature. Users should be able to use the tracker offline without any Firebase setup.

    Returns:
        Firebase config dictionary, or None if not configured/accessible

    Raises:
        JSONParseError: If file exists with content but contains invalid JSON
    """
    firebase_config_path = Path(__file__).parent / "firebase_config.json"

    if not firebase_config_path.exists():
        print("  Firebase config: not found (cloud sync disabled)")
        return None

    try:
        with open(firebase_config_path, encoding="utf-8") as f:
            content = f.read()
    except PermissionError:
        print(f"  Warning: Cannot read {firebase_config_path.name} (permission denied)")
        return None

    if not content.strip():
        print(f"  Warning: {firebase_config_path.name} is empty, skipping")
        return None

    try:
        config = json.loads(content)
    except json.JSONDecodeError as e:
        raise JSONParseError(
            f"Invalid JSON in firebase_config.json: {e}",
            file_path=str(firebase_config_path),
            suggestion="Fix JSON syntax or remove file to disable Firebase",
        ) from e

    print(f"  Firebase config: loaded from {firebase_config_path.name}")
    return config


def run_generator(name: str, func, *args, **kwargs):
    """Run a generator function with error handling.

    This function intentionally catches all exceptions (not just specific types)
    to provide consistent error handling for the 10+ generator functions in the
    build pipeline. By wrapping ANY exception in GeneratorError, we ensure:

    1. Consistent error formatting with generator name context
    2. Programming errors (AttributeError, NameError, etc.) are properly reported
    3. The full exception chain is preserved via 'from e' for debugging

    Narrowing the catch would defeat the purpose - generator bugs are exactly
    what this wrapper should catch and report with context.

    Args:
        name: Name of the generator (for error messages)
        func: Generator function to call
        *args: Positional arguments for the generator
        **kwargs: Keyword arguments for the generator

    Returns:
        Result from the generator function

    Raises:
        GeneratorError: Wraps any exception from the generator function
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise GeneratorError(name, e) from e


def write_output(content: str, output_path: Path) -> None:
    """Write final HTML output with error handling.

    Args:
        content: HTML content to write
        output_path: Path to write the file to

    Raises:
        FileIOError: If write fails (permission, disk space, etc.)
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    except PermissionError as err:
        raise FileIOError(
            "Permission denied writing tracker.html",
            file_path=str(output_path),
            suggestion="Close any programs using the file and check write permissions",
        ) from err
    except OSError as e:
        raise FileIOError(
            f"Failed to write tracker.html: {e}",
            file_path=str(output_path),
            suggestion="Check disk space and directory permissions",
        ) from e


def build_tracker() -> str:
    """Build the complete tracker.html file.

    Returns:
        Path to the generated tracker.html file

    Raises:
        GrindPulseError: If any step of the build process fails
    """
    # Load parsed data with error handling
    parsed_data = load_parsed_data()

    # Load Firebase config (optional)
    firebase_config = load_firebase_config()

    print("Building tracker.html...")
    print(f"  Files: {len(parsed_data['file_list'])}")
    print(f"  Total problems: {sum(len(parsed_data['data'][f]) for f in parsed_data['file_list'])}")
    print(f"  Duplicates: {len(parsed_data['duplicate_map'])}")

    # Generate components with error handling
    print("\nGenerating components...")
    firebase_enabled = firebase_config is not None

    html_structure = run_generator(
        "html_generator", generate_html_structure, parsed_data["file_list"], firebase_enabled
    )
    css = run_generator("css_generator", generate_css)
    js_awareness = run_generator("js_awareness_generator", generate_js_awareness)
    js_settings = run_generator("js_settings_generator", generate_js_settings)
    js_config_sync = run_generator("js_config_sync_generator", generate_js_config_sync)
    js_import_export = run_generator("js_import_export_generator", generate_js_import_export)
    js_conflict_dialog = run_generator("js_conflict_dialog_generator", generate_js_conflict_dialog)
    js_shared = run_generator("js_shared_generator", generate_js_shared)
    js_firebase = run_generator("js_firebase_generator", generate_js_firebase, firebase_config)
    js_core = run_generator("js_core_generator", generate_js_core)
    js_sync = run_generator("js_sync_generator", generate_js_sync)

    # Embed data as JavaScript
    data_js = f"""
const PROBLEM_DATA = {json.dumps(parsed_data, indent=2)};
const DUPLICATE_MAP = PROBLEM_DATA.duplicate_map;
    """

    # Combine all JavaScript (order matters: data -> shared -> awareness -> settings -> config_sync -> import_export -> conflict_dialog -> firebase -> core -> sync)
    full_js = (
        data_js
        + "\n"
        + js_shared
        + "\n"
        + js_awareness
        + "\n"
        + js_settings
        + "\n"
        + js_config_sync
        + "\n"
        + js_import_export
        + "\n"
        + js_conflict_dialog
        + "\n"
        + js_firebase
        + "\n"
        + js_core
        + "\n"
        + js_sync
    )

    # Replace placeholders
    # NOTE: DATA_PLACEHOLDER is replaced with empty string because data is now
    # embedded directly in full_js as the data_js component. The placeholder
    # remains in html_generator.py for backward compatibility and clarity.
    final_html = html_structure.replace("{CSS_PLACEHOLDER}", css)
    final_html = final_html.replace("{DATA_PLACEHOLDER}", "")
    final_html = final_html.replace("{JS_PLACEHOLDER}", full_js)

    # Write final file
    output_path = Path(__file__).parent / "tracker.html"
    write_output(final_html, output_path)

    print(f"\nSuccessfully created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")

    return str(output_path)


def main() -> int:
    """Main entry point with exit code handling.

    Returns:
        Exit code: 0 for success, 1 for error, 130 for interrupt
    """
    try:
        build_tracker()
        return 0
    except GrindPulseError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nBuild interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nUnexpected error ({type(e).__name__}): {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
