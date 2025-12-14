# GrindPulse

A dynamic, interactive HTML-based tracker for coding interview preparation problems across multiple curated lists.

## Quick Start

1. **Open the tracker**: Double-click `tracker.html` in any modern web browser
2. **Track your progress**: Check off problems as you solve them
3. **Export your data**: Download updated TSV files with your progress

No installation, no server, no dependencies required. Works completely offline.

---

## Features

### Dynamic Multi-File Tracking
- Automatically loads all TSV files from `raw/` folder
- Currently tracking 4 problem lists:
  - **Blind 75** (75 problems)
  - **NeetCode 150** (150 problems)
  - **NeetCode 250** (250 problems)
  - **Salesforce** (16 problems)
- Total: 491 problems with 137 duplicates identified

### Cross-File Synchronization
- When you mark a problem as solved in one list, it automatically updates in all other lists
- 137 problems appear in multiple lists and stay synchronized
- Visual badges show which other lists contain each problem

### Progress Tracking
- Per-list progress bars with percentages
- Overall progress (counts unique problems only)
- Real-time updates as you work

### Advanced Filtering
- Search by problem name
- Filter by difficulty (Easy/Medium/Hard)
- Filter by pattern (Hash Table, Two Pointers, etc.)
- Filter by status (Solved/Unsolved)

### Data Persistence
- All changes auto-save to browser localStorage
- Your progress persists across sessions
- No account or login required

### Export Functionality
- Export individual TSV files with your progress
- Export all files at once
- Exported files include all tracking data

---

## How to Use

### Tracking Problems

1. **Switch between lists** using the tabs at the top
2. **Search** for specific problems using the search box
3. **Filter** problems by difficulty, pattern, or status
4. **Check "Solved"** when you complete a problem
   - Automatically records the date/time
   - Syncs across all lists containing this problem
5. **Enter your solve time** (optional)
6. **Add notes** in the Comments field (optional)

### Understanding the Interface

#### Columns
1. **Problem Name** - The name of the coding challenge
2. **Difficulty** - Color-coded badge (Green=Easy, Orange=Medium, Red=Hard)
3. **Intermediate Time** - Target time for intermediate level
4. **Advanced Time** - Target time for advanced level
5. **Top Time** - Target time for expert level
6. **Pattern** - Click "Show" to reveal the problem pattern
7. **Solved** - Checkbox to mark completion
8. **Time to Solve** - Enter how long it took you (minutes)
9. **Comments** - Add personal notes or insights
10. **Solved Date** - Automatically shows when you solved it (e.g., "3 days ago")

#### Duplicate Badges
Yellow badges like "Also in: NeetCode150, Blind75" indicate the problem appears in multiple lists. Edits sync across all instances.

---

## File Structure

```
GrindPulse/
├── tracker.html          # Main tracker (OPEN THIS FILE)
├── raw/                  # Source TSV files (problem templates)
│   ├── blind75.tsv
│   ├── neetcode150.tsv
│   ├── neetcode250.tsv
│   └── salesforce.tsv
├── data_parser.py        # Parser sub-agent
├── html_generator.py     # HTML structure generator
├── css_generator.py      # CSS styling generator
├── js_core_generator.py  # Core JavaScript logic
├── js_sync_generator.py  # Cross-file sync engine
├── build_tracker.py      # Integration script
├── parsed_data.json      # Intermediate data file
├── BUILD_SUMMARY.md      # Detailed build report
└── README.md             # This file
```

---

## Adding New Problem Lists

1. Create a new TSV file in the `raw/` folder
2. Follow this format (6 columns, tab-separated):
   ```
   Problem Name    Difficulty    Intermediate Max time    Advanced Max time    Top of the crop max time    Problem Pattern
   ```
3. Run the rebuild script:
   ```bash
   python3 build_tracker.py
   ```
4. Refresh `tracker.html` in your browser

The new list will automatically appear as a new tab.

---

## Exporting Your Progress

### Export Single List
Click the "Export [filename].tsv" button at the top of any tab to download that list with your current progress.

### Export All Lists
Click the "Export All TSVs" button in the header to download all lists at once.

### What's Exported
Exported TSV files include 10 columns:
1. Original 6 columns from source data
2. Solved status (true/false)
3. Time to Solve (minutes)
4. Comments (your notes)
5. Solved Date (ISO timestamp)

---

## Companion Data Repository

This tracker has a companion private repository for storing your personal progress data:

**Repository**: `GrindPulse-data` (private, encrypted with git-crypt)

### Why Use a Separate Data Repo?

1. **Privacy**: Your solved status, times, and comments are personal data
2. **Backup**: Browser localStorage can be cleared; git provides version history
3. **Portability**: Sync progress across machines via git
4. **Security**: git-crypt encrypts all data files on GitHub

### Workflow

1. Use `tracker.html` to track your progress
2. Export your progress using "Export All TSVs" button
3. Save exported files to `GrindPulse-data/exports/`
4. Commit and push to backup your progress

### Setting Up the Data Repo

```bash
# Clone the data repo (requires git-crypt key)
git clone https://github.com/jaodsilv/GrindPulse-data.git ../data

# Unlock encryption (one-time setup)
cd ../data
git-crypt unlock /path/to/git-crypt-key
```

---

## Technical Details

### Browser Compatibility
- ✓ Chrome/Edge
- ✓ Firefox
- ✓ Safari
- ✗ Internet Explorer

### Data Storage
- Uses browser localStorage
- Separate storage key per problem list
- Typical storage: ~50-100 KB
- No server or database required

### Privacy & Security
- All data stays on your computer
- No data transmission
- No tracking or analytics
- Works completely offline

---

## Rebuilding the Tracker

If you modify the source TSV files or want to regenerate the tracker:

```bash
python3 build_tracker.py
```

This will:
1. Parse all TSV files in `raw/` folder
2. Detect duplicates across files
3. Generate a new `tracker.html` with updated data
4. Preserve your existing progress (stored in localStorage)

---

## Statistics

- **Total Problems**: 491
- **Unique Problems**: 354 (137 duplicates)
- **Problem Lists**: 4
- **Difficulty Breakdown**:
  - Easy: ~150 problems
  - Medium: ~250 problems
  - Hard: ~90 problems
- **Patterns Covered**: 30+ different problem patterns

---

## Support

This is a standalone tool with no external dependencies. If you encounter issues:

1. **Clear browser cache** and reload
2. **Check browser console** (F12) for errors
3. **Try a different browser**
4. **Rebuild the tracker** using `build_tracker.py`

---

## Credits

Built using a coordinated multi-agent system:
1. Data Parser Agent
2. HTML Structure Generator Agent
3. CSS Styling Agent
4. JavaScript Core Logic Agent
5. Cross-File Sync Engine Agent

Generated on: October 20, 2025
