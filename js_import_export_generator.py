#!/usr/bin/env python3
"""
JavaScript Import/Export Generator
Implements multi-format import/export functionality for TSV, CSV, JSON, XML, and YAML
"""


def generate_js_import_export():
    """Generate JavaScript import/export logic"""

    js = '''
    // ============================================
    // IMPORT/EXPORT FUNCTIONALITY
    // ============================================

    // ============================================
    // HAMBURGER MENU FUNCTIONS
    // ============================================

    // Track currently open menu
    let activeImportExportMenu = null;

    /**
     * Toggle import/export menu visibility
     * @param {string} menuId - Either a fileKey or 'global'
     */
    function toggleImportExportMenu(menuId) {
      const menu = document.getElementById(`import-export-menu-${menuId}`);
      if (!menu) return;

      const isCurrentlyOpen = menu.style.display === 'block';

      // Close any other open menu
      if (activeImportExportMenu && activeImportExportMenu !== menuId) {
        hideImportExportMenu(activeImportExportMenu);
      }

      if (isCurrentlyOpen) {
        hideImportExportMenu(menuId);
      } else {
        showImportExportMenu(menuId);
      }
    }

    /**
     * Show import/export menu
     * @param {string} menuId - Either a fileKey or 'global'
     */
    function showImportExportMenu(menuId) {
      const menu = document.getElementById(`import-export-menu-${menuId}`);
      const btn = menu ? menu.parentElement.querySelector('.hamburger-btn') : null;

      if (!menu) return;

      menu.style.display = 'block';
      activeImportExportMenu = menuId;

      if (btn) {
        btn.setAttribute('aria-expanded', 'true');
      }

      // Add click-outside listener after a small delay (to avoid immediate close)
      setTimeout(() => {
        document.addEventListener('click', handleImportExportClickOutside);
      }, 0);
    }

    /**
     * Hide import/export menu
     * @param {string} menuId - Either a fileKey or 'global'
     */
    function hideImportExportMenu(menuId) {
      const menu = document.getElementById(`import-export-menu-${menuId}`);
      const btn = menu ? menu.parentElement.querySelector('.hamburger-btn') : null;

      if (!menu) return;

      menu.style.display = 'none';

      if (btn) {
        btn.setAttribute('aria-expanded', 'false');
      }

      if (activeImportExportMenu === menuId) {
        activeImportExportMenu = null;
        document.removeEventListener('click', handleImportExportClickOutside);
      }
    }

    /**
     * Handle click outside to close menu
     */
    function handleImportExportClickOutside(e) {
      if (!activeImportExportMenu) return;

      const menu = document.getElementById(`import-export-menu-${activeImportExportMenu}`);
      const wrapper = menu ? menu.parentElement : null;

      if (wrapper && !wrapper.contains(e.target)) {
        hideImportExportMenu(activeImportExportMenu);
      }
    }

    /**
     * Close all import/export menus (utility function)
     */
    function closeAllImportExportMenus() {
      if (activeImportExportMenu) {
        hideImportExportMenu(activeImportExportMenu);
      }
    }

    // Close menu on Escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && activeImportExportMenu) {
        hideImportExportMenu(activeImportExportMenu);
      }
    });

    // ============================================
    // IMPORT STATE
    // ============================================

    // Current import state (used during conflict resolution)
    let pendingImport = {
      fileKey: null,
      data: null,
      mode: null,
      conflicts: []
    };

    // ============================================
    // MIME TYPES
    // ============================================
    const MIME_TYPES = {
      tsv: 'text/tab-separated-values;charset=utf-8;',
      csv: 'text/csv;charset=utf-8;',
      json: 'application/json;charset=utf-8;',
      xml: 'application/xml;charset=utf-8;',
      yaml: 'text/yaml;charset=utf-8;'
    };

    const FILE_EXTENSIONS = {
      tsv: '.tsv',
      csv: '.csv',
      json: '.json',
      xml: '.xml',
      yaml: '.yaml'
    };

    // ============================================
    // MODE FILTERING
    // ============================================

    /**
     * Filter problems based on export mode
     * @param {Array} problems - Array of problem objects
     * @param {string} mode - 'full', 'user', or 'problems'
     * @returns {Array} Filtered problem array
     */
    function filterByMode(problems, mode) {
      switch (mode) {
        case 'problems':
          // Static problem data only
          return problems.map(p => ({
            name: p.name,
            difficulty: p.difficulty,
            intermediate_time: p.intermediate_time,
            advanced_time: p.advanced_time,
            top_time: p.top_time,
            pattern: p.pattern
          }));

        case 'user':
          // User progress data only
          return problems.map(p => ({
            name: p.name,
            solved: p.solved,
            time_to_solve: p.time_to_solve,
            comments: p.comments,
            solved_date: p.solved_date
          }));

        case 'full':
        default:
          // All data
          return problems.map(p => ({
            name: p.name,
            difficulty: p.difficulty,
            intermediate_time: p.intermediate_time,
            advanced_time: p.advanced_time,
            top_time: p.top_time,
            pattern: p.pattern,
            solved: p.solved,
            time_to_solve: p.time_to_solve,
            comments: p.comments,
            solved_date: p.solved_date
          }));
      }
    }

    // ============================================
    // FORMAT SERIALIZERS
    // ============================================

    /**
     * Serialize problems to TSV format
     */
    function serializeToTSV(problems, mode) {
      const headers = getHeadersForMode(mode);
      let tsv = headers.join('\\t') + '\\n';

      problems.forEach(problem => {
        const row = headers.map(h => escapeTSVValue(problem[fieldFromHeader(h)]));
        tsv += row.join('\\t') + '\\n';
      });

      return tsv;
    }

    /**
     * Serialize problems to CSV format
     */
    function serializeToCSV(problems, mode) {
      const headers = getHeadersForMode(mode);
      let csv = headers.map(h => escapeCSVValue(h)).join(',') + '\\n';

      problems.forEach(problem => {
        const row = headers.map(h => escapeCSVValue(problem[fieldFromHeader(h)]));
        csv += row.join(',') + '\\n';
      });

      return csv;
    }

    /**
     * Serialize problems to JSON format
     */
    function serializeToJSON(problems, mode, fileKey) {
      const exportData = {
        fileKey: fileKey,
        mode: mode,
        exportDate: new Date().toISOString(),
        version: '1.0',
        problems: problems
      };
      return JSON.stringify(exportData, null, 2);
    }

    /**
     * Serialize problems to XML format
     */
    function serializeToXML(problems, mode, fileKey) {
      let xml = '<?xml version="1.0" encoding="UTF-8"?>\\n';
      xml += `<export fileKey="${escapeXMLAttr(fileKey)}" mode="${mode}" exportDate="${new Date().toISOString()}" version="1.0">\\n`;
      xml += '  <problems>\\n';

      problems.forEach(problem => {
        xml += '    <problem>\\n';
        for (const [key, value] of Object.entries(problem)) {
          xml += `      <${key}>${escapeXMLValue(value)}</${key}>\\n`;
        }
        xml += '    </problem>\\n';
      });

      xml += '  </problems>\\n';
      xml += '</export>';
      return xml;
    }

    /**
     * Serialize problems to YAML format
     */
    function serializeToYAML(problems, mode, fileKey) {
      let yaml = `fileKey: ${fileKey}\\n`;
      yaml += `mode: ${mode}\\n`;
      yaml += `exportDate: "${new Date().toISOString()}"\\n`;
      yaml += 'version: "1.0"\\n';
      yaml += 'problems:\\n';

      problems.forEach(problem => {
        yaml += '  - ';
        const entries = Object.entries(problem);
        entries.forEach(([key, value], idx) => {
          const prefix = idx === 0 ? '' : '    ';
          yaml += `${prefix}${key}: ${formatYAMLValue(value)}\\n`;
        });
      });

      return yaml;
    }

    // ============================================
    // FORMAT PARSERS
    // ============================================

    /**
     * Parse TSV content to problems array
     */
    function parseFromTSV(content) {
      const lines = content.trim().split('\\n');
      if (lines.length < 2) return { problems: [], fileKey: null, mode: null };

      const headers = lines[0].split('\\t').map(h => h.trim());
      const problems = [];

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split('\\t');
        if (values.length < headers.length) continue;

        const problem = {};
        headers.forEach((header, idx) => {
          const field = fieldFromHeader(header);
          problem[field] = parseFieldValue(field, values[idx]);
        });
        problems.push(problem);
      }

      return { problems, fileKey: null, mode: detectModeFromFields(problems[0]) };
    }

    /**
     * Parse CSV content to problems array
     */
    function parseFromCSV(content) {
      const lines = parseCSVLines(content);
      if (lines.length < 2) return { problems: [], fileKey: null, mode: null };

      const headers = lines[0].map(h => h.trim());
      const problems = [];

      for (let i = 1; i < lines.length; i++) {
        const values = lines[i];
        if (values.length < headers.length) continue;

        const problem = {};
        headers.forEach((header, idx) => {
          const field = fieldFromHeader(header);
          problem[field] = parseFieldValue(field, values[idx]);
        });
        problems.push(problem);
      }

      return { problems, fileKey: null, mode: detectModeFromFields(problems[0]) };
    }

    /**
     * Parse JSON content to problems array
     */
    function parseFromJSON(content) {
      try {
        const data = JSON.parse(content);
        // Handle both array format and object format
        if (Array.isArray(data)) {
          return { problems: data, fileKey: null, mode: detectModeFromFields(data[0]) };
        }
        return {
          problems: data.problems || [],
          fileKey: data.fileKey || null,
          mode: data.mode || detectModeFromFields((data.problems || [])[0])
        };
      } catch (e) {
        console.error('JSON parse error:', e);
        return { problems: [], fileKey: null, mode: null };
      }
    }

    /**
     * Parse XML content to problems array
     */
    function parseFromXML(content) {
      try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(content, 'application/xml');

        const exportEl = doc.querySelector('export');
        const fileKey = exportEl ? exportEl.getAttribute('fileKey') : null;
        const mode = exportEl ? exportEl.getAttribute('mode') : null;

        const problemElements = doc.querySelectorAll('problem');
        const problems = [];

        problemElements.forEach(el => {
          const problem = {};
          for (const child of el.children) {
            problem[child.tagName] = parseFieldValue(child.tagName, child.textContent);
          }
          problems.push(problem);
        });

        return { problems, fileKey, mode: mode || detectModeFromFields(problems[0]) };
      } catch (e) {
        console.error('XML parse error:', e);
        return { problems: [], fileKey: null, mode: null };
      }
    }

    /**
     * Parse YAML content to problems array
     */
    function parseFromYAML(content) {
      try {
        const lines = content.split('\\n');
        let fileKey = null;
        let mode = null;
        const problems = [];
        let currentProblem = null;
        let inProblems = false;

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith('#')) continue;

          if (trimmed.startsWith('fileKey:')) {
            fileKey = parseYAMLValue(trimmed.substring(8).trim());
          } else if (trimmed.startsWith('mode:')) {
            mode = parseYAMLValue(trimmed.substring(5).trim());
          } else if (trimmed === 'problems:') {
            inProblems = true;
          } else if (inProblems) {
            if (trimmed.startsWith('- ')) {
              if (currentProblem) problems.push(currentProblem);
              currentProblem = {};
              const rest = trimmed.substring(2);
              if (rest.includes(':')) {
                const [key, ...valueParts] = rest.split(':');
                const value = valueParts.join(':').trim();
                currentProblem[key.trim()] = parseFieldValue(key.trim(), parseYAMLValue(value));
              }
            } else if (currentProblem && trimmed.includes(':')) {
              const [key, ...valueParts] = trimmed.split(':');
              const value = valueParts.join(':').trim();
              currentProblem[key.trim()] = parseFieldValue(key.trim(), parseYAMLValue(value));
            }
          }
        }

        if (currentProblem) problems.push(currentProblem);

        return { problems, fileKey, mode: mode || detectModeFromFields(problems[0]) };
      } catch (e) {
        console.error('YAML parse error:', e);
        return { problems: [], fileKey: null, mode: null };
      }
    }

    // ============================================
    // HELPER FUNCTIONS
    // ============================================

    function getHeadersForMode(mode) {
      switch (mode) {
        case 'problems':
          return ['Problem Name', 'Difficulty', 'Intermediate Time', 'Advanced Time', 'Top Time', 'Pattern'];
        case 'user':
          return ['Problem Name', 'Solved', 'Time to Solve', 'Comments', 'Solved Date'];
        case 'full':
        default:
          return ['Problem Name', 'Difficulty', 'Intermediate Time', 'Advanced Time', 'Top Time', 'Pattern', 'Solved', 'Time to Solve', 'Comments', 'Solved Date'];
      }
    }

    function fieldFromHeader(header) {
      const map = {
        'Problem Name': 'name',
        'Difficulty': 'difficulty',
        'Intermediate Time': 'intermediate_time',
        'Intermediate Max time': 'intermediate_time',
        'Advanced Time': 'advanced_time',
        'Advanced Max time': 'advanced_time',
        'Top Time': 'top_time',
        'Top of the crop max time': 'top_time',
        'Pattern': 'pattern',
        'Problem Pattern': 'pattern',
        'Solved': 'solved',
        'Time to Solve': 'time_to_solve',
        'Comments': 'comments',
        'Solved Date': 'solved_date'
      };
      return map[header] || header.toLowerCase().replace(/ /g, '_');
    }

    function parseFieldValue(field, value) {
      if (value === null || value === undefined) return '';
      const str = String(value).trim();

      if (field === 'solved') {
        return str.toLowerCase() === 'true' || str === '1';
      }
      return str;
    }

    function detectModeFromFields(problem) {
      if (!problem) return 'full';
      const hasUserFields = 'solved' in problem || 'time_to_solve' in problem || 'comments' in problem || 'solved_date' in problem;
      const hasProblemFields = 'difficulty' in problem || 'pattern' in problem || 'intermediate_time' in problem;

      if (hasUserFields && hasProblemFields) return 'full';
      if (hasUserFields) return 'user';
      if (hasProblemFields) return 'problems';
      return 'full';
    }

    // TSV escaping
    function escapeTSVValue(value) {
      if (value === null || value === undefined) return '';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      return String(value).replace(/\\t/g, ' ').replace(/\\n/g, ' ').replace(/\\r/g, '');
    }

    // CSV escaping
    function escapeCSVValue(value) {
      if (value === null || value === undefined) return '';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      const str = String(value);
      if (str.includes(',') || str.includes('"') || str.includes('\\n') || str.includes('\\r')) {
        return '"' + str.replace(/"/g, '""') + '"';
      }
      return str;
    }

    // CSV parsing - handles quoted values
    function parseCSVLines(content) {
      const lines = [];
      let currentLine = [];
      let currentValue = '';
      let inQuotes = false;

      for (let i = 0; i < content.length; i++) {
        const char = content[i];
        const nextChar = content[i + 1];

        if (inQuotes) {
          if (char === '"' && nextChar === '"') {
            currentValue += '"';
            i++;
          } else if (char === '"') {
            inQuotes = false;
          } else {
            currentValue += char;
          }
        } else {
          if (char === '"') {
            inQuotes = true;
          } else if (char === ',') {
            currentLine.push(currentValue);
            currentValue = '';
          } else if (char === '\\n' || (char === '\\r' && nextChar === '\\n')) {
            if (char === '\\r') i++;
            currentLine.push(currentValue);
            if (currentLine.length > 0) lines.push(currentLine);
            currentLine = [];
            currentValue = '';
          } else if (char !== '\\r') {
            currentValue += char;
          }
        }
      }

      // Handle last value
      currentLine.push(currentValue);
      if (currentLine.length > 0 && currentLine.some(v => v !== '')) {
        lines.push(currentLine);
      }

      return lines;
    }

    // XML escaping
    function escapeXMLValue(value) {
      if (value === null || value === undefined) return '';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    }

    function escapeXMLAttr(value) {
      if (value === null || value === undefined) return '';
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // YAML formatting
    function formatYAMLValue(value) {
      if (value === null || value === undefined) return '""';
      if (typeof value === 'boolean') return value ? 'true' : 'false';
      const str = String(value);
      // Quote strings that need it
      if (str.includes(':') || str.includes('#') || str.includes('\\n') || str.includes('"') || str.includes("'") || str.trim() !== str) {
        return '"' + str.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"') + '"';
      }
      return str || '""';
    }

    function parseYAMLValue(value) {
      if (!value) return '';
      const trimmed = value.trim();
      // Remove quotes if present
      if ((trimmed.startsWith('"') && trimmed.endsWith('"')) ||
          (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
        return trimmed.slice(1, -1);
      }
      return trimmed;
    }

    // ============================================
    // EXPORT FUNCTIONS
    // ============================================

    /**
     * Export a single tab
     */
    function exportTab(fileKey) {
      const formatSelect = document.getElementById(`format-select-${fileKey}`);
      const modeSelect = document.getElementById(`mode-select-${fileKey}`);

      const format = formatSelect ? formatSelect.value : 'json';
      const mode = modeSelect ? modeSelect.value : 'full';

      const problems = filterByMode(PROBLEM_DATA.data[fileKey], mode);
      const content = serializeData(problems, format, mode, fileKey);
      const filename = `${fileKey}_${mode}${FILE_EXTENSIONS[format]}`;

      downloadFile(filename, content, MIME_TYPES[format]);
    }

    /**
     * Export all tabs
     */
    function exportAll() {
      const formatSelect = document.getElementById('global-format-select');
      const modeSelect = document.getElementById('global-mode-select');

      const format = formatSelect ? formatSelect.value : 'json';
      const mode = modeSelect ? modeSelect.value : 'full';

      PROBLEM_DATA.file_list.forEach(fileKey => {
        const problems = filterByMode(PROBLEM_DATA.data[fileKey], mode);
        const content = serializeData(problems, format, mode, fileKey);
        const filename = `${fileKey}_${mode}${FILE_EXTENSIONS[format]}`;

        // Small delay between downloads to avoid browser blocking
        setTimeout(() => {
          downloadFile(filename, content, MIME_TYPES[format]);
        }, 100 * PROBLEM_DATA.file_list.indexOf(fileKey));
      });
    }

    /**
     * Serialize data to specified format
     */
    function serializeData(problems, format, mode, fileKey) {
      switch (format) {
        case 'tsv': return serializeToTSV(problems, mode);
        case 'csv': return serializeToCSV(problems, mode);
        case 'json': return serializeToJSON(problems, mode, fileKey);
        case 'xml': return serializeToXML(problems, mode, fileKey);
        case 'yaml': return serializeToYAML(problems, mode, fileKey);
        default: return serializeToJSON(problems, mode, fileKey);
      }
    }

    // ============================================
    // IMPORT FUNCTIONS
    // ============================================

    /**
     * Trigger file import dialog for a tab
     */
    function triggerImport(fileKey) {
      const input = document.getElementById(`import-file-${fileKey}`);
      if (input) {
        input.dataset.fileKey = fileKey;
        input.click();
      }
    }

    /**
     * Trigger file import dialog for all tabs
     */
    function triggerImportAll() {
      const input = document.getElementById('import-file-all');
      if (input) {
        input.click();
      }
    }

    /**
     * Handle file selection for import
     */
    function handleFileImport(event, fileKey) {
      const file = event.target.files[0];
      if (!file) return;

      const modeSelect = document.getElementById(`mode-select-${fileKey}`);
      const selectedMode = modeSelect ? modeSelect.value : 'full';

      const reader = new FileReader();
      reader.onload = function(e) {
        const content = e.target.result;
        const format = detectFormat(file.name, content);
        const parsed = parseData(content, format);

        if (!parsed.problems || parsed.problems.length === 0) {
          alert('No valid data found in the file. Please check the format.');
          return;
        }

        // Use selected mode, or detected mode if available
        const mode = selectedMode || parsed.mode || 'full';

        // Detect conflicts
        const conflicts = detectConflicts(fileKey, parsed.problems, mode);

        if (conflicts.length > 0) {
          // Show conflict dialog
          pendingImport = {
            fileKey: fileKey,
            data: parsed.problems,
            mode: mode,
            conflicts: conflicts
          };
          showConflictDialog();
        } else {
          // Apply import directly
          applyImport(fileKey, parsed.problems, mode, {});
          alert(`Successfully imported ${parsed.problems.length} problem(s).`);
        }
      };

      reader.onerror = function() {
        alert('Error reading file. Please try again.');
      };

      reader.readAsText(file);

      // Reset file input
      event.target.value = '';
    }

    /**
     * Handle multiple file import
     */
    function handleMultiFileImport(event) {
      const files = event.target.files;
      if (!files || files.length === 0) return;

      const modeSelect = document.getElementById('global-mode-select');
      const selectedMode = modeSelect ? modeSelect.value : 'full';

      let processedCount = 0;
      const totalFiles = files.length;
      const allConflicts = [];

      Array.from(files).forEach(file => {
        const reader = new FileReader();
        reader.onload = function(e) {
          const content = e.target.result;
          const format = detectFormat(file.name, content);
          const parsed = parseData(content, format);

          if (parsed.problems && parsed.problems.length > 0) {
            const fileKey = parsed.fileKey || file.name.replace(/\\.[^.]+$/, '').toLowerCase().replace(/[^a-z0-9]/g, '_');

            // Check if fileKey exists
            if (!PROBLEM_DATA.data[fileKey]) {
              // New tab - handle Problem Set import
              if (selectedMode === 'problems' || parsed.mode === 'problems') {
                createNewTab(fileKey, parsed.problems);
              } else {
                alert(`File "${file.name}" references unknown tab "${fileKey}". Use "Problem Set" mode to create new tabs.`);
              }
            } else {
              const conflicts = detectConflicts(fileKey, parsed.problems, selectedMode);
              if (conflicts.length > 0) {
                allConflicts.push({ fileKey, data: parsed.problems, mode: selectedMode, conflicts });
              } else {
                applyImport(fileKey, parsed.problems, selectedMode, {});
              }
            }
          }

          processedCount++;
          if (processedCount === totalFiles) {
            if (allConflicts.length > 0) {
              // Handle first conflict set (can be improved to handle all)
              pendingImport = allConflicts[0];
              showConflictDialog();
            } else {
              alert(`Successfully processed ${totalFiles} file(s).`);
            }
          }
        };
        reader.readAsText(file);
      });

      // Reset file input
      event.target.value = '';
    }

    /**
     * Detect file format from filename or content
     */
    function detectFormat(filename, content) {
      const ext = filename.split('.').pop().toLowerCase();
      if (['tsv', 'csv', 'json', 'xml', 'yaml', 'yml'].includes(ext)) {
        return ext === 'yml' ? 'yaml' : ext;
      }

      // Content-based detection
      const trimmed = content.trim();
      if (trimmed.startsWith('{') || trimmed.startsWith('[')) return 'json';
      if (trimmed.startsWith('<?xml') || trimmed.startsWith('<export')) return 'xml';
      if (trimmed.includes('\\t') && !trimmed.includes(',')) return 'tsv';
      if (trimmed.startsWith('fileKey:') || trimmed.startsWith('problems:')) return 'yaml';
      return 'csv';
    }

    /**
     * Parse data from specified format
     */
    function parseData(content, format) {
      switch (format) {
        case 'tsv': return parseFromTSV(content);
        case 'csv': return parseFromCSV(content);
        case 'json': return parseFromJSON(content);
        case 'xml': return parseFromXML(content);
        case 'yaml': return parseFromYAML(content);
        default: return parseFromJSON(content);
      }
    }

    // ============================================
    // CONFLICT DETECTION AND RESOLUTION
    // ============================================

    /**
     * Detect conflicts between existing and imported data
     */
    function detectConflicts(fileKey, importedData, mode) {
      const existingData = PROBLEM_DATA.data[fileKey];
      if (!existingData) return [];

      const conflicts = [];

      importedData.forEach((imported, importIdx) => {
        const existingIdx = existingData.findIndex(e => e.name === imported.name);

        if (existingIdx !== -1) {
          const existing = existingData[existingIdx];
          let hasConflict = false;

          if (mode === 'user' || mode === 'full') {
            // Check user data conflicts
            if ((imported.solved !== undefined && existing.solved !== imported.solved) ||
                (imported.time_to_solve !== undefined && existing.time_to_solve !== imported.time_to_solve) ||
                (imported.comments !== undefined && existing.comments !== imported.comments) ||
                (imported.solved_date !== undefined && existing.solved_date !== imported.solved_date)) {
              hasConflict = true;
            }
          }

          if (mode === 'problems' || mode === 'full') {
            // Check problem definition conflicts
            if ((imported.difficulty !== undefined && existing.difficulty !== imported.difficulty) ||
                (imported.pattern !== undefined && existing.pattern !== imported.pattern) ||
                (imported.intermediate_time !== undefined && existing.intermediate_time !== imported.intermediate_time) ||
                (imported.advanced_time !== undefined && existing.advanced_time !== imported.advanced_time) ||
                (imported.top_time !== undefined && existing.top_time !== imported.top_time)) {
              hasConflict = true;
            }
          }

          if (hasConflict) {
            conflicts.push({
              name: imported.name,
              existingIdx: existingIdx,
              importIdx: importIdx,
              existing: existing,
              imported: imported
            });
          }
        }
      });

      return conflicts;
    }

    /**
     * Apply import with conflict resolutions
     */
    function applyImport(fileKey, importedData, mode, resolutions) {
      const existingData = PROBLEM_DATA.data[fileKey];
      let addedCount = 0;
      let updatedCount = 0;

      importedData.forEach(imported => {
        const existingIdx = existingData.findIndex(e => e.name === imported.name);
        const resolution = resolutions[imported.name] || 'overwrite';

        if (existingIdx !== -1) {
          // Existing problem
          if (resolution === 'skip') return;

          if (resolution === 'keep-latest') {
            const existingDate = new Date(existingData[existingIdx].solved_date || 0);
            const importedDate = new Date(imported.solved_date || 0);
            if (importedDate <= existingDate) return;
          }

          // Apply update based on mode
          const existing = existingData[existingIdx];

          if (mode === 'user' || mode === 'full') {
            if (imported.solved !== undefined) existing.solved = imported.solved;
            if (imported.time_to_solve !== undefined) existing.time_to_solve = imported.time_to_solve;
            if (imported.comments !== undefined) existing.comments = imported.comments;
            if (imported.solved_date !== undefined) existing.solved_date = imported.solved_date;
          }

          if (mode === 'problems' || mode === 'full') {
            if (imported.difficulty !== undefined) existing.difficulty = imported.difficulty;
            if (imported.intermediate_time !== undefined) existing.intermediate_time = imported.intermediate_time;
            if (imported.advanced_time !== undefined) existing.advanced_time = imported.advanced_time;
            if (imported.top_time !== undefined) existing.top_time = imported.top_time;
            if (imported.pattern !== undefined) existing.pattern = imported.pattern;
          }

          updatedCount++;
        } else if (mode === 'problems' || mode === 'full') {
          // New problem - add to list
          const newProblem = {
            name: imported.name,
            difficulty: imported.difficulty || 'Medium',
            intermediate_time: imported.intermediate_time || '',
            advanced_time: imported.advanced_time || '',
            top_time: imported.top_time || '',
            pattern: imported.pattern || '',
            solved: imported.solved || false,
            time_to_solve: imported.time_to_solve || '',
            comments: imported.comments || '',
            solved_date: imported.solved_date || ''
          };
          existingData.push(newProblem);
          addedCount++;
        }
      });

      // Save and sync
      saveToLocalStorage(fileKey);
      syncAfterImport(fileKey);
      renderTable(fileKey);
      updateProgress(fileKey);
      updateOverallProgress();

      if (typeof updateAwarenessColors === 'function') {
        updateAwarenessColors();
      }

      return { added: addedCount, updated: updatedCount };
    }

    /**
     * Sync duplicates after import
     */
    function syncAfterImport(fileKey) {
      const problems = PROBLEM_DATA.data[fileKey];
      problems.forEach(problem => {
        if (DUPLICATE_MAP && DUPLICATE_MAP[problem.name]) {
          // Sync each user data field
          if (typeof syncDuplicates === 'function') {
            syncDuplicates(problem.name, 'solved', problem.solved);
            syncDuplicates(problem.name, 'time_to_solve', problem.time_to_solve);
            syncDuplicates(problem.name, 'comments', problem.comments);
            syncDuplicates(problem.name, 'solved_date', problem.solved_date);
          }
        }
      });
    }

    /**
     * Create a new tab from imported problem set
     */
    function createNewTab(fileKey, problems) {
      // Add to PROBLEM_DATA
      PROBLEM_DATA.data[fileKey] = problems.map(p => ({
        name: p.name,
        difficulty: p.difficulty || 'Medium',
        intermediate_time: p.intermediate_time || '',
        advanced_time: p.advanced_time || '',
        top_time: p.top_time || '',
        pattern: p.pattern || '',
        solved: p.solved || false,
        time_to_solve: p.time_to_solve || '',
        comments: p.comments || '',
        solved_date: p.solved_date || ''
      }));
      PROBLEM_DATA.file_list.push(fileKey);

      // Update duplicate map
      problems.forEach(p => {
        const existingFiles = [];
        PROBLEM_DATA.file_list.forEach(fk => {
          if (PROBLEM_DATA.data[fk].some(prob => prob.name === p.name)) {
            existingFiles.push(fk);
          }
        });
        if (existingFiles.length > 1) {
          DUPLICATE_MAP[p.name] = existingFiles;
        }
      });

      // Dynamically create tab UI
      createTabUI(fileKey);

      // Save and render
      saveToLocalStorage(fileKey);
      renderTable(fileKey);
      updateProgress(fileKey);
      updateOverallProgress();

      alert(`Created new tab "${fileKey}" with ${problems.length} problem(s).`);
    }

    /**
     * Initialize export preference dropdowns with saved values and add event listeners
     */
    function initExportPreferences() {
      // Get saved preferences
      const savedFormat = typeof getExportFormat === 'function' ? getExportFormat() : 'json';
      const savedMode = typeof getExportMode === 'function' ? getExportMode() : 'user';

      // Set global dropdowns
      const globalFormatSelect = document.getElementById('global-format-select');
      const globalModeSelect = document.getElementById('global-mode-select');

      if (globalFormatSelect) {
        globalFormatSelect.value = savedFormat;
        globalFormatSelect.addEventListener('change', function() {
          if (typeof setExportFormat === 'function') setExportFormat(this.value);
        });
      }

      if (globalModeSelect) {
        globalModeSelect.value = savedMode;
        globalModeSelect.addEventListener('change', function() {
          if (typeof setExportMode === 'function') setExportMode(this.value);
        });
      }

      // Set per-tab dropdowns
      PROBLEM_DATA.file_list.forEach(fileKey => {
        const formatSelect = document.getElementById(`format-select-${fileKey}`);
        const modeSelect = document.getElementById(`mode-select-${fileKey}`);

        if (formatSelect) {
          formatSelect.value = savedFormat;
          formatSelect.addEventListener('change', function() {
            if (typeof setExportFormat === 'function') setExportFormat(this.value);
          });
        }

        if (modeSelect) {
          modeSelect.value = savedMode;
          modeSelect.addEventListener('change', function() {
            if (typeof setExportMode === 'function') setExportMode(this.value);
          });
        }
      });
    }

    /**
     * Dynamically create tab UI elements
     */
    function createTabUI(fileKey) {
      const displayName = fileKey.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());

      // Create tab button
      const tabContainer = document.querySelector('.tab-container');
      const tabButton = document.createElement('button');
      tabButton.className = 'tab-button';
      tabButton.dataset.tab = fileKey;
      tabButton.textContent = displayName;
      tabButton.addEventListener('click', function() {
        switchTab(fileKey);
      });
      tabContainer.appendChild(tabButton);

      // Create tab content (simplified version)
      const container = document.querySelector('.container');
      const tabContent = document.createElement('div');
      tabContent.id = `tab-${fileKey}`;
      tabContent.className = 'tab-content';
      tabContent.innerHTML = `
        <div class="progress-section">
          <div class="progress-bar-container">
            <div class="progress-bar" id="progress-${fileKey}"></div>
          </div>
          <div class="progress-text" id="progress-text-${fileKey}">Solved 0 / 0 problems (0%)</div>
        </div>
        <div class="filter-section">
          <input type="text" id="search-${fileKey}" class="search-box" placeholder="Search problems...">
          <select id="difficulty-filter-${fileKey}" class="filter-dropdown">
            <option value="">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
          </select>
          <select id="pattern-filter-${fileKey}" class="filter-dropdown">
            <option value="">All Patterns</option>
          </select>
          <select id="solved-filter-${fileKey}" class="filter-dropdown">
            <option value="">All Status</option>
            <option value="solved">Solved</option>
            <option value="unsolved">Unsolved</option>
          </select>
          <select id="color-filter-${fileKey}" class="filter-dropdown">
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
            <button class="hamburger-btn" onclick="toggleImportExportMenu('${fileKey}')" aria-label="Import/Export Menu" aria-expanded="false">
              <span aria-hidden="true">&#9776;</span>
            </button>
            <div class="import-export-menu" id="import-export-menu-${fileKey}" style="display:none;">
              <div class="import-export-menu-header">Import / Export</div>
              <div class="import-export-menu-content">
                <label class="import-export-menu-label">Format:</label>
                <select id="format-select-${fileKey}" class="filter-dropdown format-select">
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="tsv">TSV</option>
                  <option value="xml">XML</option>
                  <option value="yaml">YAML</option>
                </select>
                <label class="import-export-menu-label">Mode:</label>
                <select id="mode-select-${fileKey}" class="filter-dropdown mode-select">
                  <option value="full">Full Data</option>
                  <option value="user">User Progress</option>
                  <option value="problems">Problem Set</option>
                </select>
                <div class="import-export-menu-divider"></div>
                <button class="import-export-menu-item export-action" onclick="exportTab('${fileKey}'); hideImportExportMenu('${fileKey}');">
                  <span>&#8681;</span> Export Tab
                </button>
                <button class="import-export-menu-item import-action" onclick="triggerImport('${fileKey}'); hideImportExportMenu('${fileKey}');">
                  <span>&#8679;</span> Import to Tab
                </button>
              </div>
              <input type="file" id="import-file-${fileKey}" style="display:none" accept=".tsv,.csv,.json,.xml,.yaml,.yml" onchange="handleFileImport(event, '${fileKey}')">
            </div>
          </div>
        </div>
        <div class="table-container">
          <table id="table-${fileKey}">
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
            <tbody id="tbody-${fileKey}">
            </tbody>
          </table>
        </div>
      `;
      container.appendChild(tabContent);

      // Setup event listeners for new tab
      const searchBox = document.getElementById(`search-${fileKey}`);
      const difficultyFilter = document.getElementById(`difficulty-filter-${fileKey}`);
      const patternFilter = document.getElementById(`pattern-filter-${fileKey}`);
      const solvedFilter = document.getElementById(`solved-filter-${fileKey}`);
      const colorFilter = document.getElementById(`color-filter-${fileKey}`);

      if (searchBox) searchBox.addEventListener('input', () => applyFilters(fileKey));
      if (difficultyFilter) difficultyFilter.addEventListener('change', () => applyFilters(fileKey));
      if (patternFilter) patternFilter.addEventListener('change', () => applyFilters(fileKey));
      if (solvedFilter) solvedFilter.addEventListener('change', () => applyFilters(fileKey));
      if (colorFilter) colorFilter.addEventListener('change', () => applyFilters(fileKey));

      // Populate pattern filter
      const patterns = new Set();
      PROBLEM_DATA.data[fileKey].forEach(p => {
        if (p.pattern) patterns.add(p.pattern);
      });
      const patternSelect = document.getElementById(`pattern-filter-${fileKey}`);
      Array.from(patterns).sort().forEach(pattern => {
        const option = document.createElement('option');
        option.value = pattern;
        option.textContent = pattern;
        patternSelect.appendChild(option);
      });
    }
    '''

    return js


if __name__ == "__main__":
    print(generate_js_import_export())
