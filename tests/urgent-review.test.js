/**
 * Unit Tests for Most Urgent Review Filter Functions
 */

import {
  calculateDaysUntilFlashing,
  applyUrgentReviewFilter,
  updateUrgentBtnState,
  setMockProblemData,
  resetState,
  setConfig,
  getConfig
} from './urgent-review.js';

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeProblem(overrides = {}) {
  return {
    name: 'Test Problem',
    solved: true,
    difficulty: 'Medium',
    time_to_solve: 30,
    top_time: 15,
    advanced_time: 25,
    intermediate_time: 35,
    ...overrides
  };
}

function dateAgo(days) {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString();
}

function makeRow(index, visible = true) {
  return {
    dataset: { index: String(index) },
    style: { display: visible ? '' : 'none' }
  };
}

function makeBtn(disabled = false) {
  return { disabled };
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe('Most Urgent Review Filter', () => {

  beforeEach(() => {
    resetState();
    setMockProblemData({
      file_list: ['test'],
      data: { test: [] }
    });
  });

  // ── calculateDaysUntilFlashing ─────────────────────────────────────────────

  describe('calculateDaysUntilFlashing', () => {

    it('returns Infinity for unsolved problem', () => {
      const problem = makeProblem({ solved: false, solved_date: dateAgo(5) });
      expect(calculateDaysUntilFlashing(problem)).toBe(Infinity);
    });

    it('returns Infinity for solved problem with no solved_date', () => {
      const problem = makeProblem({ solved: true, solved_date: undefined });
      expect(calculateDaysUntilFlashing(problem)).toBe(Infinity);
    });

    it('returns Infinity for solved problem with invalid solved_date', () => {
      const problem = makeProblem({ solved: true, solved_date: 'not-a-date' });
      expect(calculateDaysUntilFlashing(problem)).toBe(Infinity);
    });

    it('returns 0 for problem already at darkRed threshold', () => {
      const problem = makeProblem({ solved_date: dateAgo(90) });
      expect(calculateDaysUntilFlashing(problem)).toBe(0);
    });

    it('returns 0 for problem past darkRed threshold', () => {
      const problem = makeProblem({ solved_date: dateAgo(180) });
      expect(calculateDaysUntilFlashing(problem)).toBe(0);
    });

    it('returns positive integer for problem approaching darkRed', () => {
      const problem = makeProblem({ solved_date: dateAgo(1) });
      const result = calculateDaysUntilFlashing(problem);
      expect(result).toBeGreaterThan(0);
      expect(Number.isInteger(result)).toBe(true);
    });

    it('returns Infinity for top-tier Easy (multiplier 0, never flashes)', () => {
      const problem = makeProblem({
        solved_date: dateAgo(10),
        difficulty: 'Easy',
        time_to_solve: 10,
        top_time: 15
      });
      expect(calculateDaysUntilFlashing(problem)).toBe(Infinity);
    });

    it('problem solved more recently has more days until flashing', () => {
      const recent = makeProblem({ solved_date: dateAgo(2) });
      const older = makeProblem({ solved_date: dateAgo(20) });
      const daysRecent = calculateDaysUntilFlashing(recent);
      const daysOlder = calculateDaysUntilFlashing(older);
      if (daysOlder === 0) {
        expect(daysRecent).toBeGreaterThanOrEqual(0);
      } else {
        expect(daysRecent).toBeGreaterThan(daysOlder);
      }
    });

    it('below-tier problem flashes sooner than top-Hard-tier (same days elapsed)', () => {
      const date = dateAgo(5);
      const topProblem = makeProblem({
        solved_date: date,
        difficulty: 'Hard',
        time_to_solve: 10,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      });
      const belowProblem = makeProblem({
        solved_date: date,
        difficulty: 'Medium',
        time_to_solve: 40,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      });
      const daysTop = calculateDaysUntilFlashing(topProblem);
      const daysBelow = calculateDaysUntilFlashing(belowProblem);
      expect(daysBelow).toBeLessThan(daysTop);
    });

    it('uses default darkRed threshold of 90', () => {
      expect(getConfig().thresholds.darkRed).toBe(90);
    });

    it('respects custom darkRed threshold — lower threshold means fewer days', () => {
      const problem = makeProblem({ solved_date: dateAgo(1) });
      const defaultDays = calculateDaysUntilFlashing(problem);

      setConfig({
        ...getConfig(),
        thresholds: { ...getConfig().thresholds, darkRed: 50 }
      });
      const customDays = calculateDaysUntilFlashing(problem);

      expect(customDays).toBeLessThan(defaultDays);
    });

  });

  // ── applyUrgentReviewFilter ────────────────────────────────────────────────

  describe('applyUrgentReviewFilter', () => {

    it('returns null and leaves rows unchanged when no solved problems', () => {
      const problems = [
        makeProblem({ solved: false }),
        makeProblem({ solved: false })
      ];
      const rows = [makeRow(0), makeRow(1)];
      const statusEl = { textContent: '' };

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(result).toBeNull();
      expect(rows[0].style.display).toBe('');
      expect(rows[1].style.display).toBe('');
      expect(statusEl.textContent).toBe('');
    });

    it('returns null when all problems are unsolved (no status set)', () => {
      const problems = [makeProblem({ solved: false })];
      const rows = [makeRow(0)];
      const statusEl = { textContent: 'previous' };

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(result).toBeNull();
      expect(statusEl.textContent).toBe('previous');
    });

    it('shows only the problem with minimum daysUntilFlashing', () => {
      const problems = [
        makeProblem({ name: 'P0', solved_date: dateAgo(2) }),
        makeProblem({ name: 'P1', solved_date: dateAgo(20) }),
        makeProblem({ name: 'P2', solved: false })
      ];
      const rows = [makeRow(0), makeRow(1), makeRow(2)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result).not.toBeNull();
      expect(result.urgentIndices.has(1)).toBe(true);
      expect(result.urgentIndices.has(0)).toBe(false);
      expect(rows[1].style.display).toBe('');
      expect(rows[0].style.display).toBe('none');
      expect(rows[2].style.display).toBe('none');
    });

    it('handles ties — shows all problems with same minimum daysUntilFlashing', () => {
      const sameDate = dateAgo(15);
      const problems = [
        makeProblem({ name: 'P0', solved_date: sameDate }),
        makeProblem({ name: 'P1', solved_date: sameDate }),
        makeProblem({ name: 'P2', solved_date: dateAgo(2) })
      ];
      const rows = [makeRow(0), makeRow(1), makeRow(2)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result.urgentIndices.has(0)).toBe(true);
      expect(result.urgentIndices.has(1)).toBe(true);
      expect(result.urgentIndices.has(2)).toBe(false);
      expect(rows[0].style.display).toBe('');
      expect(rows[1].style.display).toBe('');
      expect(rows[2].style.display).toBe('none');
    });

    it('shows already-flashing problems (minDays === 0) as most urgent', () => {
      const problems = [
        makeProblem({ name: 'P0', solved_date: dateAgo(200) }),
        makeProblem({ name: 'P1', solved_date: dateAgo(2) })
      ];
      const rows = [makeRow(0), makeRow(1)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result.minDays).toBe(0);
      expect(result.urgentIndices.has(0)).toBe(true);
      expect(result.urgentIndices.has(1)).toBe(false);
    });

    it('sets status "flashing NOW" when minDays is 0', () => {
      const problems = [makeProblem({ name: 'P0', solved_date: dateAgo(200) })];
      const rows = [makeRow(0)];
      const statusEl = { textContent: '' };

      applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(statusEl.textContent).toBe('1 problem(s) flashing NOW');
    });

    it('sets status with day count when minDays > 0', () => {
      const problems = [makeProblem({ name: 'P0', solved_date: dateAgo(5) })];
      const rows = [makeRow(0)];
      const statusEl = { textContent: '' };

      applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(statusEl.textContent).toMatch(/1 problem\(s\) flashing in \d+ day\(s\)/);
    });

    it('status message includes correct count for multiple urgent problems', () => {
      const sameDate = dateAgo(15);
      const problems = [
        makeProblem({ name: 'P0', solved_date: sameDate }),
        makeProblem({ name: 'P1', solved_date: sameDate })
      ];
      const rows = [makeRow(0), makeRow(1)];
      const statusEl = { textContent: '' };

      applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(statusEl.textContent).toMatch(/^2 problem\(s\)/);
    });

    it('works without statusEl (no crash)', () => {
      const problems = [makeProblem({ solved_date: dateAgo(5) })];
      const rows = [makeRow(0)];

      expect(() => {
        applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
      }).not.toThrow();
    });

    it('returns minDays as a non-negative finite number', () => {
      const problems = [
        makeProblem({ name: 'P0', solved_date: dateAgo(10) }),
        makeProblem({ name: 'P1', solved_date: dateAgo(2) })
      ];
      const rows = [makeRow(0), makeRow(1)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result.minDays).toBeGreaterThanOrEqual(0);
      expect(isFinite(result.minDays)).toBe(true);
    });

    it('returns null for empty problem list', () => {
      const result = applyUrgentReviewFilter('test', { problems: [], rows: [], statusEl: null });
      expect(result).toBeNull();
    });

  });

  // ── updateUrgentBtnState ───────────────────────────────────────────────────

  describe('updateUrgentBtnState', () => {

    it('disables button when no solved problems', () => {
      const problems = [
        makeProblem({ solved: false }),
        makeProblem({ solved: false })
      ];
      const btn = makeBtn(false);

      updateUrgentBtnState('test', { problems, btn });

      expect(btn.disabled).toBe(true);
    });

    it('enables button when at least one solved problem exists', () => {
      const problems = [
        makeProblem({ solved: false }),
        makeProblem({ solved: true })
      ];
      const btn = makeBtn(true);

      updateUrgentBtnState('test', { problems, btn });

      expect(btn.disabled).toBe(false);
    });

    it('enables button when all problems are solved', () => {
      const problems = [
        makeProblem({ solved: true }),
        makeProblem({ solved: true })
      ];
      const btn = makeBtn(true);

      updateUrgentBtnState('test', { problems, btn });

      expect(btn.disabled).toBe(false);
    });

    it('disables button for empty problem list', () => {
      const btn = makeBtn(false);

      updateUrgentBtnState('test', { problems: [], btn });

      expect(btn.disabled).toBe(true);
    });

    it('handles null btn gracefully (no crash)', () => {
      const problems = [makeProblem({ solved: true })];
      expect(() => updateUrgentBtnState('test', { problems, btn: null })).not.toThrow();
    });

  });

  // ── Integration ────────────────────────────────────────────────────────────

  describe('Integration', () => {

    it('full workflow: update button state then filter to most urgent', () => {
      const oldDate = dateAgo(50);
      const newDate = dateAgo(2);
      const problems = [
        makeProblem({ name: 'OldSolved', solved_date: oldDate }),
        makeProblem({ name: 'NewSolved', solved_date: newDate }),
        makeProblem({ name: 'Unsolved', solved: false })
      ];

      setMockProblemData({ file_list: ['test'], data: { test: problems } });

      const btn = makeBtn(true);
      updateUrgentBtnState('test', { problems, btn });
      expect(btn.disabled).toBe(false);

      const rows = [makeRow(0), makeRow(1), makeRow(2)];
      const statusEl = { textContent: '' };
      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(result).not.toBeNull();
      expect(result.urgentIndices.has(0)).toBe(true);
      expect(result.urgentIndices.has(1)).toBe(false);
      expect(result.urgentIndices.has(2)).toBe(false);
      expect(statusEl.textContent).toBeTruthy();
    });

    it('daysUntilFlashing ordering is consistent: recently solved has more days', () => {
      const recentProblem = makeProblem({ solved_date: dateAgo(1) });
      const oldProblem = makeProblem({ solved_date: dateAgo(30) });

      const recentDays = calculateDaysUntilFlashing(recentProblem);
      const oldDays = calculateDaysUntilFlashing(oldProblem);

      if (oldDays > 0) {
        expect(recentDays).toBeGreaterThan(oldDays);
      } else {
        expect(recentDays).toBeGreaterThanOrEqual(0);
      }
    });

    it('filter result urgentIndices is a Set', () => {
      const problems = [makeProblem({ solved_date: dateAgo(10) })];
      const rows = [makeRow(0)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result.urgentIndices).toBeInstanceOf(Set);
    });

  });

});
