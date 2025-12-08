# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Offline-first web application for tracking coding interview preparation progress across multiple problem lists (Blind 75, NeetCode 150/250, Salesforce). Generates a single self-contained HTML file with embedded CSS/JS from Python scripts.

## Build Commands

```bash
python build_tracker.py    # Generate tracker.html from TSV data
```

## Test Commands

```bash
cd tests && npm test              # Run all tests
cd tests && npm run test:watch    # Watch mode
cd tests && npm run test:coverage # With coverage report (90% threshold)
```

## Architecture

### Build Pipeline (Python → HTML)

The project uses a multi-agent generation pattern where Python scripts create different aspects of the final HTML:

1. `data_parser.py` - Parses TSV files, detects duplicates across problem lists
2. `html_generator.py` - Creates HTML structure with dynamic tabs
3. `css_generator.py` - Generates embedded CSS styling
4. `js_core_generator.py` - Core JavaScript (tabs, filters, localStorage, exports)
5. `js_sync_generator.py` - Cross-file synchronization for duplicate problems
6. `js_awareness_generator.py` - Spaced repetition awareness color indicators
7. `js_settings_generator.py` - Settings panel UI
8. `js_import_export_generator.py` - Multi-format import/export (TSV, CSV, JSON, XML, YAML)
9. `js_conflict_dialog_generator.py` - Import conflict resolution dialog
10. `js_firebase_generator.py` - Optional Firebase cloud sync (if `firebase_config.json` exists)
11. `build_tracker.py` - Orchestrates all generators into single `tracker.html`

### Key Design Patterns

- **Single-File Delivery**: All CSS/JS/data embedded in tracker.html
- **Data-Driven UI**: Problem data embedded as JSON; UI renders dynamically
- **Cross-File Sync**: Updates to duplicate problems sync across all lists via `DUPLICATE_MAP`
- **Offline-First**: Uses browser localStorage; no server required
- **Conditional Features**: Firebase sync only enabled when config file exists

### JavaScript Dependency Order

Components must be combined in this order (set in `build_tracker.py`):
1. Data (PROBLEM_DATA, DUPLICATE_MAP)
2. Awareness algorithm
3. Settings
4. Import/Export
5. Conflict Dialog
6. Firebase
7. Core logic
8. Sync engine

## Testing

### Test Architecture

- **Framework**: Jest with ES modules (`--experimental-vm-modules`)
- **Coverage Target**: 90% (branches, functions, lines, statements)
- **Test Isolation**: Each test resets state via `beforeEach()`
- **Location**: `tests/awareness.js` contains testable copy of awareness functions

### Important: Test Sync Requirement

The awareness functions in `tests/awareness.js` are extracted from `js_awareness_generator.py`. When modifying awareness logic, update both:
1. `js_awareness_generator.py` (source of truth for tracker.html)
2. `tests/awareness.js` (testable module)

## File Structure

```
├── build_tracker.py           # Run this to regenerate tracker.html
├── tracker.html               # GENERATED OUTPUT - do not edit directly
├── parsed_data.json           # Intermediate data (auto-generated)
├── firebase_config.json       # Optional Firebase config
├── raw/                       # TSV source data - edit these to modify problems
│   ├── blind75.tsv
│   ├── neetcode150.tsv
│   ├── neetcode250.tsv
│   └── salesforce.tsv
├── *_generator.py             # Code generation scripts
└── tests/
    ├── awareness.js           # Testable awareness functions
    ├── awareness.test.js      # Test suite
    └── package.json           # Jest configuration
```

## Adding New Problem Lists

1. Create new TSV file in `raw/` with columns: Name, Difficulty, IntermediateTime, AdvancedTime, TopTime, Pattern, Solved, TimeToSolve, Comments, SolvedDate
2. Run `python build_tracker.py` - new tab auto-created from filename

## Adding New JavaScript Features

1. Create new generator file: `js_<feature>_generator.py`
2. Add `generate_js_<feature>()` function returning JavaScript string
3. Import in `build_tracker.py` and add to `full_js` concatenation (respecting dependency order)
4. Update HTML generator if new UI elements needed
