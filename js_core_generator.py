#!/usr/bin/env python3
"""
JavaScript Core Logic Sub-Agent
Implements tab switching, filtering, localStorage, and validation
"""


def generate_js_core():
    """Generate JavaScript core logic"""

    js = """
    // Global state
    let currentTab = PROBLEM_DATA.file_list[0];
    let allPatterns = new Set();
    let sortState = {};

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
      // Initialize config sync first (loads filter/export/UI preferences from localStorage)
      if (typeof initConfigSync === 'function') {
        initConfigSync();
      }

      if (!isLocalStorageAvailable()) {
        showStorageToast('localStorage is not available. Your progress will not be saved.', 'warning');
      }
      loadFromLocalStorage();
      populatePatternFilters();
      PROBLEM_DATA.file_list.forEach(fileKey => {
        PROBLEM_DATA.data[fileKey].forEach((problem, idx) => { problem._originalIndex = idx; });
        restoreSortStateForTab(fileKey);
      });
      renderAllTabs();
      initAwareness();
      updateAllProgress();
      PROBLEM_DATA.file_list.forEach(fileKey => {
        updateRandomBtnState(fileKey);
        updateUrgentBtnState(fileKey);
        initSortHeaders(fileKey);
      });
      setupEventListeners();
      initSettingsButton();

      // Restore saved filter states and active tab from config
      if (typeof restoreFilterStates === 'function') {
        restoreFilterStates();
      }
      if (typeof restoreActiveTab === 'function') {
        restoreActiveTab();
      }

      // Initialize export preferences from saved config
      if (typeof initExportPreferences === 'function') {
        initExportPreferences();
      }

      // Initialize Firebase cloud sync (if configured)
      if (typeof initFirebase === 'function') {
        initFirebase();
      }
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
          searchBox.addEventListener('input', () => {
            applyFilters(fileKey);
            if (typeof saveFilterState === 'function') saveFilterState(fileKey);
          });
        }
        if (difficultyFilter) {
          difficultyFilter.addEventListener('change', () => {
            applyFilters(fileKey);
            if (typeof saveFilterState === 'function') saveFilterState(fileKey);
          });
        }
        if (patternFilter) {
          patternFilter.addEventListener('change', () => {
            applyFilters(fileKey);
            if (typeof saveFilterState === 'function') saveFilterState(fileKey);
          });
        }
        if (solvedFilter) {
          solvedFilter.addEventListener('change', () => {
            applyFilters(fileKey);
            if (typeof saveFilterState === 'function') saveFilterState(fileKey);
          });
        }

        const colorFilter = document.getElementById(`color-filter-${fileKey}`);
        if (colorFilter) {
          colorFilter.addEventListener('change', () => {
            applyFilters(fileKey);
            if (typeof saveFilterState === 'function') saveFilterState(fileKey);
          });
        }
      });
    }

    // Tab switching
    function switchTab(tabName) {
      currentTab = tabName;

      // Save active tab to config
      if (typeof saveActiveTab === 'function') {
        saveActiveTab(tabName);
      }

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

    // Check if localStorage is available
    function isLocalStorageAvailable() {
      try {
        const testKey = '__storage_test__';
        localStorage.setItem(testKey, '1');
        localStorage.getItem(testKey);
        localStorage.removeItem(testKey);
        return true;
      } catch (e) {
        return false;
      }
    }

    // Show a toast notification for storage errors
    function showStorageToast(message, type) {
      const existing = document.getElementById('storage-toast');
      if (existing) existing.remove();
      const toast = document.createElement('div');
      toast.id = 'storage-toast';
      toast.className = 'sync-toast ' + (type === 'error' ? 'sync-toast-error' : 'sync-toast-warning');
      toast.style.bottom = '70px';
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 5000);
    }

    // Load data from localStorage
    function loadFromLocalStorage() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        try {
          const saved = localStorage.getItem(`tracker_${fileKey}`);
          if (saved) {
            const savedData = JSON.parse(saved);
            // Merge saved data with original data
            const savedMap = {};
            savedData.forEach(function(item) { if (item && item.name) savedMap[item.name] = item; });
            PROBLEM_DATA.data[fileKey].forEach(function(problem) {
              const saved = savedMap[problem.name];
              if (saved) {
                problem.solved = saved.solved || false;
                problem.time_to_solve = saved.time_to_solve || "";
                problem.comments = saved.comments || "";
                problem.solved_date = saved.solved_date || "";
              }
            });
          }
        } catch (e) {
          console.error(`Error loading saved data for ${fileKey}:`, e);
          showStorageToast('Your saved progress could not be loaded. Data may be corrupted.', 'error');
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
      try {
        localStorage.setItem(`tracker_${fileKey}`, JSON.stringify(data));
      } catch (e) {
        console.error(`Error saving data for ${fileKey}:`, e);
        showStorageToast('Your progress could not be saved. Consider exporting your data as a backup.', 'warning');
      }

      // Trigger cloud sync (debounced) if Firebase is enabled
      if (typeof syncToCloudDebounced === 'function' && typeof isCloudSyncEnabled === 'function' && isCloudSyncEnabled()) {
        syncToCloudDebounced(fileKey);
      }
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

      const sorted = getSortedProblems(fileKey);
      sorted.forEach((problem) => {
        const row = createTableRow(problem, problem._originalIndex, fileKey);
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

      const rawLink = problem.link ? problem.link.trim() : '';
      const safeLink = rawLink && /^(https?:\\/\\/|\\/|[^:]*$)/.test(rawLink) &&
        !/^(javascript|data|vbscript):/i.test(rawLink) ? rawLink : '';

      if (safeLink) {
        const link = document.createElement('a');
        link.href = safeLink;
        link.textContent = problem.name;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.className = 'problem-link';

        const icon = document.createElement('span');
        icon.className = 'external-link-icon';
        icon.textContent = ' \\u2197';
        icon.setAttribute('aria-hidden', 'true');

        nameTd.appendChild(link);
        nameTd.appendChild(icon);
      } else {
        nameTd.textContent = problem.name;
      }

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
        updateUrgentBtnState(fileKey);
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
      const urgentBtn = document.getElementById(`urgent-review-btn-${fileKey}`);
      if (urgentBtn) urgentBtn.classList.remove('active');

      const searchTerm = document.getElementById(`search-${fileKey}`).value.toLowerCase();
      const difficultyFilter = document.getElementById(`difficulty-filter-${fileKey}`).value;
      const patternFilter = document.getElementById(`pattern-filter-${fileKey}`).value;
      const solvedFilter = document.getElementById(`solved-filter-${fileKey}`).value;
      const colorFilter = document.getElementById(`color-filter-${fileKey}`).value;

      const tbody = document.getElementById(`tbody-${fileKey}`);
      const rows = tbody.querySelectorAll('tr');

      rows.forEach(row => {
        const idx = parseInt(row.dataset.index, 10);
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

      updateRandomBtnState(fileKey);
      updateUrgentBtnState(fileKey);
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

    // Download file with specified MIME type
    function downloadFile(filename, content, mimeType) {
      const type = mimeType || 'text/plain;charset=utf-8;';
      const blob = new Blob([content], { type: type });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
      link.click();
      URL.revokeObjectURL(link.href);
    }

    // Pick a random visible problem for the given tab
    function pickRandomProblem(fileKey) {
      const tbody = document.getElementById(`tbody-${fileKey}`);
      if (!tbody) return;
      const visibleRows = Array.from(tbody.querySelectorAll('tr')).filter(
        row => row.style.display !== 'none'
      );

      if (visibleRows.length === 0) {
        updateRandomBtnState(fileKey);
        return;
      }

      const randomIndex = Math.floor(Math.random() * visibleRows.length);
      const selectedRow = visibleRows[randomIndex];

      Array.from(tbody.querySelectorAll('tr')).forEach(r => r.classList.remove('random-highlight'));
      selectedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
      selectedRow.classList.add('random-highlight');
      setTimeout(() => selectedRow.classList.remove('random-highlight'), 4000);
    }

    // Enable or disable the random button based on visible row count
    function updateRandomBtnState(fileKey) {
      const btn = document.getElementById(`random-btn-${fileKey}`);
      if (!btn) return;
      const tbody = document.getElementById(`tbody-${fileKey}`);
      if (!tbody) { btn.disabled = true; return; }
      const visibleRows = Array.from(tbody.querySelectorAll('tr')).filter(
        row => row.style.display !== 'none'
      );
      btn.disabled = visibleRows.length === 0;
    }

    // Calculate days until a problem starts flashing (awareness-flashing)
    // Returns 0 if already flashing, Infinity if not solved or no date
    function calculateDaysUntilFlashing(problem) {
      if (!problem.solved) return Infinity;
      const result = calculateAwarenessScore(problem);
      if (result.score < 0) return Infinity;
      if (result.score >= AWARENESS_CONFIG.thresholds.darkRed) return 0;
      const commitmentFactor = getCommitmentFactor();
      const tierDiffMultiplier = getTierDifficultyMultiplier(problem);
      const solvedFactor = getSolvedFactor(problem);
      const dailyRate = AWARENESS_CONFIG.baseRate * commitmentFactor * tierDiffMultiplier / solvedFactor;
      if (dailyRate <= 0) return Infinity;
      const daysNeeded = (AWARENESS_CONFIG.thresholds.darkRed - result.score) / dailyRate;
      return Math.ceil(daysNeeded);
    }

    // Apply urgent review filter: show only the most urgently-due solved problems
    function applyUrgentReviewFilter(fileKey) {
      const btn = document.getElementById(`urgent-review-btn-${fileKey}`);
      if (btn && btn.classList.contains('active')) {
        btn.classList.remove('active');
        applyFilters(fileKey);
        updateProgress(fileKey);
        return;
      }

      const TIER_RANK = { 'awareness-flashing': 5, 'awareness-dark-red': 4, 'awareness-red': 3, 'awareness-yellow': 2, 'awareness-green': 1, 'awareness-white': 0, 'unsolved-problem': -1 };
      const problems = PROBLEM_DATA.data[fileKey];
      const tbody = document.getElementById(`tbody-${fileKey}`);
      if (!tbody) return;

      const solvedProblems = problems
        .map((problem, idx) => {
          const days = calculateDaysUntilFlashing(problem);
          if (days === Infinity) return null;
          const scoreResult = calculateAwarenessScore(problem);
          const tier = TIER_RANK[getAwarenessClass(scoreResult.score)] || 0;
          return { idx, days, tier };
        })
        .filter(item => item !== null);

      if (solvedProblems.length === 0) return;

      const maxTier = Math.max(...solvedProblems.map(item => item.tier));
      const globalMinDays = Math.min(...solvedProblems.map(item => item.days));
      const urgentIndices = new Set(
        solvedProblems.filter(item => item.tier === maxTier || item.days === globalMinDays).map(item => item.idx)
      );

      const rows = tbody.querySelectorAll('tr');
      rows.forEach(row => {
        const idx = parseInt(row.dataset.index, 10);
        row.style.display = urgentIndices.has(idx) ? '' : 'none';
      });

      if (btn) btn.classList.add('active');
      updateRandomBtnState(fileKey);
      updateUrgentBtnState(fileKey);

      const count = urgentIndices.size;
      const statusEl = document.getElementById(`progress-text-${fileKey}`);
      if (statusEl) {
        const msg = globalMinDays === 0
          ? `${count} problem(s) flashing NOW`
          : `${count} problem(s) flashing in ${globalMinDays} day(s)`;
        statusEl.textContent = msg;
      }
    }

    // Enable or disable the urgent-review button based on solved problems in tab
    function updateUrgentBtnState(fileKey) {
      const btn = document.getElementById(`urgent-review-btn-${fileKey}`);
      if (!btn) return;
      const problems = PROBLEM_DATA.data[fileKey];
      const hasSolved = problems.some(p => p.solved);
      btn.disabled = !hasSolved;
    }

    // Sort support

    function getSortValue(problem, column) {
      switch (column) {
        case 'difficulty': {
          const map = { Easy: 1, Medium: 2, Hard: 3 };
          return map[problem.difficulty] != null ? map[problem.difficulty] : null;
        }
        case 'intermediate_time':
        case 'advanced_time':
        case 'top_time':
        case 'time_to_solve': {
          const v = parseFloat(problem[column]);
          return isNaN(v) ? null : v;
        }
        case 'solved_date': {
          if (!problem.solved_date) return null;
          const d = Date.parse(problem.solved_date);
          return isNaN(d) ? null : d;
        }
        case 'name':
          return problem.name ? problem.name.toLowerCase() : null;
        default:
          return null;
      }
    }

    function getSortedProblems(fileKey) {
      const problems = [...PROBLEM_DATA.data[fileKey]];
      const state = sortState[fileKey];
      if (!state || !state.column || state.direction === 'none') return problems;
      const { column, direction } = state;
      const asc = direction === 'asc';
      return problems.sort((a, b) => {
        const va = getSortValue(a, column);
        const vb = getSortValue(b, column);
        if (va === null && vb === null) return 0;
        if (va === null) return 1;
        if (vb === null) return -1;
        if (va < vb) return asc ? -1 : 1;
        if (va > vb) return asc ? 1 : -1;
        return 0;
      });
    }

    function saveSortStateForTab(fileKey) {
      try {
        localStorage.setItem(`tracker_sort_${fileKey}`, JSON.stringify(sortState[fileKey] || {}));
      } catch (e) {}
    }

    function restoreSortStateForTab(fileKey) {
      try {
        const saved = localStorage.getItem(`tracker_sort_${fileKey}`);
        if (saved) {
          const parsed = JSON.parse(saved);
          if (parsed && typeof parsed.column === 'string' && (parsed.direction === 'asc' || parsed.direction === 'desc')) {
            sortState[fileKey] = parsed;
          }
        }
      } catch (e) {}
    }

    function initSortHeaders(fileKey) {
      const table = document.getElementById(`table-${fileKey}`);
      if (!table) return;
      table.querySelectorAll('th[data-sort]').forEach(th => {
        th.addEventListener('click', function() {
          const col = this.dataset.sort;
          const current = sortState[fileKey] || { column: null, direction: 'none' };
          let nextDir;
          if (current.column !== col || current.direction === 'none') {
            nextDir = 'asc';
          } else if (current.direction === 'asc') {
            nextDir = 'desc';
          } else {
            nextDir = 'none';
          }
          sortState[fileKey] = { column: col, direction: nextDir };
          saveSortStateForTab(fileKey);
          updateSortHeaders(fileKey);
          renderTable(fileKey);
        });
      });
      updateSortHeaders(fileKey);
    }

    function updateSortHeaders(fileKey) {
      const table = document.getElementById(`table-${fileKey}`);
      if (!table) return;
      const state = sortState[fileKey] || {};
      table.querySelectorAll('th[data-sort]').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        const indicator = th.querySelector('.sort-indicator');
        if (indicator) indicator.textContent = '';
        if (state.column === th.dataset.sort) {
          if (state.direction === 'asc') {
            th.classList.add('sort-asc');
            if (indicator) indicator.textContent = ' \\u2191';
          } else if (state.direction === 'desc') {
            th.classList.add('sort-desc');
            if (indicator) indicator.textContent = ' \\u2193';
          }
        }
      });
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
    """

    return js


if __name__ == "__main__":
    print(generate_js_core())
