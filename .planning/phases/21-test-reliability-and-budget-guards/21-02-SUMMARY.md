---
phase: 21-test-reliability-and-budget-guards
plan: "02"
subsystem: test-policy
tags: [llm, cost-control, guardrails, docs]
requires:
  - phase: 21-test-reliability-and-budget-guards
    provides: deterministic baseline test gate from 21-01
provides:
  - default-off LLM-assisted test wrapper with explicit opt-in
  - low-cost/local profile enforcement with fail-closed behavior
  - unit-tested LLM test gate policy module
  - README/CONTRIBUTING policy documentation and cross-links
affects: [contributor-workflow, test-policy, cost-controls]
tech-stack:
  added: [bash guard wrapper, validation module + tests]
  patterns: [explicit opt-in, fail-closed profile validation]
key-files:
  created:
    - scripts/run-llm-tests.sh
    - apps/web/src/validation/llm-test-gate.ts
    - apps/web/src/validation/llm-test-gate.test.ts
  modified:
    - package.json
    - apps/web/package.json
    - README.md
    - CONTRIBUTING.md
key-decisions:
  - "Keep LLM-assisted tests completely outside default `test`/`gate:test` command paths."
  - "Require `RUN_LLM_TESTS=1` plus `TEST_MODEL_PROFILE=local|budget`; reject unsupported profiles."
patterns-established:
  - "LLM Guard Pattern: default-off wrapper, explicit opt-in, fail-closed profile validation."
duration: 11 min
completed: 2026-02-25
---

# Phase 21 Plan 02: LLM Cost Guard Summary

**LLM-assisted tests are now default-off and can only run via explicit low-cost/local opt-in path, with policy logic covered by unit tests and documented for contributors.**

## Performance

- **Duration:** 11 min
- **Tasks:** 3
- **Files modified:** 4
- **Files created:** 3

## Accomplishments

- Added `scripts/run-llm-tests.sh` guard wrapper:
  - default mode exits without running LLM tests,
  - opt-in requires `RUN_LLM_TESTS=1`,
  - profile must be `local` or `budget`,
  - invalid profile fails non-zero with remediation output.
- Added root `test:llm` command and workspace `@viflo/web test:llm` placeholder path.
- Added `evaluateLlmTestGate()` policy module and tests covering allow/deny scenarios.
- Added README and CONTRIBUTING sections documenting default-off policy, explicit opt-in command, allowed profiles, and failure behavior.

## Verification Run Results

Executed in this session:

- `bash scripts/run-llm-tests.sh` -> **pass** (default-off message, no LLM tests run)
- `RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=local bash scripts/run-llm-tests.sh` -> **pass**
- `RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=premium bash scripts/run-llm-tests.sh` -> **fail closed** (exit code 2)
- `pnpm --filter @viflo/web run test src/validation/llm-test-gate.test.ts` -> **pass**
- `rg -n "LLM-Assisted Test Policy|RUN_LLM_TESTS|TEST_MODEL_PROFILE|test:llm|local|budget" README.md CONTRIBUTING.md` -> **pass** (policy sections present)

## Deviations from Plan

- None beyond normal refinement of script wording and docs placement.

## Next Phase Readiness

- COST-01 guard behavior is in place and documented.
- Phase 21 is ready for verification and roadmap/state updates.
