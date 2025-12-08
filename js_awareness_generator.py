#!/usr/bin/env python3
"""
Awareness Logic Sub-Agent
Implements spaced repetition awareness calculations and color management
"""

# SYNCHRONIZATION REQUIREMENT:
# Core calculation functions in this file are duplicated in tests/awareness.js for testing.
# When modifying getTierName(), getTierDifficultyMultiplier(), getCommitmentFactor(),
# getSolvedFactor(), getDaysSinceCompletion(), calculateAwarenessScore(), or getAwarenessClass(),
# you MUST update both files to keep them in sync.
# After changes, run tests to verify: cd tests && npm test

def generate_js_awareness():
    """Generate JavaScript awareness logic"""

    js = '''
    // Default awareness configuration
    const DEFAULT_AWARENESS_CONFIG = {
      // === USER-FACING SETTINGS ===
      commitment: {
        problemsPerDay: 2         // Default: 2 problems/day
      },
      thresholds: {
        white: 10,
        green: 30,
        yellow: 50,
        red: 70,
        darkRed: 90
      },
      // === ADVANCED/DEBUG SETTINGS ===
      baseRate: 2.0,              // Points per day (debug only)
      baseSolvedScaling: 0.1,     // How much solved count affects decay

      // Combined tier-difficulty multipliers
      // Top tier: Easy=mastered (0), Medium<Hard (inverted - deep mastery)
      // Other tiers: Easy>Medium>Hard (standard - easy forgotten faster)
      tierDifficultyMultipliers: {
        top: {
          Easy: 0,                // Mastered completely - never needs review
          Medium: 0.25,           // Deep mastery - very slow decay
          Hard: 0.4               // Great but hard problems have nuances that fade
        },
        advanced: {
          Easy: 1.2,              // Good grasp, but easy problems forgotten fast
          Medium: 0.9,            // Solid understanding
          Hard: 0.7               // Hard problems stick better
        },
        intermediate: {
          Easy: 1.5,              // Quick grasp but quick to forget
          Medium: 1.0,            // Baseline
          Hard: 0.75              // Harder = more processing = sticks longer
        },
        below: {
          Easy: 1.8,              // Took too long on easy - needs frequent review
          Medium: 1.3,            // Struggled with medium - needs review
          Hard: 1.0               // Struggled with hard - expected, baseline
        }
      },

      tierSolvedBonus: {          // Extra solved_factor bonus per tier
        top: 0.3,                 // Top performers benefit most from high solved count
        advanced: 0.2,
        intermediate: 0.1,
        below: 0                  // Below intermediate doesn't benefit
      },

      flashInterval: 500,         // ms for flashing animation

      // Refresh settings
      refreshInterval: 86400000,  // 24 hours in milliseconds (default: daily)
      refreshOnFocus: true        // Refresh when window regains focus
    };

    // Current awareness config (loaded from localStorage or defaults)
    let AWARENESS_CONFIG = JSON.parse(JSON.stringify(DEFAULT_AWARENESS_CONFIG));

    // Load awareness config from localStorage
    function loadAwarenessConfig() {
      const saved = localStorage.getItem('tracker_awareness_config');
      if (saved) {
        try {
          const savedConfig = JSON.parse(saved);
          // Deep merge with defaults to handle missing fields
          AWARENESS_CONFIG = deepMerge(DEFAULT_AWARENESS_CONFIG, savedConfig);
        } catch (e) {
          console.error('Error loading awareness config:', e);
          AWARENESS_CONFIG = JSON.parse(JSON.stringify(DEFAULT_AWARENESS_CONFIG));
        }
      }
    }

    // Deep merge two objects
    function deepMerge(target, source) {
      const result = JSON.parse(JSON.stringify(target));
      for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
          result[key] = deepMerge(result[key] || {}, source[key]);
        } else {
          result[key] = source[key];
        }
      }
      return result;
    }

    // Save awareness config to localStorage
    function saveAwarenessConfig() {
      localStorage.setItem('tracker_awareness_config', JSON.stringify(AWARENESS_CONFIG));
    }

    // Reset awareness config to defaults
    function resetAwarenessConfig() {
      AWARENESS_CONFIG = JSON.parse(JSON.stringify(DEFAULT_AWARENESS_CONFIG));
      localStorage.removeItem('tracker_awareness_config');
    }

    // Get tier name as string (for matrix lookup and solved bonus)
    function getTierName(problem) {
      const timeToSolve = parseFloat(problem.time_to_solve);

      // If no time recorded, use "below" tier
      if (isNaN(timeToSolve) || timeToSolve <= 0) {
        return 'below';
      }

      const topTime = parseFloat(problem.top_time) || Infinity;
      const advancedTime = parseFloat(problem.advanced_time) || Infinity;
      const intermediateTime = parseFloat(problem.intermediate_time) || Infinity;

      if (timeToSolve <= topTime) {
        return 'top';
      } else if (timeToSolve <= advancedTime) {
        return 'advanced';
      } else if (timeToSolve <= intermediateTime) {
        return 'intermediate';
      } else {
        return 'below';
      }
    }

    // Get combined tier-difficulty multiplier
    // Top tier has inverted behavior: Easy=0 (mastered), Medium<Hard
    // Other tiers: Easy>Medium>Hard (standard)
    function getTierDifficultyMultiplier(problem) {
      const tier = getTierName(problem);
      const difficulty = problem.difficulty || 'Medium';
      const matrix = AWARENESS_CONFIG.tierDifficultyMultipliers;

      // Fallback to intermediate-Medium if tier or difficulty not found
      if (!matrix[tier]) return 1.0;
      if (matrix[tier][difficulty] === undefined) return 1.0;

      return matrix[tier][difficulty];
    }

    // Get total unique solved count across all problem lists
    function getTotalUniqueSolvedCount() {
      const solvedNames = new Set();
      PROBLEM_DATA.file_list.forEach(fileKey => {
        PROBLEM_DATA.data[fileKey].forEach(p => {
          if (p.solved) solvedNames.add(p.name);
        });
      });
      return solvedNames.size;
    }

    // Get commitment factor (higher commitment = faster decay)
    function getCommitmentFactor() {
      const commitment = AWARENESS_CONFIG.commitment.problemsPerDay;
      const baseline = 2;  // 2 problems/day is baseline
      return commitment / baseline;
    }

    // Get solved factor (higher solved count = slower decay, especially for higher tiers)
    function getSolvedFactor(problem) {
      const totalSolved = getTotalUniqueSolvedCount();
      const tier = getTierName(problem);
      const baseScaling = AWARENESS_CONFIG.baseSolvedScaling;
      const tierBonus = AWARENESS_CONFIG.tierSolvedBonus[tier];

      // Logarithmic scaling: early solutions have big impact, diminishing returns later
      // log2(1) = 0, so minimum solved_factor is 1
      return 1 + (baseScaling + tierBonus) * Math.log2(totalSolved + 1);
    }

    // Normalize date to ISO format, returns null if invalid
    function normalizeDateToISO(dateInput) {
      if (!dateInput) return null;

      const date = new Date(dateInput);
      if (isNaN(date.getTime())) return null;

      return date.toISOString();
    }

    // Calculate days since completion
    // Returns: { days: number, valid: boolean }
    function getDaysSinceCompletion(solvedDate) {
      if (!solvedDate) return { days: -1, valid: true };  // No date is valid (unsolved)

      const now = new Date();
      const date = new Date(solvedDate);

      // Handle invalid dates
      if (isNaN(date.getTime())) {
        console.warn('Invalid date format for solved_date:', solvedDate);
        return { days: -1, valid: false };
      }

      // Handle future dates (clock skew)
      if (date > now) return { days: 0, valid: true };

      const diffMs = now - date;
      const diffDays = diffMs / (1000 * 60 * 60 * 24);
      return { days: diffDays, valid: true };
    }

    // Calculate awareness score for a problem
    // Returns: { score: number, invalidDate: boolean }
    function calculateAwarenessScore(problem) {
      // Not solved - return -1 to indicate no awareness styling
      if (!problem.solved) return { score: -1, invalidDate: false };

      const dateResult = getDaysSinceCompletion(problem.solved_date);

      // Invalid date
      if (!dateResult.valid) return { score: -1, invalidDate: true };

      // No valid date (unsolved)
      if (dateResult.days < 0) return { score: -1, invalidDate: false };

      const commitmentFactor = getCommitmentFactor();
      const tierDiffMultiplier = getTierDifficultyMultiplier(problem);
      const solvedFactor = getSolvedFactor(problem);

      // Enhanced formula with combined tier-difficulty multiplier:
      // days * baseRate * commitmentFactor * tierDiffMult / solvedFactor
      //
      // Special behaviors:
      // - Top tier + Easy = 0 multiplier = score stays 0 = always white (mastered)
      // - Top tier: Medium < Hard (inverted - deep mastery of medium decays slower)
      // - Other tiers: Easy > Medium > Hard (standard - easy problems forgotten faster)
      const score = dateResult.days * AWARENESS_CONFIG.baseRate * commitmentFactor * tierDiffMultiplier / solvedFactor;

      return { score, invalidDate: false };
    }

    // Get CSS class for awareness score
    function getAwarenessClass(score) {
      if (score < 0) return 'unsolved-problem';

      const thresholds = AWARENESS_CONFIG.thresholds;

      if (score < thresholds.white) return 'awareness-white';
      if (score < thresholds.green) return 'awareness-green';
      if (score < thresholds.yellow) return 'awareness-yellow';
      if (score < thresholds.red) return 'awareness-red';
      if (score < thresholds.darkRed) return 'awareness-dark-red';
      return 'awareness-flashing';
    }

    // All awareness CSS classes for removal
    const AWARENESS_CLASSES = [
      'awareness-white',
      'awareness-green',
      'awareness-yellow',
      'awareness-red',
      'awareness-dark-red',
      'awareness-flashing',
      'unsolved-problem'
    ];

    // Debounce utility for preventing rapid-fire updates
    function debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }

    // Update awareness color for a single row
    function updateRowAwareness(fileKey, idx) {
      const tbody = document.getElementById(`tbody-${fileKey}`);
      if (!tbody) return;

      const row = tbody.querySelector(`tr[data-index="${idx}"]`);
      if (!row) return;

      const problem = PROBLEM_DATA.data[fileKey][idx];
      const result = calculateAwarenessScore(problem);
      const newClass = getAwarenessClass(result.score);

      // Remove all awareness classes and invalid-date class
      AWARENESS_CLASSES.forEach(cls => row.classList.remove(cls));
      row.classList.remove('invalid-date');

      // Add the new class
      row.classList.add(newClass);

      // Add invalid-date indicator if needed
      if (result.invalidDate) {
        row.classList.add('invalid-date');
      }
    }

    // Update awareness colors for all problems in a specific tab
    function updateTabAwareness(fileKey) {
      PROBLEM_DATA.data[fileKey].forEach((problem, idx) => {
        updateRowAwareness(fileKey, idx);
      });
    }

    // Update awareness colors for problems
    // @param {boolean} allTabs - If true, update all tabs; if false, update only current tab
    function updateAwarenessColors(allTabs = false) {
      if (allTabs) {
        PROBLEM_DATA.file_list.forEach(fileKey => {
          updateTabAwareness(fileKey);
        });
      } else {
        // Only update current visible tab (currentTab is defined in js_core_generator.py)
        updateTabAwareness(currentTab);
      }
    }

    // Auto-refresh management
    let awarenessRefreshInterval = null;
    let focusHandler = null;

    function setupAwarenessRefresh() {
      // Clear existing interval if any
      if (awarenessRefreshInterval) {
        clearInterval(awarenessRefreshInterval);
        awarenessRefreshInterval = null;
      }

      // Set up new interval based on config (0 = manual only)
      if (AWARENESS_CONFIG.refreshInterval > 0) {
        awarenessRefreshInterval = setInterval(() => updateAwarenessColors(true), AWARENESS_CONFIG.refreshInterval);
      }

      // Remove existing focus listener if any
      if (focusHandler) {
        window.removeEventListener('focus', focusHandler);
        focusHandler = null;
      }

      // Add focus listener if enabled (debounced to prevent rapid updates)
      if (AWARENESS_CONFIG.refreshOnFocus) {
        focusHandler = debounce(function() {
          updateAwarenessColors(true);  // Update all tabs on focus since user may have been away
        }, 300);
        window.addEventListener('focus', focusHandler);
      }
    }

    // Manual refresh function (can be called from button)
    function manualRefreshAwareness() {
      updateAwarenessColors(true);  // Update all tabs for manual refresh
    }

    // Initialize awareness on load
    function initAwareness() {
      loadAwarenessConfig();
      updateAwarenessColors(true);  // Update all tabs on initial load
      setupAwarenessRefresh();
    }
    '''

    return js

if __name__ == "__main__":
    print(generate_js_awareness())
