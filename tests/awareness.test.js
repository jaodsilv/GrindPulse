/**
 * Unit Tests for Awareness Indicator Functions
 */

import {
  DEFAULT_AWARENESS_CONFIG,
  calculateAwarenessScore,
  getTierDifficultyMultiplier,
  getTierName,
  getDaysSinceCompletion,
  getCommitmentFactor,
  getSolvedFactor,
  getTotalUniqueSolvedCount,
  normalizeDateToISO,
  getAwarenessClass,
  validateThresholdOrdering,
  setMockProblemData,
  resetConfig,
  setConfig,
  getConfig
} from './awareness.js';

describe('Awareness Indicator System', () => {

  beforeEach(() => {
    // Reset to default config before each test
    resetConfig();

    // Reset mock problem data
    setMockProblemData({
      file_list: ['test'],
      data: {
        test: []
      }
    });
  });

  describe('getTierName', () => {
    it('should return "below" for missing time_to_solve', () => {
      const problem = {};
      expect(getTierName(problem)).toBe('below');
    });

    it('should return "below" for zero time_to_solve', () => {
      const problem = { time_to_solve: 0 };
      expect(getTierName(problem)).toBe('below');
    });

    it('should return "below" for negative time_to_solve', () => {
      const problem = { time_to_solve: -5 };
      expect(getTierName(problem)).toBe('below');
    });

    it('should return "top" when time_to_solve <= top_time', () => {
      const problem = {
        time_to_solve: 10,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };
      expect(getTierName(problem)).toBe('top');
    });

    it('should return "advanced" when time_to_solve <= advanced_time', () => {
      const problem = {
        time_to_solve: 20,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };
      expect(getTierName(problem)).toBe('advanced');
    });

    it('should return "intermediate" when time_to_solve <= intermediate_time', () => {
      const problem = {
        time_to_solve: 30,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };
      expect(getTierName(problem)).toBe('intermediate');
    });

    it('should return "below" when time_to_solve > intermediate_time', () => {
      const problem = {
        time_to_solve: 40,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };
      expect(getTierName(problem)).toBe('below');
    });

    it('should handle missing tier times gracefully', () => {
      const problem = { time_to_solve: 10 };
      expect(getTierName(problem)).toBe('top');
    });

    it('should handle string time values', () => {
      const problem = {
        time_to_solve: '20',
        top_time: '15',
        advanced_time: '25',
        intermediate_time: '35'
      };
      expect(getTierName(problem)).toBe('advanced');
    });
  });

  describe('getTierDifficultyMultiplier', () => {
    describe('Top tier', () => {
      const topProblem = {
        time_to_solve: 10,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };

      it('should return 0 for Easy (mastered)', () => {
        expect(getTierDifficultyMultiplier({ ...topProblem, difficulty: 'Easy' })).toBe(0);
      });

      it('should return 0.25 for Medium (deep mastery)', () => {
        expect(getTierDifficultyMultiplier({ ...topProblem, difficulty: 'Medium' })).toBe(0.25);
      });

      it('should return 0.4 for Hard', () => {
        expect(getTierDifficultyMultiplier({ ...topProblem, difficulty: 'Hard' })).toBe(0.4);
      });

      it('should default to Medium when difficulty is missing', () => {
        expect(getTierDifficultyMultiplier(topProblem)).toBe(0.25);
      });
    });

    describe('Advanced tier', () => {
      const advancedProblem = {
        time_to_solve: 20,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };

      it('should return 1.2 for Easy', () => {
        expect(getTierDifficultyMultiplier({ ...advancedProblem, difficulty: 'Easy' })).toBe(1.2);
      });

      it('should return 0.9 for Medium', () => {
        expect(getTierDifficultyMultiplier({ ...advancedProblem, difficulty: 'Medium' })).toBe(0.9);
      });

      it('should return 0.7 for Hard', () => {
        expect(getTierDifficultyMultiplier({ ...advancedProblem, difficulty: 'Hard' })).toBe(0.7);
      });
    });

    describe('Intermediate tier', () => {
      const intermediateProblem = {
        time_to_solve: 30,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };

      it('should return 1.5 for Easy', () => {
        expect(getTierDifficultyMultiplier({ ...intermediateProblem, difficulty: 'Easy' })).toBe(1.5);
      });

      it('should return 1.0 for Medium (baseline)', () => {
        expect(getTierDifficultyMultiplier({ ...intermediateProblem, difficulty: 'Medium' })).toBe(1.0);
      });

      it('should return 0.75 for Hard', () => {
        expect(getTierDifficultyMultiplier({ ...intermediateProblem, difficulty: 'Hard' })).toBe(0.75);
      });
    });

    describe('Below tier', () => {
      const belowProblem = {
        time_to_solve: 40,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35
      };

      it('should return 1.8 for Easy', () => {
        expect(getTierDifficultyMultiplier({ ...belowProblem, difficulty: 'Easy' })).toBe(1.8);
      });

      it('should return 1.3 for Medium', () => {
        expect(getTierDifficultyMultiplier({ ...belowProblem, difficulty: 'Medium' })).toBe(1.3);
      });

      it('should return 1.0 for Hard', () => {
        expect(getTierDifficultyMultiplier({ ...belowProblem, difficulty: 'Hard' })).toBe(1.0);
      });
    });

    describe('Edge cases', () => {
      it('should return 1.0 for invalid tier', () => {
        // Mock config with missing tier
        setConfig({
          ...getConfig(),
          tierDifficultyMultipliers: {}
        });

        const problem = { time_to_solve: 10 };
        expect(getTierDifficultyMultiplier(problem)).toBe(1.0);
      });

      it('should return 1.0 for invalid difficulty in valid tier', () => {
        const problem = {
          time_to_solve: 10,
          top_time: 15,
          difficulty: 'VeryHard' // Invalid difficulty
        };
        expect(getTierDifficultyMultiplier(problem)).toBe(1.0);
      });
    });
  });

  describe('getDaysSinceCompletion', () => {
    it('should return { days: -1, valid: true } for no date', () => {
      expect(getDaysSinceCompletion(null)).toEqual({ days: -1, valid: true });
      expect(getDaysSinceCompletion(undefined)).toEqual({ days: -1, valid: true });
      expect(getDaysSinceCompletion('')).toEqual({ days: -1, valid: true });
    });

    it('should return { days: -1, valid: false } for invalid date', () => {
      const result = getDaysSinceCompletion('invalid-date');
      expect(result.valid).toBe(false);
      expect(result.days).toBe(-1);
    });

    it('should return { days: 0, valid: true } for future dates', () => {
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 10);

      const result = getDaysSinceCompletion(futureDate.toISOString());
      expect(result.valid).toBe(true);
      expect(result.days).toBe(0);
    });

    it('should calculate correct days for past dates', () => {
      const pastDate = new Date();
      pastDate.setDate(pastDate.getDate() - 10);

      const result = getDaysSinceCompletion(pastDate.toISOString());
      expect(result.valid).toBe(true);
      expect(result.days).toBeGreaterThanOrEqual(9.9); // Account for timing
      expect(result.days).toBeLessThan(10.1);
    });

    it('should handle ISO date strings', () => {
      const date = '2024-01-01T00:00:00.000Z';
      const result = getDaysSinceCompletion(date);
      expect(result.valid).toBe(true);
      expect(result.days).toBeGreaterThan(0);
    });

    it('should handle various date formats', () => {
      const formats = [
        '2024-01-01',
        'Jan 1, 2024',
        '01/01/2024'
      ];

      formats.forEach(format => {
        const result = getDaysSinceCompletion(format);
        expect(result.valid).toBe(true);
        expect(result.days).toBeGreaterThan(0);
      });
    });
  });

  describe('normalizeDateToISO', () => {
    it('should return null for null/undefined/empty input', () => {
      expect(normalizeDateToISO(null)).toBeNull();
      expect(normalizeDateToISO(undefined)).toBeNull();
      expect(normalizeDateToISO('')).toBeNull();
    });

    it('should return null for invalid date string', () => {
      expect(normalizeDateToISO('not-a-date')).toBeNull();
      expect(normalizeDateToISO('abc123')).toBeNull();
    });

    it('should convert valid date string to ISO format', () => {
      const result = normalizeDateToISO('2024-01-01');
      expect(result).toBeTruthy();
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });

    it('should handle Date objects', () => {
      const date = new Date('2024-01-01');
      const result = normalizeDateToISO(date);
      expect(result).toBeTruthy();
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });

    it('should handle various valid date formats', () => {
      const formats = [
        '2024-01-15',
        'Jan 15, 2024',
        '01/15/2024',
        new Date('2024-01-15')
      ];

      formats.forEach(format => {
        const result = normalizeDateToISO(format);
        expect(result).toBeTruthy();
        expect(typeof result).toBe('string');
      });
    });
  });

  describe('getTotalUniqueSolvedCount', () => {
    it('should return 0 for no solved problems', () => {
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: [
            { name: 'Problem 1', solved: false },
            { name: 'Problem 2', solved: false }
          ]
        }
      });

      expect(getTotalUniqueSolvedCount()).toBe(0);
    });

    it('should count unique solved problems', () => {
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: [
            { name: 'Problem 1', solved: true },
            { name: 'Problem 2', solved: true },
            { name: 'Problem 3', solved: false }
          ]
        }
      });

      expect(getTotalUniqueSolvedCount()).toBe(2);
    });

    it('should count duplicates only once across lists', () => {
      setMockProblemData({
        file_list: ['list1', 'list2'],
        data: {
          list1: [
            { name: 'Two Sum', solved: true },
            { name: 'Valid Parentheses', solved: true }
          ],
          list2: [
            { name: 'Two Sum', solved: true }, // Duplicate
            { name: 'Merge Intervals', solved: true }
          ]
        }
      });

      expect(getTotalUniqueSolvedCount()).toBe(3); // Two Sum, Valid Parentheses, Merge Intervals
    });

    it('should handle empty problem lists', () => {
      setMockProblemData({
        file_list: [],
        data: {}
      });

      expect(getTotalUniqueSolvedCount()).toBe(0);
    });
  });

  describe('getCommitmentFactor', () => {
    it('should return 1.0 for default commitment (2 problems/day)', () => {
      expect(getCommitmentFactor()).toBe(1.0);
    });

    it('should return 0.5 for 1 problem/day', () => {
      setConfig({
        ...getConfig(),
        commitment: { problemsPerDay: 1 }
      });
      expect(getCommitmentFactor()).toBe(0.5);
    });

    it('should return 2.0 for 4 problems/day', () => {
      setConfig({
        ...getConfig(),
        commitment: { problemsPerDay: 4 }
      });
      expect(getCommitmentFactor()).toBe(2.0);
    });

    it('should return 5.0 for 10 problems/day', () => {
      setConfig({
        ...getConfig(),
        commitment: { problemsPerDay: 10 }
      });
      expect(getCommitmentFactor()).toBe(5.0);
    });
  });

  describe('getSolvedFactor', () => {
    it('should return 1.0 when no problems solved (log2(1) = 0)', () => {
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: []
        }
      });

      const problem = { time_to_solve: 10, top_time: 15 };
      expect(getSolvedFactor(problem)).toBe(1.0);
    });

    it('should increase with more solved problems', () => {
      const problem = { time_to_solve: 10, top_time: 15 }; // top tier

      // 0 solved
      setMockProblemData({
        file_list: ['list1'],
        data: { list1: [] }
      });
      const factor0 = getSolvedFactor(problem);

      // 10 solved
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: Array(10).fill(null).map((_, i) => ({
            name: `Problem ${i}`,
            solved: true
          }))
        }
      });
      const factor10 = getSolvedFactor(problem);

      expect(factor10).toBeGreaterThan(factor0);
    });

    it('should give higher bonus to top tier problems', () => {
      // Setup with 10 solved problems
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: Array(10).fill(null).map((_, i) => ({
            name: `Problem ${i}`,
            solved: true
          }))
        }
      });

      const topProblem = { time_to_solve: 10, top_time: 15 };
      const belowProblem = { time_to_solve: 100 }; // No tier times = below

      const topFactor = getSolvedFactor(topProblem);
      const belowFactor = getSolvedFactor(belowProblem);

      expect(topFactor).toBeGreaterThan(belowFactor);
    });

    it('should use logarithmic scaling (diminishing returns)', () => {
      const problem = { time_to_solve: 10, top_time: 15 };

      // Calculate factors for different solved counts
      const factors = [0, 10, 20, 40, 80].map(count => {
        setMockProblemData({
          file_list: ['list1'],
          data: {
            list1: Array(count).fill(null).map((_, i) => ({
              name: `Problem ${i}`,
              solved: true
            }))
          }
        });
        return getSolvedFactor(problem);
      });

      // Check that growth rate decreases (logarithmic property)
      const growth1 = factors[1] - factors[0];
      const growth2 = factors[2] - factors[1];
      const growth3 = factors[3] - factors[2];
      const growth4 = factors[4] - factors[3];

      expect(growth2).toBeLessThan(growth1);
      expect(growth3).toBeLessThan(growth2);
      expect(growth4).toBeLessThan(growth3);
    });
  });

  describe('calculateAwarenessScore', () => {
    beforeEach(() => {
      // Set up mock data with 10 solved problems for consistent testing
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: Array(10).fill(null).map((_, i) => ({
            name: `Problem ${i}`,
            solved: true
          }))
        }
      });
    });

    describe('Unsolved problems', () => {
      it('should return { score: -1, invalidDate: false } for unsolved problem', () => {
        const problem = { solved: false };
        expect(calculateAwarenessScore(problem)).toEqual({
          score: -1,
          invalidDate: false
        });
      });

      it('should return -1 even if solved_date is present', () => {
        const problem = {
          solved: false,
          solved_date: '2024-01-01'
        };
        expect(calculateAwarenessScore(problem)).toEqual({
          score: -1,
          invalidDate: false
        });
      });
    });

    describe('Invalid dates', () => {
      it('should return { score: -1, invalidDate: true } for invalid date', () => {
        const problem = {
          solved: true,
          solved_date: 'invalid-date',
          time_to_solve: 10,
          top_time: 15,
          difficulty: 'Medium'
        };
        expect(calculateAwarenessScore(problem)).toEqual({
          score: -1,
          invalidDate: true
        });
      });

      it('should return { score: -1, invalidDate: false } for missing date', () => {
        const problem = {
          solved: true,
          time_to_solve: 10,
          top_time: 15,
          difficulty: 'Medium'
        };
        expect(calculateAwarenessScore(problem)).toEqual({
          score: -1,
          invalidDate: false
        });
      });
    });

    describe('Future dates', () => {
      it('should return score 0 for future dates', () => {
        const futureDate = new Date();
        futureDate.setDate(futureDate.getDate() + 10);

        const problem = {
          solved: true,
          solved_date: futureDate.toISOString(),
          time_to_solve: 10,
          top_time: 15,
          difficulty: 'Medium'
        };

        const result = calculateAwarenessScore(problem);
        expect(result.invalidDate).toBe(false);
        expect(result.score).toBe(0);
      });
    });

    describe('Score calculation', () => {
      it('should always return 0 for Top tier + Easy (mastered)', () => {
        const pastDate = new Date();
        pastDate.setDate(pastDate.getDate() - 30);

        const problem = {
          solved: true,
          solved_date: pastDate.toISOString(),
          time_to_solve: 10,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Easy'
        };

        const result = calculateAwarenessScore(problem);
        expect(result.score).toBe(0); // Multiplier is 0
      });

      it('should increase score with more days passed', () => {
        const problem = {
          solved: true,
          time_to_solve: 30,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Medium'
        };

        const date10 = new Date();
        date10.setDate(date10.getDate() - 10);

        const date30 = new Date();
        date30.setDate(date30.getDate() - 30);

        const score10 = calculateAwarenessScore({
          ...problem,
          solved_date: date10.toISOString()
        }).score;

        const score30 = calculateAwarenessScore({
          ...problem,
          solved_date: date30.toISOString()
        }).score;

        expect(score30).toBeGreaterThan(score10);
      });

      it('should have higher score for below tier vs top tier (same difficulty)', () => {
        const date = new Date();
        date.setDate(date.getDate() - 20);
        const dateStr = date.toISOString();

        const topProblem = {
          solved: true,
          solved_date: dateStr,
          time_to_solve: 10,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Medium'
        };

        const belowProblem = {
          solved: true,
          solved_date: dateStr,
          time_to_solve: 40,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Medium'
        };

        const topScore = calculateAwarenessScore(topProblem).score;
        const belowScore = calculateAwarenessScore(belowProblem).score;

        expect(belowScore).toBeGreaterThan(topScore);
      });

      it('should have higher score with higher commitment', () => {
        const date = new Date();
        date.setDate(date.getDate() - 20);

        const problem = {
          solved: true,
          solved_date: date.toISOString(),
          time_to_solve: 30,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Medium'
        };

        // Default commitment (2 problems/day)
        const score1 = calculateAwarenessScore(problem).score;

        // Higher commitment (4 problems/day)
        setConfig({
          ...getConfig(),
          commitment: { problemsPerDay: 4 }
        });
        const score2 = calculateAwarenessScore(problem).score;

        expect(score2).toBeGreaterThan(score1);
      });

      it('should have lower score with more solved problems', () => {
        const date = new Date();
        date.setDate(date.getDate() - 20);

        const problem = {
          solved: true,
          solved_date: date.toISOString(),
          time_to_solve: 30,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35,
          difficulty: 'Medium'
        };

        // 10 solved (from beforeEach)
        const score10 = calculateAwarenessScore(problem).score;

        // 50 solved
        setMockProblemData({
          file_list: ['list1'],
          data: {
            list1: Array(50).fill(null).map((_, i) => ({
              name: `Problem ${i}`,
              solved: true
            }))
          }
        });
        const score50 = calculateAwarenessScore(problem).score;

        expect(score50).toBeLessThan(score10);
      });
    });

    describe('Different tier/difficulty combinations', () => {
      const testDate = new Date();
      testDate.setDate(testDate.getDate() - 30);
      const dateStr = testDate.toISOString();

      const tiers = [
        { tier: 'top', time_to_solve: 10 },
        { tier: 'advanced', time_to_solve: 20 },
        { tier: 'intermediate', time_to_solve: 30 },
        { tier: 'below', time_to_solve: 40 }
      ];

      const difficulties = ['Easy', 'Medium', 'Hard'];

      tiers.forEach(({ tier, time_to_solve }) => {
        difficulties.forEach(difficulty => {
          it(`should calculate score for ${tier} tier + ${difficulty}`, () => {
            const problem = {
              solved: true,
              solved_date: dateStr,
              time_to_solve,
              top_time: 15,
              advanced_time: 25,
              intermediate_time: 35,
              difficulty
            };

            const result = calculateAwarenessScore(problem);
            expect(result.invalidDate).toBe(false);
            expect(typeof result.score).toBe('number');

            // Top + Easy should be exactly 0
            if (tier === 'top' && difficulty === 'Easy') {
              expect(result.score).toBe(0);
            } else {
              expect(result.score).toBeGreaterThanOrEqual(0);
            }
          });
        });
      });
    });

    describe('Edge cases', () => {
      it('should handle missing difficulty (defaults to Medium)', () => {
        const date = new Date();
        date.setDate(date.getDate() - 20);

        const problem = {
          solved: true,
          solved_date: date.toISOString(),
          time_to_solve: 30,
          top_time: 15,
          advanced_time: 25,
          intermediate_time: 35
          // No difficulty specified
        };

        const result = calculateAwarenessScore(problem);
        expect(result.invalidDate).toBe(false);
        expect(result.score).toBeGreaterThan(0);
      });

      it('should handle missing time_to_solve (defaults to below tier)', () => {
        const date = new Date();
        date.setDate(date.getDate() - 20);

        const problem = {
          solved: true,
          solved_date: date.toISOString(),
          difficulty: 'Medium'
          // No time_to_solve
        };

        const result = calculateAwarenessScore(problem);
        expect(result.invalidDate).toBe(false);
        expect(result.score).toBeGreaterThan(0);
      });

      it('should produce non-negative scores', () => {
        const date = new Date();
        date.setDate(date.getDate() - 1);

        const problem = {
          solved: true,
          solved_date: date.toISOString(),
          time_to_solve: 10,
          top_time: 15,
          difficulty: 'Hard'
        };

        const result = calculateAwarenessScore(problem);
        expect(result.score).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('getAwarenessClass', () => {
    it('should return "unsolved-problem" for negative score', () => {
      expect(getAwarenessClass(-1)).toBe('unsolved-problem');
      expect(getAwarenessClass(-100)).toBe('unsolved-problem');
    });

    it('should return "awareness-white" for score < white threshold', () => {
      expect(getAwarenessClass(0)).toBe('awareness-white');
      expect(getAwarenessClass(5)).toBe('awareness-white');
      expect(getAwarenessClass(9.99)).toBe('awareness-white');
    });

    it('should return "awareness-green" for white <= score < green', () => {
      expect(getAwarenessClass(10)).toBe('awareness-green');
      expect(getAwarenessClass(20)).toBe('awareness-green');
      expect(getAwarenessClass(29.99)).toBe('awareness-green');
    });

    it('should return "awareness-yellow" for green <= score < yellow', () => {
      expect(getAwarenessClass(30)).toBe('awareness-yellow');
      expect(getAwarenessClass(40)).toBe('awareness-yellow');
      expect(getAwarenessClass(49.99)).toBe('awareness-yellow');
    });

    it('should return "awareness-red" for yellow <= score < red', () => {
      expect(getAwarenessClass(50)).toBe('awareness-red');
      expect(getAwarenessClass(60)).toBe('awareness-red');
      expect(getAwarenessClass(69.99)).toBe('awareness-red');
    });

    it('should return "awareness-dark-red" for red <= score < darkRed', () => {
      expect(getAwarenessClass(70)).toBe('awareness-dark-red');
      expect(getAwarenessClass(80)).toBe('awareness-dark-red');
      expect(getAwarenessClass(89.99)).toBe('awareness-dark-red');
    });

    it('should return "awareness-flashing" for score >= darkRed', () => {
      expect(getAwarenessClass(90)).toBe('awareness-flashing');
      expect(getAwarenessClass(100)).toBe('awareness-flashing');
      expect(getAwarenessClass(1000)).toBe('awareness-flashing');
    });

    it('should respect custom thresholds', () => {
      setConfig({
        ...getConfig(),
        thresholds: {
          white: 5,
          green: 15,
          yellow: 25,
          red: 35,
          darkRed: 45
        }
      });

      expect(getAwarenessClass(4)).toBe('awareness-white');
      expect(getAwarenessClass(5)).toBe('awareness-green');
      expect(getAwarenessClass(15)).toBe('awareness-yellow');
      expect(getAwarenessClass(25)).toBe('awareness-red');
      expect(getAwarenessClass(35)).toBe('awareness-dark-red');
      expect(getAwarenessClass(45)).toBe('awareness-flashing');
    });
  });

  describe('validateThresholdOrdering', () => {
    it('should keep valid ordered thresholds unchanged', () => {
      const thresholds = {
        white: 10,
        green: 30,
        yellow: 50,
        red: 70,
        darkRed: 90
      };

      const result = validateThresholdOrdering(thresholds);
      expect(result).toEqual(thresholds);
    });

    it('should correct out-of-order thresholds', () => {
      const thresholds = {
        white: 50,  // Out of order
        green: 30,  // Out of order
        yellow: 20, // Out of order
        red: 70,
        darkRed: 90
      };

      const result = validateThresholdOrdering(thresholds);
      expect(result.white).toBe(50);
      expect(result.green).toBe(51); // Corrected
      expect(result.yellow).toBe(52); // Corrected
      expect(result.red).toBe(70);
      expect(result.darkRed).toBe(90);
    });

    it('should correct equal thresholds by incrementing', () => {
      const thresholds = {
        white: 10,
        green: 10,  // Equal
        yellow: 10, // Equal
        red: 10,    // Equal
        darkRed: 90
      };

      const result = validateThresholdOrdering(thresholds);
      expect(result.white).toBe(10);
      expect(result.green).toBe(11);
      expect(result.yellow).toBe(12);
      expect(result.red).toBe(13);
      expect(result.darkRed).toBe(90);
    });

    it('should cap thresholds at 200', () => {
      const thresholds = {
        white: 10,
        green: 250,  // Over limit
        yellow: 300, // Over limit
        red: 350,    // Over limit
        darkRed: 400 // Over limit
      };

      const result = validateThresholdOrdering(thresholds);
      expect(result.green).toBeLessThanOrEqual(200);
      expect(result.yellow).toBeLessThanOrEqual(200);
      expect(result.red).toBeLessThanOrEqual(200);
      expect(result.darkRed).toBeLessThanOrEqual(200);
    });

    it('should handle all thresholds equal and over limit', () => {
      const thresholds = {
        white: 250,
        green: 250,
        yellow: 250,
        red: 250,
        darkRed: 250
      };

      const result = validateThresholdOrdering(thresholds);
      expect(result.white).toBeLessThanOrEqual(200);
      expect(result.green).toBeLessThanOrEqual(200);
      expect(result.yellow).toBeLessThanOrEqual(200);
      expect(result.red).toBeLessThanOrEqual(200);
      expect(result.darkRed).toBeLessThanOrEqual(200);

      // Should maintain ordering
      expect(result.white).toBeLessThan(result.green);
      expect(result.green).toBeLessThan(result.yellow);
      expect(result.yellow).toBeLessThan(result.red);
      expect(result.red).toBeLessThan(result.darkRed);
    });

    it('should not modify the original object', () => {
      const thresholds = {
        white: 10,
        green: 10,
        yellow: 50,
        red: 70,
        darkRed: 90
      };

      const original = { ...thresholds };
      validateThresholdOrdering(thresholds);

      expect(thresholds).toEqual(original);
    });
  });

  describe('Integration tests', () => {
    it('should produce consistent results across full workflow', () => {
      // Setup: 20 solved problems
      setMockProblemData({
        file_list: ['list1'],
        data: {
          list1: Array(20).fill(null).map((_, i) => ({
            name: `Problem ${i}`,
            solved: true
          }))
        }
      });

      const date = new Date();
      date.setDate(date.getDate() - 45);

      const problem = {
        name: 'Test Problem',
        solved: true,
        solved_date: date.toISOString(),
        time_to_solve: 30,
        top_time: 15,
        advanced_time: 25,
        intermediate_time: 35,
        difficulty: 'Medium'
      };

      const result = calculateAwarenessScore(problem);
      expect(result.invalidDate).toBe(false);
      expect(result.score).toBeGreaterThan(0);

      const cssClass = getAwarenessClass(result.score);
      expect(cssClass).toBeTruthy();
      expect(['awareness-white', 'awareness-green', 'awareness-yellow',
              'awareness-red', 'awareness-dark-red', 'awareness-flashing'])
        .toContain(cssClass);
    });

    it('should handle complete problem lifecycle', () => {
      const problem = {
        name: 'Lifecycle Test',
        solved: false
      };

      // Unsolved
      let result = calculateAwarenessScore(problem);
      expect(result.score).toBe(-1);
      expect(getAwarenessClass(result.score)).toBe('unsolved-problem');

      // Just solved (today)
      problem.solved = true;
      problem.solved_date = new Date().toISOString();
      problem.time_to_solve = 20;
      problem.top_time = 15;
      problem.advanced_time = 25;
      problem.difficulty = 'Medium';

      result = calculateAwarenessScore(problem);
      expect(result.score).toBeGreaterThanOrEqual(0);
      expect(result.score).toBeLessThan(10); // Should be white
      expect(getAwarenessClass(result.score)).toBe('awareness-white');
    });
  });
});
