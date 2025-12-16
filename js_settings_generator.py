#!/usr/bin/env python3
"""
Settings Panel Sub-Agent
Implements awareness settings panel UI and configuration management
"""


def generate_js_settings():
    """Generate JavaScript settings panel logic"""

    js = """
    // Create and inject settings panel HTML into DOM
    function createSettingsPanel() {
      const overlay = document.createElement('div');
      overlay.id = 'settings-overlay';
      overlay.className = 'settings-overlay';
      overlay.onclick = function(e) {
        if (e.target === this) closeSettingsPanel();
      };

      const panel = document.createElement('div');
      panel.className = 'settings-panel';
      panel.innerHTML = `
        <div class="settings-header">
          <h2>Awareness Settings</h2>
          <button type="button" id="settings-close-btn" class="settings-close">&times;</button>
        </div>

        <form id="settings-form">
        <div class="settings-content">
          <div class="settings-section">
            <h3>Your Commitment</h3>
            <p class="settings-hint">How many problems do you plan to solve?</p>
            <label>
              Problems per day:
              <select id="setting-commitment" class="settings-input settings-select">
                <option value="0.14">1 per week</option>
                <option value="0.5">1 every 2 days</option>
                <option value="1">1 per day</option>
                <option value="2">2 per day (recommended)</option>
                <option value="3">3 per day</option>
                <option value="5">5 per day</option>
              </select>
            </label>
          </div>

          <div class="settings-section">
            <h3>Color Thresholds</h3>
            <p class="settings-hint">Score ranges for each color level</p>
            <label>
              White → Green:
              <input type="number" id="setting-threshold-white" step="1" min="1" max="200" class="settings-input">
            </label>
            <label>
              Green → Yellow:
              <input type="number" id="setting-threshold-green" step="1" min="1" max="200" class="settings-input">
            </label>
            <label>
              Yellow → Red:
              <input type="number" id="setting-threshold-yellow" step="1" min="1" max="200" class="settings-input">
            </label>
            <label>
              Red → Dark Red:
              <input type="number" id="setting-threshold-red" step="1" min="1" max="200" class="settings-input">
            </label>
            <label>
              Dark Red → Flashing:
              <input type="number" id="setting-threshold-darkRed" step="1" min="1" max="200" class="settings-input">
            </label>
          </div>

          <div class="settings-section">
            <h3>Auto-Refresh</h3>
            <p class="settings-hint">How often to update awareness colors automatically</p>
            <label>
              Refresh interval:
              <select id="setting-refreshInterval" class="settings-input settings-select">
                <option value="3600000">Every hour</option>
                <option value="21600000">Every 6 hours</option>
                <option value="43200000">Every 12 hours</option>
                <option value="86400000">Daily (recommended)</option>
                <option value="0">Manual only</option>
              </select>
            </label>
            <label>
              Refresh on focus:
              <input type="checkbox" id="setting-refreshOnFocus" class="checkbox-input">
            </label>
          </div>

          <div class="settings-section" id="cloud-sync-section" style="display: none;">
            <h3>Cloud Sync</h3>
            <p class="settings-hint">Sync your progress across devices with Google account</p>
            <div class="settings-row">
              <span>Status:</span>
              <span id="settings-sync-status">Not signed in</span>
            </div>
            <div class="settings-row">
              <span>Last sync:</span>
              <span id="settings-last-sync">Never</span>
            </div>
            <div>
              <button type="button" onclick="forceSyncNow()">Sync Now</button>
              <button type="button" onclick="clearCloudData()">Clear Cloud Data</button>
            </div>
          </div>

          <div class="settings-section settings-advanced-toggle">
            <button type="button" id="settings-toggle-advanced" class="settings-toggle-btn">
              <span id="advanced-toggle-icon">&#9654;</span> Show Advanced Settings
            </button>
          </div>

          <div id="advanced-settings" class="settings-advanced" style="display: none;">
            <div class="settings-section">
              <h3>Base Rate (Debug)</h3>
              <label>
                Points per day:
                <input type="number" id="setting-baseRate" step="0.1" min="0.1" max="10" class="settings-input">
              </label>
            </div>

            <div class="settings-section">
              <h3>Solved Count Scaling</h3>
              <p class="settings-hint">How much solved count affects decay (higher = slower decay as you solve more)</p>
              <label>
                Base scaling:
                <input type="number" id="setting-baseSolvedScaling" step="0.01" min="0" max="1" class="settings-input">
              </label>
            </div>

            <div class="settings-section">
              <h3>Tier Solved Bonus</h3>
              <p class="settings-hint">Extra solved count benefit per tier (higher tier = more benefit)</p>
              <label>
                Top Tier bonus:
                <input type="number" id="setting-tierBonus-top" step="0.05" min="0" max="1" class="settings-input">
              </label>
              <label>
                Advanced bonus:
                <input type="number" id="setting-tierBonus-advanced" step="0.05" min="0" max="1" class="settings-input">
              </label>
              <label>
                Intermediate bonus:
                <input type="number" id="setting-tierBonus-intermediate" step="0.05" min="0" max="1" class="settings-input">
              </label>
              <label>
                Below Intermediate bonus:
                <input type="number" id="setting-tierBonus-below" step="0.05" min="0" max="1" class="settings-input">
              </label>
            </div>

            <div class="settings-section">
              <h3>Tier-Difficulty Matrix</h3>
              <p class="settings-hint">Combined decay multiplier. Top+Easy=0 (mastered). Lower = slower decay.</p>
              <table class="settings-matrix">
                <thead>
                  <tr>
                    <th></th>
                    <th>Easy</th>
                    <th>Medium</th>
                    <th>Hard</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="settings-matrix-label">Top</td>
                    <td><input type="number" id="setting-tdm-top-Easy" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-top-Medium" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-top-Hard" step="0.05" min="0" max="3" class="settings-input"></td>
                  </tr>
                  <tr>
                    <td class="settings-matrix-label">Advanced</td>
                    <td><input type="number" id="setting-tdm-advanced-Easy" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-advanced-Medium" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-advanced-Hard" step="0.05" min="0" max="3" class="settings-input"></td>
                  </tr>
                  <tr>
                    <td class="settings-matrix-label">Intermediate</td>
                    <td><input type="number" id="setting-tdm-intermediate-Easy" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-intermediate-Medium" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-intermediate-Hard" step="0.05" min="0" max="3" class="settings-input"></td>
                  </tr>
                  <tr>
                    <td class="settings-matrix-label">Below</td>
                    <td><input type="number" id="setting-tdm-below-Easy" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-below-Medium" step="0.05" min="0" max="3" class="settings-input"></td>
                    <td><input type="number" id="setting-tdm-below-Hard" step="0.05" min="0" max="3" class="settings-input"></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="settings-buttons">
          <button type="button" id="settings-reset-btn" class="settings-btn-secondary">Reset to Defaults</button>
          <button type="submit" class="settings-btn-primary">Save & Close</button>
        </div>
        </form>
      `;

      overlay.appendChild(panel);
      document.body.appendChild(overlay);
    }

    // Initialize all event listeners for settings panel
    function initSettingsPanel() {
      // Close button
      document.getElementById('settings-close-btn').addEventListener('click', closeSettingsPanel);

      // Form submission
      document.getElementById('settings-form').addEventListener('submit', function(e) {
        e.preventDefault();
        saveAndCloseSettings();
      });

      // Toggle advanced settings
      document.getElementById('settings-toggle-advanced').addEventListener('click', toggleAdvancedSettings);

      // Reset button
      document.getElementById('settings-reset-btn').addEventListener('click', resetSettingsToDefaults);
    }

    // Handle ESC key to close settings
    function handleSettingsKeydown(e) {
      if (e.key === 'Escape') {
        closeSettingsPanel();
      }
    }

    // Toggle advanced settings visibility
    function toggleAdvancedSettings() {
      const advancedDiv = document.getElementById('advanced-settings');
      const toggleIcon = document.getElementById('advanced-toggle-icon');
      const toggleBtn = document.querySelector('.settings-toggle-btn');

      if (advancedDiv.style.display === 'none') {
        advancedDiv.style.display = 'block';
        toggleIcon.innerHTML = '&#9660;';  // Down arrow
        toggleBtn.innerHTML = '<span id="advanced-toggle-icon">&#9660;</span> Hide Advanced Settings';
      } else {
        advancedDiv.style.display = 'none';
        toggleIcon.innerHTML = '&#9654;';  // Right arrow
        toggleBtn.innerHTML = '<span id="advanced-toggle-icon">&#9654;</span> Show Advanced Settings';
      }
    }

    // Clamp value to min/max range, with fallback default
    function clampValue(value, min, max, defaultVal) {
      if (isNaN(value)) return defaultVal;
      return Math.max(min, Math.min(max, value));
    }

    // Validate threshold ordering: white < green < yellow < red < darkRed
    function validateThresholdOrdering(thresholds) {
      const order = ['white', 'green', 'yellow', 'red', 'darkRed'];
      const validated = { ...thresholds };

      for (let i = 1; i < order.length; i++) {
        const prev = order[i - 1];
        const curr = order[i];
        if (validated[curr] <= validated[prev]) {
          validated[curr] = Math.min(validated[prev] + 1, 200);
        }
      }
      return validated;
    }

    // Populate settings inputs with current config values
    function populateSettingsInputs() {
      // Commitment dropdown
      const commitmentSelect = document.getElementById('setting-commitment');
      const commitmentValue = String(AWARENESS_CONFIG.commitment.problemsPerDay);
      for (let i = 0; i < commitmentSelect.options.length; i++) {
        if (commitmentSelect.options[i].value === commitmentValue) {
          commitmentSelect.selectedIndex = i;
          break;
        }
      }

      // Base rate
      document.getElementById('setting-baseRate').value = AWARENESS_CONFIG.baseRate;

      // Solved count scaling
      document.getElementById('setting-baseSolvedScaling').value = AWARENESS_CONFIG.baseSolvedScaling;

      // Tier solved bonus
      document.getElementById('setting-tierBonus-top').value = AWARENESS_CONFIG.tierSolvedBonus.top;
      document.getElementById('setting-tierBonus-advanced').value = AWARENESS_CONFIG.tierSolvedBonus.advanced;
      document.getElementById('setting-tierBonus-intermediate').value = AWARENESS_CONFIG.tierSolvedBonus.intermediate;
      document.getElementById('setting-tierBonus-below').value = AWARENESS_CONFIG.tierSolvedBonus.below;

      // Tier-Difficulty Matrix
      const tiers = ['top', 'advanced', 'intermediate', 'below'];
      const difficulties = ['Easy', 'Medium', 'Hard'];
      tiers.forEach(tier => {
        difficulties.forEach(diff => {
          const input = document.getElementById(`setting-tdm-${tier}-${diff}`);
          if (input) {
            input.value = AWARENESS_CONFIG.tierDifficultyMultipliers[tier][diff];
          }
        });
      });

      // Thresholds
      document.getElementById('setting-threshold-white').value = AWARENESS_CONFIG.thresholds.white;
      document.getElementById('setting-threshold-green').value = AWARENESS_CONFIG.thresholds.green;
      document.getElementById('setting-threshold-yellow').value = AWARENESS_CONFIG.thresholds.yellow;
      document.getElementById('setting-threshold-red').value = AWARENESS_CONFIG.thresholds.red;
      document.getElementById('setting-threshold-darkRed').value = AWARENESS_CONFIG.thresholds.darkRed;

      // Refresh settings
      const refreshSelect = document.getElementById('setting-refreshInterval');
      const refreshValue = String(AWARENESS_CONFIG.refreshInterval);
      for (let i = 0; i < refreshSelect.options.length; i++) {
        if (refreshSelect.options[i].value === refreshValue) {
          refreshSelect.selectedIndex = i;
          break;
        }
      }
      document.getElementById('setting-refreshOnFocus').checked = AWARENESS_CONFIG.refreshOnFocus;
    }

    // Read settings from inputs and update config
    function readSettingsFromInputs() {
      // Commitment
      const commitmentSelect = document.getElementById('setting-commitment');
      AWARENESS_CONFIG.commitment.problemsPerDay = parseFloat(commitmentSelect.value) || 2;

      // Base rate (clamp 0.1 - 10)
      AWARENESS_CONFIG.baseRate = clampValue(
        parseFloat(document.getElementById('setting-baseRate').value),
        0.1, 10, 2.0
      );

      // Solved count scaling (clamp 0 - 1)
      AWARENESS_CONFIG.baseSolvedScaling = clampValue(
        parseFloat(document.getElementById('setting-baseSolvedScaling').value),
        0, 1, 0.1
      );

      // Tier solved bonus (clamp 0 - 1)
      AWARENESS_CONFIG.tierSolvedBonus.top = clampValue(
        parseFloat(document.getElementById('setting-tierBonus-top').value),
        0, 1, 0.3
      );
      AWARENESS_CONFIG.tierSolvedBonus.advanced = clampValue(
        parseFloat(document.getElementById('setting-tierBonus-advanced').value),
        0, 1, 0.2
      );
      AWARENESS_CONFIG.tierSolvedBonus.intermediate = clampValue(
        parseFloat(document.getElementById('setting-tierBonus-intermediate').value),
        0, 1, 0.1
      );
      AWARENESS_CONFIG.tierSolvedBonus.below = clampValue(
        parseFloat(document.getElementById('setting-tierBonus-below').value),
        0, 1, 0
      );

      // Tier-Difficulty Matrix (clamp 0 - 3)
      const tiers = ['top', 'advanced', 'intermediate', 'below'];
      const difficulties = ['Easy', 'Medium', 'Hard'];
      const defaultMatrix = {
        top: { Easy: 0, Medium: 0.25, Hard: 0.4 },
        advanced: { Easy: 1.2, Medium: 0.9, Hard: 0.7 },
        intermediate: { Easy: 1.5, Medium: 1.0, Hard: 0.75 },
        below: { Easy: 1.8, Medium: 1.3, Hard: 1.0 }
      };
      tiers.forEach(tier => {
        difficulties.forEach(diff => {
          const input = document.getElementById(`setting-tdm-${tier}-${diff}`);
          if (input) {
            AWARENESS_CONFIG.tierDifficultyMultipliers[tier][diff] = clampValue(
              parseFloat(input.value),
              0, 3, defaultMatrix[tier][diff]
            );
          }
        });
      });

      // Thresholds (clamp 1 - 200)
      let rawThresholds = {
        white: clampValue(parseInt(document.getElementById('setting-threshold-white').value), 1, 200, 10),
        green: clampValue(parseInt(document.getElementById('setting-threshold-green').value), 1, 200, 30),
        yellow: clampValue(parseInt(document.getElementById('setting-threshold-yellow').value), 1, 200, 50),
        red: clampValue(parseInt(document.getElementById('setting-threshold-red').value), 1, 200, 70),
        darkRed: clampValue(parseInt(document.getElementById('setting-threshold-darkRed').value), 1, 200, 90)
      };

      // Validate ordering (white < green < yellow < red < darkRed)
      const validatedThresholds = validateThresholdOrdering(rawThresholds);
      AWARENESS_CONFIG.thresholds = validatedThresholds;

      // Update input fields to reflect validated values
      document.getElementById('setting-threshold-white').value = validatedThresholds.white;
      document.getElementById('setting-threshold-green').value = validatedThresholds.green;
      document.getElementById('setting-threshold-yellow').value = validatedThresholds.yellow;
      document.getElementById('setting-threshold-red').value = validatedThresholds.red;
      document.getElementById('setting-threshold-darkRed').value = validatedThresholds.darkRed;

      // Refresh settings
      AWARENESS_CONFIG.refreshInterval = parseInt(document.getElementById('setting-refreshInterval').value) || 86400000;
      AWARENESS_CONFIG.refreshOnFocus = document.getElementById('setting-refreshOnFocus').checked;
    }

    // Setup real-time preview on input change
    function setupSettingsPreview() {
      const inputs = document.querySelectorAll('.settings-input');
      inputs.forEach(input => {
        input.addEventListener('input', function() {
          readSettingsFromInputs();
          updateAwarenessColors();
        });
      });
    }

    // Open settings panel
    function openSettingsPanel() {
      let overlay = document.getElementById('settings-overlay');
      if (!overlay) {
        createSettingsPanel();
        overlay = document.getElementById('settings-overlay');
        initSettingsPanel();
        setupSettingsPreview();
      }
      populateSettingsInputs();
      overlay.classList.add('visible');
      document.addEventListener('keydown', handleSettingsKeydown);
    }

    // Close settings panel
    function closeSettingsPanel() {
      const overlay = document.getElementById('settings-overlay');
      if (overlay) {
        overlay.classList.remove('visible');
      }
      document.removeEventListener('keydown', handleSettingsKeydown);
      // Reload config to discard unsaved changes
      loadAwarenessConfig();
      updateAwarenessColors();
    }

    // Save settings and close
    function saveAndCloseSettings() {
      readSettingsFromInputs();
      saveAwarenessConfig();

      // Sync awareness config to cloud if Firebase is enabled
      if (typeof syncAwarenessConfigToCloud === 'function' && typeof isCloudSyncEnabled === 'function' && isCloudSyncEnabled()) {
        syncAwarenessConfigToCloud();
      }

      updateAwarenessColors();
      setupAwarenessRefresh();  // Re-setup with new interval
      const overlay = document.getElementById('settings-overlay');
      if (overlay) {
        overlay.classList.remove('visible');
      }
    }

    // Reset settings to defaults
    function resetSettingsToDefaults() {
      resetAwarenessConfig();
      populateSettingsInputs();
      updateAwarenessColors();
    }

    // Setup settings button click handler
    function initSettingsButton() {
      const settingsBtn = document.getElementById('settings-btn');
      if (settingsBtn) {
        settingsBtn.addEventListener('click', openSettingsPanel);
      }
    }
    """

    return js


if __name__ == "__main__":
    print(generate_js_settings())
