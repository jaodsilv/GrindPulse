# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**GrindPulse** - Offline-first web application for tracking coding interview preparation progress across multiple problem lists (Blind 75, NeetCode 150/250, Salesforce). Generates a single self-contained HTML file with embedded CSS/JS from Python scripts.

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

## Release Process

The release workflow uses a PR-based approach to respect branch protection rules on main.

### Trigger Options

The release can be triggered in two ways:

1. **Manual (`workflow_dispatch`)**: Run from GitHub Actions UI with version bump type selection
   - Choose bump type: `patch`, `minor`, or `major`
   - Optional `dry_run` mode to validate without creating releases
2. **Tag Push**: Push a tag matching `v*.*.*` pattern (e.g., `git tag v1.2.3 && git push --tags`)
   - Skips version bump PR creation (tag already exists)
   - Only runs build, test, and GitHub Release creation
   - Useful for manual releases or re-releasing existing tags

### How Releases Work

When triggered via `workflow_dispatch`:

1. **Validation**: Calculates the new version based on bump type (patch/minor/major)
2. **Build**: Creates the `tracker.html` artifact
3. **Test**: Runs the test suite to validate the build
4. **Changelog**: Generates changelog from commits since last tag
5. **Release**:
   - Creates a `release/version-bump-X.Y.Z` branch with updated `version.txt`
   - Opens a PR for manual approval (respects branch protection)
   - Creates the git tag via GitHub API (immediate)
   - Creates the GitHub Release with attached `tracker.html`

### Post-Release Steps

After the release workflow completes:

1. Review and merge the version bump PR to update `version.txt` on main
2. The release and tag are already created and available

**Note:** There is a brief period where the tag exists but `version.txt` on main still shows the previous version. This is expected and resolves once the version bump PR is merged.

### Dry Run Mode

Use `dry_run: true` to validate the release process without:
- Creating branches or PRs
- Creating tags
- Publishing GitHub Releases

Useful for testing version calculations and build/test pipelines.

**Note:** Build artifacts are still uploaded during dry runs (consumes storage with 90-day retention).

### Tag Semantics

The release tag points to the main branch HEAD at the time of release (before the version bump commit). This is intentional:
- The tag represents the exact code that was built and tested
- The version bump PR is a metadata-only change that follows the release
- This ensures the tagged commit matches what users download

### Design Decision (Issue #12)

The PR-based approach was chosen over direct push to main because:

1. Respects existing branch protection rules
2. Maintains audit trail through PR history
3. Does not require additional PAT secrets
4. Tags are created via GitHub API (not affected by branch protection)

### Branch Cleanup

After merging version bump PRs, the `release/version-bump-X.Y.Z` branches remain. To automatically clean up merged branches, enable "Automatically delete head branches" in repository settings (Settings > General > Pull Requests).

### Required Permissions

The release workflow requires these GitHub token permissions:

- `contents: write` - Create tags, push branches, upload release assets
- `pull-requests: write` - Create and manage version bump PRs

### Troubleshooting

Common failure scenarios and recovery steps:

1. **Branch already exists error**
   - Cause: Previous workflow run failed after creating branch but before completing
   - Fix: Delete the orphan branch manually: `git push origin --delete release/version-bump-X.Y.Z`

2. **Tag creation failed but PR was created**
   - The workflow automatically attempts cleanup by closing the PR and deleting the branch
   - If cleanup fails, manually close the PR and delete the branch before retrying

3. **Release created but version bump PR failed**
   - The release and tag are valid; manually create a PR to update version.txt
   - Or delete the release/tag and retry the workflow

4. **Network/authentication errors during branch check**
   - The workflow distinguishes between "branch not found" and actual errors
   - Check GitHub Actions runner connectivity and token permissions

5. **Workflow retry detected (tag already exists)**
   - The workflow detects when a tag already exists pointing to the correct SHA
   - Release creation is automatically skipped to prevent duplicates
   - A summary indicates the existing release URL

6. **Build artifact size validation fails**
   - Under 100KB: tracker.html is likely missing embedded content (build failure)
   - Over 2MB: tracker.html may contain unexpected content (investigate build)
   - Both cases fail the build step immediately to prevent releasing corrupted artifacts

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
8. `js_config_sync_generator.py` - Config sync for filters, export prefs, UI settings (local + cloud)
9. `js_import_export_generator.py` - Multi-format import/export (TSV, CSV, JSON, XML, YAML)
10. `js_conflict_dialog_generator.py` - Import conflict resolution dialog
11. `js_firebase_generator.py` - Optional Firebase cloud sync (if `firebase_config.json` exists)
12. `build_tracker.py` - Orchestrates all generators into single `tracker.html`

### Key Design Patterns

- **Single-File Delivery**: All CSS/JS/data embedded in tracker.html
- **Data-Driven UI**: Problem data embedded as JSON; UI renders dynamically
- **Cross-File Sync**: Updates to duplicate problems sync across all lists via `DUPLICATE_MAP`
- **Offline-First**: Uses browser localStorage; no server required
- **Conditional Features**: Firebase sync only enabled when config file exists

### JavaScript Dependency Order

Components must be combined in this order (set in `build_tracker.py`):
1. Data (PROBLEM_DATA, DUPLICATE_MAP)
2. Shared utilities (escapeHTML, truncateText, etc.)
3. Awareness algorithm
4. Settings
5. Config Sync (filter/export/UI preferences)
6. Import/Export
7. Conflict Dialog
8. Firebase
9. Core logic
10. Sync engine

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
