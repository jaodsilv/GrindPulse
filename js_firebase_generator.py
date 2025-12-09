#!/usr/bin/env python3
"""
JavaScript Firebase Cloud Sync Generator
Implements Firebase Firestore sync with Google Sign-In
"""


def generate_js_firebase(firebase_config=None):
    """Generate JavaScript for Firebase cloud sync

    Args:
        firebase_config: dict with Firebase config, or None if not configured
    """

    # Generate config embedding
    if firebase_config:
        config_js = f'''
    // Firebase Configuration (embedded at build time)
    const FIREBASE_CONFIG = {repr(firebase_config).replace("'", '"')};
    const FIREBASE_ENABLED = true;
'''
    else:
        config_js = '''
    // Firebase not configured
    const FIREBASE_CONFIG = null;
    const FIREBASE_ENABLED = false;
'''

    js = config_js + '''
    // ============================================
    // FIREBASE CLOUD SYNC
    // ============================================

    // Global state for Firebase
    let firebaseApp = null;
    let firebaseDb = null;
    let firebaseAuth = null;
    let currentUser = null;
    let realtimeListeners = [];
    let syncQueue = [];
    let lastSyncTime = null;
    let isSyncing = false;

    // Debounce timers
    let syncDebounceTimer = null;
    let syncAllDebounceTimer = null;

    // ============================================
    // INITIALIZATION
    // ============================================

    /**
     * Initialize Firebase
     */
    function initFirebase() {
      if (!FIREBASE_ENABLED || !FIREBASE_CONFIG) {
        console.log('Firebase not configured');
        showFirebaseSetupInstructions();
        return;
      }

      try {
        // Initialize Firebase app
        firebaseApp = firebase.initializeApp(FIREBASE_CONFIG);
        firebaseAuth = firebase.auth();
        firebaseDb = firebase.firestore();

        // Enable offline persistence
        firebaseDb.enablePersistence({ synchronizeTabs: true })
          .catch(err => {
            if (err.code === 'failed-precondition') {
              console.warn('Firestore persistence failed: multiple tabs open');
            } else if (err.code === 'unimplemented') {
              console.warn('Firestore persistence not available in this browser');
            }
          });

        // Setup auth state observer
        firebaseAuth.onAuthStateChanged(handleAuthStateChange);

        // Show auth UI
        showAuthUI();

        console.log('Firebase initialized successfully');
      } catch (error) {
        console.error('Firebase initialization failed:', error);
        updateSyncStatusUI('error', 'Firebase init failed');
      }
    }

    /**
     * Show Firebase setup instructions when not configured
     */
    function showFirebaseSetupInstructions() {
      const header = document.querySelector('header');
      if (!header) return;

      const notice = document.createElement('div');
      notice.className = 'firebase-setup-notice';
      notice.innerHTML = `
        <span>Cloud sync not configured.</span>
        <a href="https://console.firebase.google.com/" target="_blank">Setup Firebase</a>
      `;
      header.appendChild(notice);
    }

    /**
     * Show auth UI elements
     */
    function showAuthUI() {
      const authBtn = document.getElementById('auth-btn');
      const syncStatus = document.getElementById('sync-status');

      if (authBtn) authBtn.style.display = 'flex';
      if (syncStatus) syncStatus.style.display = 'flex';

      updateSyncStatusUI('offline');
    }

    // ============================================
    // AUTHENTICATION
    // ============================================

    /**
     * Check if the current protocol supports Firebase Auth
     * OAuth requires http://, https://, or chrome-extension:// protocols
     */
    function isFirebaseAuthSupported() {
      const protocol = window.location.protocol;
      return protocol === 'http:' || protocol === 'https:' || protocol === 'chrome-extension:';
    }

    /**
     * Show instructions for running a local server
     * Called when user tries to sign in from file:// protocol
     */
    function showLocalServerInstructions() {
      // Remove existing modal if any
      const existing = document.getElementById('local-server-overlay');
      if (existing) {
        existing.remove();
      }

      const overlay = document.createElement('div');
      overlay.id = 'local-server-overlay';
      overlay.className = 'settings-overlay visible';
      overlay.innerHTML = `
        <div class="settings-panel" role="dialog" aria-labelledby="local-server-title" aria-modal="true" style="max-width: 550px;">
          <div class="settings-header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <h2 id="local-server-title">Local Server Required</h2>
            <button class="settings-close" onclick="hideLocalServerInstructions()" aria-label="Close">&times;</button>
          </div>
          <div class="settings-content">
            <div style="margin-bottom: 20px; padding: 16px; background: #fef3c7; border-radius: 8px; color: #92400e;">
              <p style="margin: 0;"><strong>Cloud sync requires a web server.</strong></p>
              <p style="margin: 8px 0 0 0; font-size: 0.9rem;">
                Google Sign-In cannot work when opening the file directly (file:// protocol).
                You need to serve this file through a local web server.
              </p>
            </div>

            <div class="settings-section">
              <h3>Quick Start Options</h3>
              <p style="font-size: 0.9rem; color: #666; margin-bottom: 12px;">
                Run one of these commands in the folder containing tracker.html:
              </p>

              <div style="margin-bottom: 16px;">
                <div style="font-weight: 600; color: #333; margin-bottom: 6px;">Python (built-in):</div>
                <code style="display: block; padding: 10px 12px; background: #1f2937; color: #10b981; border-radius: 6px; font-family: monospace; font-size: 0.9rem;">
                  python -m http.server 8000
                </code>
              </div>

              <div style="margin-bottom: 16px;">
                <div style="font-weight: 600; color: #333; margin-bottom: 6px;">Node.js (npx):</div>
                <code style="display: block; padding: 10px 12px; background: #1f2937; color: #10b981; border-radius: 6px; font-family: monospace; font-size: 0.9rem;">
                  npx serve .
                </code>
              </div>

              <div style="margin-bottom: 16px;">
                <div style="font-weight: 600; color: #333; margin-bottom: 6px;">VS Code:</div>
                <p style="font-size: 0.9rem; color: #666; margin: 0;">
                  Install the "Live Server" extension, then right-click tracker.html and select "Open with Live Server"
                </p>
              </div>
            </div>

            <div class="settings-section" style="border-bottom: none; margin-bottom: 0; padding-bottom: 0;">
              <h3>Then Open:</h3>
              <a href="http://localhost:8000/tracker.html" style="display: block; padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; text-align: center; font-weight: 600;">
                http://localhost:8000/tracker.html
              </a>
              <p style="font-size: 0.85rem; color: #666; margin-top: 10px; text-align: center;">
                (Port may vary depending on server used)
              </p>
            </div>

            <div style="margin-top: 20px; padding: 12px; background: #dbeafe; border-radius: 8px; color: #1e40af; font-size: 0.9rem;">
              <strong>Note:</strong> All local features (progress tracking, export) work without a server.
              Only cloud sync requires this setup.
            </div>
          </div>
          <div class="settings-buttons">
            <button class="settings-btn-secondary" onclick="hideLocalServerInstructions()">Close</button>
          </div>
        </div>
      `;

      document.body.appendChild(overlay);

      // Close on Escape key
      const handleEscape = (e) => {
        if (e.key === 'Escape') {
          hideLocalServerInstructions();
          document.removeEventListener('keydown', handleEscape);
        }
      };
      document.addEventListener('keydown', handleEscape);

      // Close on backdrop click
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          hideLocalServerInstructions();
        }
      });
    }

    /**
     * Hide local server instructions modal
     */
    function hideLocalServerInstructions() {
      const overlay = document.getElementById('local-server-overlay');
      if (overlay) {
        overlay.remove();
      }
    }

    /**
     * Handle auth state changes
     */
    function handleAuthStateChange(user) {
      currentUser = user;

      if (user) {
        console.log('User signed in:', user.email);
        updateAuthUI(user);
        updateSyncStatusUI('syncing', 'Connecting...');

        // Initial sync from cloud
        pullFromCloud().then(() => {
          setupRealtimeListeners();
          updateSyncStatusUI('synced');
        }).catch(err => {
          console.error('Initial sync failed:', err);
          updateSyncStatusUI('error', 'Sync failed');
        });
      } else {
        console.log('User signed out');
        updateAuthUI(null);
        teardownListeners();
        updateSyncStatusUI('offline');
      }
    }

    /**
     * Sign in with Google
     */
    async function signInWithGoogle() {
      if (!firebaseAuth) {
        alert('Firebase not initialized. Please check configuration.');
        return;
      }

      // Check if protocol supports Firebase Auth
      if (!isFirebaseAuthSupported()) {
        showLocalServerInstructions();
        return;
      }

      try {
        const provider = new firebase.auth.GoogleAuthProvider();
        await firebaseAuth.signInWithPopup(provider);
      } catch (error) {
        console.error('Sign-in failed:', error);
        if (error.code !== 'auth/popup-closed-by-user') {
          alert('Sign-in failed: ' + error.message);
        }
      }
    }

    /**
     * Sign out
     */
    async function signOutFirebase() {
      if (!firebaseAuth) return;

      try {
        await firebaseAuth.signOut();
        // Note: local data is kept intact per user preference
      } catch (error) {
        console.error('Sign-out failed:', error);
      }
    }

    /**
     * Update auth UI based on user state
     */
    function updateAuthUI(user) {
      const authBtn = document.getElementById('auth-btn');
      const authAvatar = document.getElementById('auth-avatar');
      const authText = document.getElementById('auth-text');
      const cloudSyncSection = document.getElementById('cloud-sync-section');

      if (!authBtn) return;

      if (user) {
        authBtn.onclick = showAuthMenu;
        authBtn.title = user.email;

        if (authAvatar) {
          authAvatar.src = user.photoURL || '';
          authAvatar.style.display = user.photoURL ? 'block' : 'none';
        }
        if (authText) {
          authText.textContent = user.displayName || user.email.split('@')[0];
        }

        // Show cloud sync section in settings
        if (cloudSyncSection) {
          cloudSyncSection.style.display = 'block';
        }
      } else {
        authBtn.onclick = signInWithGoogle;
        authBtn.title = 'Sign in with Google';

        if (authAvatar) {
          authAvatar.style.display = 'none';
        }
        if (authText) {
          authText.textContent = 'Sign In';
        }

        // Hide cloud sync section in settings
        if (cloudSyncSection) {
          cloudSyncSection.style.display = 'none';
        }
      }
    }

    /**
     * Show auth dropdown menu
     */
    function showAuthMenu() {
      // Remove existing menu if any
      const existing = document.getElementById('auth-menu');
      if (existing) {
        existing.remove();
        return;
      }

      const authBtn = document.getElementById('auth-btn');
      if (!authBtn || !currentUser) return;

      const menu = document.createElement('div');
      menu.id = 'auth-menu';
      menu.className = 'auth-menu';
      menu.innerHTML = `
        <div class="auth-menu-header">
          <img src="${currentUser.photoURL || ''}" alt="" class="auth-menu-avatar">
          <div class="auth-menu-info">
            <div class="auth-menu-name">${currentUser.displayName || ''}</div>
            <div class="auth-menu-email">${currentUser.email}</div>
          </div>
        </div>
        <div class="auth-menu-divider"></div>
        <button class="auth-menu-item" onclick="forceSyncNow()">
          <span>Sync Now</span>
        </button>
        <button class="auth-menu-item" onclick="signOutFirebase(); hideAuthMenu();">
          <span>Sign Out</span>
        </button>
      `;

      authBtn.parentNode.appendChild(menu);

      // Close on click outside
      setTimeout(() => {
        document.addEventListener('click', hideAuthMenuOnClickOutside);
      }, 0);
    }

    /**
     * Hide auth menu
     */
    function hideAuthMenu() {
      const menu = document.getElementById('auth-menu');
      if (menu) menu.remove();
      document.removeEventListener('click', hideAuthMenuOnClickOutside);
    }

    function hideAuthMenuOnClickOutside(e) {
      const menu = document.getElementById('auth-menu');
      const authBtn = document.getElementById('auth-btn');
      if (menu && !menu.contains(e.target) && !authBtn.contains(e.target)) {
        hideAuthMenu();
      }
    }

    // ============================================
    // SYNC STATUS UI
    // ============================================

    /**
     * Update sync status indicator
     */
    function updateSyncStatusUI(status, message) {
      const syncIcon = document.getElementById('sync-icon');
      const syncText = document.getElementById('sync-text');
      const settingsStatus = document.getElementById('settings-sync-status');
      const settingsLastSync = document.getElementById('settings-last-sync');

      if (!syncIcon || !syncText) return;

      // Remove all status classes
      syncIcon.className = 'sync-icon';

      switch (status) {
        case 'offline':
          syncIcon.classList.add('offline');
          syncIcon.innerHTML = '&#9679;'; // Circle
          syncText.textContent = 'Offline';
          break;
        case 'syncing':
          syncIcon.classList.add('syncing');
          syncIcon.innerHTML = '&#8635;'; // Refresh
          syncText.textContent = message || 'Syncing...';
          isSyncing = true;
          break;
        case 'synced':
          syncIcon.classList.add('synced');
          syncIcon.innerHTML = '&#10003;'; // Checkmark
          lastSyncTime = new Date();
          syncText.textContent = 'Synced';
          isSyncing = false;
          break;
        case 'error':
          syncIcon.classList.add('error');
          syncIcon.innerHTML = '&#9888;'; // Warning
          syncText.textContent = message || 'Error';
          syncText.title = message || '';
          isSyncing = false;
          break;
      }

      // Update settings panel if open
      if (settingsStatus) {
        settingsStatus.textContent = currentUser ?
          (status === 'synced' ? 'Connected' : status) : 'Not signed in';
      }
      if (settingsLastSync && lastSyncTime) {
        settingsLastSync.textContent = formatRelativeTime(lastSyncTime.toISOString());
      }
    }

    // ============================================
    // CLOUD SYNC FUNCTIONS
    // ============================================

    /**
     * Check if cloud sync is enabled and user is signed in
     */
    function isCloudSyncEnabled() {
      return FIREBASE_ENABLED && currentUser !== null;
    }

    /**
     * Sanitize problem name for Firestore document ID
     */
    function sanitizeProblemName(name) {
      return name.replace(/[\\/\\\\#$\\[\\]]/g, '_').substring(0, 100);
    }

    /**
     * Sync a single problem to cloud (debounced)
     */
    function syncToCloudDebounced(fileKey) {
      if (!isCloudSyncEnabled()) return;

      clearTimeout(syncDebounceTimer);
      syncDebounceTimer = setTimeout(() => {
        syncFileToCloud(fileKey);
      }, 2000);
    }

    /**
     * Sync all data to cloud (debounced)
     */
    function syncAllToCloudDebounced() {
      if (!isCloudSyncEnabled()) return;

      clearTimeout(syncAllDebounceTimer);
      syncAllDebounceTimer = setTimeout(() => {
        syncAllToCloud();
      }, 5000);
    }

    /**
     * Sync a specific file's problems to cloud
     */
    async function syncFileToCloud(fileKey) {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      updateSyncStatusUI('syncing');

      try {
        const problems = PROBLEM_DATA.data[fileKey];
        const batch = firebaseDb.batch();
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);

        for (const problem of problems) {
          if (problem.solved || problem.time_to_solve || problem.comments) {
            const docId = sanitizeProblemName(problem.name);
            const docRef = userRef.collection('progress').doc(docId);

            batch.set(docRef, {
              name: problem.name,
              solved: problem.solved || false,
              time_to_solve: problem.time_to_solve || '',
              comments: problem.comments || '',
              solved_date: problem.solved_date || '',
              updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
              updatedFrom: 'web'
            }, { merge: true });
          }
        }

        await batch.commit();
        updateSyncStatusUI('synced');
      } catch (error) {
        console.error('Sync to cloud failed:', error);
        updateSyncStatusUI('error', error.message);
      }
    }

    /**
     * Sync all problems to cloud
     */
    async function syncAllToCloud() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      updateSyncStatusUI('syncing', 'Uploading...');

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);

        // Process in batches (Firestore limit is 500 per batch)
        let batch = firebaseDb.batch();
        let batchCount = 0;

        for (const fileKey of PROBLEM_DATA.file_list) {
          const problems = PROBLEM_DATA.data[fileKey];

          for (const problem of problems) {
            if (problem.solved || problem.time_to_solve || problem.comments) {
              const docId = sanitizeProblemName(problem.name);
              const docRef = userRef.collection('progress').doc(docId);

              batch.set(docRef, {
                name: problem.name,
                solved: problem.solved || false,
                time_to_solve: problem.time_to_solve || '',
                comments: problem.comments || '',
                solved_date: problem.solved_date || '',
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                updatedFrom: 'web'
              }, { merge: true });

              batchCount++;

              // Commit batch when reaching limit
              if (batchCount >= 400) {
                await batch.commit();
                batch = firebaseDb.batch();
                batchCount = 0;
              }
            }
          }
        }

        // Commit remaining
        if (batchCount > 0) {
          await batch.commit();
        }

        updateSyncStatusUI('synced');
      } catch (error) {
        console.error('Sync all to cloud failed:', error);
        updateSyncStatusUI('error', error.message);
      }
    }

    /**
     * Pull all data from cloud and merge with local
     */
    async function pullFromCloud() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      updateSyncStatusUI('syncing', 'Downloading...');

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        const snapshot = await userRef.collection('progress').get();

        if (snapshot.empty) {
          console.log('No cloud data found, uploading local data');
          await syncAllToCloud();
          return;
        }

        // Build map of cloud data by problem name
        const cloudData = {};
        snapshot.forEach(doc => {
          const data = doc.data();
          cloudData[data.name] = data;
        });

        // Merge with local data
        const conflicts = [];

        for (const fileKey of PROBLEM_DATA.file_list) {
          const problems = PROBLEM_DATA.data[fileKey];

          for (let idx = 0; idx < problems.length; idx++) {
            const problem = problems[idx];
            const cloud = cloudData[problem.name];

            if (cloud) {
              // Check for conflicts
              const conflict = detectSyncConflict(problem, cloud);

              if (conflict.hasConflict) {
                conflicts.push({
                  fileKey,
                  idx,
                  name: problem.name,
                  local: problem,
                  cloud: cloud
                });
              } else if (conflict.winner === 'cloud') {
                // Cloud is newer, update local
                applyCloudData(problem, cloud);
                saveToLocalStorage(fileKey);
              }
              // If winner is 'local', keep local data
            }
          }
        }

        // Handle conflicts
        if (conflicts.length > 0) {
          showSyncConflictDialog(conflicts);
        } else {
          // Re-render UI with merged data
          renderAllTabs();
          updateAllProgress();
          updateSyncStatusUI('synced');
        }

        // Load all config settings from cloud (filter, export, UI preferences)
        if (typeof loadAllConfigsFromCloud === 'function') {
          await loadAllConfigsFromCloud();
        }
      } catch (error) {
        console.error('Pull from cloud failed:', error);
        updateSyncStatusUI('error', error.message);
        throw error;
      }
    }

    /**
     * Apply cloud data to local problem
     */
    function applyCloudData(problem, cloud) {
      problem.solved = cloud.solved || false;
      problem.time_to_solve = cloud.time_to_solve || '';
      problem.comments = cloud.comments || '';
      problem.solved_date = cloud.solved_date || '';
    }

    /**
     * Force sync now
     */
    async function forceSyncNow() {
      if (!isCloudSyncEnabled()) {
        alert('Please sign in to sync');
        return;
      }

      hideAuthMenu();

      try {
        await syncAllToCloud();
        await pullFromCloud();
      } catch (error) {
        console.error('Force sync failed:', error);
        alert('Sync failed: ' + error.message);
      }
    }

    // ============================================
    // REAL-TIME LISTENERS
    // ============================================

    /**
     * Setup real-time listeners for cloud changes
     */
    function setupRealtimeListeners() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      const userRef = firebaseDb.collection('users').doc(currentUser.uid);

      // Listen for changes to progress collection
      const unsubscribe = userRef.collection('progress')
        .onSnapshot(snapshot => {
          snapshot.docChanges().forEach(change => {
            if (change.type === 'modified') {
              handleCloudChange(change.doc.data());
            }
          });
        }, error => {
          console.error('Realtime listener error:', error);
          updateSyncStatusUI('error', 'Connection lost');
        });

      realtimeListeners.push(unsubscribe);

      // Setup config real-time listeners (filter, export, UI preferences)
      if (typeof setupConfigRealtimeListeners === 'function') {
        setupConfigRealtimeListeners();
      }
    }

    /**
     * Handle incoming cloud changes
     */
    function handleCloudChange(cloudData) {
      // Skip if this change originated from this device
      if (cloudData.updatedFrom === 'web' && !isSyncing) {
        // Could be from another tab, so we should still apply
      }

      const problemName = cloudData.name;

      // Find and update all instances of this problem
      for (const fileKey of PROBLEM_DATA.file_list) {
        const problems = PROBLEM_DATA.data[fileKey];
        const idx = problems.findIndex(p => p.name === problemName);

        if (idx !== -1) {
          const problem = problems[idx];

          // Update if cloud is newer (compare timestamps)
          const localDate = problem.solved_date ? new Date(problem.solved_date) : new Date(0);
          const cloudDate = cloudData.updatedAt ? cloudData.updatedAt.toDate() : new Date(0);

          if (cloudDate > localDate || !problem.solved_date) {
            applyCloudData(problem, cloudData);
            saveToLocalStorage(fileKey);

            // Update DOM
            if (typeof updateDOMField === 'function') {
              updateDOMField(fileKey, idx, 'solved', problem.solved);
              updateDOMField(fileKey, idx, 'time_to_solve', problem.time_to_solve);
              updateDOMField(fileKey, idx, 'comments', problem.comments);
            }

            // Update awareness and progress
            if (typeof updateRowAwareness === 'function') {
              updateRowAwareness(fileKey, idx);
            }
            updateProgress(fileKey);
          }
        }
      }

      updateOverallProgress();
    }

    /**
     * Teardown all real-time listeners
     */
    function teardownListeners() {
      realtimeListeners.forEach(unsubscribe => {
        if (typeof unsubscribe === 'function') {
          unsubscribe();
        }
      });
      realtimeListeners = [];
    }

    // ============================================
    // CONFLICT RESOLUTION
    // ============================================

    /**
     * Detect if there's a sync conflict between local and cloud data
     */
    function detectSyncConflict(local, cloud) {
      // If data is identical, no conflict
      if (local.solved === cloud.solved &&
          local.time_to_solve === cloud.time_to_solve &&
          local.comments === cloud.comments) {
        return { hasConflict: false };
      }

      // Get timestamps
      const localTime = local.solved_date ? new Date(local.solved_date).getTime() : 0;
      const cloudTime = cloud.updatedAt ? cloud.updatedAt.toDate().getTime() :
                       (cloud.solved_date ? new Date(cloud.solved_date).getTime() : 0);

      const TOLERANCE = 5000; // 5 seconds

      // Clear winner if timestamps differ significantly
      if (cloudTime > localTime + TOLERANCE) {
        return { hasConflict: false, winner: 'cloud' };
      }
      if (localTime > cloudTime + TOLERANCE) {
        return { hasConflict: false, winner: 'local' };
      }

      // True conflict - timestamps are close but data differs
      return { hasConflict: true };
    }

    /**
     * Show sync conflict resolution dialog
     */
    function showSyncConflictDialog(conflicts) {
      // Create or get overlay
      let overlay = document.getElementById('sync-conflict-overlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'sync-conflict-overlay';
        overlay.className = 'sync-conflict-overlay';
        document.body.appendChild(overlay);
      }

      overlay.innerHTML = `
        <div class="sync-conflict-panel" role="dialog" aria-labelledby="sync-conflict-title" aria-modal="true">
          <div class="sync-conflict-header">
            <h2 id="sync-conflict-title">Sync Conflicts Detected</h2>
            <button class="sync-conflict-close" onclick="hideSyncConflictDialog()">&times;</button>
          </div>

          <div class="sync-conflict-description">
            <p>Your local data differs from cloud data for ${conflicts.length} problem(s). Choose how to resolve:</p>
          </div>

          <div class="sync-conflict-global-actions">
            <button onclick="resolveAllSyncConflicts('local')">Keep All Local</button>
            <button onclick="resolveAllSyncConflicts('cloud')">Keep All Cloud</button>
            <button onclick="resolveAllSyncConflicts('merge')">Auto-Merge All</button>
          </div>

          <div class="sync-conflict-list" id="sync-conflict-list">
            ${conflicts.map((c, i) => `
              <div class="sync-conflict-item" data-index="${i}">
                <div class="sync-conflict-name">${escapeHTML(c.name)}</div>
                <div class="sync-conflict-comparison">
                  <div class="sync-conflict-local">
                    <h4>Local</h4>
                    <div>Solved: ${c.local.solved ? 'Yes' : 'No'}</div>
                    <div>Time: ${c.local.time_to_solve || '-'}</div>
                    <div>Comments: ${truncateText(c.local.comments, 30) || '-'}</div>
                  </div>
                  <div class="sync-conflict-cloud">
                    <h4>Cloud</h4>
                    <div>Solved: ${c.cloud.solved ? 'Yes' : 'No'}</div>
                    <div>Time: ${c.cloud.time_to_solve || '-'}</div>
                    <div>Comments: ${truncateText(c.cloud.comments, 30) || '-'}</div>
                  </div>
                </div>
                <div class="sync-conflict-options">
                  <label><input type="radio" name="conflict-${i}" value="local"> Keep Local</label>
                  <label><input type="radio" name="conflict-${i}" value="cloud" checked> Keep Cloud</label>
                  <label><input type="radio" name="conflict-${i}" value="merge"> Merge</label>
                </div>
              </div>
            `).join('')}
          </div>

          <div class="sync-conflict-footer">
            <button class="sync-conflict-btn-secondary" onclick="hideSyncConflictDialog()">Cancel</button>
            <button class="sync-conflict-btn-primary" onclick="applySyncConflictResolutions()">Apply</button>
          </div>
        </div>
      `;

      // Store conflicts for resolution
      window.pendingSyncConflicts = conflicts;
      overlay.style.display = 'flex';
    }

    /**
     * Hide sync conflict dialog
     */
    function hideSyncConflictDialog() {
      const overlay = document.getElementById('sync-conflict-overlay');
      if (overlay) {
        overlay.style.display = 'none';
      }
      window.pendingSyncConflicts = null;
      updateSyncStatusUI('synced');
    }

    /**
     * Resolve all conflicts with same strategy
     */
    function resolveAllSyncConflicts(strategy) {
      const conflicts = window.pendingSyncConflicts || [];
      conflicts.forEach((c, i) => {
        const radio = document.querySelector(`input[name="conflict-${i}"][value="${strategy}"]`);
        if (radio) radio.checked = true;
      });
    }

    /**
     * Apply selected conflict resolutions
     */
    async function applySyncConflictResolutions() {
      const conflicts = window.pendingSyncConflicts || [];

      for (let i = 0; i < conflicts.length; i++) {
        const conflict = conflicts[i];
        const selected = document.querySelector(`input[name="conflict-${i}"]:checked`);
        const resolution = selected ? selected.value : 'cloud';

        const problem = PROBLEM_DATA.data[conflict.fileKey][conflict.idx];

        switch (resolution) {
          case 'local':
            // Keep local, push to cloud
            break;
          case 'cloud':
            // Apply cloud data
            applyCloudData(problem, conflict.cloud);
            break;
          case 'merge':
            // Smart merge: solved=true wins, non-empty wins, concatenate comments
            problem.solved = problem.solved || conflict.cloud.solved;
            problem.time_to_solve = problem.time_to_solve || conflict.cloud.time_to_solve;
            if (problem.comments && conflict.cloud.comments &&
                problem.comments !== conflict.cloud.comments) {
              problem.comments = problem.comments + '\\n---\\n' + conflict.cloud.comments;
            } else {
              problem.comments = problem.comments || conflict.cloud.comments;
            }
            problem.solved_date = problem.solved_date || conflict.cloud.solved_date;
            break;
        }

        saveToLocalStorage(conflict.fileKey);
      }

      // Sync resolved data to cloud
      await syncAllToCloud();

      // Re-render UI
      renderAllTabs();
      updateAllProgress();

      hideSyncConflictDialog();
    }

    // ============================================
    // AWARENESS CONFIG SYNC
    // ============================================

    /**
     * Sync awareness config to cloud
     */
    async function syncAwarenessConfigToCloud() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        await userRef.collection('config').doc('awareness').set({
          ...AWARENESS_CONFIG,
          updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
      } catch (error) {
        console.error('Failed to sync awareness config:', error);
      }
    }

    /**
     * Load awareness config from cloud
     */
    async function loadAwarenessConfigFromCloud() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);
        const doc = await userRef.collection('config').doc('awareness').get();

        if (doc.exists) {
          const cloudConfig = doc.data();
          // Merge with local config (cloud takes precedence)
          AWARENESS_CONFIG = deepMerge(AWARENESS_CONFIG, cloudConfig);
          saveAwarenessConfig();
        }
      } catch (error) {
        console.error('Failed to load awareness config from cloud:', error);
      }
    }

    /**
     * Clear all cloud data for current user
     */
    async function clearCloudData() {
      if (!isCloudSyncEnabled() || !firebaseDb) return;

      if (!confirm('This will delete ALL your cloud data. Local data will be kept. Continue?')) {
        return;
      }

      updateSyncStatusUI('syncing', 'Clearing...');

      try {
        const userRef = firebaseDb.collection('users').doc(currentUser.uid);

        // Delete progress collection
        const progressDocs = await userRef.collection('progress').get();
        const batch = firebaseDb.batch();
        progressDocs.forEach(doc => batch.delete(doc.ref));
        await batch.commit();

        // Delete config
        await userRef.collection('config').doc('awareness').delete();

        updateSyncStatusUI('synced');
        alert('Cloud data cleared successfully');
      } catch (error) {
        console.error('Failed to clear cloud data:', error);
        updateSyncStatusUI('error', error.message);
        alert('Failed to clear cloud data: ' + error.message);
      }
    }
    '''

    return js


if __name__ == "__main__":
    # Test with sample config
    sample_config = {
        "apiKey": "test-api-key",
        "authDomain": "test-project.firebaseapp.com",
        "projectId": "test-project"
    }
    print(generate_js_firebase(sample_config))
