# Phase 6, Plan 2: Coverage Ratchet — Summary

**Completed:** 2026-02-23  
**Status:** ✅ Complete

---

## Files Created/Modified

| File                                   | Purpose                      | Status   |
| -------------------------------------- | ---------------------------- | -------- |
| `apps/web/scripts/coverage-ratchet.ts` | Coverage ratchet script      | Created  |
| `apps/web/.coverage/baseline.json`     | Coverage baseline storage    | Created  |
| `apps/web/package.json`                | Updated with ratchet scripts | Modified |
| `.github/workflows/ci.yml`             | Added coverage ratchet step  | Modified |

---

## Coverage Ratchet Script

**Location:** `apps/web/scripts/coverage-ratchet.ts`

### Features

- Reads coverage from `coverage/coverage-summary.json`
- Compares against `.coverage/baseline.json`
- Fails if any metric decreases by >0.01%
- Auto-updates baseline when coverage improves
- Creates initial baseline if none exists

### Usage

```bash
# Check coverage against baseline (fails if regression)
pnpm run test:coverage:ratchet

# Update baseline to current coverage
pnpm run test:coverage:update
```

### Commands

| Command           | Behavior                                          |
| ----------------- | ------------------------------------------------- |
| `check` (default) | Compares current vs baseline, fails on regression |
| `update`          | Updates baseline to current coverage              |

---

## Baseline File Format

**Location:** `apps/web/.coverage/baseline.json`

```json
{
  "version": "1.0.0",
  "timestamp": "2026-02-23T21:36:54.176Z",
  "coverage": {
    "lines": 98.11,
    "functions": 100,
    "branches": 95.45,
    "statements": 98.11
  }
}
```

---

## CI Integration

The CI workflow now includes the coverage ratchet step:

```yaml
- name: Run tests
  run: pnpm run test

- name: Run coverage ratchet
  run: pnpm run test:coverage:ratchet

- name: Run build
  run: pnpm run build
```

The ratchet runs after tests and will fail the pipeline if coverage regresses.

---

## Example Output

### Successful Check

```
📊 Coverage Comparison
   Current:  lines: 98.11%, functions: 100.00%, branches: 95.45%, statements: 98.11%
   Baseline: lines: 98.11%, functions: 100.00%, branches: 95.45%, statements: 98.11%

✅ Coverage meets baseline
```

### Regression Detected

```
📊 Coverage Comparison
   Current:  lines: 95.00%, functions: 100.00%, branches: 90.00%, statements: 95.00%
   Baseline: lines: 98.11%, functions: 100.00%, branches: 95.45%, statements: 98.11%

❌ Coverage regression detected:
   • lines: 98.11% → 95.00% (-3.11%)
   • branches: 95.45% → 90.00% (-5.45%)

To update baseline (if intentional):
   pnpm run test:coverage:update
```

### Baseline Update

```
✅ Coverage baseline updated
   lines: 98.11%, functions: 100.00%, branches: 95.45%, statements: 98.11%
```

---

## Verification

```bash
# Test ratchet check (should pass with current coverage)
cd apps/web && pnpm run test:coverage:ratchet

# Verify baseline file exists
cat apps/web/.coverage/baseline.json

# Verify CI step is present
grep -A1 "Run coverage ratchet" .github/workflows/ci.yml
```

---

## Requirements Closed

- ✅ **QUAL-05**: Coverage ratchet script enforces that coverage percentage never decreases between runs
