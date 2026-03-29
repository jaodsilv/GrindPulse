/**
 * Unit Tests for Name-Based localStorage Loading (Issue #76)
 */

import { applyNameBasedLoad, loadAndApplyFromLocalStorage } from './local-storage-load.js';

function makeProblems(...names) {
  return names.map(name => ({
    name,
    solved: false,
    time_to_solve: '',
    comments: '',
    solved_date: ''
  }));
}

function makeLocalStorage(initial = {}, throwOnGet = false) {
  const store = Object.assign({}, initial);
  return {
    _store: store,
    getItem(key) {
      if (throwOnGet) throw new Error('Storage access denied');
      return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
    },
    setItem(key, val) { store[key] = val; },
    removeItem(key) { delete store[key]; }
  };
}

function makeDocument() {
  const elements = [];
  const byId = {};
  const body = {
    children: elements,
    appendChild(el) {
      el.parentNode = body;
      elements.push(el);
      if (el.id) byId[el.id] = el;
    },
    removeChild(el) {
      const idx = elements.indexOf(el);
      if (idx !== -1) elements.splice(idx, 1);
      if (el.id && byId[el.id] === el) delete byId[el.id];
    }
  };
  return {
    body,
    getElementById(id) { return byId[id] || null; },
    createElement(tag) {
      return {
        tag, id: '', className: '', textContent: '', parentNode: null,
        remove() { if (this.parentNode) this.parentNode.removeChild(this); }
      };
    },
    _getToasts() { return elements; }
  };
}

function makeFakeTimer() {
  const pending = [];
  const fn = (cb, delay) => pending.push({ cb, delay });
  fn._pending = pending;
  fn.flush = () => { pending.forEach(t => t.cb()); pending.length = 0; };
  return fn;
}

// ─────────────────────────────────────────────
// applyNameBasedLoad — name matching
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — name-based matching', () => {
  it('merges saved fields onto problem with matching name', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { name: 'Two Sum', solved: true, time_to_solve: '15', comments: 'easy', solved_date: '2025-01-01' }
    ]);
    expect(problems[0].solved).toBe(true);
    expect(problems[0].time_to_solve).toBe('15');
    expect(problems[0].comments).toBe('easy');
    expect(problems[0].solved_date).toBe('2025-01-01');
  });

  it('matches by name regardless of array position', () => {
    const problems = makeProblems('Two Sum', 'Valid Parentheses', 'Merge Intervals');
    const savedData = [
      { name: 'Merge Intervals', solved: true, time_to_solve: '20', comments: '', solved_date: '2025-02-01' },
      { name: 'Two Sum', solved: true, time_to_solve: '10', comments: '', solved_date: '2025-01-01' }
    ];
    applyNameBasedLoad(problems, savedData);
    expect(problems[0].solved).toBe(true);
    expect(problems[0].time_to_solve).toBe('10');
    expect(problems[2].solved).toBe(true);
    expect(problems[2].time_to_solve).toBe('20');
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — index shift resilience
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — index shift resilience', () => {
  it('still maps data correctly when problem order changes', () => {
    const savedData = [
      { name: 'Two Sum', solved: true, time_to_solve: '5', comments: '', solved_date: '' },
      { name: 'Valid Parentheses', solved: false, time_to_solve: '', comments: '', solved_date: '' }
    ];
    const reorderedProblems = makeProblems('Valid Parentheses', 'Two Sum');
    applyNameBasedLoad(reorderedProblems, savedData);
    expect(reorderedProblems[0].solved).toBe(false);
    expect(reorderedProblems[1].solved).toBe(true);
    expect(reorderedProblems[1].time_to_solve).toBe('5');
  });

  it('does not corrupt data when a problem is inserted at the front of the list', () => {
    const savedData = [
      { name: 'Binary Search', solved: true, time_to_solve: '8', comments: '', solved_date: '2025-03-01' }
    ];
    const problems = makeProblems('NEW PROBLEM', 'Binary Search');
    applyNameBasedLoad(problems, savedData);
    expect(problems[0].solved).toBe(false);
    expect(problems[1].solved).toBe(true);
    expect(problems[1].time_to_solve).toBe('8');
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — missing problems
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — missing problems', () => {
  it('silently ignores saved items not present in the current list', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { name: 'Removed Problem', solved: true, time_to_solve: '10', comments: '', solved_date: '' },
      { name: 'Two Sum', solved: true, time_to_solve: '5', comments: '', solved_date: '' }
    ]);
    expect(problems.length).toBe(1);
    expect(problems[0].solved).toBe(true);
  });

  it('does not throw when all saved names are absent from problem list', () => {
    const problems = makeProblems('Two Sum');
    expect(() => applyNameBasedLoad(problems, [
      { name: 'Ghost Problem', solved: true, time_to_solve: '', comments: '', solved_date: '' }
    ])).not.toThrow();
    expect(problems[0].solved).toBe(false);
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — new problems
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — new problems', () => {
  it('leaves new problems (not in saved data) with default values', () => {
    const problems = makeProblems('Two Sum', 'Brand New Problem');
    applyNameBasedLoad(problems, [
      { name: 'Two Sum', solved: true, time_to_solve: '5', comments: '', solved_date: '' }
    ]);
    expect(problems[1].solved).toBe(false);
    expect(problems[1].time_to_solve).toBe('');
    expect(problems[1].comments).toBe('');
    expect(problems[1].solved_date).toBe('');
  });

  it('handles an empty saved data array without modifying any problems', () => {
    const problems = makeProblems('Two Sum', 'Merge Intervals');
    applyNameBasedLoad(problems, []);
    expect(problems[0].solved).toBe(false);
    expect(problems[1].solved).toBe(false);
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — duplicate names across files
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — duplicate names across files', () => {
  it('applies saved data independently per call (file-key scoping)', () => {
    const blind75Problems = makeProblems('Two Sum', 'Valid Parentheses');
    const neetcodeProblems = makeProblems('Two Sum', 'Merge Intervals');

    applyNameBasedLoad(blind75Problems, [
      { name: 'Two Sum', solved: true, time_to_solve: '5', comments: 'blind75 note', solved_date: '2025-01-01' }
    ]);
    applyNameBasedLoad(neetcodeProblems, [
      { name: 'Two Sum', solved: false, time_to_solve: '', comments: 'neetcode note', solved_date: '' }
    ]);

    expect(blind75Problems[0].solved).toBe(true);
    expect(blind75Problems[0].comments).toBe('blind75 note');
    expect(neetcodeProblems[0].solved).toBe(false);
    expect(neetcodeProblems[0].comments).toBe('neetcode note');
  });

  it('does not cross-contaminate data between two lists sharing a problem name', () => {
    const list1 = makeProblems('Two Sum');
    const list2 = makeProblems('Two Sum');

    applyNameBasedLoad(list1, [{ name: 'Two Sum', solved: true, time_to_solve: '3', comments: '', solved_date: '' }]);
    applyNameBasedLoad(list2, [{ name: 'Two Sum', solved: false, time_to_solve: '7', comments: '', solved_date: '' }]);

    expect(list1[0].time_to_solve).toBe('3');
    expect(list2[0].time_to_solve).toBe('7');
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — empty/null name handling
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — empty/null name handling', () => {
  it('skips saved items with null name', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { name: null, solved: true, time_to_solve: '10', comments: '', solved_date: '' }
    ]);
    expect(problems[0].solved).toBe(false);
  });

  it('skips saved items with empty string name', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { name: '', solved: true, time_to_solve: '10', comments: '', solved_date: '' }
    ]);
    expect(problems[0].solved).toBe(false);
  });

  it('skips saved items with undefined name', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { solved: true, time_to_solve: '10', comments: '', solved_date: '' }
    ]);
    expect(problems[0].solved).toBe(false);
  });

  it('skips null entries in saved array', () => {
    const problems = makeProblems('Two Sum');
    expect(() => applyNameBasedLoad(problems, [null, { name: 'Two Sum', solved: true, time_to_solve: '', comments: '', solved_date: '' }])).not.toThrow();
    expect(problems[0].solved).toBe(true);
  });
});

// ─────────────────────────────────────────────
// applyNameBasedLoad — backward compatibility
// ─────────────────────────────────────────────
describe('applyNameBasedLoad — backward compatibility', () => {
  it('gracefully handles old index-based format (items without name)', () => {
    const problems = makeProblems('Two Sum', 'Valid Parentheses');
    const oldFormat = [
      { solved: true, time_to_solve: '5', comments: '', solved_date: '' },
      { solved: false, time_to_solve: '', comments: '', solved_date: '' }
    ];
    expect(() => applyNameBasedLoad(problems, oldFormat)).not.toThrow();
    expect(problems[0].solved).toBe(false);
    expect(problems[1].solved).toBe(false);
  });

  it('applies named items even when mixed with nameless items', () => {
    const problems = makeProblems('Two Sum', 'Valid Parentheses');
    const mixedFormat = [
      { solved: true, time_to_solve: '5', comments: '', solved_date: '' },
      { name: 'Valid Parentheses', solved: true, time_to_solve: '12', comments: 'stack', solved_date: '2025-04-01' }
    ];
    applyNameBasedLoad(problems, mixedFormat);
    expect(problems[0].solved).toBe(false);
    expect(problems[1].solved).toBe(true);
    expect(problems[1].time_to_solve).toBe('12');
  });

  it('defaults falsy field values to empty/false instead of propagating them', () => {
    const problems = makeProblems('Two Sum');
    applyNameBasedLoad(problems, [
      { name: 'Two Sum', solved: null, time_to_solve: null, comments: null, solved_date: null }
    ]);
    expect(problems[0].solved).toBe(false);
    expect(problems[0].time_to_solve).toBe('');
    expect(problems[0].comments).toBe('');
    expect(problems[0].solved_date).toBe('');
  });
});

// ─────────────────────────────────────────────
// loadAndApplyFromLocalStorage
// ─────────────────────────────────────────────
describe('loadAndApplyFromLocalStorage — basic I/O', () => {
  it('loads and applies data from localStorage by file key', () => {
    const savedData = [{ name: 'Two Sum', solved: true, time_to_solve: '5', comments: '', solved_date: '' }];
    const ls = makeLocalStorage({ tracker_blind75: JSON.stringify(savedData) });
    const problems = makeProblems('Two Sum');
    loadAndApplyFromLocalStorage('blind75', problems, ls, null, null);
    expect(problems[0].solved).toBe(true);
    expect(problems[0].time_to_solve).toBe('5');
  });

  it('does nothing when key does not exist in localStorage', () => {
    const ls = makeLocalStorage();
    const problems = makeProblems('Two Sum');
    loadAndApplyFromLocalStorage('blind75', problems, ls, null, null);
    expect(problems[0].solved).toBe(false);
  });

  it('does nothing when localStorage is null', () => {
    const problems = makeProblems('Two Sum');
    expect(() => loadAndApplyFromLocalStorage('blind75', problems, null, null, null)).not.toThrow();
    expect(problems[0].solved).toBe(false);
  });

  it('does not modify problems when saved JSON is not an array', () => {
    const ls = makeLocalStorage({ tracker_blind75: JSON.stringify({ name: 'Two Sum', solved: true }) });
    const problems = makeProblems('Two Sum');
    loadAndApplyFromLocalStorage('blind75', problems, ls, null, null);
    expect(problems[0].solved).toBe(false);
  });
});

describe('loadAndApplyFromLocalStorage — error handling', () => {
  it('shows error toast and does not throw when stored JSON is invalid', () => {
    const ls = makeLocalStorage({ tracker_blind75: '{bad json' });
    const doc = makeDocument();
    const timer = makeFakeTimer();
    const problems = makeProblems('Two Sum');
    expect(() => loadAndApplyFromLocalStorage('blind75', problems, ls, doc, timer)).not.toThrow();
    expect(doc._getToasts().length).toBe(1);
    expect(doc._getToasts()[0].className).toContain('sync-toast-error');
  });

  it('error toast message mentions load/corrupted/progress', () => {
    const ls = makeLocalStorage({ tracker_blind75: 'not-json' });
    const doc = makeDocument();
    const timer = makeFakeTimer();
    const problems = makeProblems('Two Sum');
    loadAndApplyFromLocalStorage('blind75', problems, ls, doc, timer);
    const text = doc._getToasts()[0].textContent.toLowerCase();
    expect(text).toMatch(/load|corrupt|progress/);
  });

  it('leaves problems unmodified after parse error', () => {
    const ls = makeLocalStorage({ tracker_blind75: '{{invalid' });
    const problems = makeProblems('Two Sum');
    loadAndApplyFromLocalStorage('blind75', problems, ls, null, null);
    expect(problems[0].solved).toBe(false);
  });

  it('does not throw when localStorage.getItem throws', () => {
    const ls = makeLocalStorage({}, true);
    const problems = makeProblems('Two Sum');
    expect(() => loadAndApplyFromLocalStorage('blind75', problems, ls, null, null)).not.toThrow();
  });
});

// ─────────────────────────────────────────────
// Integration: full load cycle with shifted index
// ─────────────────────────────────────────────
describe('Integration: name-based load vs index-based corruption', () => {
  it('name-based load correctly hydrates problems after a new problem is prepended', () => {
    const savedData = [
      { name: 'Two Sum', solved: true, time_to_solve: '5', comments: 'classic', solved_date: '2025-01-01' },
      { name: 'Valid Parentheses', solved: true, time_to_solve: '8', comments: '', solved_date: '2025-01-02' }
    ];
    const ls = makeLocalStorage({ tracker_blind75: JSON.stringify(savedData) });

    const updatedList = makeProblems('NEW PROBLEM', 'Two Sum', 'Valid Parentheses');
    loadAndApplyFromLocalStorage('blind75', updatedList, ls, null, null);

    expect(updatedList[0].solved).toBe(false);
    expect(updatedList[1].solved).toBe(true);
    expect(updatedList[1].comments).toBe('classic');
    expect(updatedList[2].solved).toBe(true);
    expect(updatedList[2].time_to_solve).toBe('8');
  });

  it('produces correct results for both files independently in a multi-file scenario', () => {
    const blind75Saved = [{ name: 'Two Sum', solved: true, time_to_solve: '5', comments: '', solved_date: '' }];
    const neetcodeSaved = [{ name: 'Merge Intervals', solved: true, time_to_solve: '15', comments: '', solved_date: '' }];
    const ls = makeLocalStorage({
      tracker_blind75: JSON.stringify(blind75Saved),
      tracker_neetcode150: JSON.stringify(neetcodeSaved)
    });

    const blind75 = makeProblems('Two Sum', 'Valid Parentheses');
    const neetcode = makeProblems('Two Sum', 'Merge Intervals');

    loadAndApplyFromLocalStorage('blind75', blind75, ls, null, null);
    loadAndApplyFromLocalStorage('neetcode150', neetcode, ls, null, null);

    expect(blind75[0].solved).toBe(true);
    expect(blind75[1].solved).toBe(false);
    expect(neetcode[0].solved).toBe(false);
    expect(neetcode[1].solved).toBe(true);
  });
});
