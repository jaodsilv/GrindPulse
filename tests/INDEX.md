# Awareness Indicator Test Suite - Complete Index

## Quick Navigation

1. [Getting Started](#getting-started)
2. [File Directory](#file-directory)
3. [Documentation Guide](#documentation-guide)
4. [Common Tasks](#common-tasks)
5. [Function Reference](#function-reference)

---

## Getting Started

### First Time Setup
```bash
cd D:\src\neetcode-coding-challenges-tracker\awareness-indicator\tests
npm install
npm test
```

**New to the project?** Start here:
1. Read [SETUP.md](SETUP.md) - 5 minutes
2. Run `npm test` to verify installation
3. Review [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 10 minutes
4. Explore test code in awareness.test.js

**Need details?** Continue with:
1. [README.md](README.md) - Comprehensive documentation
2. [TEST_DESIGN.md](TEST_DESIGN.md) - Design rationale
3. [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

---

## File Directory

### Core Test Files
```
tests/
├── awareness.js              [280 lines]
│   Extracted JavaScript functions made testable
│   • 10 exported functions
│   • Mock helpers for testing
│   • Configuration management
│
├── awareness.test.js         [800+ lines]
│   Comprehensive test suite
│   • 100+ unit tests
│   • Edge case coverage
│   • Integration tests
│
└── package.json              [40 lines]
    Jest configuration
    • Test scripts
    • Dependencies
    • Coverage thresholds
```

### Documentation Files
```
docs/
├── README.md                 [800+ lines] ★ COMPREHENSIVE
│   Complete test documentation
│   • Installation & running
│   • Function coverage
│   • Test scenarios
│   • Debugging tips
│   • Mathematical formulas
│
├── SETUP.md                  [200 lines] ★ QUICK START
│   Installation and first run
│   • Prerequisites
│   • Quick start commands
│   • Expected output
│   • Troubleshooting
│
├── QUICK_REFERENCE.md        [400 lines] ★ CHEATSHEET
│   One-page reference
│   • Common commands
│   • Test patterns
│   • Assertions
│   • Quick examples
│
├── TEST_DESIGN.md            [600 lines] ★ IN-DEPTH
│   Design and implementation
│   • Architecture
│   • Coverage details
│   • Edge cases
│   • Mathematical properties
│
├── TEST_SUMMARY.md           [500 lines] ★ OVERVIEW
│   High-level summary
│   • Test breakdown
│   • Coverage matrix
│   • Key scenarios
│   • Quick stats
│
├── ARCHITECTURE.md           [600 lines] ★ VISUAL
│   System architecture
│   • Diagrams
│   • Data flow
│   • Dependencies
│   • Performance
│
└── INDEX.md                  [This file] ★ NAVIGATION
    Complete navigation guide
```

### Support Files
```
.gitignore                    Excludes node_modules, coverage
```

---

## Documentation Guide

### Choose Your Path

#### 🚀 "I want to run tests NOW"
→ [SETUP.md](SETUP.md) (5 min read)
- Installation steps
- Run commands
- Verify success

#### 📋 "I need a quick reference"
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (10 min read)
- Common commands
- Test patterns
- Function signatures
- Quick examples

#### 📚 "I want comprehensive details"
→ [README.md](README.md) (30 min read)
- Everything about the test suite
- All functions documented
- All test scenarios
- Complete guide

#### 🎨 "I want to understand the architecture"
→ [ARCHITECTURE.md](ARCHITECTURE.md) (20 min read)
- Visual diagrams
- Data flow
- System structure
- Dependencies

#### 🔍 "I want design rationale"
→ [TEST_DESIGN.md](TEST_DESIGN.md) (25 min read)
- Why tests are structured this way
- Coverage strategies
- Edge case rationale
- Mathematical verification

#### 📊 "I want a high-level overview"
→ [TEST_SUMMARY.md](TEST_SUMMARY.md) (15 min read)
- Test statistics
- Coverage summary
- Key scenarios
- Quick metrics

---

## Common Tasks

### Running Tests

```bash
# Run all tests
npm test

# Watch mode (auto-rerun on changes)
npm run test:watch

# Coverage report
npm run test:coverage

# Run specific test
npm test -- -t "calculateAwarenessScore"

# Verbose output
npm test -- --verbose
```

**More details:** [SETUP.md](SETUP.md#running-tests) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md#running-specific-tests)

### Writing Tests

```javascript
describe('myFunction', () => {
  beforeEach(() => {
    resetConfig();
    setMockProblemData({ file_list: [], data: {} });
  });

  it('should do something', () => {
    const result = myFunction(input);
    expect(result).toBe(expected);
  });
});
```

**More details:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md#example-adding-a-new-test) or [TEST_DESIGN.md](TEST_DESIGN.md#test-data-strategies)

### Debugging Tests

```javascript
// 1. Add console.log
console.log('Result:', result);

// 2. Run only one test
it.only('should run only this', () => { /* ... */ });

// 3. Skip a test
it.skip('should skip this', () => { /* ... */ });

// 4. Run specific pattern
npm test -- -t "score calculation"
```

**More details:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md#debugging-tests) or [README.md](README.md#debugging-tips)

### Checking Coverage

```bash
npm run test:coverage

# View HTML report
# Open: coverage/lcov-report/index.html
```

**More details:** [SETUP.md](SETUP.md#generate-coverage-report) or [README.md](README.md#test-coverage)

### Understanding Test Failures

```
FAIL  awareness.test.js
  ✕ should return 0 for Top tier + Easy
    Expected: 0
    Received: 1.5

    > 234 |     expect(result.score).toBe(0);
```

**Troubleshooting:** [README.md](README.md#debugging-tips) or [QUICK_REFERENCE.md](QUICK_REFERENCE.md#common-issues)

---

## Function Reference

### Core Calculation Functions

| Function | Purpose | Tests | Doc |
|----------|---------|-------|-----|
| `calculateAwarenessScore(problem)` | Calculate awareness decay score | 26 | [Details](#calculateawarenessscore) |
| `getTierDifficultyMultiplier(problem)` | Get decay multiplier | 15 | [Details](#gettierdiffcultymultiplier) |
| `getTierName(problem)` | Determine performance tier | 9 | [Details](#gettiername) |

### Helper Functions

| Function | Purpose | Tests | Doc |
|----------|---------|-------|-----|
| `getDaysSinceCompletion(date)` | Calculate days passed | 8 | [Details](#getdayssincecompletion) |
| `normalizeDateToISO(date)` | Convert to ISO format | 8 | [Details](#normalizedatetoiso) |
| `getTotalUniqueSolvedCount()` | Count solved problems | 4 | [Details](#gettotaluniquesolvedcount) |
| `getCommitmentFactor()` | Get commitment scaling | 4 | [Details](#getcommitmentfactor) |
| `getSolvedFactor(problem)` | Get solved scaling | 4 | [Details](#getsolvedfactor) |

### UI Functions

| Function | Purpose | Tests | Doc |
|----------|---------|-------|-----|
| `getAwarenessClass(score)` | Map score to CSS class | 14 | [Details](#getawarenessclass) |
| `validateThresholdOrdering(thresholds)` | Fix threshold order | 6 | [Details](#validatethresholdordering) |

### Function Details

#### calculateAwarenessScore
```javascript
calculateAwarenessScore(problem)
// Returns: { score: number, invalidDate: boolean }
```
- Main calculation function
- Handles unsolved, invalid dates, future dates
- Calculates decay score based on time, tier, difficulty, commitment, solved count
- **Special:** Top tier + Easy always returns 0 (mastered)

**Full documentation:** [README.md](README.md#1-calculateawarenessscoreproblem) | [TEST_DESIGN.md](TEST_DESIGN.md#calculateawarenessscoreproblem)

#### getTierDifficultyMultiplier
```javascript
getTierDifficultyMultiplier(problem)
// Returns: number (0 to 1.8)
```
- Gets decay multiplier from tier-difficulty matrix
- Top tier: Easy=0, Medium=0.25, Hard=0.4 (inverted)
- Other tiers: Easy>Medium>Hard (standard)
- Defaults to 1.0 if invalid

**Full documentation:** [README.md](README.md#2-gettierdiffcultymultiplierproblem) | [QUICK_REFERENCE.md](QUICK_REFERENCE.md#tier-multipliers)

#### getTierName
```javascript
getTierName(problem)
// Returns: 'top' | 'advanced' | 'intermediate' | 'below'
```
- Determines performance tier from time_to_solve
- Compares against tier time thresholds
- Defaults to 'below' if no time recorded

**Full documentation:** [README.md](README.md#gettiername) | [TEST_DESIGN.md](TEST_DESIGN.md#gettiername)

#### getDaysSinceCompletion
```javascript
getDaysSinceCompletion(solvedDate)
// Returns: { days: number, valid: boolean }
```
- Calculates days since problem was solved
- Handles invalid dates, future dates (returns 0)
- Returns valid: false for unparseable dates

**Full documentation:** [README.md](README.md#getdayssincecompletion) | [TEST_DESIGN.md](TEST_DESIGN.md#getdayssincecompletion)

#### normalizeDateToISO
```javascript
normalizeDateToISO(dateInput)
// Returns: string | null
```
- Converts various date formats to ISO string
- Returns null for invalid dates
- Handles Date objects, strings

**Full documentation:** [README.md](README.md#normalizedatetoiso)

#### getTotalUniqueSolvedCount
```javascript
getTotalUniqueSolvedCount()
// Returns: number
```
- Counts unique solved problems across all lists
- Deduplicates by problem name
- Used for solved factor calculation

**Full documentation:** [README.md](README.md#gettotaluniquesolvedcount)

#### getCommitmentFactor
```javascript
getCommitmentFactor()
// Returns: number
```
- Calculates commitment scaling factor
- Formula: problemsPerDay / 2
- Higher commitment = faster decay

**Full documentation:** [README.md](README.md#getcommitmentfactor) | [QUICK_REFERENCE.md](QUICK_REFERENCE.md#commitment-factor)

#### getSolvedFactor
```javascript
getSolvedFactor(problem)
// Returns: number
```
- Calculates solved count scaling factor
- Logarithmic scaling (diminishing returns)
- Tier bonus: top > advanced > intermediate > below

**Full documentation:** [README.md](README.md#getsolvedfactor) | [TEST_DESIGN.md](TEST_DESIGN.md#getsolvedfactor)

#### getAwarenessClass
```javascript
getAwarenessClass(score)
// Returns: string (CSS class name)
```
- Maps score to CSS class
- Thresholds: 10, 30, 50, 70, 90 (default)
- Returns 'unsolved-problem' for score < 0

**Full documentation:** [README.md](README.md#getawarenessclass) | [QUICK_REFERENCE.md](QUICK_REFERENCE.md#css-classes)

#### validateThresholdOrdering
```javascript
validateThresholdOrdering(thresholds)
// Returns: { white, green, yellow, red, darkRed }
```
- Ensures thresholds are strictly ordered
- Corrects out-of-order values
- Caps at 200 maximum

**Full documentation:** [README.md](README.md#validatethresholdordering) | [TEST_DESIGN.md](TEST_DESIGN.md#validatethresholdordering)

---

## Test Statistics

```
Total Tests: 100+
Coverage: >95%
Time: 2-5 seconds

Breakdown:
├── Core Functions (26)
├── Tier Functions (24)
├── Date Functions (16)
├── Scaling Functions (12)
├── UI Functions (20)
└── Integration (2)
```

**Full breakdown:** [TEST_SUMMARY.md](TEST_SUMMARY.md#test-breakdown) or [TEST_DESIGN.md](TEST_DESIGN.md#test-coverage-summary)

---

## Learning Path

### For New Contributors

1. **Day 1: Setup & Run**
   - Read [SETUP.md](SETUP.md)
   - Install and run tests
   - Verify all pass

2. **Day 2: Understanding**
   - Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
   - Review awareness.test.js
   - Try modifying a test

3. **Day 3: Deep Dive**
   - Read [README.md](README.md)
   - Understand all functions
   - Write a new test

4. **Day 4: Architecture**
   - Read [ARCHITECTURE.md](ARCHITECTURE.md)
   - Study data flow
   - Understand dependencies

5. **Week 2: Mastery**
   - Read [TEST_DESIGN.md](TEST_DESIGN.md)
   - Contribute new tests
   - Improve coverage

### For Maintainers

1. **Regular Tasks**
   - Run `npm test` before commits
   - Check coverage with `npm run test:coverage`
   - Update tests when code changes

2. **When Adding Features**
   - Write tests first (TDD)
   - Ensure >90% coverage
   - Update documentation

3. **Monthly Review**
   - Review test performance
   - Check for flaky tests
   - Update dependencies

**More details:** [TEST_DESIGN.md](TEST_DESIGN.md#test-maintenance)

---

## Help & Troubleshooting

### Common Issues

1. **"Cannot find module 'jest'"**
   → Run `npm install` in tests directory

2. **Tests fail after code change**
   → Check if formulas changed, update expected values

3. **Coverage drops**
   → Run `npm run test:coverage` and check HTML report

4. **Flaky date tests**
   → Use relative dates and ranges instead of exact values

**Full troubleshooting:** [SETUP.md](SETUP.md#troubleshooting) or [README.md](README.md#troubleshooting)

### Getting Help

1. Check relevant documentation file
2. Review test code comments
3. Examine function implementation
4. Check generator code (js_awareness_generator.py)

---

## Resources

### Internal Documentation
- [README.md](README.md) - Comprehensive guide
- [SETUP.md](SETUP.md) - Quick start
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheatsheet
- [TEST_DESIGN.md](TEST_DESIGN.md) - Design details
- [TEST_SUMMARY.md](TEST_SUMMARY.md) - Overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [INDEX.md](INDEX.md) - This file

### External Resources
- Jest Documentation: https://jestjs.io/
- JavaScript Testing: https://testingjavascript.com/
- TDD Principles: https://martinfowler.com/bliki/TestDrivenDevelopment.html

### Source Code
- `awareness.js` - Functions under test
- `awareness.test.js` - Test suite
- `../js_awareness_generator.py` - Original generator

---

## Quick Commands

```bash
# Setup
npm install

# Run
npm test
npm run test:watch
npm run test:coverage

# Debug
npm test -- -t "pattern"
npm test -- --verbose

# Help
npm test -- --help
```

---

**Complete Index v1.0** | Last Updated: 2025-12-06

**Need help?** Start with the documentation that matches your goal above, or read the comprehensive [README.md](README.md).
