# Phase 21 Plan 2: LLM Test Budget Guards — Summary

**Phase:** 21-test-reliability-and-budget-guards  
**Plan:** 2  
**Status:** ✅ Complete  
**Executed:** 2026-02-25

---

## What Was Delivered

### 1. llm-test-gate.ts

- `evaluateLlmTestGate(input)` function
- Default deny when `RUN_LLM_TESTS` not set
- Requires `TEST_MODEL_PROFILE=local|budget`
- Fail-closed on invalid configuration
- Returns structured decision with reason

### 2. llm-test-gate.test.ts (5 tests)

- Default denial (no opt-in)
- Opt-in with local profile
- Opt-in with budget profile
- Denial with missing profile
- Denial with unsupported profile

### 3. run-llm-tests.sh

- Environment validation gate
- Graceful skip when disabled
- Clear error messages with remediation
- Exit code 0 (skip), 2 (invalid config)

### 4. package.json Scripts

- `test:llm` placeholder in apps/web
- `test:llm` workspace script calling run-llm-tests.sh

---

## Usage

```bash
# LLM tests disabled by default (exits 0)
pnpm run test:llm

# Run with local profile
RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=local pnpm run test:llm

# Run with budget profile
RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=budget pnpm run test:llm

# Invalid profile fails closed (exit 2)
RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=premium pnpm run test:llm
```

---

## Requirements Satisfied

| Requirement                                        | Status |
| -------------------------------------------------- | ------ |
| COST-01: LLM tests off by default, explicit opt-in | ✅     |
