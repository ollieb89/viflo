# Phase 20: Gate Enforcement Hardening - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Repository-level quality and security gates are deterministic, active, and reproducible locally. This phase covers merge-blocking CI gate enforcement, local parity command path, pre-commit secret scanning enforcement, and bootstrap/refresh of security hooks. It does not add new capabilities beyond gate hardening.

</domain>

<decisions>
## Implementation Decisions

### CI gate trigger policy

- Enforcement runs on both PR and push.
- Push workflow runs on `main` and `release/*` only as a fast pre-merge safety net.
- PR workflow runs on all PRs targeting protected branches, with full enforcement.
- Protected branches are `main` and `release/*`.
- Draft PRs still run checks, but enforcement is required when PR is marked Ready for review.
- Skipped checks do not satisfy merge requirements by default.
- A maintainer may override skipped-check enforcement only via audited override label (example: `ci-override`).

### Local parity command experience

- Provide both a canonical full parity command and per-gate commands.
- One canonical full parity command that mirrors CI.
- Per-gate commands for fast local iteration.
- Full parity execution runs all gates, reports all failures, and exits non-zero.
- Output is sectioned by gate with clear pass/fail status for scanability and deterministic CI mirroring.
- On failure, include lightweight actionable next-step hints per gate (including example fix command).
- Do not auto-execute fixes.

### Secret-scan enforcement behavior

- Pre-commit secret scanning hard-blocks on any finding.
- False-positive/exception handling requires maintainer-reviewed baseline/allowlist updates.
- Rollout allows baseline usage so only new findings block commits.
- Exceptions must be auditable via versioned baseline updates and explicit PR rationale.
- Versioned baseline/allowlist file changes.
- Explicit PR explanation for the exception.

### Bootstrap/install flow for security hooks

- Hook setup uses both auto-attempt and explicit re-run paths.
- Auto-attempt during setup/onboarding.
- Explicit re-run command as deterministic recovery path.
- If setup fails locally, onboarding continues with clear warning and remediation steps.
- Setup command auto-refreshes hooks when drift/version mismatch is detected.
- Canonical setup docs live in both README and CONTRIBUTING, cross-linked.

### Claude's Discretion

- Exact command names and script naming for full parity vs per-gate entrypoints.
- Exact warning text and remediation copy shown when hook bootstrap fails.
- Exact audited metadata shape for override label usage and where it is recorded.

</decisions>

<specifics>
## Specific Ideas

- Push gate scope should remain a fast "pre-merge safety net" (`main` and `release/*` only).
- Draft PR checks should surface results early for iteration before formal Ready-for-review enforcement.
- Security model should stay simple for contributors: any secret finding blocks by default.
- Determinism/trust constraint: no auto-fix execution in parity command output.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

_Phase: 20-gate-enforcement-hardening_
_Context gathered: 2026-02-25_
