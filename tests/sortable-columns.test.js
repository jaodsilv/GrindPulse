/**
 * Unit Tests for Sortable Columns Functions
 */

import {
  getSortValue,
  getSortedProblems,
  cycleSortState,
  saveSortState,
  restoreSortState,
  initSortHeaders,
  setMockProblemData,
  setMockLocalStorage,
  setSortState,
  getSortStateSnapshot,
  resetState
} from './sortable-columns.js';

// ── Minimal localStorage mock ─────────────────────────────────────────────────

function makeLocalStorage(throwOnSet = false, throwOnGet = false) {
  const store = {};
  return {
    _store: store,
    setItem(key, val) {
      if (throwOnSet) throw new DOMException('QuotaExceededError', 'QuotaExceededError');
      store[key] = val;
    },
    getItem(key) {
      if (throwOnGet) throw new Error('Storage access denied');
      return Object.prototype.hasOwnProperty.call(store, key) ? store[key] : null;
    },
    removeItem(key) { delete store[key]; }
  };
}

// ── Minimal header element mock ───────────────────────────────────────────────

function makeHeader(column) {
  const listeners = {};
  return {
    column,
    element: {
      dataset: { column },
      addEventListener(event, cb) {
        listeners[event] = listeners[event] || [];
        listeners[event].push(cb);
      },
      _click() {
        (listeners['click'] || []).forEach(cb => cb());
      }
    }
  };
}

// ─────────────────────────────────────────────────────────────────────────────

beforeEach(() => {
  resetState();
});

// ── getSortValue ──────────────────────────────────────────────────────────────

describe('getSortValue', () => {
  describe('difficulty column', () => {
    it('returns 1 for Easy', () => {
      expect(getSortValue({ difficulty: 'Easy' }, 'difficulty')).toBe(1);
    });

    it('returns 2 for Medium', () => {
      expect(getSortValue({ difficulty: 'Medium' }, 'difficulty')).toBe(2);
    });

    it('returns 3 for Hard', () => {
      expect(getSortValue({ difficulty: 'Hard' }, 'difficulty')).toBe(3);
    });

    it('returns null for empty string difficulty', () => {
      expect(getSortValue({ difficulty: '' }, 'difficulty')).toBeNull();
    });

    it('returns null for null difficulty', () => {
      expect(getSortValue({ difficulty: null }, 'difficulty')).toBeNull();
    });

    it('returns null for undefined difficulty', () => {
      expect(getSortValue({}, 'difficulty')).toBeNull();
    });

    it('returns null for unknown difficulty string', () => {
      expect(getSortValue({ difficulty: 'VeryHard' }, 'difficulty')).toBeNull();
    });
  });

  describe('name column', () => {
    it('returns lowercased name', () => {
      expect(getSortValue({ name: 'Two Sum' }, 'name')).toBe('two sum');
    });

    it('returns lowercased already-lowercase name', () => {
      expect(getSortValue({ name: 'merge intervals' }, 'name')).toBe('merge intervals');
    });

    it('returns null for null name', () => {
      const v = getSortValue({ name: null }, 'name');
      expect(v).toBeNull();
    });

    it('returns null for empty name', () => {
      const v = getSortValue({ name: '' }, 'name');
      expect(v).toBeNull();
    });

    it('returns null for missing name', () => {
      const v = getSortValue({}, 'name');
      expect(v).toBeNull();
    });
  });

  describe('numeric time columns', () => {
    const numericCols = ['time_to_solve', 'intermediate_time', 'advanced_time', 'top_time'];

    numericCols.forEach(col => {
      it(`returns parsed float for ${col}`, () => {
        expect(getSortValue({ [col]: 25 }, col)).toBe(25);
      });

      it(`returns parsed float for string value in ${col}`, () => {
        expect(getSortValue({ [col]: '30.5' }, col)).toBe(30.5);
      });

      it(`returns null for empty string in ${col}`, () => {
        expect(getSortValue({ [col]: '' }, col)).toBeNull();
      });

      it(`returns null for null in ${col}`, () => {
        expect(getSortValue({ [col]: null }, col)).toBeNull();
      });

      it(`returns null for undefined in ${col}`, () => {
        expect(getSortValue({}, col)).toBeNull();
      });

      it(`returns null for non-numeric string in ${col}`, () => {
        expect(getSortValue({ [col]: 'abc' }, col)).toBeNull();
      });
    });
  });

  describe('solved_date column', () => {
    it('returns Date.parse timestamp for valid ISO date', () => {
      const date = '2024-01-15T00:00:00.000Z';
      expect(getSortValue({ solved_date: date }, 'solved_date')).toBe(Date.parse(date));
    });

    it('returns Date.parse timestamp for YYYY-MM-DD format', () => {
      const date = '2024-06-01';
      const result = getSortValue({ solved_date: date }, 'solved_date');
      expect(result).toBe(Date.parse(date));
    });

    it('returns null for empty string', () => {
      expect(getSortValue({ solved_date: '' }, 'solved_date')).toBeNull();
    });

    it('returns null for null', () => {
      expect(getSortValue({ solved_date: null }, 'solved_date')).toBeNull();
    });

    it('returns null for undefined', () => {
      expect(getSortValue({}, 'solved_date')).toBeNull();
    });

    it('returns null for invalid date string', () => {
      expect(getSortValue({ solved_date: 'not-a-date' }, 'solved_date')).toBeNull();
    });
  });

  describe('unknown column', () => {
    it('returns null for unknown column', () => {
      expect(getSortValue({ foo: 'bar' }, 'nonexistent')).toBeNull();
    });
  });
});

// ── getSortedProblems ─────────────────────────────────────────────────────────

describe('getSortedProblems', () => {
  const problems = [
    { name: 'Two Sum', difficulty: 'Easy' },
    { name: 'Merge Intervals', difficulty: 'Medium' },
    { name: 'Binary Tree Max Depth', difficulty: 'Easy' },
    { name: 'Trapping Rain Water', difficulty: 'Hard' },
    { name: 'Valid Parentheses', difficulty: 'Medium' }
  ];

  beforeEach(() => {
    setMockProblemData({ file_list: ['test'], data: { test: problems } });
  });

  it('returns original order when no sort state set', () => {
    const result = getSortedProblems('test');
    expect(result.map(p => p.name)).toEqual(problems.map(p => p.name));
  });

  it('returns original order when direction is none', () => {
    setSortState({ test: { column: 'difficulty', direction: 'none' } });
    const result = getSortedProblems('test');
    expect(result.map(p => p.name)).toEqual(problems.map(p => p.name));
  });

  it('sorts by difficulty ascending (Easy < Medium < Hard)', () => {
    setSortState({ test: { column: 'difficulty', direction: 'asc' } });
    const result = getSortedProblems('test');
    const diffs = result.map(p => p.difficulty);
    expect(diffs[0]).toBe('Easy');
    expect(diffs[1]).toBe('Easy');
    expect(diffs[2]).toBe('Medium');
    expect(diffs[3]).toBe('Medium');
    expect(diffs[4]).toBe('Hard');
  });

  it('sorts by difficulty descending (Hard < Medium < Easy)', () => {
    setSortState({ test: { column: 'difficulty', direction: 'desc' } });
    const result = getSortedProblems('test');
    const diffs = result.map(p => p.difficulty);
    expect(diffs[0]).toBe('Hard');
    expect(diffs[1]).toBe('Medium');
    expect(diffs[2]).toBe('Medium');
    expect(diffs[3]).toBe('Easy');
    expect(diffs[4]).toBe('Easy');
  });

  it('puts null/empty difficulty values last regardless of asc direction', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'A', difficulty: null },
          { name: 'B', difficulty: 'Hard' },
          { name: 'C', difficulty: '' },
          { name: 'D', difficulty: 'Easy' }
        ]
      }
    });
    setSortState({ test: { column: 'difficulty', direction: 'asc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('D');
    expect(result[1].name).toBe('B');
    expect(['A', 'C']).toContain(result[2].name);
    expect(['A', 'C']).toContain(result[3].name);
  });

  it('puts null/empty difficulty values last regardless of desc direction', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'A', difficulty: null },
          { name: 'B', difficulty: 'Easy' },
          { name: 'C', difficulty: '' },
          { name: 'D', difficulty: 'Hard' }
        ]
      }
    });
    setSortState({ test: { column: 'difficulty', direction: 'desc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('D');
    expect(result[1].name).toBe('B');
    expect(['A', 'C']).toContain(result[2].name);
    expect(['A', 'C']).toContain(result[3].name);
  });

  it('maintains stable sort for equal values (original order preserved)', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'First Medium', difficulty: 'Medium' },
          { name: 'Second Medium', difficulty: 'Medium' },
          { name: 'Third Medium', difficulty: 'Medium' }
        ]
      }
    });
    setSortState({ test: { column: 'difficulty', direction: 'asc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('First Medium');
    expect(result[1].name).toBe('Second Medium');
    expect(result[2].name).toBe('Third Medium');
  });

  it('does not mutate the original problem array', () => {
    const original = [
      { name: 'Z', difficulty: 'Hard' },
      { name: 'A', difficulty: 'Easy' }
    ];
    setMockProblemData({ file_list: ['test'], data: { test: original } });
    setSortState({ test: { column: 'difficulty', direction: 'asc' } });
    getSortedProblems('test');
    expect(original[0].name).toBe('Z');
    expect(original[1].name).toBe('A');
  });

  it('returns empty array for unknown fileKey', () => {
    expect(getSortedProblems('nonexistent')).toEqual([]);
  });

  it('sorts by name ascending', () => {
    setSortState({ test: { column: 'name', direction: 'asc' } });
    const result = getSortedProblems('test');
    const names = result.map(p => p.name.toLowerCase());
    const sorted = [...names].sort();
    expect(names).toEqual(sorted);
  });

  it('sorts by name descending', () => {
    setSortState({ test: { column: 'name', direction: 'desc' } });
    const result = getSortedProblems('test');
    const names = result.map(p => p.name.toLowerCase());
    const sorted = [...names].sort().reverse();
    expect(names).toEqual(sorted);
  });

  it('sorts numeric time columns ascending', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'C', time_to_solve: 30 },
          { name: 'A', time_to_solve: 10 },
          { name: 'B', time_to_solve: 20 }
        ]
      }
    });
    setSortState({ test: { column: 'time_to_solve', direction: 'asc' } });
    const result = getSortedProblems('test');
    expect(result.map(p => p.time_to_solve)).toEqual([10, 20, 30]);
  });

  it('puts empty time_to_solve last in ascending sort', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'Empty', time_to_solve: '' },
          { name: 'Fast', time_to_solve: 5 },
          { name: 'Slow', time_to_solve: 60 }
        ]
      }
    });
    setSortState({ test: { column: 'time_to_solve', direction: 'asc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('Fast');
    expect(result[1].name).toBe('Slow');
    expect(result[2].name).toBe('Empty');
  });

  it('sorts solved_date ascending (older first)', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'Recent', solved_date: '2024-06-01' },
          { name: 'Old', solved_date: '2023-01-01' },
          { name: 'Middle', solved_date: '2024-01-15' }
        ]
      }
    });
    setSortState({ test: { column: 'solved_date', direction: 'asc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('Old');
    expect(result[1].name).toBe('Middle');
    expect(result[2].name).toBe('Recent');
  });

  it('puts empty solved_date last in descending sort', () => {
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: [
          { name: 'NoDate', solved_date: '' },
          { name: 'HasDate', solved_date: '2024-01-01' }
        ]
      }
    });
    setSortState({ test: { column: 'solved_date', direction: 'desc' } });
    const result = getSortedProblems('test');
    expect(result[0].name).toBe('HasDate');
    expect(result[1].name).toBe('NoDate');
  });
});

// ── Sort state cycling ────────────────────────────────────────────────────────

describe('cycleSortState', () => {
  it('starts at asc when no previous state', () => {
    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().test).toEqual({ column: 'difficulty', direction: 'asc' });
  });

  it('cycles none→asc→desc→none', () => {
    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().test.direction).toBe('asc');

    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().test.direction).toBe('desc');

    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().test.direction).toBe('none');

    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().test.direction).toBe('asc');
  });

  it('resets to asc when switching to a different column', () => {
    setSortState({ test: { column: 'difficulty', direction: 'desc' } });
    cycleSortState('test', 'name');
    const state = getSortStateSnapshot().test;
    expect(state.column).toBe('name');
    expect(state.direction).toBe('asc');
  });

  it('does not affect other fileKeys', () => {
    setSortState({ other: { column: 'name', direction: 'desc' } });
    cycleSortState('test', 'difficulty');
    expect(getSortStateSnapshot().other).toEqual({ column: 'name', direction: 'desc' });
  });

  it('cycles independently for different fileKeys', () => {
    cycleSortState('list1', 'difficulty');
    cycleSortState('list2', 'name');
    cycleSortState('list1', 'difficulty');

    expect(getSortStateSnapshot().list1.direction).toBe('desc');
    expect(getSortStateSnapshot().list2.direction).toBe('asc');
  });
});

// ── saveSortState / restoreSortState ──────────────────────────────────────────

describe('saveSortState / restoreSortState', () => {
  let ls;

  beforeEach(() => {
    ls = makeLocalStorage();
    setMockLocalStorage(ls);
  });

  it('round-trips sort state through localStorage', () => {
    setSortState({ test: { column: 'difficulty', direction: 'asc' } });
    saveSortState('test');

    resetState();
    setMockLocalStorage(ls);

    const restored = restoreSortState('test');
    expect(restored).toBe(true);
    expect(getSortStateSnapshot().test).toEqual({ column: 'difficulty', direction: 'asc' });
  });

  it('persists correct localStorage key', () => {
    setSortState({ mylist: { column: 'name', direction: 'desc' } });
    saveSortState('mylist');
    expect(ls._store['tracker_sort_mylist']).toBeDefined();
  });

  it('returns false when no key in localStorage', () => {
    const restored = restoreSortState('test');
    expect(restored).toBe(false);
  });

  it('returns false and does not throw when localStorage throws on getItem', () => {
    const badLs = makeLocalStorage(false, true);
    setMockLocalStorage(badLs);
    expect(() => restoreSortState('test')).not.toThrow();
    expect(restoreSortState('test')).toBe(false);
  });

  it('does not throw when no localStorage available', () => {
    setMockLocalStorage(null);
    expect(() => saveSortState('test')).not.toThrow();
    expect(restoreSortState('test')).toBe(false);
  });

  it('restores column and direction correctly for all directions', () => {
    const directions = ['asc', 'desc', 'none'];
    for (const direction of directions) {
      ls = makeLocalStorage();
      setMockLocalStorage(ls);
      setSortState({ test: { column: 'name', direction } });
      saveSortState('test');

      resetState();
      setMockLocalStorage(ls);

      restoreSortState('test');
      expect(getSortStateSnapshot().test.direction).toBe(direction);
    }
  });

  it('ignores malformed JSON in localStorage', () => {
    ls.setItem('tracker_sort_test', 'not-json{{{');
    setMockLocalStorage(ls);
    expect(() => restoreSortState('test')).not.toThrow();
    expect(restoreSortState('test')).toBe(false);
  });

  it('ignores localStorage value with wrong shape', () => {
    ls.setItem('tracker_sort_test', JSON.stringify({ bad: 'shape' }));
    setMockLocalStorage(ls);
    expect(restoreSortState('test')).toBe(false);
  });

  it('does not save state when no state for fileKey', () => {
    saveSortState('test');
    expect(ls._store['tracker_sort_test']).toBeUndefined();
  });
});

// ── initSortHeaders ───────────────────────────────────────────────────────────

describe('initSortHeaders', () => {
  let ls;

  beforeEach(() => {
    ls = makeLocalStorage();
    setMockLocalStorage(ls);
  });

  it('attaches click handlers to all headers', () => {
    const diffHeader = makeHeader('difficulty');
    const nameHeader = makeHeader('name');

    initSortHeaders('test', [diffHeader, nameHeader]);

    diffHeader.element._click();
    expect(getSortStateSnapshot().test).toEqual({ column: 'difficulty', direction: 'asc' });

    diffHeader.element._click();
    expect(getSortStateSnapshot().test).toEqual({ column: 'difficulty', direction: 'desc' });
  });

  it('calls onStateChange callback after click', () => {
    const header = makeHeader('difficulty');
    const calls = [];
    initSortHeaders('test', [header], (fk, col, dir) => calls.push({ fk, col, dir }));

    header.element._click();
    expect(calls).toHaveLength(1);
    expect(calls[0]).toEqual({ fk: 'test', col: 'difficulty', dir: 'asc' });
  });

  it('saves state to localStorage on click', () => {
    const header = makeHeader('name');
    initSortHeaders('test', [header]);

    header.element._click();
    expect(ls._store['tracker_sort_test']).toBeDefined();
    const saved = JSON.parse(ls._store['tracker_sort_test']);
    expect(saved).toEqual({ column: 'name', direction: 'asc' });
  });

  it('works without onStateChange callback', () => {
    const header = makeHeader('difficulty');
    initSortHeaders('test', [header]);
    expect(() => header.element._click()).not.toThrow();
  });

  it('cycles through all three states across three clicks', () => {
    const header = makeHeader('difficulty');
    initSortHeaders('test', [header]);

    header.element._click();
    expect(getSortStateSnapshot().test.direction).toBe('asc');

    header.element._click();
    expect(getSortStateSnapshot().test.direction).toBe('desc');

    header.element._click();
    expect(getSortStateSnapshot().test.direction).toBe('none');
  });
});
