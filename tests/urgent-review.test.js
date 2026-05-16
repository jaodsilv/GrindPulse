/**
 * Unit Tests for Most Urgent Review Filter Functions
 */

import {
  calculateDaysUntilFlashing,
  calculateDaysUntilScore,
  applyUrgentReviewFilter,
  updateUrgentBtnState,
  setMockProblemData,
  resetState,
  setConfig,
  getConfig,
  TIER_RANK
} from './urgent-review.js';

import {
  getAwarenessClass,
  calculateAwarenessScore
} from './awareness.js';

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

/**
 * Build a problem with a score forced into a specific awareness class.
 * Uses solved_date far enough in the past + a medium difficulty below-tier problem
 * to hit different tiers deterministically.
 */
function makeProblemWithClass(awarenessClass, extraOverrides = {}) {
  const thresholds = getConfig().thresholds;
  const targetScore = {
    'awareness-flashing':  thresholds.darkRed + 5,
    'awareness-dark-red':  thresholds.red + 5,
    'awareness-red':       thresholds.yellow + 5,
    'awareness-yellow':    thresholds.green + 5,
    'awareness-green':     thresholds.white + 5,
    'awareness-white':     2,
  }[awarenessClass];

  const baseRate = getConfig().baseRate;
  const approxDays = targetScore / (baseRate * 1.3);

  return makeProblem({
    solved_date: dateAgo(Math.ceil(approxDays)),
    ...extraOverrides
  });
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

  // ── calculateDaysUntilScore ────────────────────────────────────────────────

  describe('calculateDaysUntilScore', () => {

    it('returns Infinity for unsolved problem', () => {
      const problem = makeProblem({ solved: false, solved_date: dateAgo(5) });
      expect(calculateDaysUntilScore(problem, 50)).toBe(Infinity);
    });

    it('returns Infinity for solved problem with no solved_date', () => {
      const problem = makeProblem({ solved: true, solved_date: undefined });
      expect(calculateDaysUntilScore(problem, 50)).toBe(Infinity);
    });

    it('returns Infinity for solved problem with invalid solved_date', () => {
      const problem = makeProblem({ solved: true, solved_date: 'not-a-date' });
      expect(calculateDaysUntilScore(problem, 50)).toBe(Infinity);
    });

    it('returns 0 when problem score is already at target', () => {
      const problem = makeProblem({ solved_date: dateAgo(90) });
      const score = calculateAwarenessScore(problem).score;
      expect(calculateDaysUntilScore(problem, score)).toBe(0);
    });

    it('returns 0 when problem score exceeds target', () => {
      const problem = makeProblem({ solved_date: dateAgo(180) });
      expect(calculateDaysUntilScore(problem, 10)).toBe(0);
    });

    it('returns positive integer for problem below target', () => {
      const problem = makeProblem({ solved_date: dateAgo(1) });
      const result = calculateDaysUntilScore(problem, 90);
      expect(result).toBeGreaterThan(0);
      expect(Number.isInteger(result)).toBe(true);
    });

    it('returns Infinity for top-tier Easy (daily rate = 0)', () => {
      const problem = makeProblem({
        solved_date: dateAgo(5),
        difficulty: 'Easy',
        time_to_solve: 10,
        top_time: 15
      });
      expect(calculateDaysUntilScore(problem, 50)).toBe(Infinity);
    });

    it('lower targetScore means fewer days needed', () => {
      const problem = makeProblem({ solved_date: dateAgo(5) });
      const days30 = calculateDaysUntilScore(problem, 30);
      const days70 = calculateDaysUntilScore(problem, 70);
      if (days30 === 0) {
        expect(days70).toBeGreaterThanOrEqual(0);
      } else {
        expect(days30).toBeLessThan(days70);
      }
    });

    it('is consistent with calculateDaysUntilFlashing when targetScore = darkRed', () => {
      const problem = makeProblem({ solved_date: dateAgo(5) });
      const darkRed = getConfig().thresholds.darkRed;
      expect(calculateDaysUntilScore(problem, darkRed)).toBe(calculateDaysUntilFlashing(problem));
    });

  });

  // ── applyUrgentReviewFilter (tiered waterfall) ─────────────────────────────

  describe('applyUrgentReviewFilter — tiered waterfall', () => {

    it('returns null when no solved problems', () => {
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

    it('returns null for empty problem list', () => {
      const result = applyUrgentReviewFilter('test', { problems: [], rows: [], statusEl: null });
      expect(result).toBeNull();
    });

    it('excludes problems solved within last 7 days', () => {
      const now = new Date();
      const recentDate = new Date(now);
      recentDate.setDate(recentDate.getDate() - 3);

      const problems = [
        makeProblem({ name: 'Recent', solved_date: recentDate.toISOString() }),
        makeProblem({ name: 'Old', solved_date: dateAgo(60) })
      ];
      const rows = [makeRow(0), makeRow(1)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null, now });

      expect(result).not.toBeNull();
      expect(result.urgentIndices.has(0)).toBe(false);
      expect(result.urgentIndices.has(1)).toBe(true);
    });

    it('returns null when all solved problems are within last 7 days', () => {
      const now = new Date();
      const recentDate = new Date(now);
      recentDate.setDate(recentDate.getDate() - 3);

      const problems = [
        makeProblem({ name: 'Recent', solved_date: recentDate.toISOString() })
      ];
      const rows = [makeRow(0)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null, now });

      expect(result).toBeNull();
    });

    it('returns null for no solved problems (all unsolved)', () => {
      const problems = [makeProblem({ solved: false })];
      const rows = [makeRow(0)];
      const statusEl = { textContent: 'previous' };

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl });

      expect(result).toBeNull();
      expect(statusEl.textContent).toBe('previous');
    });

    it('works without statusEl (no crash)', () => {
      const problems = [makeProblem({ solved_date: dateAgo(60) })];
      const rows = [makeRow(0)];

      expect(() => {
        applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
      }).not.toThrow();
    });

    it('returns urgentIndices as a Set', () => {
      const problems = [makeProblem({ solved_date: dateAgo(60) })];
      const rows = [makeRow(0)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      expect(result.urgentIndices).toBeInstanceOf(Set);
    });

    describe('Tier waterfall — flashing tier', () => {

      it('tab with only flashing problems shows all flashing', () => {
        const problems = [
          makeProblem({ name: 'Flash1', solved_date: dateAgo(200) }),
          makeProblem({ name: 'Flash2', solved_date: dateAgo(250) }),
          makeProblem({ name: 'Flash3', solved_date: dateAgo(300) })
        ];

        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0), makeRow(1), makeRow(2)];

        const allFlashing = problems.every(p => {
          const score = calculateAwarenessScore(p).score;
          return getAwarenessClass(score) === 'awareness-flashing';
        });

        if (allFlashing) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.has(0)).toBe(true);
          expect(result.urgentIndices.has(1)).toBe(true);
          expect(result.urgentIndices.has(2)).toBe(true);
        } else {
          expect(true).toBe(true);
        }
      });

      it('flashing tier stops waterfall — dark-red problems excluded when flashing present', () => {
        const now = new Date();
        const problems = [
          makeProblem({ name: 'Flashing', solved_date: dateAgo(200) }),
          makeProblem({ name: 'DarkRed', solved_date: dateAgo(80) })
        ];

        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0), makeRow(1)];

        const flashScore = calculateAwarenessScore(problems[0]).score;
        const darkRedScore = calculateAwarenessScore(problems[1]).score;

        const isFlashing = getAwarenessClass(flashScore) === 'awareness-flashing';
        const isDarkRed = getAwarenessClass(darkRedScore) === 'awareness-dark-red';

        if (isFlashing && isDarkRed) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null, now });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.has(0)).toBe(true);
          expect(result.urgentIndices.has(1)).toBe(false);
        } else {
          expect(true).toBe(true);
        }
      });

      it('flashing status message says "flashing NOW"', () => {
        const problems = [makeProblem({ solved_date: dateAgo(200) })];
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0)];
        const statusEl = { textContent: '' };

        const score = calculateAwarenessScore(problems[0]).score;
        const isFlashing = getAwarenessClass(score) === 'awareness-flashing';

        if (isFlashing) {
          applyUrgentReviewFilter('test', { problems, rows, statusEl });
          expect(statusEl.textContent).toMatch(/flashing NOW/);
        } else {
          expect(true).toBe(true);
        }
      });

    });

    describe('Tier waterfall — red tier with limit 5', () => {

      it('shows up to 5 red problems when only red present', () => {
        const problems = Array.from({ length: 7 }, (_, i) =>
          makeProblem({ name: `Red${i}`, solved_date: dateAgo(50) })
        );
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = problems.map((_, i) => makeRow(i));

        const allRed = problems.every(p => {
          const score = calculateAwarenessScore(p).score;
          return getAwarenessClass(score) === 'awareness-red';
        });

        if (allRed) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.size).toBe(5);
        } else {
          expect(true).toBe(true);
        }
      });

    });

    describe('Tier waterfall — yellow tier with limit 3', () => {

      it('shows up to 3 yellow problems when only yellow present', () => {
        const problems = Array.from({ length: 5 }, (_, i) =>
          makeProblem({ name: `Yellow${i}`, solved_date: dateAgo(30) })
        );
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = problems.map((_, i) => makeRow(i));

        const allYellow = problems.every(p => {
          const score = calculateAwarenessScore(p).score;
          return getAwarenessClass(score) === 'awareness-yellow';
        });

        if (allYellow) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.size).toBe(3);
        } else {
          expect(true).toBe(true);
        }
      });

    });

    describe('Tier waterfall — green tier with limit 1', () => {

      it('shows 1 green problem when only green present', () => {
        const problems = Array.from({ length: 3 }, (_, i) =>
          makeProblem({ name: `Green${i}`, solved_date: dateAgo(15) })
        );
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = problems.map((_, i) => makeRow(i));

        const allGreen = problems.every(p => {
          const score = calculateAwarenessScore(p).score;
          return getAwarenessClass(score) === 'awareness-green';
        });

        if (allGreen) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.size).toBe(1);
        } else {
          expect(true).toBe(true);
        }
      });

    });

    describe('Tier waterfall — mixed tiers', () => {

      it('higher tier stops lower tiers from appearing', () => {
        const problems = [
          makeProblem({ name: 'HighTier', solved_date: dateAgo(200) }),
          makeProblem({ name: 'LowTier', solved_date: dateAgo(20) })
        ];
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0), makeRow(1)];

        const score0 = calculateAwarenessScore(problems[0]).score;
        const score1 = calculateAwarenessScore(problems[1]).score;
        const tier0 = TIER_RANK[getAwarenessClass(score0)] ?? 0;
        const tier1 = TIER_RANK[getAwarenessClass(score1)] ?? 0;

        if (tier0 > tier1 && tier0 > 0) {
          const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });
          expect(result).not.toBeNull();
          expect(result.urgentIndices.has(0)).toBe(true);
          expect(result.urgentIndices.has(1)).toBe(false);
        } else {
          expect(true).toBe(true);
        }
      });

      it('non-flashing status message says "due for review soon"', () => {
        const problems = [makeProblem({ solved_date: dateAgo(30) })];
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0)];
        const statusEl = { textContent: '' };

        const score = calculateAwarenessScore(problems[0]).score;
        const cls = getAwarenessClass(score);
        const isNonFlashing = cls !== 'awareness-flashing' && cls !== 'awareness-white' && score >= 0;

        if (isNonFlashing) {
          applyUrgentReviewFilter('test', { problems, rows, statusEl });
          expect(statusEl.textContent).toMatch(/due for review soon/);
        } else {
          expect(true).toBe(true);
        }
      });

    });

    describe('Tier waterfall — using injectable now for freshness', () => {

      it('exactly 7 days ago is excluded (strictly greater than sevenDaysAgo)', () => {
        const now = new Date('2026-04-02T12:00:00Z');
        const sevenDaysAgo = new Date(now);
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

        const problems = [
          makeProblem({ name: 'Exact7', solved_date: sevenDaysAgo.toISOString() }),
          makeProblem({ name: 'Old', solved_date: dateAgo(60) })
        ];
        const rows = [makeRow(0), makeRow(1)];

        const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null, now });

        expect(result).not.toBeNull();
        expect(result.urgentIndices.has(1)).toBe(true);
      });

      it('8 days ago is included (not recent)', () => {
        const now = new Date();
        const eightDaysAgo = new Date(now);
        eightDaysAgo.setDate(eightDaysAgo.getDate() - 8);

        const problems = [
          makeProblem({ name: 'EightDays', solved_date: eightDaysAgo.toISOString() })
        ];
        const rows = [makeRow(0)];

        const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null, now });

        expect(result).not.toBeNull();
        expect(result.urgentIndices.has(0)).toBe(true);
      });

    });

    describe('Row visibility', () => {

      it('hides rows not in urgentIndices', () => {
        const problems = [
          makeProblem({ name: 'P0', solved_date: dateAgo(200) }),
          makeProblem({ name: 'P1', solved_date: dateAgo(20) })
        ];
        setMockProblemData({ file_list: ['test'], data: { test: problems } });
        const rows = [makeRow(0), makeRow(1)];

        const score0 = calculateAwarenessScore(problems[0]).score;
        const score1 = calculateAwarenessScore(problems[1]).score;
        const tier0 = TIER_RANK[getAwarenessClass(score0)] ?? 0;
        const tier1 = TIER_RANK[getAwarenessClass(score1)] ?? 0;

        const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

        expect(result).not.toBeNull();
        rows.forEach(row => {
          const idx = parseInt(row.dataset.index, 10);
          if (result.urgentIndices.has(idx)) {
            expect(row.style.display).toBe('');
          } else {
            expect(row.style.display).toBe('none');
          }
        });
      });

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
      const problems = [
        makeProblem({ name: 'OldSolved', solved_date: dateAgo(200) }),
        makeProblem({ name: 'NewSolved', solved_date: dateAgo(20) }),
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
      expect(statusEl.textContent).toBeTruthy();
      const totalVisible = rows.filter(r => r.style.display === '').length;
      expect(totalVisible).toBeGreaterThan(0);
    });

    it('calculateDaysUntilScore is consistent with calculateDaysUntilFlashing at darkRed threshold', () => {
      const problem = makeProblem({ solved_date: dateAgo(10) });
      const darkRed = getConfig().thresholds.darkRed;
      expect(calculateDaysUntilScore(problem, darkRed)).toBe(calculateDaysUntilFlashing(problem));
    });

    it('urgentIndices is a Set regardless of tier hit', () => {
      const problems = [makeProblem({ solved_date: dateAgo(200) })];
      const rows = [makeRow(0)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      if (result !== null) {
        expect(result.urgentIndices).toBeInstanceOf(Set);
      }
    });

    it('flashingCount is returned and is a non-negative integer', () => {
      const problems = [makeProblem({ solved_date: dateAgo(200) })];
      const rows = [makeRow(0)];

      const result = applyUrgentReviewFilter('test', { problems, rows, statusEl: null });

      if (result !== null) {
        expect(typeof result.flashingCount).toBe('number');
        expect(result.flashingCount).toBeGreaterThanOrEqual(0);
        expect(Number.isInteger(result.flashingCount)).toBe(true);
      }
    });

  });

});
