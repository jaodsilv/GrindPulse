/**
 * Unit Tests for Random Problem Selector Functions
 */

import {
  getVisibleRowIndices,
  pickRandomIndex,
  shouldEnableRandomBtn,
  applyHighlight,
  pickRandomProblemLogic
} from './random-selector.js';

function makeScrollSpy() {
  let called = false;
  let lastArgs = null;
  const fn = (...args) => { called = true; lastArgs = args[0]; };
  fn.wasCalled = () => called;
  fn.lastArgs = () => lastArgs;
  fn.mockClear = () => { called = false; lastArgs = null; };
  return fn;
}

function makeRow(index, visible = true) {
  const classList = new Set();
  const scrollIntoView = makeScrollSpy();
  return {
    dataset: { index: String(index) },
    style: { display: visible ? '' : 'none' },
    classList: {
      add: (cls) => classList.add(cls),
      remove: (cls) => classList.delete(cls),
      has: (cls) => classList.has(cls),
      _set: classList
    },
    scrollIntoView
  };
}

function makeRows(specs) {
  return specs.map(({ index, visible }) => makeRow(index, visible));
}

describe('Random Problem Selector', () => {

  describe('getVisibleRowIndices', () => {
    it('returns all indices when all rows are visible', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true },
        { index: 2, visible: true }
      ]);
      expect(getVisibleRowIndices(rows)).toEqual([0, 1, 2]);
    });

    it('returns only visible row indices', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: false },
        { index: 2, visible: true }
      ]);
      expect(getVisibleRowIndices(rows)).toEqual([0, 2]);
    });

    it('returns empty array when all rows are hidden', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: false }
      ]);
      expect(getVisibleRowIndices(rows)).toEqual([]);
    });

    it('returns empty array for empty rows list', () => {
      expect(getVisibleRowIndices([])).toEqual([]);
    });

    it('treats display="" (empty string) as visible', () => {
      const row = makeRow(3, true);
      row.style.display = '';
      expect(getVisibleRowIndices([row])).toEqual([3]);
    });

    it('treats display="none" as hidden', () => {
      const row = makeRow(5, false);
      expect(getVisibleRowIndices([row])).toEqual([]);
    });

    it('parses string indices to integers', () => {
      const row = makeRow(7, true);
      const result = getVisibleRowIndices([row]);
      expect(typeof result[0]).toBe('number');
      expect(result[0]).toBe(7);
    });
  });

  describe('pickRandomIndex', () => {
    it('returns -1 for empty array', () => {
      expect(pickRandomIndex([])).toBe(-1);
    });

    it('returns -1 for null input', () => {
      expect(pickRandomIndex(null)).toBe(-1);
    });

    it('returns -1 for undefined input', () => {
      expect(pickRandomIndex(undefined)).toBe(-1);
    });

    it('returns the single element for single-element array', () => {
      expect(pickRandomIndex([42])).toBe(42);
    });

    it('returns a value from the provided array', () => {
      const indices = [0, 3, 7, 12];
      const result = pickRandomIndex(indices);
      expect(indices).toContain(result);
    });

    it('uses the provided RNG function', () => {
      const indices = [10, 20, 30];
      // Math.floor(rng * 3): 0.0->0, 0.33->0 (0.33*3=0.99->0), 0.34->1 (0.34*3=1.02->1), 0.66->1, 0.67->2 (0.67*3=2.01->2), 0.99->2
      expect(pickRandomIndex(indices, () => 0.0)).toBe(10);
      expect(pickRandomIndex(indices, () => 0.33)).toBe(10);
      expect(pickRandomIndex(indices, () => 0.34)).toBe(20);
      expect(pickRandomIndex(indices, () => 0.66)).toBe(20);
      expect(pickRandomIndex(indices, () => 0.99)).toBe(30);
    });

    it('never returns out-of-bounds index', () => {
      const indices = [5, 10, 15, 20, 25];
      for (let i = 0; i < 100; i++) {
        const result = pickRandomIndex(indices);
        expect(indices).toContain(result);
      }
    });

    it('is uniformly distributed (statistical test)', () => {
      const indices = [0, 1, 2, 3, 4];
      const counts = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0 };
      const N = 5000;

      for (let i = 0; i < N; i++) {
        const result = pickRandomIndex(indices);
        counts[result]++;
      }

      const expected = N / indices.length;
      const tolerance = expected * 0.15;

      for (const idx of indices) {
        expect(counts[idx]).toBeGreaterThan(expected - tolerance);
        expect(counts[idx]).toBeLessThan(expected + tolerance);
      }
    });
  });

  describe('shouldEnableRandomBtn', () => {
    it('returns false when visible count is 0', () => {
      expect(shouldEnableRandomBtn(0)).toBe(false);
    });

    it('returns true when visible count is 1', () => {
      expect(shouldEnableRandomBtn(1)).toBe(true);
    });

    it('returns true when visible count is greater than 1', () => {
      expect(shouldEnableRandomBtn(10)).toBe(true);
      expect(shouldEnableRandomBtn(100)).toBe(true);
    });
  });

  describe('applyHighlight', () => {
    it('adds highlight class to the selected row', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true },
        { index: 2, visible: true }
      ]);
      applyHighlight(rows, 1);
      expect(rows[1].classList.has('random-highlight')).toBe(true);
    });

    it('removes highlight class from all other rows', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true },
        { index: 2, visible: true }
      ]);
      rows[0].classList.add('random-highlight');
      rows[2].classList.add('random-highlight');

      applyHighlight(rows, 1);

      expect(rows[0].classList.has('random-highlight')).toBe(false);
      expect(rows[2].classList.has('random-highlight')).toBe(false);
    });

    it('returns { highlighted, cleared } describing changes', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true },
        { index: 2, visible: true }
      ]);
      const result = applyHighlight(rows, 1);
      expect(result.highlighted).toBe(1);
      expect(result.cleared).toEqual([0, 2]);
    });

    it('returns highlighted: null when no row matches selectedIndex', () => {
      const rows = makeRows([{ index: 0, visible: true }]);
      const result = applyHighlight(rows, 99);
      expect(result.highlighted).toBeNull();
    });

    it('handles empty rows list without error', () => {
      expect(() => applyHighlight([], 0)).not.toThrow();
    });
  });

  describe('pickRandomProblemLogic', () => {
    it('returns selectedIndex=-1 when all rows are hidden', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: false }
      ]);
      const result = pickRandomProblemLogic(rows);
      expect(result.selectedIndex).toBe(-1);
      expect(result.visibleCount).toBe(0);
    });

    it('returns selectedIndex=-1 for empty rows list', () => {
      const result = pickRandomProblemLogic([]);
      expect(result.selectedIndex).toBe(-1);
      expect(result.visibleCount).toBe(0);
    });

    it('returns a valid visible row index', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: false },
        { index: 2, visible: true }
      ]);
      const result = pickRandomProblemLogic(rows);
      expect([0, 2]).toContain(result.selectedIndex);
      expect(result.visibleCount).toBe(2);
    });

    it('highlights the selected row', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true }
      ]);
      const { selectedIndex } = pickRandomProblemLogic(rows, () => 0.0);
      const selectedRow = rows.find(r => parseInt(r.dataset.index, 10) === selectedIndex);
      expect(selectedRow.classList.has('random-highlight')).toBe(true);
    });

    it('calls scrollIntoView on the selected row', () => {
      const rows = makeRows([
        { index: 0, visible: true }
      ]);
      pickRandomProblemLogic(rows, () => 0.0);
      expect(rows[0].scrollIntoView.wasCalled()).toBe(true);
      expect(rows[0].scrollIntoView.lastArgs()).toEqual({ behavior: 'smooth', block: 'center' });
    });

    it('does not call scrollIntoView when no rows are visible', () => {
      const rows = makeRows([{ index: 0, visible: false }]);
      pickRandomProblemLogic(rows);
      expect(rows[0].scrollIntoView.wasCalled()).toBe(false);
    });

    it('does not highlight any row when no rows are visible', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: false }
      ]);
      pickRandomProblemLogic(rows);
      for (const row of rows) {
        expect(row.classList.has('random-highlight')).toBe(false);
      }
    });

    it('reports correct visibleCount', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: false },
        { index: 2, visible: true },
        { index: 3, visible: true }
      ]);
      const { visibleCount } = pickRandomProblemLogic(rows);
      expect(visibleCount).toBe(3);
    });

    it('only selects from visible rows across multiple calls', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: true },
        { index: 2, visible: false },
        { index: 3, visible: true }
      ]);

      for (let i = 0; i < 50; i++) {
        const { selectedIndex } = pickRandomProblemLogic(rows);
        expect([1, 3]).toContain(selectedIndex);
      }
    });

    it('uses injected RNG for deterministic selection', () => {
      const rows = makeRows([
        { index: 10, visible: true },
        { index: 20, visible: true },
        { index: 30, visible: true }
      ]);
      const { selectedIndex } = pickRandomProblemLogic(rows, () => 0.99);
      expect(selectedIndex).toBe(30);
    });

    it('handles single visible row correctly', () => {
      const rows = makeRows([{ index: 5, visible: true }]);
      const result = pickRandomProblemLogic(rows);
      expect(result.selectedIndex).toBe(5);
      expect(result.visibleCount).toBe(1);
    });
  });

  describe('Integration: filter-aware random selection', () => {
    it('respects filter state — only picks visible rows', () => {
      const rows = makeRows([
        { index: 0, visible: true },
        { index: 1, visible: true },
        { index: 2, visible: false },
        { index: 3, visible: false },
        { index: 4, visible: true }
      ]);

      const selected = new Set();
      for (let i = 0; i < 100; i++) {
        const { selectedIndex } = pickRandomProblemLogic(rows);
        selected.add(selectedIndex);
      }

      expect(selected.has(2)).toBe(false);
      expect(selected.has(3)).toBe(false);
      expect(selected.size).toBeGreaterThan(0);
    });

    it('button should be disabled when no visible rows', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: false }
      ]);
      const visible = getVisibleRowIndices(rows);
      expect(shouldEnableRandomBtn(visible.length)).toBe(false);
    });

    it('button should be enabled when at least one row is visible', () => {
      const rows = makeRows([
        { index: 0, visible: false },
        { index: 1, visible: true }
      ]);
      const visible = getVisibleRowIndices(rows);
      expect(shouldEnableRandomBtn(visible.length)).toBe(true);
    });
  });
});
