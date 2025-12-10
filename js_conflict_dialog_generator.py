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
     * Show the conflict resolution dialog
     */
    function showConflictDialog() {
      const overlay = document.getElementById('conflict-overlay');
      if (!overlay) {
        createConflictDialogHTML();
      }

      renderConflictList();
      document.getElementById('conflict-overlay').style.display = 'flex';

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
      // Clear pending import
      pendingImport = {
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

      // Close on Escape
      document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && overlay.style.display === 'flex') {
          hideConflictDialog();
        }
      });
    }

    /**
     * Render the conflict list
     */
    function renderConflictList() {
      const listContainer = document.getElementById('conflict-list');
      if (!listContainer) return;

      listContainer.innerHTML = '';

      pendingImport.conflicts.forEach((conflict, idx) => {
        const item = document.createElement('div');
        item.className = 'conflict-item';
        item.dataset.name = conflict.name;

        item.innerHTML = `
          <div class="conflict-problem-name">${escapeHTML(conflict.name)}</div>
          <div class="conflict-comparison">
            <div class="conflict-existing">
              <h4>Current Data</h4>
              <div class="conflict-data">${formatConflictData(conflict.existing, pendingImport.mode)}</div>
            </div>
            <div class="conflict-arrow">&#8594;</div>
            <div class="conflict-imported">
              <h4>Imported Data</h4>
              <div class="conflict-data">${formatConflictData(conflict.imported, pendingImport.mode)}</div>
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

      let html = '<ul class="conflict-data-list">';

      if (mode === 'user' || mode === 'full') {
        html += `<li><strong>Solved:</strong> ${data.solved ? 'Yes' : 'No'}</li>`;
        if (data.time_to_solve) html += `<li><strong>Time:</strong> ${data.time_to_solve} min</li>`;
        if (data.comments) html += `<li><strong>Comments:</strong> ${truncateText(data.comments, 50)}</li>`;
        if (data.solved_date) html += `<li><strong>Date:</strong> ${formatDate(data.solved_date)}</li>`;
      }

      if (mode === 'problems' || mode === 'full') {
        if (data.difficulty) html += `<li><strong>Difficulty:</strong> ${data.difficulty}</li>`;
        if (data.pattern) html += `<li><strong>Pattern:</strong> ${data.pattern}</li>`;
        if (data.intermediate_time) html += `<li><strong>Int. Time:</strong> ${data.intermediate_time}</li>`;
        if (data.advanced_time) html += `<li><strong>Adv. Time:</strong> ${data.advanced_time}</li>`;
        if (data.top_time) html += `<li><strong>Top Time:</strong> ${data.top_time}</li>`;
      }

      html += '</ul>';
      return html;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHTML(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
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
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch (e) {
        return isoDate;
      }
    }

    /**
     * Apply resolution to all conflicts
     */
    function applyToAllConflicts(resolution) {
      pendingImport.conflicts.forEach((conflict, idx) => {
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
      if (!pendingImport.fileKey || !pendingImport.data) {
        alert('No import data available.');
        hideConflictDialog();
        return;
      }

      // Gather resolutions
      const resolutions = {};
      pendingImport.conflicts.forEach((conflict, idx) => {
        const selected = document.querySelector(`input[name="conflict-${idx}"]:checked`);
        resolutions[conflict.name] = selected ? selected.value : 'overwrite';
      });

      // Apply import
      const result = applyImport(
        pendingImport.fileKey,
        pendingImport.data,
        pendingImport.mode,
        resolutions
      );

      hideConflictDialog();

      alert(`Import complete! Updated: ${result.updated}, Added: ${result.added}`);
    }
    '''

    return js


if __name__ == "__main__":
    print(generate_js_conflict_dialog())
