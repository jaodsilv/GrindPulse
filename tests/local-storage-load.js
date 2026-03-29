/**
 * Name-based localStorage loading functions (Extracted for Testing)
 * These functions mirror the fixed loadFromLocalStorage() in js_core_generator.py.
 *
 * SYNCHRONIZATION REQUIREMENT:
 * When modifying loadFromLocalStorage() in js_core_generator.py, update this file too.
 * Verify with: npm test
 */

export const FIELDS = ['solved', 'time_to_solve', 'comments', 'solved_date'];

/**
 * applyNameBasedLoad(problems, savedData)
 *
 * Merges saved data array (keyed by name) onto a problems array in-place.
 * - Matches each saved item to the current problem list by name.
 * - Problems not present in saved data retain default values.
 * - Saved items whose name doesn't appear in the current list are silently ignored.
 * - Saved items missing a name field are skipped.
 * - Old format (index-based, no name) degrades gracefully: only named items are applied.
 *
 * @param {Array} problems - Current problem objects (each must have a .name property)
 * @param {Array} savedData - Parsed localStorage array (each item may have .name + field values)
 */
export function applyNameBasedLoad(problems, savedData) {
  const nameMap = {};
  for (const item of savedData) {
    if (item && item.name) {
      nameMap[item.name] = item;
    }
  }

  for (const problem of problems) {
    const saved = nameMap[problem.name];
    if (saved) {
      problem.solved = saved.solved || false;
      problem.time_to_solve = saved.time_to_solve || '';
      problem.comments = saved.comments || '';
      problem.solved_date = saved.solved_date || '';
    }
  }
}

/**
 * loadAndApplyFromLocalStorage(fileKey, problems, _localStorage, _document, _setTimeout)
 *
 * Loads saved data for a file key from localStorage and applies it to the problems array
 * using name-based matching via applyNameBasedLoad().
 *
 * @param {string} fileKey - The file identifier (e.g. 'blind75')
 * @param {Array} problems - Current problem objects for this file
 * @param {object} _localStorage - Injectable localStorage (falls back to global)
 * @param {object} _document - Injectable document (for toast)
 * @param {function} _setTimeout - Injectable setTimeout (for toast)
 */
export function loadAndApplyFromLocalStorage(fileKey, problems, _localStorage, _document, _setTimeout) {
  const ls = _localStorage || (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!ls) return;

  let saved;
  try {
    const raw = ls.getItem(`tracker_${fileKey}`);
    if (!raw) return;
    saved = JSON.parse(raw);
  } catch (e) {
    const doc = _document || (typeof document !== 'undefined' ? document : null);
    const setTO = _setTimeout || (typeof setTimeout !== 'undefined' ? setTimeout : null);
    if (doc && doc.body) {
      const existing = doc.getElementById('storage-toast');
      if (existing) existing.remove();
      const toast = doc.createElement('div');
      toast.id = 'storage-toast';
      toast.className = 'sync-toast sync-toast-error';
      toast.textContent = 'Your saved progress could not be loaded. Data may be corrupted.';
      doc.body.appendChild(toast);
      if (setTO) {
        setTO(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 5000);
      }
    }
    return;
  }

  if (!Array.isArray(saved)) return;
  applyNameBasedLoad(problems, saved);
}
