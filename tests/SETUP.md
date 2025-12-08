# Test Setup Guide

Quick guide to get the awareness indicator tests up and running.

## Prerequisites

1. Node.js (version 14 or higher)
2. npm (comes with Node.js)

## Quick Start

```bash
# Navigate to tests directory
cd D:\src\neetcode-coding-challenges-tracker\awareness-indicator\tests

# Install dependencies
npm install

# Run tests
npm test
```

## What Gets Installed

The `npm install` command installs:
- **Jest**: Testing framework (v29.7.0)
- Jest automatically installs its dependencies

Total install size: ~50-60 MB

## Expected Output

After running `npm test`, you should see:

```
PASS  tests/awareness.test.js
  Awareness Indicator System
    getTierName
      ✓ should return "below" for missing time_to_solve
      ✓ should return "below" for zero time_to_solve
      ... (more tests)
    getTierDifficultyMultiplier
      Top tier
        ✓ should return 0 for Easy (mastered)
        ... (more tests)
    calculateAwarenessScore
      ... (45+ tests)
    ... (more test suites)

Test Suites: 1 passed, 1 total
Tests:       100+ passed, 100+ total
Snapshots:   0 total
Time:        2-5s
```

## Running Specific Tests

### Run tests matching a pattern
```bash
npm test -- -t "calculateAwarenessScore"
```

### Run in watch mode (re-runs on file changes)
```bash
npm run test:watch
```

### Generate coverage report
```bash
npm run test:coverage
```

Coverage report will be in `coverage/lcov-report/index.html`

## Test Files

1. **awareness.js**
   - Extracted JavaScript functions from the Python generator
   - Made testable by exporting functions and adding mock helpers
   - This is the code under test

2. **awareness.test.js**
   - 100+ unit tests
   - Covers all functions and edge cases
   - Uses Jest's describe/it/expect syntax

3. **package.json**
   - Jest configuration
   - Test scripts
   - Dependencies

## Troubleshooting

### Issue: "npm: command not found"
**Solution**: Install Node.js from nodejs.org

### Issue: "Cannot find module 'jest'"
**Solution**: Run `npm install` in the tests directory

### Issue: Tests fail with module errors
**Solution**:
- Check Node.js version: `node --version` (should be 14+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

### Issue: "Experimental modules" warning
**Solution**: This is expected. Jest uses experimental VM modules for ES6 import/export

### Issue: Permission denied on Windows
**Solution**: Run terminal as administrator or check antivirus settings

## Test Development Workflow

1. **Make changes to awareness.js**
   ```bash
   # Edit awareness.js to add/modify functions
   ```

2. **Add corresponding tests**
   ```bash
   # Edit awareness.test.js to add tests
   ```

3. **Run tests in watch mode**
   ```bash
   npm run test:watch
   ```

4. **Check coverage**
   ```bash
   npm run test:coverage
   ```

5. **Verify >90% coverage maintained**
   ```
   File            | % Stmts | % Branch | % Funcs | % Lines
   ----------------|---------|----------|---------|--------
   awareness.js    |   98.5  |   95.2   |  100.0  |  98.5
   ```

## Integration with Build Process

These tests are standalone and don't affect the main build process:

```
awareness-indicator/
├── build_tracker.py          # Main build (generates tracker.html)
├── js_awareness_generator.py # Generates awareness JS code
└── tests/                    # Standalone test suite
    ├── awareness.js          # Extracted functions for testing
    └── awareness.test.js     # Tests
```

The tests verify the logic that gets embedded in `tracker.html`, but they're separate from the actual build.

## Next Steps

After setup:

1. Read [README.md](README.md) for detailed test documentation
2. Run `npm test` to verify everything works
3. Explore test output and coverage reports
4. Try modifying tests to understand the system

## CI/CD Integration (Future)

To integrate with CI/CD:

```yaml
# .github/workflows/test.yml
name: Test Awareness Indicators

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd tests && npm install
      - run: cd tests && npm test
      - run: cd tests && npm run test:coverage
```

## Questions?

1. Check [README.md](README.md) for detailed documentation
2. Review test code comments in awareness.test.js
3. Examine the generated JS in js_awareness_generator.py
