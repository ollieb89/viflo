# Phase 6 Verification: Test Suite

**Phase:** 6
**Name:** Test Suite
**Date Completed:** 2026-02-23
**Requirements:** QUAL-03, QUAL-04, QUAL-05

---

## What Was Built

### Summary

Phase 6 added a Vitest test suite to the `apps/web/` package, testing two utility functions that dogfood viflo's own file formats (skill frontmatter validation and plan parsing). A coverage ratchet script was created to prevent coverage regression between runs. The CI workflow was updated to run tests and the coverage ratchet on every push and PR.

### Artifacts Created

| Artifact | Location | Purpose |
|----------|----------|---------|
| Web package config | `apps/web/package.json` | Package with Vitest scripts and @viflo/web identity |
| TypeScript config | `apps/web/tsconfig.json` | TypeScript configuration for apps/web |
| Vitest config | `apps/web/vitest.config.ts` | Vitest configuration with V8 coverage provider |
| Skill validation | `apps/web/src/validation/skill.ts` | Validates SKILL.md YAML frontmatter |
| Skill validation tests | `apps/web/src/validation/skill.test.ts` | 8 tests for skill validation |
| Plan parsing | `apps/web/src/parsing/plan.ts` | Parses PLAN.md XML structure |
| Plan parsing tests | `apps/web/src/parsing/plan.test.ts` | 5 tests for plan parsing |
| Coverage ratchet | `apps/web/scripts/coverage-ratchet.ts` | Enforces coverage never decreases |
| Coverage baseline | `apps/web/.coverage/baseline.json` | Stored baseline at 98.11% lines |

### Files Modified

| File | Changes |
|------|---------|
| `.github/workflows/ci.yml` | Added "Run coverage ratchet" step after test step |
| `package.json` (root) | Updated test scripts to delegate to `apps/web` via pnpm filter |

---

## Verification Checklist

### Vitest Test Suite (QUAL-03)

- [x] `apps/web/` package exists with `package.json` and `vitest.config.ts`
- [x] `src/validation/skill.ts` — `validateSkillFrontmatter()` utility function
- [x] `src/validation/skill.test.ts` — 8 tests covering valid/invalid frontmatter
- [x] `src/parsing/plan.ts` — `parsePlanFile()` and `countTasksByType()` utility functions
- [x] `src/parsing/plan.test.ts` — 5 tests covering plan parsing scenarios
- [x] All 13 tests pass: `pnpm test` exits 0
- [x] ≥1 test per utility function (4 functions, 13 tests total)

### CI Integration (QUAL-04)

- [x] Root `package.json` test script delegates to `pnpm --filter @viflo/web test`
- [x] `.github/workflows/ci.yml` includes "Run tests" step calling `pnpm run test`
- [x] CI step "Run coverage ratchet" runs after tests
- [x] Pipeline fails if any test fails (sequential fail-fast job)

### Coverage Ratchet (QUAL-05)

- [x] `apps/web/scripts/coverage-ratchet.ts` exists and is executable
- [x] `apps/web/.coverage/baseline.json` exists with baseline at 98.11% lines
- [x] Ratchet reads `coverage/coverage-summary.json` after Vitest run
- [x] Ratchet fails with non-zero exit code on coverage regression
- [x] Ratchet auto-updates baseline when coverage improves
- [x] CI workflow includes "Run coverage ratchet" step that will fail pipeline on regression

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Vitest over Jest** | Per 06-CONTEXT.md: Vitest is the standard for modern TypeScript projects |
| **Scope to `apps/web/`** | Per 06-CONTEXT.md: isolated package with its own test configuration |
| **Coverage ratchet as separate script** | Separates "run tests" from "enforce coverage" — more composable |
| **V8 coverage provider** | Built-in to Node, no additional instrumentation needed |
| **Dogfood viflo formats** | Utility functions test viflo's own SKILL.md and PLAN.md file formats |
| **Baseline stored in `.coverage/`** | Separate from `coverage/` (generated) to distinguish stored vs ephemeral |

---

## Test Results

### Test Suite Output

```
 ✓ src/validation/skill.test.ts (8 tests)
 ✓ src/parsing/plan.test.ts (5 tests)

 Test Files  2 passed (2)
 Tests       13 passed (13)
 Duration    ~500ms
```

### Coverage

| Metric | Value |
|--------|-------|
| Lines | 98.11% |
| Functions | 100.00% |
| Branches | 95.45% |
| Statements | 98.11% |

Per-file breakdown:

| File | Statements | Branches | Functions | Lines |
|------|-----------|----------|-----------|-------|
| `parsing/plan.ts` | 100% | 100% | 100% | 100% |
| `validation/skill.ts` | 95.91% | 92.30% | 100% | 95.91% |

---

## Issues Encountered

| Issue | Resolution |
|-------|------------|
| Coverage ratchet CI step ran from repo root (wrong directory) | Added `working-directory: apps/web` to the "Run coverage ratchet" step in `ci.yml`; also added separate `apps/web` dependency install step |

---

## Commit References

Phase 6 commits from git log (2026-02-23):

- `feat(06-01)` — Add Vitest test suite for skill validation and plan parsing utilities
- `feat(06-02)` — Add coverage ratchet script and CI integration
- `fix(ci)` — Run coverage ratchet from apps/web directory
- `fix(ci)` — Install apps/web dependencies in CI workflow

---

*Verification completed as part of v1.1 Dogfooding milestone.*
