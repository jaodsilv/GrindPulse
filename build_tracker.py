#!/usr/bin/env python3
"""
Final Integration Script
Assembles all components into tracker.html
"""

import json
import sys
from pathlib import Path

# Import sub-agent generators
sys.path.insert(0, str(Path(__file__).parent))
from html_generator import generate_html_structure
from css_generator import generate_css
from js_core_generator import generate_js_core
from js_sync_generator import generate_js_sync
from js_awareness_generator import generate_js_awareness
from js_settings_generator import generate_js_settings
from js_config_sync_generator import generate_js_config_sync
from js_import_export_generator import generate_js_import_export
from js_conflict_dialog_generator import generate_js_conflict_dialog
from js_shared_generator import generate_js_shared
from js_firebase_generator import generate_js_firebase


def build_tracker():
    """Build the complete tracker.html file"""

    # Load parsed data
    with open("parsed_data.json", "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    # Load Firebase config if it exists
    firebase_config = None
    firebase_config_path = Path(__file__).parent / "firebase_config.json"
    if firebase_config_path.exists():
        with open(firebase_config_path, "r", encoding="utf-8") as f:
            firebase_config = json.load(f)
        print(f"  Firebase config: loaded from {firebase_config_path.name}")
    else:
        print("  Firebase config: not found (cloud sync disabled)")

    print("Building tracker.html...")
    print(f"  Files: {len(parsed_data['file_list'])}")
    print(
        f"  Total problems: {sum(len(parsed_data['data'][f]) for f in parsed_data['file_list'])}"
    )
    print(f"  Duplicates: {len(parsed_data['duplicate_map'])}")

    # Generate components
    print("\nGenerating components...")
    firebase_enabled = firebase_config is not None
    html_structure = generate_html_structure(parsed_data["file_list"], firebase_enabled)
    css = generate_css()
    js_awareness = generate_js_awareness()
    js_settings = generate_js_settings()
    js_config_sync = generate_js_config_sync()
    js_import_export = generate_js_import_export()
    js_conflict_dialog = generate_js_conflict_dialog()
    js_shared = generate_js_shared()
    js_firebase = generate_js_firebase(firebase_config)
    js_core = generate_js_core()
    js_sync = generate_js_sync()

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
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"\nSuccessfully created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")

    return str(output_path)


if __name__ == "__main__":
    build_tracker()
