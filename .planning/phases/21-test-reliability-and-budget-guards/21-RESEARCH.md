# Phase 21: Test Reliability and Budget Guards - Research

**Researched:** 2026-02-25
**Domain:** `apps/web` test reliability baseline, coverage regression enforcement, and fail-closed budget guards for optional LLM-assisted test paths
**Confidence:** HIGH

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

- `apps/web` tests must run in both local parity and CI paths.
- Baseline includes at least five stable tests for core components/utilities.
- Flaky tests found during this phase must be stabilized or replaced.
- Coverage regression must fail CI when coverage drops below explicit baseline.
- Coverage baseline must be version-controlled and intentionally updated.
- LLM-assisted test paths must be off by default.
- LLM-assisted test paths require explicit runtime opt-in.
- Opt-in mode must enforce low-cost/local constraints and fail closed on invalid config.

### Claude's Discretion

- Exact file layout for test helpers and baseline metadata.
- Concrete mechanism for low-cost/local enforcement (env policy, script guard, or both).
- Naming of scripts and CI labels.

### Deferred Ideas (OUT OF SCOPE)

- LLM test quality dashboards and trends.
- Cross-package test infra redesign beyond `apps/web` baseline.

---

## Phase Requirements

| ID      | Description                                                                              | Research Support                                                                       |
| ------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| TEST-01 | `apps/web` has a working Vitest setup that runs in CI                                    | Vitest is present and currently wired through root `gate:test` path                    |
| TEST-02 | `apps/web` includes at least 5 baseline unit tests                                       | Current suite has 17 passing tests across core parsing/validation/live checks          |
| TEST-03 | Coverage ratchet blocks CI when coverage falls below locked baseline                     | Ratchet script + baseline exist, but CI test gate does not yet enforce ratchet         |
| COST-01 | LLM-assisted tests disabled by default and only run in low-cost/local mode when explicit | No standardized guard wrapper exists yet; needs explicit fail-closed policy entrypoint |

---

## Summary

Phase 21 is mostly scaffolded, but not yet fully enforced. `apps/web` already has Vitest setup, baseline tests, and a coverage-ratchet implementation. The remaining work is to make the CI/local parity path deterministic for coverage enforcement and to add an explicit, fail-closed guard for any optional LLM-assisted test mode.

Current evidence from repository inspection:

- Root gate runner executes `pnpm run test` via `scripts/quality-gate.sh`, and root `test` maps to `pnpm --filter @viflo/web test`.
- `apps/web` has Vitest config and baseline tests (`plan`, `skill`, and `sc-reflect-live` suites).
- Coverage ratchet is implemented in `apps/web/scripts/coverage-ratchet.ts` and baseline is checked into `apps/web/.coverage/baseline.json`.
- CI `test` job currently runs only `bash scripts/quality-gate.sh --gate test`, which does not include `test:coverage:ratchet`.

Reliability risk discovered during validation: one live test file (`coverage-ratchet.test.ts`) shells out to `npx tsx` from temp directories, which can cause nondeterministic behavior in constrained/non-interactive environments. This is fixable by avoiding `npx` resolution in temp dirs (invoke `tsx` via project-resolved path or run Node directly on compiled/ts runtime entrypoint).

**Primary recommendation:** keep `scripts/quality-gate.sh` as canonical parity runner, but make `gate:test` enforce both unit tests and coverage ratchet in CI-equivalent mode; then add an explicit LLM-test guard script that defaults off and allows execution only when opt-in + approved low-cost/local profile are both present.

---

## Standard Stack

### Core

| Tool                                | Version / Source                       | Purpose                     | Why Standard                                        |
| ----------------------------------- | -------------------------------------- | --------------------------- | --------------------------------------------------- |
| Vitest                              | `apps/web` (`vitest` 1.x)              | Unit test execution         | Already integrated and stable for current web tests |
| V8 coverage (`@vitest/coverage-v8`) | `apps/web`                             | Coverage metrics generation | Already configured in `vitest.config.ts`            |
| Coverage ratchet script             | `apps/web/scripts/coverage-ratchet.ts` | Baseline regression guard   | Existing implementation matches TEST-03 intent      |
| Root gate runner                    | `scripts/quality-gate.sh`              | Local/CI command parity     | Existing canonical gate entrypoint from Phase 20    |

### Supporting

| Tool                                              | Purpose                       | When to Use                          |
| ------------------------------------------------- | ----------------------------- | ------------------------------------ |
| `apps/web/.coverage/baseline.json`                | Locked coverage baseline      | Required artifact for ratchet checks |
| Root `package.json` scripts (`gate:test`, `test`) | Unified command surface       | CI and local parity invocation       |
| GitHub Actions `ci.yml` `test` job                | Required merge gate execution | Must call parity test+coverage path  |

### Alternatives Considered

| Instead of                           | Could Use                     | Tradeoff                                                                          |
| ------------------------------------ | ----------------------------- | --------------------------------------------------------------------------------- |
| Coverage ratchet script              | Vitest static thresholds only | Static thresholds are coarse; ratchet preserves non-regression from real baseline |
| Requiring LLM tests in normal `test` | Separate opt-in guard command | Keeping default tests deterministic/cost-free is safer and matches COST-01        |
| `npx tsx` in temp dirs               | Project-resolved runner       | `npx` from temp dirs can prompt/install and create flake/hang risk                |

---

## Architecture Patterns

### Pattern 1: Canonical Test Gate Includes Coverage Ratchet

**What:** Keep one parity command path, but ensure `gate:test` includes ratchet check (directly or via root script chain).

**Recommended shape:**

- Root `gate:test` -> web unit tests + coverage ratchet.
- CI `test` job remains `bash scripts/quality-gate.sh --gate test`.
- Local dev runs same gate command for exact parity.

### Pattern 2: Baseline Is Immutable in CI

**What:** CI check mode must fail if baseline is missing or regressed; never auto-write baseline in CI.

**Why:** Keeps baseline updates explicit and reviewable in PRs.

### Pattern 3: Fail-Closed LLM Test Guard

**What:** Add a dedicated wrapper command for optional LLM-assisted tests.

**Policy shape (recommended):**

- Default behavior: exit with message (`RUN_LLM_TESTS=1` required).
- Opt-in requires approved profile variable (for example `TEST_MODEL_PROFILE=local|budget`).
- Any other value fails closed with actionable remediation.
- This command is excluded from default CI `test` gate unless explicitly needed by a separate, opt-in workflow.

### Pattern 4: Stabilize Test Runner Calls in Live Tests

**What:** Replace `npx tsx` from temp working dirs with deterministic invocation strategy.

**Why:** Prevent tool resolution hangs and preserve reliability in CI/non-interactive shells.

---

## Don't Hand-Roll

| Problem                             | Don't Build                                  | Use Instead                                            | Why                                      |
| ----------------------------------- | -------------------------------------------- | ------------------------------------------------------ | ---------------------------------------- |
| Coverage regression logic           | Custom ad-hoc shell parsing of coverage text | Existing `coverage-ratchet.ts` JSON-summary comparison | Already deterministic and baseline-aware |
| LLM cost policy spread across tests | Per-test ad-hoc env checks                   | Single guard wrapper command                           | Centralized policy, easier audit         |
| Separate local/CI test flows        | Distinct command sets                        | Root gate + web scripts parity                         | Prevents drift and reproducer mismatch   |

---

## Common Pitfalls

### Pitfall 1: Coverage appears implemented but is not enforced by CI gate

**What goes wrong:** TEST-03 is technically present in code but not active in merge-blocking path.
**How to avoid:** Make CI `test` gate run ratchet check as part of canonical command.

### Pitfall 2: Baseline mutates implicitly

**What goes wrong:** Baseline changes outside explicit update flow.
**How to avoid:** Keep update command separate (`test:coverage:update`) and require PR review for baseline diffs.

### Pitfall 3: Tool resolution flake from `npx` in temporary dirs

**What goes wrong:** Tests hang/fail non-deterministically due to package resolution prompts.
**How to avoid:** Invoke project-resolved runtime path, not temp-dir `npx` fallback.

### Pitfall 4: LLM tests accidentally become default path

**What goes wrong:** Costly network/model-dependent checks run on normal `test`.
**How to avoid:** Dedicated opt-in command plus explicit profile guard; keep default test path offline and deterministic.

---

## Code Examples (Planner Seed)

### Example: explicit root test scripts for parity + ratchet

```json
{
  "scripts": {
    "test": "pnpm --filter @viflo/web run test",
    "test:web:ci": "pnpm --filter @viflo/web run test && pnpm --filter @viflo/web run test:coverage:ratchet",
    "gate:test": "bash scripts/quality-gate.sh --gate test"
  }
}
```

### Example: fail-closed LLM test guard contract

```bash
# scripts/run-llm-tests.sh
# default off
[[ "${RUN_LLM_TESTS:-0}" == "1" ]] || { echo "LLM tests disabled. Set RUN_LLM_TESTS=1."; exit 0; }
case "${TEST_MODEL_PROFILE:-}" in
  local|budget) ;;
  *) echo "Invalid TEST_MODEL_PROFILE. Use local|budget."; exit 2 ;;
esac
pnpm --filter @viflo/web run test:llm
```

---

## Open Questions (for planner)

1. Should `gate:test` call a dedicated `test:web:ci` script, or should root `test` itself include ratchet for maximum simplicity?
2. Should LLM opt-in checks live in one script at repo root, or in `apps/web` with root forwarding command?
3. Should the `coverage-ratchet.test.ts` execution strategy be refactored first (reliability), before wiring stricter CI enforcement?
4. Do we require CODEOWNERS review on `.coverage/baseline.json` changes in this phase, or leave as standard review?

---

## Sources

### Repository Evidence (HIGH)

- `/package.json` (gate/test script wiring and parity entrypoints)
- `/.github/workflows/ci.yml` (current required gates and CI test command)
- `/scripts/quality-gate.sh` (canonical gate orchestration)
- `/apps/web/package.json` (web test + coverage scripts)
- `/apps/web/vitest.config.ts` (coverage reporter configuration)
- `/apps/web/scripts/coverage-ratchet.ts` (baseline comparison and CI fail behavior)
- `/apps/web/.coverage/baseline.json` (current locked baseline artifact)
- `/apps/web/src/parsing/plan.test.ts` (baseline tests)
- `/apps/web/src/validation/skill.test.ts` (baseline tests)
- `/apps/web/src/live/sc-reflect-live.test.ts` (baseline tests)
- `/apps/web/src/live/coverage-ratchet.test.ts` (ratchet behavior tests and runner risk)
