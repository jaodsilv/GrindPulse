#!/usr/bin/env python3
"""
HTML Structure Generator Sub-Agent
Creates the HTML skeleton and table structure
"""


def generate_html_structure(file_list, firebase_enabled=False):
    """Generate HTML structure with dynamic tabs

    Args:
        file_list: List of file keys for tabs
        firebase_enabled: Whether Firebase is configured
    """

    # Generate tab buttons
    tabs_html = ""
    for idx, file_name in enumerate(file_list):
        # Convert filename to display name
        display_name = file_name.replace("_", " ").title()
        if "neetcode" in file_name.lower():
            display_name = "NeetCode " + file_name.replace("neetcode", "").replace("_", " ").strip()
        elif "blind" in file_name.lower():
            display_name = "Blind " + file_name.replace("blind", "").replace("_", " ").strip()

        active_class = "active" if idx == 0 else ""
        tabs_html += f'        <button class="tab-button {active_class}" data-tab="{file_name}">{display_name}</button>\n'

    # Generate tab content containers
    tab_contents_html = ""
    for idx, file_name in enumerate(file_list):
        active_class = "active" if idx == 0 else ""
        tab_contents_html += f"""
    <div id="tab-{file_name}" class="tab-content {active_class}">
      <div class="progress-section">
        <div class="progress-bar-container">
          <div class="progress-bar" id="progress-{file_name}"></div>
        </div>
        <div class="progress-text" id="progress-text-{file_name}">Solved 0 / 0 problems (0%)</div>
      </div>

      <div class="filter-section">
        <input type="text" id="search-{file_name}" class="search-box" placeholder="Search problems...">

        <select id="difficulty-filter-{file_name}" class="filter-dropdown">
          <option value="">All Difficulties</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>

        <select id="pattern-filter-{file_name}" class="filter-dropdown">
          <option value="">All Patterns</option>
        </select>

        <select id="solved-filter-{file_name}" class="filter-dropdown">
          <option value="">All Status</option>
          <option value="solved">Solved</option>
          <option value="unsolved">Unsolved</option>
        </select>

        <select id="color-filter-{file_name}" class="filter-dropdown">
          <option value="">All Colors</option>
          <option value="awareness-white">White (Fresh)</option>
          <option value="awareness-green">Green</option>
          <option value="awareness-yellow">Yellow</option>
          <option value="awareness-red">Red</option>
          <option value="awareness-dark-red">Dark Red</option>
          <option value="awareness-flashing">Flashing (Urgent)</option>
          <option value="unsolved-problem">Unsolved</option>
        </select>

        <div class="import-export-wrapper">
          <button class="hamburger-btn" onclick="toggleImportExportMenu('{file_name}')" aria-label="Import/Export Menu" aria-expanded="false">
            <span aria-hidden="true">&#9776;</span>
          </button>
          <div class="import-export-menu" id="import-export-menu-{file_name}" style="display:none;">
            <div class="import-export-menu-header">Import / Export</div>
            <div class="import-export-menu-content">
              <label class="import-export-menu-label">Format:</label>
              <select id="format-select-{file_name}" class="filter-dropdown format-select">
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="tsv">TSV</option>
                <option value="xml">XML</option>
                <option value="yaml">YAML</option>
              </select>
              <label class="import-export-menu-label">Mode:</label>
              <select id="mode-select-{file_name}" class="filter-dropdown mode-select">
                <option value="full">Full Data</option>
                <option value="user">User Progress</option>
                <option value="problems">Problem Set</option>
              </select>
              <div class="import-export-menu-divider"></div>
              <button class="import-export-menu-item export-action" onclick="exportTab('{file_name}'); hideImportExportMenu('{file_name}');">
                <span>&#8681;</span> Export Tab
              </button>
              <button class="import-export-menu-item import-action" onclick="triggerImport('{file_name}'); hideImportExportMenu('{file_name}');">
                <span>&#8679;</span> Import to Tab
              </button>
            </div>
            <input type="file" id="import-file-{file_name}" style="display:none" accept=".tsv,.csv,.json,.xml,.yaml,.yml" onchange="handleFileImport(event, '{file_name}')">
          </div>
        </div>
      </div>

      <div class="table-container">
        <table id="table-{file_name}">
          <thead>
            <tr>
              <th>Problem Name</th>
              <th>Difficulty</th>
              <th>Intermediate Time</th>
              <th>Advanced Time</th>
              <th>Top Time</th>
              <th>Pattern</th>
              <th>Solved</th>
              <th>Time to Solve</th>
              <th>Comments</th>
              <th>Solved Date</th>
            </tr>
          </thead>
          <tbody id="tbody-{file_name}">
          </tbody>
        </table>
      </div>
    </div>
"""

    # Firebase SDK scripts (only if enabled)
    # NOTE: Firebase SDK version is pinned (10.7.0) for stability. To update:
    # 1. Check https://firebase.google.com/docs/web/learn-more#available-libraries for latest
    # 2. Test locally before updating version
    # 3. Dependabot will not auto-update CDN links - manual process required
    firebase_scripts = (
        """
  <!-- Firebase SDK (pinned version for stability - update manually after testing) -->
  <script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore-compat.js"></script>
"""
        if firebase_enabled
        else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GrindPulse</title>
  <link rel="icon" href="data:,">{firebase_scripts}
  <style>
    /* CSS will be inserted here */
    {{CSS_PLACEHOLDER}}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-content">
        <div class="header-title">
          <h1>GrindPulse</h1>
          <div class="overall-progress">
            <div class="progress-text" id="overall-progress-text">Overall: 0 / 0 unique problems (0%)</div>
          </div>
        </div>
        <div class="header-controls">
          <div id="sync-status" class="sync-status" style="display:none" title="Cloud Sync Status">
            <span id="sync-icon" class="sync-icon">&#9679;</span>
            <span id="sync-text" class="sync-text">Offline</span>
          </div>
          <button id="sync-now-btn" class="sync-now-btn" style="display:none" title="Sync Now" aria-label="Sync Now" onclick="manualSyncNow()">&#8635;</button>
          <button id="auth-btn" class="auth-btn" style="display:none" title="Sign in with Google">
            <img id="auth-avatar" class="auth-avatar" src="" alt="" style="display:none">
            <span id="auth-text">Sign In</span>
          </button>
          <button id="refresh-btn" class="refresh-btn" title="Refresh Awareness Colors" aria-label="Refresh Awareness Colors" onclick="manualRefreshAwareness()"><span aria-hidden="true">&#8635;</span></button>
          <button id="settings-btn" class="settings-btn" title="Awareness Settings" aria-label="Awareness Settings"><span aria-hidden="true">&#9881;</span></button>
        </div>
      </div>
    </header>

    <div class="tab-container">
{tabs_html}
    </div>

    <div class="import-export-section">
      <div class="global-import-export">
        <span class="import-export-label">All Tabs:</span>
        <div class="import-export-wrapper">
          <button class="hamburger-btn" onclick="toggleImportExportMenu('global')" aria-label="Global Import/Export Menu" aria-expanded="false">
            <span aria-hidden="true">&#9776;</span>
          </button>
          <div class="import-export-menu" id="import-export-menu-global" style="display:none;">
            <div class="import-export-menu-header">Global Import / Export</div>
            <div class="import-export-menu-content">
              <label class="import-export-menu-label">Format:</label>
              <select id="global-format-select" class="filter-dropdown format-select">
                <option value="json">JSON</option>
                <option value="csv">CSV</option>
                <option value="tsv">TSV</option>
                <option value="xml">XML</option>
                <option value="yaml">YAML</option>
              </select>
              <label class="import-export-menu-label">Mode:</label>
              <select id="global-mode-select" class="filter-dropdown mode-select">
                <option value="full">Full Data</option>
                <option value="user">User Progress</option>
                <option value="problems">Problem Set</option>
              </select>
              <div class="import-export-menu-divider"></div>
              <button class="import-export-menu-item export-action" onclick="exportAll(); hideImportExportMenu('global');">
                <span>&#8681;</span> Export All Tabs
              </button>
              <button class="import-export-menu-item import-action" onclick="triggerImportAll(); hideImportExportMenu('global');">
                <span>&#8679;</span> Import Files
              </button>
            </div>
            <input type="file" id="import-file-all" style="display:none" accept=".tsv,.csv,.json,.xml,.yaml,.yml" multiple onchange="handleMultiFileImport(event)">
          </div>
        </div>
      </div>
    </div>

{tab_contents_html}
  </div>

  <script>
    // Data will be embedded here
    {{DATA_PLACEHOLDER}}

    // JavaScript will be inserted here
    {{JS_PLACEHOLDER}}
  </script>
</body>
</html>
"""

    return html


if __name__ == "__main__":
    import json

    # Read parsed data
    with open("parsed_data.json") as f:
        data = json.load(f)

    html = generate_html_structure(data["file_list"])
    print(html)
