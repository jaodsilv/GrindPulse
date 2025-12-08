#!/usr/bin/env python3
"""
JavaScript Core Logic Sub-Agent
Implements tab switching, filtering, localStorage, and validation
"""

def generate_js_core():
    """Generate JavaScript core logic"""

    js = '''
    // Global state
    let currentTab = PROBLEM_DATA.file_list[0];
    let allPatterns = new Set();

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
      loadFromLocalStorage();
      initAwareness();
      populatePatternFilters();
      renderAllTabs();
      updateAllProgress();
      setupEventListeners();
      initSettingsButton();
    });

    // Setup event listeners
    function setupEventListeners() {
      // Tab switching
      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', function() {
          switchTab(this.dataset.tab);
        });
      });

      // Search and filter listeners for each tab
      PROBLEM_DATA.file_list.forEach(fileKey => {
        const searchBox = document.getElementById(`search-${fileKey}`);
        const difficultyFilter = document.getElementById(`difficulty-filter-${fileKey}`);
        const patternFilter = document.getElementById(`pattern-filter-${fileKey}`);
        const solvedFilter = document.getElementById(`solved-filter-${fileKey}`);

        if (searchBox) {
          searchBox.addEventListener('input', () => applyFilters(fileKey));
        }
        if (difficultyFilter) {
          difficultyFilter.addEventListener('change', () => applyFilters(fileKey));
        }
        if (patternFilter) {
          patternFilter.addEventListener('change', () => applyFilters(fileKey));
        }
        if (solvedFilter) {
          solvedFilter.addEventListener('change', () => applyFilters(fileKey));
        }

        const colorFilter = document.getElementById(`color-filter-${fileKey}`);
        if (colorFilter) {
          colorFilter.addEventListener('change', () => applyFilters(fileKey));
        }
      });
    }

    // Tab switching
    function switchTab(tabName) {
      currentTab = tabName;

      // Update tab buttons
      document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
          btn.classList.add('active');
        }
      });

      // Update tab content
      document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
      });
      document.getElementById(`tab-${tabName}`).classList.add('active');
    }

    // Load data from localStorage
    function loadFromLocalStorage() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        const saved = localStorage.getItem(`tracker_${fileKey}`);
        if (saved) {
          try {
            const savedData = JSON.parse(saved);
            // Merge saved data with original data
            PROBLEM_DATA.data[fileKey].forEach((problem, idx) => {
              if (savedData[idx]) {
                problem.solved = savedData[idx].solved || false;
                problem.time_to_solve = savedData[idx].time_to_solve || "";
                problem.comments = savedData[idx].comments || "";
                problem.solved_date = savedData[idx].solved_date || "";
              }
            });
          } catch (e) {
            console.error(`Error loading saved data for ${fileKey}:`, e);
          }
        }
      });
    }

    // Save to localStorage
    function saveToLocalStorage(fileKey) {
      const data = PROBLEM_DATA.data[fileKey].map(p => ({
        name: p.name,
        solved: p.solved,
        time_to_solve: p.time_to_solve,
        comments: p.comments,
        solved_date: p.solved_date
      }));
      localStorage.setItem(`tracker_${fileKey}`, JSON.stringify(data));
    }

    // Populate pattern filter dropdowns
    function populatePatternFilters() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        PROBLEM_DATA.data[fileKey].forEach(problem => {
          if (problem.pattern) {
            allPatterns.add(problem.pattern);
          }
        });
      });

      const sortedPatterns = Array.from(allPatterns).sort();

      PROBLEM_DATA.file_list.forEach(fileKey => {
        const select = document.getElementById(`pattern-filter-${fileKey}`);
        sortedPatterns.forEach(pattern => {
          const option = document.createElement('option');
          option.value = pattern;
          option.textContent = pattern;
          select.appendChild(option);
        });
      });
    }

    // Render all tabs
    function renderAllTabs() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        renderTable(fileKey);
      });
    }

    // Render table for a specific tab
    function renderTable(fileKey) {
      const tbody = document.getElementById(`tbody-${fileKey}`);
      tbody.innerHTML = '';

      PROBLEM_DATA.data[fileKey].forEach((problem, idx) => {
        const row = createTableRow(problem, idx, fileKey);
        tbody.appendChild(row);
      });

      applyFilters(fileKey);
    }

    // Create table row
    function createTableRow(problem, idx, fileKey) {
      const tr = document.createElement('tr');
      tr.dataset.index = idx;

      // Problem Name + Duplicate Badge
      const nameTd = document.createElement('td');
      nameTd.textContent = problem.name;

      if (DUPLICATE_MAP[problem.name] && DUPLICATE_MAP[problem.name].length > 1) {
        const badge = document.createElement('span');
        badge.className = 'duplicate-badge';
        const otherFiles = DUPLICATE_MAP[problem.name].filter(f => f !== fileKey);
        badge.textContent = `Also in: ${otherFiles.join(', ')}`;
        badge.title = `This problem appears in: ${DUPLICATE_MAP[problem.name].join(', ')}`;
        nameTd.appendChild(badge);
      }

      // Difficulty
      const difficultyTd = document.createElement('td');
      const difficultyBadge = document.createElement('span');
      difficultyBadge.className = `difficulty-badge difficulty-${problem.difficulty}`;
      difficultyBadge.textContent = problem.difficulty;
      difficultyTd.appendChild(difficultyBadge);

      // Time columns
      const intermediateTd = document.createElement('td');
      intermediateTd.className = 'time-col';
      intermediateTd.textContent = problem.intermediate_time ? `${problem.intermediate_time} min` : '-';

      const advancedTd = document.createElement('td');
      advancedTd.className = 'time-col';
      advancedTd.textContent = problem.advanced_time ? `${problem.advanced_time} min` : '-';

      const topTd = document.createElement('td');
      topTd.className = 'time-col';
      topTd.textContent = problem.top_time ? `${problem.top_time} min` : '-';

      // Pattern (collapsible)
      const patternTd = document.createElement('td');
      patternTd.className = 'pattern-cell';

      const patternBtn = document.createElement('button');
      patternBtn.className = 'pattern-toggle';
      patternBtn.textContent = 'Show';
      patternBtn.onclick = function() {
        const textDiv = this.nextElementSibling;
        textDiv.classList.toggle('visible');
        this.textContent = textDiv.classList.contains('visible') ? 'Hide' : 'Show';
      };

      const patternText = document.createElement('div');
      patternText.className = 'pattern-text';
      patternText.textContent = problem.pattern || 'N/A';

      patternTd.appendChild(patternBtn);
      patternTd.appendChild(patternText);

      // Solved checkbox
      const solvedTd = document.createElement('td');
      const solvedCheckbox = document.createElement('input');
      solvedCheckbox.type = 'checkbox';
      solvedCheckbox.className = 'checkbox-input';
      solvedCheckbox.checked = problem.solved;
      solvedCheckbox.onchange = function() {
        problem.solved = this.checked;
        if (this.checked && !problem.solved_date) {
          problem.solved_date = new Date().toISOString();
          updateSolvedDateDisplay(fileKey, idx);
        } else if (!this.checked) {
          problem.solved_date = "";
          updateSolvedDateDisplay(fileKey, idx);
        }
        syncDuplicates(problem.name, 'solved', this.checked);
        syncDuplicates(problem.name, 'solved_date', problem.solved_date);
        saveToLocalStorage(fileKey);
        updateProgress(fileKey);
        updateOverallProgress();
        updateRowAwareness(fileKey, idx);
      };
      solvedTd.appendChild(solvedCheckbox);

      // Time to Solve input
      const timeTd = document.createElement('td');
      const timeInput = document.createElement('input');
      timeInput.type = 'number';
      timeInput.className = 'time-input';
      timeInput.placeholder = 'Minutes';
      timeInput.value = problem.time_to_solve;
      timeInput.oninput = function() {
        problem.time_to_solve = this.value;
        syncDuplicates(problem.name, 'time_to_solve', this.value);
        saveToLocalStorage(fileKey);
        updateRowAwareness(fileKey, idx);
      };
      timeTd.appendChild(timeInput);

      // Comments textarea
      const commentsTd = document.createElement('td');
      const commentsInput = document.createElement('textarea');
      commentsInput.className = 'comments-input';
      commentsInput.placeholder = 'Add notes...';
      commentsInput.value = problem.comments || "";
      commentsInput.oninput = function() {
        problem.comments = this.value;
        syncDuplicates(problem.name, 'comments', this.value);
        saveToLocalStorage(fileKey);
      };
      commentsTd.appendChild(commentsInput);

      // Solved Date (display only)
      const solvedDateTd = document.createElement('td');
      solvedDateTd.className = 'solved-date';
      solvedDateTd.dataset.fileKey = fileKey;
      solvedDateTd.dataset.index = idx;
      solvedDateTd.textContent = formatRelativeTime(problem.solved_date);

      tr.appendChild(nameTd);
      tr.appendChild(difficultyTd);
      tr.appendChild(intermediateTd);
      tr.appendChild(advancedTd);
      tr.appendChild(topTd);
      tr.appendChild(patternTd);
      tr.appendChild(solvedTd);
      tr.appendChild(timeTd);
      tr.appendChild(commentsTd);
      tr.appendChild(solvedDateTd);

      return tr;
    }

    // Update solved date display
    function updateSolvedDateDisplay(fileKey, idx) {
      const cell = document.querySelector(`td.solved-date[data-file-key="${fileKey}"][data-index="${idx}"]`);
      if (cell) {
        const problem = PROBLEM_DATA.data[fileKey][idx];
        cell.textContent = formatRelativeTime(problem.solved_date);
      }
    }

    // Format relative time
    function formatRelativeTime(isoDate) {
      if (!isoDate) return '';

      const now = new Date();
      const date = new Date(isoDate);
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      const diffWeek = Math.floor(diffDay / 7);
      const diffMonth = Math.floor(diffDay / 30);
      const diffYear = Math.floor(diffDay / 365);

      if (diffSec < 60) return 'just now';
      if (diffMin < 60) return `${diffMin} min ago`;
      if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`;
      if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`;
      if (diffWeek < 4) return `${diffWeek} week${diffWeek > 1 ? 's' : ''} ago`;
      if (diffMonth < 12) return `${diffMonth} month${diffMonth > 1 ? 's' : ''} ago`;
      return `${diffYear} year${diffYear > 1 ? 's' : ''} ago`;
    }

    // Apply filters
    function applyFilters(fileKey) {
      const searchTerm = document.getElementById(`search-${fileKey}`).value.toLowerCase();
      const difficultyFilter = document.getElementById(`difficulty-filter-${fileKey}`).value;
      const patternFilter = document.getElementById(`pattern-filter-${fileKey}`).value;
      const solvedFilter = document.getElementById(`solved-filter-${fileKey}`).value;
      const colorFilter = document.getElementById(`color-filter-${fileKey}`).value;

      const tbody = document.getElementById(`tbody-${fileKey}`);
      const rows = tbody.querySelectorAll('tr');

      rows.forEach(row => {
        const idx = parseInt(row.dataset.index);
        const problem = PROBLEM_DATA.data[fileKey][idx];

        let show = true;

        // Search filter
        if (searchTerm && !problem.name.toLowerCase().includes(searchTerm)) {
          show = false;
        }

        // Difficulty filter
        if (difficultyFilter && problem.difficulty !== difficultyFilter) {
          show = false;
        }

        // Pattern filter
        if (patternFilter && problem.pattern !== patternFilter) {
          show = false;
        }

        // Solved filter
        if (solvedFilter === 'solved' && !problem.solved) {
          show = false;
        }
        if (solvedFilter === 'unsolved' && problem.solved) {
          show = false;
        }

        // Color filter - check if row has the awareness class
        if (colorFilter && !row.classList.contains(colorFilter)) {
          show = false;
        }

        row.style.display = show ? '' : 'none';
      });
    }

    // Update progress for a tab
    function updateProgress(fileKey) {
      const problems = PROBLEM_DATA.data[fileKey];
      const solved = problems.filter(p => p.solved).length;
      const total = problems.length;
      const percentage = total > 0 ? Math.round((solved / total) * 100) : 0;

      const progressBar = document.getElementById(`progress-${fileKey}`);
      const progressText = document.getElementById(`progress-text-${fileKey}`);

      progressBar.style.width = `${percentage}%`;
      progressBar.textContent = `${percentage}%`;
      progressText.textContent = `Solved ${solved} / ${total} problems (${percentage}%)`;
    }

    // Update all progress bars
    function updateAllProgress() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        updateProgress(fileKey);
      });
      updateOverallProgress();
    }

    // Update overall progress (unique problems only)
    function updateOverallProgress() {
      const uniqueProblems = new Set();
      const solvedProblems = new Set();

      PROBLEM_DATA.file_list.forEach(fileKey => {
        PROBLEM_DATA.data[fileKey].forEach(problem => {
          uniqueProblems.add(problem.name);
          if (problem.solved) {
            solvedProblems.add(problem.name);
          }
        });
      });

      const total = uniqueProblems.size;
      const solved = solvedProblems.size;
      const percentage = total > 0 ? Math.round((solved / total) * 100) : 0;

      const progressText = document.getElementById('overall-progress-text');
      progressText.textContent = `Overall: ${solved} / ${total} unique problems (${percentage}%)`;
    }

    // Export tab to TSV
    function exportTabTSV(fileKey) {
      const problems = PROBLEM_DATA.data[fileKey];

      // TSV header
      let tsv = "Problem Name\\tDifficulty\\tIntermediate Max time\\tAdvanced Max time\\tTop of the crop max time\\tProblem Pattern\\tSolved\\tTime to Solve\\tComments\\tSolved Date\\n";

      problems.forEach(problem => {
        const row = [
          escapeTSV(problem.name),
          escapeTSV(problem.difficulty),
          escapeTSV(problem.intermediate_time),
          escapeTSV(problem.advanced_time),
          escapeTSV(problem.top_time),
          escapeTSV(problem.pattern),
          problem.solved ? "true" : "false",
          escapeTSV(problem.time_to_solve),
          escapeTSV(problem.comments),
          escapeTSV(problem.solved_date)
        ];
        tsv += row.join('\\t') + '\\n';
      });

      downloadFile(`${fileKey}.tsv`, tsv);
    }

    // Export all TSVs
    function exportAllTSV() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        exportTabTSV(fileKey);
      });
    }

    // Escape TSV special characters
    function escapeTSV(value) {
      if (value === null || value === undefined) return '';
      const str = String(value);
      // Replace tabs with spaces, newlines with spaces
      return str.replace(/\\t/g, ' ').replace(/\\n/g, ' ').replace(/\\r/g, '');
    }

    // Download file
    function downloadFile(filename, content) {
      const blob = new Blob([content], { type: 'text/tab-separated-values;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
    }

    // Update relative times periodically
    setInterval(() => {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        PROBLEM_DATA.data[fileKey].forEach((problem, idx) => {
          if (problem.solved_date) {
            updateSolvedDateDisplay(fileKey, idx);
          }
        });
      });
    }, 60000); // Update every minute
    '''

    return js

if __name__ == "__main__":
    print(generate_js_core())
