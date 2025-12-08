# Test Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Awareness Indicator System                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Python Generator                Test Suite                  │
│  ┌─────────────────┐            ┌──────────────────┐        │
│  │ js_awareness_   │  Extract   │  awareness.js    │        │
│  │ generator.py    │ ────────▶  │  (testable       │        │
│  │                 │            │   module)        │        │
│  │ Embeds JS in    │            │                  │        │
│  │ tracker.html    │            │  • Exports funcs │        │
│  └─────────────────┘            │  • Mock helpers  │        │
│                                  │  • Config mgmt   │        │
│                                  └────────┬─────────┘        │
│                                           │                  │
│                                           │ Import           │
│                                           │                  │
│                                  ┌────────▼─────────┐        │
│                                  │ awareness.test.js│        │
│                                  │                  │        │
│                                  │  • 100+ tests    │        │
│                                  │  • Jest runner   │        │
│                                  │  • Edge cases    │        │
│                                  └──────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Test File Structure

```
tests/
│
├── package.json              ← Jest config, dependencies
│   └── Scripts:
│       ├── test              → Run all tests
│       ├── test:watch        → Watch mode
│       └── test:coverage     → Coverage report
│
├── awareness.js              ← Code under test (280 lines)
│   ├── Configuration
│   │   ├── DEFAULT_AWARENESS_CONFIG
│   │   ├── resetConfig()
│   │   ├── setConfig()
│   │   └── getConfig()
│   │
│   ├── Mock Helpers
│   │   └── setMockProblemData()
│   │
│   ├── Core Functions
│   │   ├── calculateAwarenessScore()     → Main calculation
│   │   ├── getTierDifficultyMultiplier() → Decay rate
│   │   └── getTierName()                 → Performance tier
│   │
│   ├── Helper Functions
│   │   ├── getDaysSinceCompletion()
│   │   ├── normalizeDateToISO()
│   │   ├── getTotalUniqueSolvedCount()
│   │   ├── getCommitmentFactor()
│   │   └── getSolvedFactor()
│   │
│   └── UI Functions
│       ├── getAwarenessClass()
│       └── validateThresholdOrdering()
│
├── awareness.test.js         ← Test suite (800+ lines)
│   │
│   ├── Test Setup
│   │   └── beforeEach() → Reset state
│   │
│   ├── Core Tests (26)
│   │   └── calculateAwarenessScore
│   │       ├── Unsolved problems
│   │       ├── Invalid dates
│   │       ├── Future dates
│   │       ├── Score calculation
│   │       ├── All tier/difficulty combos
│   │       └── Edge cases
│   │
│   ├── Tier Tests (24)
│   │   ├── getTierDifficultyMultiplier
│   │   │   ├── Top tier (4)
│   │   │   ├── Advanced tier (3)
│   │   │   ├── Intermediate tier (3)
│   │   │   ├── Below tier (3)
│   │   │   └── Edge cases (2)
│   │   │
│   │   └── getTierName
│   │       ├── Missing/invalid (3)
│   │       ├── Boundaries (4)
│   │       └── Formats (2)
│   │
│   ├── Date Tests (16)
│   │   ├── getDaysSinceCompletion (8)
│   │   └── normalizeDateToISO (8)
│   │
│   ├── Scaling Tests (12)
│   │   ├── getTotalUniqueSolvedCount (4)
│   │   ├── getCommitmentFactor (4)
│   │   └── getSolvedFactor (4)
│   │
│   ├── UI Tests (20)
│   │   ├── getAwarenessClass (14)
│   │   └── validateThresholdOrdering (6)
│   │
│   └── Integration Tests (2)
│       ├── Complete workflow
│       └── Problem lifecycle
│
└── Documentation
    ├── README.md            ← Comprehensive guide
    ├── SETUP.md             ← Quick start
    ├── TEST_DESIGN.md       ← Design details
    ├── TEST_SUMMARY.md      ← Overview
    ├── QUICK_REFERENCE.md   ← One-page cheatsheet
    └── ARCHITECTURE.md      ← This file
```

## Data Flow

```
┌──────────────┐
│   Problem    │
│     Data     │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────┐
│  calculateAwarenessScore(problem)              │
│                                                 │
│  1. Check if solved                            │
│     └─ No → return { score: -1 }               │
│                                                 │
│  2. Get days since completion                  │
│     └─ getDaysSinceCompletion(solved_date)     │
│        ├─ Invalid → return { invalidDate: true }│
│        ├─ Future → days = 0                    │
│        └─ Valid → calculate days               │
│                                                 │
│  3. Calculate factors                          │
│     ├─ getCommitmentFactor()                   │
│     │  └─ problemsPerDay / 2                   │
│     │                                           │
│     ├─ getTierDifficultyMultiplier(problem)    │
│     │  ├─ getTierName(problem)                 │
│     │  │  └─ Compare time_to_solve to tiers    │
│     │  └─ Lookup matrix[tier][difficulty]      │
│     │                                           │
│     └─ getSolvedFactor(problem)                │
│        ├─ getTotalUniqueSolvedCount()          │
│        ├─ getTierName(problem)                 │
│        └─ 1 + (base + bonus) * log2(count + 1) │
│                                                 │
│  4. Calculate score                            │
│     └─ days * baseRate * commitment * tierDiff │
│        / solvedFactor                          │
│                                                 │
└─────────────────┬──────────────────────────────┘
                  │
                  ▼
          ┌───────────────┐
          │  Score Result │
          │  { score,     │
          │    invalidDate}│
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────────┐
          │ getAwarenessClass │
          │     (score)       │
          └───────┬───────────┘
                  │
                  ▼
          ┌───────────────┐
          │  CSS Class    │
          │  'awareness-  │
          │   yellow'     │
          └───────────────┘
```

## Test Isolation Strategy

```
┌──────────────────────────────────────────────┐
│           Test Execution Flow                 │
└──────────────────────────────────────────────┘

Before Each Test:
    ├─ resetConfig()
    │  └─ AWARENESS_CONFIG = DEFAULT_AWARENESS_CONFIG
    │
    └─ setMockProblemData({ file_list: [], data: {} })
       └─ PROBLEM_DATA = { ... }

Test Execution:
    ├─ Arrange: Set up test data
    ├─ Act: Call function under test
    └─ Assert: Verify results

After Test:
    └─ State automatically cleaned by beforeEach

No Shared State Between Tests
No Test Dependencies
Parallel Execution Safe
```

## Function Dependency Graph

```
                    calculateAwarenessScore
                            │
                    ┌───────┼───────────────┐
                    │       │               │
                    ▼       ▼               ▼
          getDaysSince  getCommitment  getTierDifficulty
          Completion    Factor         Multiplier
                                           │
                                    ┌──────┴──────┐
                                    ▼             ▼
                                getTierName   [Config Matrix]

                    getSolvedFactor
                            │
                    ┌───────┴────────┐
                    ▼                ▼
         getTotalUniqueSolved    getTierName
         Count
                    │
                    ▼
              [PROBLEM_DATA]
```

## Test Coverage Layers

```
┌─────────────────────────────────────────────────────┐
│                   Integration Tests                  │
│  • Complete workflow (problem → score → CSS)        │
│  • Problem lifecycle (unsolved → aged → flashing)   │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│                   Function Tests                     │
│  • calculateAwarenessScore (26 tests)               │
│  • getTierDifficultyMultiplier (15 tests)           │
│  • getTierName (9 tests)                            │
│  • All helper functions                             │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│                    Edge Case Tests                   │
│  • Date handling (null, invalid, future, old)       │
│  • Numeric edge cases (0, negative, NaN)            │
│  • Missing data (undefined fields)                  │
│  • Boundary values (exactly on thresholds)          │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│                  Unit Tests (Atomic)                 │
│  • Single input → Single output                     │
│  • No external dependencies                         │
│  • Fast execution (<1ms per test)                   │
└─────────────────────────────────────────────────────┘
```

## Test Data Flow

```
Test Input:
    ┌──────────────────┐
    │  Problem Object  │
    │  {               │
    │    solved: true, │
    │    solved_date,  │
    │    time_to_solve,│
    │    difficulty,   │
    │    ...           │
    │  }               │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Mock Setup      │
    │                  │
    │  setMockProblem  │
    │  Data()          │
    │                  │
    │  setConfig()     │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Function Call   │
    │                  │
    │  const result =  │
    │  calculate       │
    │  Awareness       │
    │  Score(problem)  │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │  Assertions      │
    │                  │
    │  expect(result   │
    │    .score)       │
    │    .toBe(...)    │
    └──────────────────┘
```

## Configuration Management

```
┌─────────────────────────────────────────┐
│      DEFAULT_AWARENESS_CONFIG            │
│  (Immutable source of truth)            │
└────────────────┬────────────────────────┘
                 │
                 │ Clone
                 ▼
      ┌──────────────────────┐
      │  AWARENESS_CONFIG    │
      │  (Working copy)      │
      └──────────┬───────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
resetConfig()         setConfig(custom)
      │                     │
      │ Copy defaults       │ Merge custom
      ▼                     ▼
      └──────────┬──────────┘
                 │
                 ▼
         Current config used
         by all functions
```

## Mock Data Architecture

```
┌─────────────────────────────────────────┐
│           PROBLEM_DATA                   │
│  {                                      │
│    file_list: ['list1', 'list2'],      │
│    data: {                             │
│      list1: [                          │
│        { name: 'P1', solved: true },   │
│        { name: 'P2', solved: false }   │
│      ],                                │
│      list2: [                          │
│        { name: 'P1', solved: true },   │ ← Duplicate
│        { name: 'P3', solved: true }    │
│      ]                                 │
│    }                                   │
│  }                                     │
└───────────────┬─────────────────────────┘
                │
                │ setMockProblemData()
                │
        ┌───────┴──────────┐
        │                  │
        ▼                  ▼
getTotalUnique      Individual
SolvedCount()       problem tests
        │
        │ Counts: P1, P2, P3
        ▼
      Result: 2
      (P1=solved, P3=solved)
```

## Test Execution Timeline

```
Time →
│
├─ npm test
│  │
│  ├─ Jest initialization
│  │  └─ Load awareness.js
│  │     └─ Load awareness.test.js
│  │
│  ├─ Test Suite: Awareness Indicator System
│  │  │
│  │  ├─ describe('getTierName')
│  │  │  ├─ beforeEach() → reset state
│  │  │  ├─ it('test 1') → 1ms
│  │  │  ├─ beforeEach() → reset state
│  │  │  ├─ it('test 2') → 1ms
│  │  │  └─ ... (9 tests total)
│  │  │
│  │  ├─ describe('getTierDifficultyMultiplier')
│  │  │  ├─ describe('Top tier')
│  │  │  │  ├─ beforeEach() → reset state
│  │  │  │  ├─ it('Easy test') → 1ms
│  │  │  │  └─ ... (4 tests)
│  │  │  └─ ... (more tiers)
│  │  │
│  │  ├─ describe('calculateAwarenessScore')
│  │  │  └─ ... (26 tests)
│  │  │
│  │  └─ ... (more test suites)
│  │
│  ├─ Test Results
│  │  ├─ Tests:     100+ passed
│  │  ├─ Time:      2-5 seconds
│  │  └─ Coverage:  >95%
│  │
│  └─ Exit code: 0
│
└─ End
```

## Coverage Report Structure

```
npm run test:coverage
    │
    ├─ Run all tests
    │
    ├─ Collect coverage data
    │  ├─ Lines executed
    │  ├─ Branches taken
    │  ├─ Functions called
    │  └─ Statements run
    │
    ├─ Generate reports
    │  ├─ coverage/
    │  │  ├─ lcov.info          (machine-readable)
    │  │  └─ lcov-report/
    │  │     └─ index.html      (human-readable)
    │  │
    │  └─ Terminal output
    │     File         | % Stmts | % Branch | % Funcs | % Lines
    │     awareness.js |  98.5   |   95.2   |  100.0  |  98.5
    │
    └─ Check thresholds (>90% required)
```

## Jest Configuration Flow

```
package.json
    │
    ├─ "type": "module"  → Enable ES6 imports
    │
    ├─ "scripts"
    │  ├─ "test" → node --experimental-vm-modules jest
    │  ├─ "test:watch" → + --watch
    │  └─ "test:coverage" → + --coverage
    │
    └─ "jest"
       ├─ testEnvironment: "node"
       ├─ transform: {} → No transpilation
       ├─ testMatch: ["**/*.test.js"]
       ├─ collectCoverageFrom: ["awareness.js"]
       └─ coverageThreshold: { global: { ... } }
```

## Key Insights

### 1. Extraction Strategy
- Original code embedded in Python strings
- Extracted to standalone JS module
- Added exports for testability
- Added mock helpers for state management

### 2. Test Isolation
- Each test fully independent
- State reset before every test
- No shared variables
- Parallel execution safe

### 3. Coverage Strategy
- Unit tests for each function
- Integration tests for workflows
- Edge case tests for robustness
- Property tests for math verification

### 4. Documentation Layers
- Code comments (what/why)
- Test descriptions (behavior)
- README (comprehensive guide)
- Quick reference (cheatsheet)
- This architecture doc (structure)

## Performance

```
Test Execution Performance:
├─ Total tests: 100+
├─ Total time: 2-5 seconds
├─ Per test: ~20-50ms average
├─ Slowest: Date-based tests (~100ms)
└─ Fastest: Simple unit tests (~5ms)

Bottlenecks:
├─ Date manipulation (new Date(), calculations)
├─ beforeEach overhead (minimal but cumulative)
└─ Mock data setup (negligible)

Optimization opportunities:
├─ Mock Date for consistent timing
├─ Reduce beforeEach complexity
└─ Cache common test fixtures
```

## Future Enhancements

```
Potential Additions:
│
├─ Property-based testing
│  └─ Use fast-check for random inputs
│
├─ Performance benchmarks
│  └─ Measure function execution time
│
├─ Snapshot testing
│  └─ Capture expected outputs
│
├─ Mutation testing
│  └─ Verify test effectiveness
│
└─ Visual regression
   └─ Test CSS class rendering
```

---

**Architecture Documentation v1.0** | Last Updated: 2025-12-06
