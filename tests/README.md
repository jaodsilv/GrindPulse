# Awareness Indicator Unit Tests

Comprehensive unit tests for the awareness indicator system's JavaScript functions.

## Overview

The awareness indicator system calculates spaced repetition scores for coding problems based on:

1. Time since completion
2. Performance tier (top/advanced/intermediate/below)
3. Problem difficulty (Easy/Medium/Hard)
4. User commitment level
5. Total problems solved

These tests validate all calculation logic, edge cases, and integration scenarios.

## Test Structure

```
tests/
├── package.json          # Jest configuration and dependencies
├── awareness.js          # Extracted JavaScript functions (testable module)
├── awareness.test.js     # Comprehensive unit tests
└── README.md            # This file
```

## Installation

Install Jest and dependencies:

```bash
cd tests
npm install
```

## Running Tests

1. **Run all tests:**
   ```bash
   npm test
   ```

2. **Watch mode (for development):**
   ```bash
   npm run test:watch
   ```

3. **Coverage report:**
   ```bash
   npm run test:coverage
   ```

## Test Coverage

The test suite covers:

### Core Functions

#### 1. `calculateAwarenessScore(problem)`
Tests for:
- Unsolved problems (score: -1)
- Invalid dates (invalidDate: true)
- Future dates (score: 0)
- Valid date calculations
- All tier/difficulty combinations
- Top tier + Easy mastery (always 0)
- Score progression over time
- Commitment factor impact
- Solved count impact

#### 2. `getTierDifficultyMultiplier(problem)`
Tests for:
- All 4 tiers (top, advanced, intermediate, below)
- All 3 difficulties per tier
- Special top tier behavior (Easy=0, inverted Medium<Hard)
- Standard tier behavior (Easy>Medium>Hard)
- Missing difficulty (defaults to Medium)
- Invalid tier/difficulty (fallback to 1.0)

#### 3. `getTierName(problem)`
Tests for:
- Missing/zero/negative time_to_solve (returns "below")
- Correct tier calculation from time thresholds
- Boundary conditions
- String vs numeric time values
- Missing tier time values

#### 4. `getDaysSinceCompletion(solvedDate)`
Tests for:
- Null/undefined/empty dates
- Invalid date strings
- Future dates (returns 0)
- Past dates (correct calculation)
- Various date formats (ISO, US, text)

#### 5. `validateThresholdOrdering(thresholds)`
Tests for:
- Valid ordered thresholds (unchanged)
- Out-of-order thresholds (correction)
- Equal thresholds (incrementation)
- Maximum boundary (200 cap)
- Immutability (doesn't modify original)

### Helper Functions

#### `getTotalUniqueSolvedCount()`
- Empty lists
- Single list counting
- Cross-list duplicate detection
- Case sensitivity

#### `getCommitmentFactor()`
- Default commitment (2 problems/day = 1.0)
- Lower commitment scaling
- Higher commitment scaling

#### `getSolvedFactor(problem)`
- Zero solved problems
- Logarithmic scaling verification
- Tier bonus differences
- Diminishing returns

#### `normalizeDateToISO(dateInput)`
- Null/undefined/empty handling
- Invalid date strings
- Valid date conversion
- Date object handling
- Various input formats

#### `getAwarenessClass(score)`
- All threshold boundaries
- Negative scores (unsolved)
- Custom threshold configurations

### Integration Tests

1. **Full workflow test**: Problem → Score → CSS Class
2. **Lifecycle test**: Unsolved → Just Solved → Aging
3. **Cross-function consistency**: All functions work together correctly

## Test Design Principles

### 1. Comprehensive Coverage
- Every function has dedicated test suite
- All branches and edge cases covered
- Target: >90% code coverage

### 2. Isolated Testing
- Each test is independent
- `beforeEach` resets state
- No test pollution

### 3. Edge Case Focus
- Boundary values
- Invalid inputs
- Missing data
- Type coercion

### 4. Real-World Scenarios
- Date handling (past, future, invalid)
- Large datasets
- Configuration variations
- Integration workflows

## Key Test Scenarios

### Tier/Difficulty Matrix Testing

All 12 combinations tested:
```
Top:          Easy (0.0), Medium (0.25), Hard (0.4)
Advanced:     Easy (1.2), Medium (0.9), Hard (0.7)
Intermediate: Easy (1.5), Medium (1.0), Hard (0.75)
Below:        Easy (1.8), Medium (1.3), Hard (1.0)
```

### Date Edge Cases

1. **Valid dates**: ISO strings, US format, text format
2. **Invalid dates**: Malformed strings, garbage input
3. **Edge dates**: Future dates, very old dates, today
4. **Missing dates**: null, undefined, empty string

### Score Calculation Properties

Verified mathematical properties:
1. **Monotonicity**: Score increases with time
2. **Tier ordering**: Below > Intermediate > Advanced > Top
3. **Commitment scaling**: Higher commitment = faster decay
4. **Solved scaling**: More solved = slower decay
5. **Logarithmic returns**: Diminishing impact of solved count

## Understanding Test Output

### Successful Test Run
```
PASS  tests/awareness.test.js
  Awareness Indicator System
    ✓ getTierName (12 tests)
    ✓ getTierDifficultyMultiplier (18 tests)
    ✓ getDaysSinceCompletion (8 tests)
    ✓ calculateAwarenessScore (45 tests)
    ...
```

### Coverage Report
```
File            | % Stmts | % Branch | % Funcs | % Lines
----------------|---------|----------|---------|--------
awareness.js    |   98.5  |   95.2   |  100.0  |  98.5
```

### Failed Test Example
```
FAIL  tests/awareness.test.js
  × should return 0 for Top tier + Easy
    Expected: 0
    Received: 1.5

    > 234 |     expect(result.score).toBe(0);
```

## Debugging Tips

### 1. Inspect Calculated Values
Add console.log in tests to see intermediate values:
```javascript
const result = calculateAwarenessScore(problem);
console.log('Score:', result.score);
console.log('Tier:', getTierName(problem));
```

### 2. Test Specific Cases
Run single test:
```bash
npm test -- -t "should return 0 for Top tier + Easy"
```

### 3. Check Configuration
Verify config is reset:
```javascript
console.log('Config:', getConfig());
```

### 4. Examine Mock Data
Check problem data state:
```javascript
console.log('Solved count:', getTotalUniqueSolvedCount());
```

## Mathematical Formulas Tested

### Awareness Score
```
score = days * baseRate * commitmentFactor * tierDiffMultiplier / solvedFactor

where:
  days = days since completion
  baseRate = 2.0 (default)
  commitmentFactor = problemsPerDay / 2
  tierDiffMultiplier = matrix[tier][difficulty]
  solvedFactor = 1 + (baseScaling + tierBonus) * log2(totalSolved + 1)
```

### Commitment Factor
```
commitmentFactor = problemsPerDay / baseline
  baseline = 2 (default)
```

### Solved Factor
```
solvedFactor = 1 + (baseSolvedScaling + tierBonus) * log2(totalSolved + 1)
  baseSolvedScaling = 0.1 (default)
  tierBonus = { top: 0.3, advanced: 0.2, intermediate: 0.1, below: 0 }
```

## Known Behaviors

### 1. Top Tier Mastery
- Top tier + Easy difficulty **always** returns score 0 (multiplier = 0)
- Represents complete mastery, never needs review

### 2. Inverted Top Tier
- Top tier: Medium (0.25) < Hard (0.4)
- Other tiers: Easy > Medium > Hard
- Rationale: Deep mastery means medium problems decay slower

### 3. Logarithmic Solved Scaling
- First 10 problems: significant impact
- Next 50 problems: moderate impact
- Beyond 100: diminishing returns
- Prevents unrealistic score suppression

### 4. Future Date Handling
- Future dates treated as "just solved" (score = 0)
- Handles clock skew gracefully
- No negative scores

### 5. Missing Data Defaults
- No time_to_solve → "below" tier
- No difficulty → "Medium"
- No solved_date → score -1 (unsolved)
- Invalid tier/difficulty → multiplier 1.0

## Maintenance

### Adding New Tests

1. **Create new describe block:**
   ```javascript
   describe('newFunction', () => {
     it('should handle basic case', () => {
       expect(newFunction()).toBe(expected);
     });
   });
   ```

2. **Follow existing patterns:**
   - Use `beforeEach` for setup
   - Test edge cases
   - Verify mathematical properties
   - Add integration tests

3. **Update this README:**
   - Document new test coverage
   - Explain test scenarios
   - Note any special behaviors

### Updating for Config Changes

If `DEFAULT_AWARENESS_CONFIG` changes:

1. Update `awareness.js` with new values
2. Update tests expecting specific thresholds
3. Add tests for new configuration options
4. Update mathematical formulas in this README

### Regression Testing

Before releasing changes:

1. Run full test suite: `npm test`
2. Check coverage: `npm run test:coverage`
3. Verify all edge cases pass
4. Run integration tests
5. Test with real problem data (manual)

## Contributing

When adding features to the awareness system:

1. **Write tests first** (TDD approach)
2. **Cover edge cases** comprehensively
3. **Document behavior** in comments and README
4. **Maintain >90% coverage**
5. **Update this README** with new test scenarios

## Troubleshooting

### "Cannot find module" Error
```bash
cd tests
npm install
```

### "Experimental modules" Warning
This is expected. We use ES modules with Jest.

### Tests Pass Locally, Fail in CI
- Check Node.js version (requires 14+)
- Verify Jest version matches package.json
- Check date/timezone issues

### Flaky Date Tests
- Date tests use relative dates (e.g., "20 days ago")
- Small timing variations are acceptable
- Use ranges instead of exact values when needed

## License

MIT - Same as parent project

## Questions?

For issues or questions about tests:
1. Check this README first
2. Review test comments in awareness.test.js
3. Examine function documentation in awareness.js
4. Review generated code in js_awareness_generator.py
