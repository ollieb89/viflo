# Phase 21: Test Reliability and Budget Guards - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers a reliable, measurable test safety net for `apps/web` and enforces budget-safe controls for optional LLM-assisted tests. Scope is limited to baseline test reliability, coverage regression protection, and explicit low-cost/local gating behavior.

</domain>

<decisions>
## Implementation Decisions

### Web Test Reliability Baseline
- `apps/web` unit tests must run in both local parity and CI paths.
- The baseline must include at least five stable tests that target core components/utilities with low flake risk.
- Any flaky test discovered during this phase should be stabilized or replaced before baseline is considered complete.

### Coverage Regression Guard
- Coverage regression must fail CI when coverage drops below the established baseline.
- Baseline should be explicit and version-controlled so changes are intentional and reviewable.
- Coverage checks should be deterministic and runnable from the same command path used in CI.

### LLM-Assisted Test Cost Controls
- LLM-assisted test paths are off by default.
- Enabling LLM-assisted tests requires explicit opt-in at runtime.
- Opt-in mode must enforce low-cost/local profile constraints and fail closed when constraints are not met.

### Claude's Discretion
- Exact file layout for test fixtures/helpers and baseline metadata.
- Concrete mechanism for enforcing low-cost/local constraints (env policy, script guard, or both).
- Naming conventions for scripts and CI job labels, as long as they remain clear and consistent.

</decisions>

<specifics>
## Specific Ideas

- Preserve parity with Phase 20’s canonical gate flow so reliability checks are easy to run locally and in CI.
- Keep failure messages actionable (what failed, expected baseline, how to remediate).
- Avoid introducing expensive/default-on LLM calls in standard test commands.

</specifics>

<deferred>
## Deferred Ideas

- Rich LLM test quality dashboards and trend analytics.
- Broader cross-package test infrastructure redesign outside `apps/web` baseline scope.

</deferred>

---

*Phase: 21-test-reliability-and-budget-guards*
*Context gathered: 2026-02-25*
