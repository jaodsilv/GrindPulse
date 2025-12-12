#!/usr/bin/env python3
"""
JavaScript Conflict Dialog Generator
Implements the conflict resolution dialog for import operations
"""


def generate_js_conflict_dialog():
    """Generate JavaScript conflict dialog logic"""

    js = '''
    // ============================================
    // CONFLICT RESOLUTION DIALOG
    // ============================================

    /**
     * Handle Escape key to close conflict dialog
     * Named function to allow proper removal with removeEventListener
     */
    function handleConflictDialogEscape(e) {
      if (e.key === 'Escape') {
        const overlay = document.getElementById('conflict-overlay');
        if (overlay && overlay.style.display === 'flex') {
          hideConflictDialog();
        }
      }
    }

    /**
     * Show the conflict resolution dialog
     */
    function showConflictDialog() {
      const overlay = document.getElementById('conflict-overlay');
      if (!overlay) {
        createConflictDialogHTML();
      }

      renderConflictList();
      document.getElementById('conflict-overlay').style.display = 'flex';

      // Add Escape key listener
      document.addEventListener('keydown', handleConflictDialogEscape);

      // Focus management
      const firstInput = document.querySelector('.conflict-option input');
      if (firstInput) firstInput.focus();
    }

    /**
     * Hide the conflict resolution dialog
     */
    function hideConflictDialog() {
      const overlay = document.getElementById('conflict-overlay');
      if (overlay) {
        overlay.style.display = 'none';
      }

      // Remove Escape key listener to prevent memory leak
      document.removeEventListener('keydown', handleConflictDialogEscape);

      // Clear pending import
      ImportExport.pendingImport = {
        fileKey: null,
        data: null,
        mode: null,
        conflicts: []
      };
    }

    /**
     * Create conflict dialog HTML structure
     */
    function createConflictDialogHTML() {
      const overlay = document.createElement('div');
      overlay.id = 'conflict-overlay';
      overlay.className = 'conflict-overlay';
      overlay.innerHTML = `
        <div class="conflict-panel" role="dialog" aria-labelledby="conflict-title" aria-modal="true">
          <div class="conflict-header">
            <h2 id="conflict-title">Import Conflicts Detected</h2>
            <button class="conflict-close" onclick="hideConflictDialog()" aria-label="Close dialog">&times;</button>
          </div>

          <div class="conflict-description">
            <p>The following problems have different values in your current data and the imported file. Choose how to resolve each conflict:</p>
          </div>

          <div class="conflict-global-actions">
            <span>Apply to all:</span>
            <button class="conflict-action-btn" onclick="applyToAllConflicts('overwrite')">Overwrite All</button>
            <button class="conflict-action-btn" onclick="applyToAllConflicts('skip')">Skip All</button>
            <button class="conflict-action-btn" onclick="applyToAllConflicts('keep-latest')">Keep Latest All</button>
          </div>

          <div class="conflict-list" id="conflict-list">
            <!-- Conflict items rendered here -->
          </div>

          <div class="conflict-footer">
            <button class="conflict-btn-secondary" onclick="cancelImport()">Cancel</button>
            <button class="conflict-btn-primary" onclick="confirmImport()">Apply & Import</button>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);

      // Close on overlay click
      overlay.addEventListener('click', function(e) {
        if (e.target === overlay) {
          hideConflictDialog();
        }
      });

      // Note: Escape key listener is added in showConflictDialog() and removed in hideConflictDialog()
      // to prevent memory leaks from accumulating listeners
    }

    /**
     * Render the conflict list
     */
    function renderConflictList() {
      const listContainer = document.getElementById('conflict-list');
      if (!listContainer) return;

      listContainer.innerHTML = '';

      ImportExport.pendingImport.conflicts.forEach((conflict, idx) => {
        const item = document.createElement('div');
        item.className = 'conflict-item';
        item.dataset.name = conflict.name;

        item.innerHTML = `
          <div class="conflict-problem-name">${escapeHTML(conflict.name)}</div>
          <div class="conflict-comparison">
            <div class="conflict-existing">
              <h4>Current Data</h4>
              <div class="conflict-data">${formatConflictData(conflict.existing, ImportExport.pendingImport.mode)}</div>
            </div>
            <div class="conflict-arrow">&#8594;</div>
            <div class="conflict-imported">
              <h4>Imported Data</h4>
              <div class="conflict-data">${formatConflictData(conflict.imported, ImportExport.pendingImport.mode)}</div>
            </div>
          </div>
          <div class="conflict-options">
            <label class="conflict-option">
              <input type="radio" name="conflict-${idx}" value="overwrite" checked>
              <span>Overwrite</span>
            </label>
            <label class="conflict-option">
              <input type="radio" name="conflict-${idx}" value="skip">
              <span>Skip</span>
            </label>
            <label class="conflict-option">
              <input type="radio" name="conflict-${idx}" value="keep-latest">
              <span>Keep Latest</span>
            </label>
          </div>
        `;

        listContainer.appendChild(item);
      });
    }

    /**
     * Format conflict data for display
     */
    function formatConflictData(data, mode) {
      if (!data) return '<em>No data</em>';

      // Validate mode parameter
      const validModes = ['full', 'problems', 'user'];
      if (!validModes.includes(mode)) {
        console.warn('formatConflictData: Invalid mode "' + mode + '", defaulting to "full"');
        mode = 'full';
      }

      let html = '<ul class="conflict-data-list">';

      if (mode === 'user' || mode === 'full') {
        html += `<li><strong>Solved:</strong> ${data.solved ? 'Yes' : 'No'}</li>`;
        if (data.time_to_solve) html += `<li><strong>Time:</strong> ${escapeHTML(String(data.time_to_solve))} min</li>`;
        if (data.comments) html += `<li><strong>Comments:</strong> ${truncateText(data.comments, 50)}</li>`;
        if (data.solved_date) html += `<li><strong>Date:</strong> ${formatDate(data.solved_date)}</li>`;
      }

      if (mode === 'problems' || mode === 'full') {
        if (data.difficulty) html += `<li><strong>Difficulty:</strong> ${escapeHTML(String(data.difficulty))}</li>`;
        if (data.pattern) html += `<li><strong>Pattern:</strong> ${escapeHTML(String(data.pattern))}</li>`;
        if (data.intermediate_time) html += `<li><strong>Int. Time:</strong> ${escapeHTML(String(data.intermediate_time))}</li>`;
        if (data.advanced_time) html += `<li><strong>Adv. Time:</strong> ${escapeHTML(String(data.advanced_time))}</li>`;
        if (data.top_time) html += `<li><strong>Top Time:</strong> ${escapeHTML(String(data.top_time))}</li>`;
      }

      html += '</ul>';
      return html;
    }

    /**
     * Truncate text with ellipsis
     */
    function truncateText(text, maxLength) {
      if (!text) return '';
      const str = String(text);
      if (str.length <= maxLength) return escapeHTML(str);
      return escapeHTML(str.substring(0, maxLength)) + '...';
    }

    /**
     * Format date for display
     */
    function formatDate(isoDate) {
      if (!isoDate) return 'N/A';
      try {
        const date = new Date(isoDate);
        if (isNaN(date.getTime())) {
          // Invalid date - escape the raw value as fallback
          return escapeHTML(String(isoDate));
        }
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch (e) {
        return escapeHTML(String(isoDate));
      }
    }

    /**
     * Backup current state before bulk operations
     */
    function backupBeforeImport(fileKey) {
      const backup = {
        timestamp: Date.now(),
        fileKey: fileKey,
        data: JSON.parse(localStorage.getItem('progress_' + fileKey) || '{}')
      };
      localStorage.setItem('import_backup', JSON.stringify(backup));
    }

    /**
     * Undo last import operation (within 1 hour)
     */
    function undoLastImport() {
      const backup = JSON.parse(localStorage.getItem('import_backup') || 'null');
      if (!backup) {
        alert('No import backup available to restore.');
        return false;
      }
      if (Date.now() - backup.timestamp > 3600000) { // 1 hour expiry
        alert('Import backup has expired (older than 1 hour).');
        localStorage.removeItem('import_backup');
        return false;
      }
      localStorage.setItem('progress_' + backup.fileKey, JSON.stringify(backup.data));
      localStorage.removeItem('import_backup');
      alert('Successfully restored data from before last import.');
      location.reload();
      return true;
    }

    /**
     * Check if undo is available
     */
    function isUndoAvailable() {
      const backup = JSON.parse(localStorage.getItem('import_backup') || 'null');
      return backup && (Date.now() - backup.timestamp < 3600000);
    }

    /**
     * Apply resolution to all conflicts
     */
    function applyToAllConflicts(resolution) {
      // Add confirmation for destructive "overwrite" operations
      if (resolution === 'overwrite') {
        if (!confirm('WARNING: This will overwrite all conflicting data. This action can be undone within 1 hour. Continue?')) {
          return;
        }
        backupBeforeImport(ImportExport.pendingImport.fileKey);
      }

      ImportExport.pendingImport.conflicts.forEach((conflict, idx) => {
        const radio = document.querySelector(`input[name="conflict-${idx}"][value="${resolution}"]`);
        if (radio) radio.checked = true;
      });
    }

    /**
     * Cancel import and close dialog
     */
    function cancelImport() {
      hideConflictDialog();
    }

    /**
     * Confirm import with selected resolutions
     */
    function confirmImport() {
      if (!ImportExport.pendingImport.fileKey || !ImportExport.pendingImport.data) {
        alert('No import data available.');
        hideConflictDialog();
        return;
      }

      // Gather resolutions
      const resolutions = {};
      ImportExport.pendingImport.conflicts.forEach((conflict, idx) => {
        const selected = document.querySelector(`input[name="conflict-${idx}"]:checked`);
        resolutions[conflict.name] = selected ? selected.value : 'overwrite';
      });

      // Check if any overwrite resolutions exist - if so, create backup
      const hasOverwrites = Object.values(resolutions).some(r => r === 'overwrite');
      if (hasOverwrites) {
        backupBeforeImport(ImportExport.pendingImport.fileKey);
      }

      // Apply import
      const result = applyImport(
        ImportExport.pendingImport.fileKey,
        ImportExport.pendingImport.data,
        ImportExport.pendingImport.mode,
        resolutions
      );

      hideConflictDialog();

      alert(`Import complete! Updated: ${result.updated}, Added: ${result.added}`);
    }
    '''

    return js


if __name__ == "__main__":
    print(generate_js_conflict_dialog())
