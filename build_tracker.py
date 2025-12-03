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

def build_tracker():
    """Build the complete tracker.html file"""

    # Load parsed data
    with open('parsed_data.json', 'r', encoding='utf-8') as f:
        parsed_data = json.load(f)

    print("Building tracker.html...")
    print(f"  Files: {len(parsed_data['file_list'])}")
    print(f"  Total problems: {sum(len(parsed_data['data'][f]) for f in parsed_data['file_list'])}")
    print(f"  Duplicates: {len(parsed_data['duplicate_map'])}")

    # Generate components
    print("\nGenerating components...")
    html_structure = generate_html_structure(parsed_data['file_list'])
    css = generate_css()
    js_core = generate_js_core()
    js_sync = generate_js_sync()

    # Embed data as JavaScript
    data_js = f'''
const PROBLEM_DATA = {json.dumps(parsed_data, indent=2)};
const DUPLICATE_MAP = PROBLEM_DATA.duplicate_map;
    '''

    # Combine all JavaScript
    full_js = data_js + "\n" + js_core + "\n" + js_sync

    # Replace placeholders
    final_html = html_structure.replace('{CSS_PLACEHOLDER}', css)
    final_html = final_html.replace('{DATA_PLACEHOLDER}', '')
    final_html = final_html.replace('{JS_PLACEHOLDER}', full_js)

    # Write final file
    output_path = Path(__file__).parent / 'tracker.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"\nSuccessfully created: {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")

    return str(output_path)

if __name__ == "__main__":
    build_tracker()
