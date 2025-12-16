#!/usr/bin/env python3
"""
JavaScript Config Sync Generator
Implements local storage and cloud sync for user configurations:
- Filter settings (active tab, filter states per tab)
- Export preferences (default format, mode)
- UI preferences (theme, column visibility, sort order)
"""


def generate_js_config_sync():
    """Generate JavaScript for configuration sync"""

    js = """
    // ============================================
    // CONFIG SYNC - LOCAL STORAGE & CLOUD SYNC
    // ============================================

    // Default configurations
    const DEFAULT_FILTER_CONFIG = {
      activeTab: PROBLEM_DATA.file_list[0],
      tabStates: {}
    };

    const DEFAULT_EXPORT_PREFS = {
      defaultFormat: 'json',
      defaultMode: 'user'
    };

    const DEFAULT_UI_PREFS = {
      theme: 'light',
      columnVisibility: {
        intermediateTime: true,
        advancedTime: true,
        topTime: true,
        pattern: true,
        comments: true,
        solvedDate: true
      },
      sortPreferences: {}
    };

    // Current config state
    let FILTER_CONFIG = JSON.parse(JSON.stringify(DEFAULT_FILTER_CONFIG));
    let EXPORT_PREFS = JSON.parse(JSON.stringify(DEFAULT_EXPORT_PREFS));
    let UI_PREFS = JSON.parse(JSON.stringify(DEFAULT_UI_PREFS));

    // Debounce timers for config sync
    let filterConfigSyncTimer = null;
    let exportPrefsSyncTimer = null;
    let uiPrefsSyncTimer = null;
    let awarenessConfigSyncTimer = null;

    // ============================================
    // FILTER CONFIG - LOCAL STORAGE
    // ============================================

    /**
     * Get default filter state for a tab
     */
    function getDefaultFilterState() {
      return {
        difficultyFilter: 'all',
        solvedFilter: 'all',
        patternFilter: 'all',
        colorFilter: 'all',
        searchTerm: ''
      };
    }

    /**
     * Load filter config from localStorage
     */
    function loadFilterConfig() {
      try {
        // Load active tab
        const savedTab = localStorage.getItem('tracker_active_tab');
        if (savedTab && PROBLEM_DATA.file_list.includes(savedTab)) {
          FILTER_CONFIG.activeTab = savedTab;
        }

        // Load filter states per tab
        PROBLEM_DATA.file_list.forEach(fileKey => {
          const savedState = localStorage.getItem(`tracker_filters_${fileKey}`);
          if (savedState) {
            FILTER_CONFIG.tabStates[fileKey] = JSON.parse(savedState);
          } else {
            FILTER_CONFIG.tabStates[fileKey] = getDefaultFilterState();
          }
        });
      } catch (e) {
        console.error('Error loading filter config:', e);
      }
    }

    /**
     * Save filter config to localStorage
     */
    function saveFilterConfig() {
      try {
        localStorage.setItem('tracker_active_tab', FILTER_CONFIG.activeTab);

        PROBLEM_DATA.file_list.forEach(fileKey => {
          if (FILTER_CONFIG.tabStates[fileKey]) {
            localStorage.setItem(
              `tracker_filters_${fileKey}`,
              JSON.stringify(FILTER_CONFIG.tabStates[fileKey])
            );
          }
        });
      } catch (e) {
        console.error('Error saving filter config:', e);
      }
    }

    /**
     * Save active tab
     */
    function saveActiveTab(tabName) {
      FILTER_CONFIG.activeTab = tabName;
      localStorage.setItem('tracker_active_tab', tabName);
      syncFilterConfigToCloudDebounced();
    }

    /**
     * Save filter state for a specific tab
     */
    function saveFilterState(fileKey) {
      const state = {
        difficultyFilter: document.getElementById(`difficulty-filter-${fileKey}`)?.value || 'all',
        solvedFilter: document.getElementById(`solved-filter-${fileKey}`)?.value || 'all',
        patternFilter: document.getElementById(`pattern-filter-${fileKey}`)?.value || 'all',
        colorFilter: document.getElementById(`color-filter-${fileKey}`)?.value || 'all',
        searchTerm: document.getElementById(`search-${fileKey}`)?.value || ''
      };

      FILTER_CONFIG.tabStates[fileKey] = state;
      localStorage.setItem(`tracker_filters_${fileKey}`, JSON.stringify(state));
      syncFilterConfigToCloudDebounced();
    }

    /**
     * Restore filter states from config to UI
     */
    function restoreFilterStates() {
      PROBLEM_DATA.file_list.forEach(fileKey => {
        const state = FILTER_CONFIG.tabStates[fileKey];
        if (!state) return;

        const difficultyFilter = document.getElementById(`difficulty-filter-${fileKey}`);
        const solvedFilter = document.getElementById(`solved-filter-${fileKey}`);
        const patternFilter = document.getElementById(`pattern-filter-${fileKey}`);
        const colorFilter = document.getElementById(`color-filter-${fileKey}`);
        const searchBox = document.getElementById(`search-${fileKey}`);

        if (difficultyFilter) difficultyFilter.value = state.difficultyFilter || 'all';
        if (solvedFilter) solvedFilter.value = state.solvedFilter || 'all';
        if (patternFilter) patternFilter.value = state.patternFilter || 'all';
        if (colorFilter) colorFilter.value = state.colorFilter || 'all';
        if (searchBox) searchBox.value = state.searchTerm || '';

        // Apply filters after restoring
        if (typeof applyFilters === 'function') {
          applyFilters(fileKey);
        }
      });
    }

    /**
     * Restore active tab from config
     */
    function restoreActiveTab() {
      if (FILTER_CONFIG.activeTab && typeof switchTab === 'function') {
        switchTab(FILTER_CONFIG.activeTab);
      }
    }

    // ============================================
    // EXPORT PREFERENCES - LOCAL STORAGE
    // ============================================

    /**
     * Load export preferences from localStorage
     */
    function loadExportPrefs() {
      try {
        const savedFormat = localStorage.getItem('tracker_export_format');
        const savedMode = localStorage.getItem('tracker_export_mode');

        if (savedFormat) EXPORT_PREFS.defaultFormat = savedFormat;
        if (savedMode) EXPORT_PREFS.defaultMode = savedMode;
      } catch (e) {
        console.error('Error loading export preferences:', e);
      }
    }

    /**
     * Save export preferences to localStorage
     */
    function saveExportPrefs() {
      try {
        localStorage.setItem('tracker_export_format', EXPORT_PREFS.defaultFormat);
        localStorage.setItem('tracker_export_mode', EXPORT_PREFS.defaultMode);
      } catch (e) {
        console.error('Error saving export preferences:', e);
      }
    }

    /**
     * Set export format preference
     */
    function setExportFormat(format) {
      EXPORT_PREFS.defaultFormat = format;
      saveExportPrefs();
      syncExportPrefsToCloudDebounced();
    }

    /**
     * Set export mode preference
     */
    function setExportMode(mode) {
      EXPORT_PREFS.defaultMode = mode;
      saveExportPrefs();
      syncExportPrefsToCloudDebounced();
    }

    /**
     * Get current export format preference
     */
    function getExportFormat() {
      return EXPORT_PREFS.defaultFormat;
    }

    /**
     * Get current export mode preference
     */
    function getExportMode() {
      return EXPORT_PREFS.defaultMode;
    }

    // ============================================
    // UI PREFERENCES - LOCAL STORAGE
    // ============================================

    /**
     * Load UI preferences from localStorage
     */
    function loadUIPrefs() {
      try {
        const savedTheme = localStorage.getItem('tracker_theme');
        const savedColumnVisibility = localStorage.getItem('tracker_column_visibility');
        const savedSort = localStorage.getItem('tracker_sort_prefs');

        if (savedTheme) UI_PREFS.theme = savedTheme;
        if (savedColumnVisibility) {
          UI_PREFS.columnVisibility = JSON.parse(savedColumnVisibility);
        }
        if (savedSort) {
          UI_PREFS.sortPreferences = JSON.parse(savedSort);
        }
      } catch (e) {
        console.error('Error loading UI preferences:', e);
      }
    }

    /**
     * Save UI preferences to localStorage
     */
    function saveUIPrefs() {
      try {
        localStorage.setItem('tracker_theme', UI_PREFS.theme);
        localStorage.setItem('tracker_column_visibility', JSON.stringify(UI_PREFS.columnVisibility));
        localStorage.setItem('tracker_sort_prefs', JSON.stringify(UI_PREFS.sortPreferences));
      } catch (e) {
        console.error('Error saving UI preferences:', e);
      }
    }

    /**
     * Set theme preference
     */
    function setTheme(theme) {
      UI_PREFS.theme = theme;
      document.body.classList.remove('theme-light', 'theme-dark');
      document.body.classList.add(`theme-${theme}`);
      saveUIPrefs();
      syncUIPrefsToCloudDebounced();
    }

    /**
     * Get current theme
     */
    function getTheme() {
      return UI_PREFS.theme;
    }

    /**
     * Set column visibility
     */
    function setColumnVisibility(column, visible) {
      UI_PREFS.columnVisibility[column] = visible;
      saveUIPrefs();
      syncUIPrefsToCloudDebounced();
      applyColumnVisibility();
    }

    /**
     * Apply column visibility to all tables
     */
    function applyColumnVisibility() {
      const columnMap = {
        intermediateTime: 2,
        advancedTime: 3,
        topTime: 4,
        pattern: 5,
        comments: 8,
        solvedDate: 9
      };

      Object.entries(UI_PREFS.columnVisibility).forEach(([column, visible]) => {
        const colIndex = columnMap[column];
        if (colIndex === undefined) return;

        // Apply to all tables
        document.querySelectorAll('table').forEach(table => {
          const cells = table.querySelectorAll(`th:nth-child(${colIndex + 1}), td:nth-child(${colIndex + 1})`);
          cells.forEach(cell => {
            cell.style.display = visible ? '' : 'none';
          });
        });
      });
    }

    /**
     * Set sort preference for a tab
     */
    function setSortPreference(fileKey, column, direction) {
      UI_PREFS.sortPreferences[fileKey] = { column, direction };
      saveUIPrefs();
      syncUIPrefsToCloudDebounced();
    }

    /**
     * Get sort preference for a tab
     */
    function getSortPreference(fileKey) {
      return UI_PREFS.sortPreferences[fileKey] || { column: 'name', direction: 'asc' };
    }

    // ============================================
    // CLOUD SYNC - DEBOUNCED FUNCTIONS
    // ============================================

    /**
     * Sync filter config to cloud (debounced - 3 seconds)
     */
    function syncFilterConfigToCloudDebounced() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled()) return;

      clearTimeout(filterConfigSyncTimer);
      filterConfigSyncTimer = setTimeout(() => {
        syncFilterConfigToCloud();
      }, 3000); // Increased from 1s to reduce sync frequency
    }

    /**
     * Sync export preferences to cloud (debounced - 5 seconds)
     */
    function syncExportPrefsToCloudDebounced() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled()) return;

      clearTimeout(exportPrefsSyncTimer);
      exportPrefsSyncTimer = setTimeout(() => {
        syncExportPrefsToCloud();
      }, 5000); // Increased from 2s to reduce sync frequency
    }

    /**
     * Sync UI preferences to cloud (debounced - 5 seconds)
     */
    function syncUIPrefsToCloudDebounced() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled()) return;

      clearTimeout(uiPrefsSyncTimer);
      uiPrefsSyncTimer = setTimeout(() => {
        syncUIPrefsToCloud();
      }, 5000); // Increased from 2s to reduce sync frequency
    }

    /**
     * Sync awareness config to cloud (debounced - 5 seconds)
     */
    function syncAwarenessConfigToCloudDebounced() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled()) return;

      clearTimeout(awarenessConfigSyncTimer);
      awarenessConfigSyncTimer = setTimeout(() => {
        syncAwarenessConfigToCloud();
      }, 5000);
    }

    // ============================================
    // CLOUD SYNC - DIRECT FUNCTIONS
    // ============================================

    /**
     * Sync filter config to cloud
     */
    async function syncFilterConfigToCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        await userRef.collection('config').doc('filters').set({
          activeTab: FILTER_CONFIG.activeTab,
          tabStates: FILTER_CONFIG.tabStates,
          updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
          updatedFrom: 'web'
        });
      } catch (error) {
        console.error('Failed to sync filter config to cloud:', error);
      }
    }

    /**
     * Sync export preferences to cloud
     */
    async function syncExportPrefsToCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        await userRef.collection('config').doc('exportPrefs').set({
          defaultFormat: EXPORT_PREFS.defaultFormat,
          defaultMode: EXPORT_PREFS.defaultMode,
          updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
          updatedFrom: 'web'
        });
      } catch (error) {
        console.error('Failed to sync export prefs to cloud:', error);
      }
    }

    /**
     * Sync UI preferences to cloud
     */
    async function syncUIPrefsToCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        await userRef.collection('config').doc('uiPrefs').set({
          theme: UI_PREFS.theme,
          columnVisibility: UI_PREFS.columnVisibility,
          sortPreferences: UI_PREFS.sortPreferences,
          updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
          updatedFrom: 'web'
        });
      } catch (error) {
        console.error('Failed to sync UI prefs to cloud:', error);
      }
    }

    // ============================================
    // CLOUD SYNC - LOAD FROM CLOUD
    // ============================================

    /**
     * Load filter config from cloud
     */
    async function loadFilterConfigFromCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        const doc = await userRef.collection('config').doc('filters').get();

        if (doc.exists) {
          const cloudConfig = doc.data();
          // Cloud wins - merge with local
          if (cloudConfig.activeTab && PROBLEM_DATA.file_list.includes(cloudConfig.activeTab)) {
            FILTER_CONFIG.activeTab = cloudConfig.activeTab;
          }
          if (cloudConfig.tabStates) {
            FILTER_CONFIG.tabStates = { ...FILTER_CONFIG.tabStates, ...cloudConfig.tabStates };
          }
          saveFilterConfig();
          restoreActiveTab();
          restoreFilterStates();
        } else {
          // No cloud data - upload local
          await syncFilterConfigToCloud();
        }
      } catch (error) {
        console.error('Failed to load filter config from cloud:', error);
      }
    }

    /**
     * Load export preferences from cloud
     */
    async function loadExportPrefsFromCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        const doc = await userRef.collection('config').doc('exportPrefs').get();

        if (doc.exists) {
          const cloudPrefs = doc.data();
          // Cloud wins
          if (cloudPrefs.defaultFormat) EXPORT_PREFS.defaultFormat = cloudPrefs.defaultFormat;
          if (cloudPrefs.defaultMode) EXPORT_PREFS.defaultMode = cloudPrefs.defaultMode;
          saveExportPrefs();
        } else {
          // No cloud data - upload local
          await syncExportPrefsToCloud();
        }
      } catch (error) {
        console.error('Failed to load export prefs from cloud:', error);
      }
    }

    /**
     * Load UI preferences from cloud
     */
    async function loadUIPrefsFromCloud() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        const doc = await userRef.collection('config').doc('uiPrefs').get();

        if (doc.exists) {
          const cloudPrefs = doc.data();
          // Smart merge for UI prefs
          if (cloudPrefs.theme) {
            UI_PREFS.theme = cloudPrefs.theme;
            document.body.classList.remove('theme-light', 'theme-dark');
            document.body.classList.add(`theme-${cloudPrefs.theme}`);
          }

          // Column visibility: OR logic (show if either wants it shown)
          if (cloudPrefs.columnVisibility) {
            Object.keys(cloudPrefs.columnVisibility).forEach(col => {
              if (cloudPrefs.columnVisibility[col]) {
                UI_PREFS.columnVisibility[col] = true;
              }
            });
          }

          // Sort preferences: cloud wins
          if (cloudPrefs.sortPreferences) {
            UI_PREFS.sortPreferences = { ...UI_PREFS.sortPreferences, ...cloudPrefs.sortPreferences };
          }

          saveUIPrefs();
          applyColumnVisibility();
        } else {
          // No cloud data - upload local
          await syncUIPrefsToCloud();
        }
      } catch (error) {
        console.error('Failed to load UI prefs from cloud:', error);
      }
    }

    // ============================================
    // REAL-TIME LISTENERS FOR CONFIG
    // ============================================

    /**
     * Setup real-time listeners for config changes
     */
    function setupConfigRealtimeListeners() {
      if (typeof isCloudSyncEnabled !== 'function' || !isCloudSyncEnabled() || !firebaseDb) return;

      const userRef = firebaseDb.collection('users').doc(currentUser.uid);

      // Listen for filter config changes
      const filterUnsubscribe = userRef.collection('config').doc('filters')
        .onSnapshot(doc => {
          if (doc.exists && doc.metadata.hasPendingWrites === false) {
            handleFilterConfigChange(doc.data());
          }
        });

      // Listen for export prefs changes
      const exportUnsubscribe = userRef.collection('config').doc('exportPrefs')
        .onSnapshot(doc => {
          if (doc.exists && doc.metadata.hasPendingWrites === false) {
            handleExportPrefsChange(doc.data());
          }
        });

      // Listen for UI prefs changes
      const uiUnsubscribe = userRef.collection('config').doc('uiPrefs')
        .onSnapshot(doc => {
          if (doc.exists && doc.metadata.hasPendingWrites === false) {
            handleUIPrefsChange(doc.data());
          }
        });

      // Listen for awareness config changes
      const awarenessUnsubscribe = userRef.collection('config').doc('awareness')
        .onSnapshot(doc => {
          if (doc.exists && doc.metadata.hasPendingWrites === false) {
            handleAwarenessConfigChange(doc.data());
          }
        });

      // Add to global listeners array for cleanup
      if (typeof realtimeListeners !== 'undefined') {
        realtimeListeners.push(filterUnsubscribe, exportUnsubscribe, uiUnsubscribe, awarenessUnsubscribe);
      }
    }

    /**
     * Handle incoming filter config changes from cloud
     */
    function handleFilterConfigChange(cloudData) {
      if (!cloudData) return;

      // Skip if this change originated from this device recently
      // (real-time listeners also fire for local writes)

      // Update active tab if different
      if (cloudData.activeTab &&
          cloudData.activeTab !== FILTER_CONFIG.activeTab &&
          PROBLEM_DATA.file_list.includes(cloudData.activeTab)) {
        FILTER_CONFIG.activeTab = cloudData.activeTab;
        localStorage.setItem('tracker_active_tab', cloudData.activeTab);
        if (typeof switchTab === 'function') {
          switchTab(cloudData.activeTab);
        }
      }

      // Update tab states
      if (cloudData.tabStates) {
        Object.keys(cloudData.tabStates).forEach(fileKey => {
          FILTER_CONFIG.tabStates[fileKey] = cloudData.tabStates[fileKey];
          localStorage.setItem(`tracker_filters_${fileKey}`, JSON.stringify(cloudData.tabStates[fileKey]));
        });
        restoreFilterStates();
      }
    }

    /**
     * Handle incoming export prefs changes from cloud
     */
    function handleExportPrefsChange(cloudData) {
      if (!cloudData) return;

      if (cloudData.defaultFormat) EXPORT_PREFS.defaultFormat = cloudData.defaultFormat;
      if (cloudData.defaultMode) EXPORT_PREFS.defaultMode = cloudData.defaultMode;
      saveExportPrefs();
    }

    /**
     * Handle incoming UI prefs changes from cloud
     */
    function handleUIPrefsChange(cloudData) {
      if (!cloudData) return;

      // Update theme
      if (cloudData.theme && cloudData.theme !== UI_PREFS.theme) {
        UI_PREFS.theme = cloudData.theme;
        document.body.classList.remove('theme-light', 'theme-dark');
        document.body.classList.add(`theme-${cloudData.theme}`);
      }

      // Update column visibility (OR logic)
      if (cloudData.columnVisibility) {
        Object.keys(cloudData.columnVisibility).forEach(col => {
          UI_PREFS.columnVisibility[col] = cloudData.columnVisibility[col];
        });
        applyColumnVisibility();
      }

      // Update sort preferences
      if (cloudData.sortPreferences) {
        UI_PREFS.sortPreferences = { ...UI_PREFS.sortPreferences, ...cloudData.sortPreferences };
      }

      saveUIPrefs();
    }

    /**
     * Handle incoming awareness config changes from cloud
     */
    function handleAwarenessConfigChange(cloudData) {
      if (!cloudData) return;

      // Use deepMerge if available, otherwise simple merge
      if (typeof deepMerge === 'function') {
        AWARENESS_CONFIG = deepMerge(AWARENESS_CONFIG, cloudData);
      } else {
        // Simple merge for top-level properties
        Object.keys(cloudData).forEach(key => {
          if (key !== 'updatedAt' && key !== 'updatedFrom') {
            AWARENESS_CONFIG[key] = cloudData[key];
          }
        });
      }

      // Save to localStorage and refresh UI
      if (typeof saveAwarenessConfig === 'function') {
        saveAwarenessConfig();
      }
      if (typeof updateAwarenessColors === 'function') {
        updateAwarenessColors(true);  // true = update all tabs
      }
    }

    // ============================================
    // INITIALIZATION
    // ============================================

    /**
     * Initialize all config on page load
     * Call this before other initialization
     */
    function initConfigSync() {
      loadFilterConfig();
      loadExportPrefs();
      loadUIPrefs();

      // Apply theme immediately
      document.body.classList.add(`theme-${UI_PREFS.theme}`);
    }

    /**
     * Load all configs from cloud after sign-in
     * Called from Firebase auth state change handler
     */
    async function loadAllConfigsFromCloud() {
      await Promise.all([
        loadFilterConfigFromCloud(),
        loadExportPrefsFromCloud(),
        loadUIPrefsFromCloud(),
        loadAwarenessConfigFromCloud()
      ]);
    }
    """

    return js


if __name__ == "__main__":
    print(generate_js_config_sync())
