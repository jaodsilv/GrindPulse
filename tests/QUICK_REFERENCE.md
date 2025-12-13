# Awareness Indicator Test Quick Reference

One-page reference for testing the awareness indicator system.

## Installation & Running

```bash
cd D:\src\GrindPulse\tests
npm install        # First time only
npm test          # Run all tests
npm run test:watch     # Watch mode
npm run test:coverage  # Coverage report
```

## File Overview

```
tests/
├── awareness.js         → Code under test (extracted from generator)
├── awareness.test.js    → 100+ unit tests
└── package.json         → Jest config
```

## Functions Tested

| Function | Purpose | Tests |
|----------|---------|-------|
| `calculateAwarenessScore(problem)` | Calculate decay score | 26 |
| `getTierDifficultyMultiplier(problem)` | Get decay rate | 15 |
| `getTierName(problem)` | Determine performance tier | 9 |
| `getDaysSinceCompletion(date)` | Calculate days passed | 8 |
| `normalizeDateToISO(date)` | Convert date to ISO | 8 |
| `getTotalUniqueSolvedCount()` | Count solved problems | 4 |
| `getCommitmentFactor()` | Calculate commitment scaling | 4 |
| `getSolvedFactor(problem)` | Calculate solved scaling | 4 |
| `getAwarenessClass(score)` | Map score to CSS class | 14 |
| `validateThresholdOrdering(thresholds)` | Fix threshold order | 6 |

## Key Test Patterns

### 1. Basic Test Structure
```javascript
describe('functionName', () => {
  it('should do something', () => {
    const input = { /* ... */ };
    const result = functionName(input);
    expect(result).toBe(expected);
  });
});
```

### 2. State Reset (Always in beforeEach)
```javascript
beforeEach(() => {
  resetConfig();
  setMockProblemData({ file_list: [], data: {} });
});
```

### 3. Setting Mock Data
```javascript
setMockProblemData({
  file_list: ['list1'],
  data: {
    list1: [
      { name: 'Problem 1', solved: true },
      { name: 'Problem 2', solved: false }
    ]
  }
});
```

### 4. Custom Configuration
```javascript
setConfig({
  ...getConfig(),
  commitment: { problemsPerDay: 4 },
  thresholds: { white: 5, green: 15, ... }
});
```

## Common Assertions

```javascript
// Equality
expect(value).toBe(5);
expect(obj).toEqual({ a: 1, b: 2 });

// Comparison
expect(value).toBeGreaterThan(0);
expect(value).toBeLessThan(100);

// Type
expect(typeof value).toBe('number');
expect(value).toBeTruthy();
expect(value).toBeNull();

// Arrays
expect(['a', 'b']).toContain('b');

// Ranges (for dates/floats)
expect(days).toBeGreaterThanOrEqual(9.9);
expect(days).toBeLessThan(10.1);
```

## Test Data Examples

### Problem Objects
```javascript
// Minimal unsolved
{ solved: false }

// Complete solved problem
{
  name: 'Two Sum',
  solved: true,
  solved_date: '2024-01-01T00:00:00.000Z',
  time_to_solve: 20,
  top_time: 15,
  advanced_time: 25,
  intermediate_time: 35,
  difficulty: 'Medium'
}

// Top tier (time <= top_time)
{ time_to_solve: 10, top_time: 15 }

// Below tier (no time)
{ time_to_solve: 0 }  // or missing
```

### Dates
```javascript
// Today
new Date().toISOString()

// 10 days ago
const past = new Date();
past.setDate(past.getDate() - 10);
past.toISOString()

// Future
const future = new Date();
future.setDate(future.getDate() + 10);
future.toISOString()

// Invalid
'not-a-date'
```

## Expected Behaviors

### Tier Multipliers
```
Top:         Easy=0, Medium=0.25, Hard=0.4
Advanced:    Easy=1.2, Medium=0.9, Hard=0.7
Intermediate: Easy=1.5, Medium=1.0, Hard=0.75
Below:       Easy=1.8, Medium=1.3, Hard=1.0
```

### CSS Classes
```
score < 0   → 'unsolved-problem'
score < 10  → 'awareness-white'
score < 30  → 'awareness-green'
score < 50  → 'awareness-yellow'
score < 70  → 'awareness-red'
score < 90  → 'awareness-dark-red'
score >= 90 → 'awareness-flashing'
```

### Special Cases
```
Top tier + Easy → always score 0 (mastered)
Future date → score 0 (just solved)
Invalid date → score -1, invalidDate: true
Unsolved → score -1, invalidDate: false
```

## Formulas

### Awareness Score
```
score = days * baseRate * commitmentFactor * tierDiffMultiplier / solvedFactor
```

### Commitment Factor
```
commitmentFactor = problemsPerDay / 2
```

### Solved Factor
```
solvedFactor = 1 + (baseSolvedScaling + tierBonus) * log2(totalSolved + 1)
```

## Running Specific Tests

```bash
# Run tests matching pattern
npm test -- -t "calculateAwarenessScore"

# Run single test file
npm test awareness.test.js

# Run with verbose output
npm test -- --verbose

# Update snapshots (if used)
npm test -- -u
```

## Debugging Tests

### 1. Add console.log
```javascript
it('should calculate correctly', () => {
  const result = calculateAwarenessScore(problem);
  console.log('Result:', result);
  console.log('Tier:', getTierName(problem));
  expect(result.score).toBeGreaterThan(0);
});
```

### 2. Isolate Test
```javascript
it.only('should run only this test', () => {
  // Only this test runs
});
```

### 3. Skip Test
```javascript
it.skip('should skip this test', () => {
  // This test is skipped
});
```

### 4. Check State
```javascript
console.log('Config:', getConfig());
console.log('Solved count:', getTotalUniqueSolvedCount());
```

## Coverage Thresholds

```json
{
  "branches": 90,
  "functions": 90,
  "lines": 90,
  "statements": 90
}
```

Run `npm run test:coverage` to check current coverage.

## Common Issues

### Tests fail after code change
1. Check if formula changed
2. Update expected values
3. Verify edge cases still valid
4. Run coverage to find gaps

### Flaky date tests
1. Use relative dates (`new Date()`)
2. Use ranges instead of exact values
3. Mock Date if needed

### State pollution
1. Ensure `beforeEach` resets state
2. Check for shared variables
3. Verify test isolation

### Coverage drops
1. Run `npm run test:coverage`
2. Check HTML report in `coverage/`
3. Add tests for uncovered lines
4. Verify branches covered

## Quick Tips

1. **Write tests first** (TDD approach)
2. **One assertion per test** (ideally)
3. **Descriptive test names** (what, not how)
4. **Test edge cases** (null, 0, negative, invalid)
5. **Keep tests fast** (no network, no files)
6. **Isolate tests** (no dependencies between tests)
7. **Use beforeEach** for common setup
8. **Document complex tests** with comments

## Example: Adding a New Test

```javascript
describe('calculateAwarenessScore', () => {
  beforeEach(() => {
    resetConfig();
    setMockProblemData({
      file_list: ['test'],
      data: { test: [] }
    });
  });

  it('should return higher score for older problems', () => {
    // Arrange
    const recentDate = new Date();
    recentDate.setDate(recentDate.getDate() - 10);

    const oldDate = new Date();
    oldDate.setDate(oldDate.getDate() - 30);

    const problem = {
      solved: true,
      time_to_solve: 20,
      top_time: 15,
      advanced_time: 25,
      difficulty: 'Medium'
    };

    // Act
    const recentScore = calculateAwarenessScore({
      ...problem,
      solved_date: recentDate.toISOString()
    }).score;

    const oldScore = calculateAwarenessScore({
      ...problem,
      solved_date: oldDate.toISOString()
    }).score;

    // Assert
    expect(oldScore).toBeGreaterThan(recentScore);
  });
});
```

## Resources

1. **README.md** - Comprehensive documentation
2. **SETUP.md** - Installation guide
3. **TEST_DESIGN.md** - Design details
4. **TEST_SUMMARY.md** - Overview
5. **Jest Docs** - https://jestjs.io/

## Help

```bash
# Jest help
npm test -- --help

# List all tests
npm test -- --listTests

# Watch usage
npm run test:watch
# Then press 'w' for more options
```

---

**Quick Reference v1.0** | Last Updated: 2025-12-06
