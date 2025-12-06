#!/usr/bin/env python3
"""
HTML Structure Generator Sub-Agent
Creates the HTML skeleton and table structure
"""

def generate_html_structure(file_list):
    """Generate HTML structure with dynamic tabs"""

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
        tab_contents_html += f'''
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

        <button class="export-btn" onclick="exportTabTSV('{file_name}')">Export {file_name}.tsv</button>
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
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Coding Challenges Tracker</title>
  <style>
    /* CSS will be inserted here */
    {{CSS_PLACEHOLDER}}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Coding Challenges Tracker</h1>
      <div class="overall-progress">
        <div class="progress-text" id="overall-progress-text">Overall: 0 / 0 unique problems (0%)</div>
      </div>
          <button id="refresh-btn" class="refresh-btn" title="Refresh Awareness Colors" aria-label="Refresh Awareness Colors" onclick="manualRefreshAwareness()">&#8635;</button>
          <button id="settings-btn" class="settings-btn" title="Awareness Settings" aria-label="Awareness Settings">&#9881;</button>
    </header>

    <div class="tab-container">
{tabs_html}
    </div>

    <div class="export-all-section">
      <button class="export-all-btn" onclick="exportAllTSV()">Export All TSVs</button>
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
'''

    return html

if __name__ == "__main__":
    import json
    import sys

    # Read parsed data
    with open('parsed_data.json', 'r') as f:
        data = json.load(f)

    html = generate_html_structure(data['file_list'])
    print(html)
