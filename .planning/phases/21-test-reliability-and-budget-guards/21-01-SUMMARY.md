---
phase: 21-test-reliability-and-budget-guards
plan: "01"
subsystem: web-testing
tags: [vitest, coverage, quality-gate, ci]
requires:
  - phase: 20-gate-enforcement-hardening
    provides: canonical gate runner and CI/local parity pattern
provides:
  - canonical `gate:test` path now runs web tests + coverage ratchet
  - CI test gate comment and enforcement alignment for coverage ratchet
  - stable coverage-ratchet live test execution without subprocess spawning
affects: [phase-21-plan-02, ci-test-gate]
tech-stack:
  added: [node-executed coverage ratchet script]
  patterns: [single test parity path, fail-closed coverage regression guard]
key-files:
  created:
    - apps/web/scripts/coverage-ratchet.cjs
  modified:
    - package.json
    - scripts/quality-gate.sh
    - .github/workflows/ci.yml
    - apps/web/package.json
    - apps/web/src/live/coverage-ratchet.test.ts
key-decisions:
  - "Route test gate through `pnpm run test:web:ci` so CI/local parity includes both unit tests and coverage ratchet."
  - "Avoid subprocess/chdir worker constraints in Vitest by running coverage-ratchet in-process in tests."
patterns-established:
  - "Test Gate Parity: `gate:test` invokes `test:web:ci` (web test + ratchet) in one canonical path."
  - "Coverage Ratchet Runtime: node-executable cjs script with explicit base-dir override for deterministic tests."
duration: 39 min
completed: 2026-02-25
---

# Phase 21 Plan 01: Test Reliability and Coverage Guard Summary

**`gate:test` now enforces `apps/web` tests plus coverage ratchet via one canonical CI/local path, and the coverage-ratchet live tests are stable in this environment.**

## Performance

- **Duration:** 39 min
- **Tasks:** 3
- **Files modified:** 6
- **Files created:** 1

## Accomplishments

- Added root `test:web:ci` script and wired `scripts/quality-gate.sh` test command to use it.
- Kept CI test job on canonical runner path and documented that it includes ratchet enforcement.
- Migrated ratchet runtime invocation from `tsx` to `node` CJS script for deterministic execution.
- Refactored `coverage-ratchet.test.ts` to run ratchet logic in-process, avoiding worker subprocess restrictions.

## Verification Run Results

Executed in this session:

- `pnpm --filter @viflo/web run test src/live/coverage-ratchet.test.ts src/validation/llm-test-gate.test.ts` -> **pass** (8 tests)
- `pnpm --filter @viflo/web run test` -> **pass** (25 tests)
- `pnpm --filter @viflo/web run test:coverage:ratchet` -> **pass**
- `pnpm run gate:test` -> **pass**
- `bash scripts/quality-gate.sh --gate test --json` -> **pass** (`summary.failed: 0`, command `pnpm run test:web:ci`)

Observed environment caveat (non-blocking for plan scope):

- Hook drift is reported in gate output (`hook missing; pre-commit command missing`) because `pre-commit` is not installed in this environment.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Vitest worker sandbox denied subprocess/chdir behavior in coverage-ratchet live test**

- **Found during:** Task 3 verification
- **Issue:** `spawnSync ... EPERM` and `process.chdir() is not supported in workers`
- **Fix:** Introduced `apps/web/scripts/coverage-ratchet.cjs`, exported `main()`, and updated live tests to run ratchet in-process with `COVERAGE_RATCHET_CWD` override.
- **Files modified:** `apps/web/src/live/coverage-ratchet.test.ts`, `apps/web/scripts/coverage-ratchet.cjs`, `apps/web/package.json`

---

**Total deviations:** 1 auto-fixed (1 blocking)

## Next Phase Readiness

- Ready for `21-02-PLAN.md` execution (LLM budget guard path), with TEST-01/TEST-02/TEST-03 enforcement in place.
