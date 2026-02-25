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
- PR checks run on every PR update (`opened`, `synchronize`, `reopened`) including draft PRs.
- PR checks on draft PRs are informative; merge-required enforcement applies once PR is marked Ready for review.
- Push enforcement runs on `main` and `release/*` only (no additional branches by default).
- If `hotfix/*` is introduced later, it should follow the same push-enforcement policy as `release/*`.
- Merge blocking must key off individual required checks for `lint`, `typecheck`, `test`, and `build`.
- A combined/aggregate status may exist for visibility, but must not replace individual required gates.
- Skipped required checks (path filters, `[skip ci]`, conditionals, etc.) do not satisfy merge requirements by default.

### Override and audit policy

- Override authority is restricted to a specific authorized team (for example `maintainers` / `release-managers`), not all write access and not repo-admin-only by default.
- Use a single override label (`ci-override`) initially.
- Override scope must be explicitly declared in PR context: which gate(s) are overridden and whether the condition is skip vs fail.
- Override usage requires mandatory PR audit evidence:
- Reason (why override is justified).
- Scope (gate(s): lint/typecheck/test/build; skip vs fail).
- Tracking link (issue/incident/ticket).
- Expiry (date or explicit condition).
- Approver evidence (authorized label applier plus approving review).
- Audit evidence should be captured via a fixed PR comment template and/or required PR checklist item.
- Override may persist through merge when audit evidence is complete (no pre-merge label removal requirement).

### Local parity command path and output contract

- Exactly one canonical root command path is the source of truth for docs and tooling.
- Optional per-gate shortcuts are allowed for faster local iteration.
- Canonical parity execution runs all gates and returns a final summary; exits non-zero if any gate fails.
- Output contract includes sectioned plain-text output by gate (default) with clear pass/fail reporting.
- Output contract also includes optional machine-readable JSON mode (for example `--json`) for tooling/editor integrations.
- Failure output includes short, concrete suggested commands per failed gate; no auto-fix execution.

### Secret-scan enforcement behavior

- Pre-commit secret scanning hard-blocks on any finding.
- Blocking applies immediately for all contributors (no grace "first commit" bypass).
- False-positive/exception handling uses baseline/allowlist updates with auditable PR rationale.
- Baseline/allowlist file ownership is enforced via CODEOWNERS to security/maintainer owners.
- Normal CODEOWNERS review is sufficient for allowlist/baseline changes; no requirement to route through the CI-override team.

### Bootstrap/install flow for security hooks

- Hook setup uses both auto-attempt and explicit re-run paths.
- Auto-attempt during setup/onboarding.
- Explicit re-run command as deterministic recovery path.
- If setup fails locally, onboarding continues with loud, explicit warning and remediation steps.
- Warning must clearly state commits/PRs will fail CI until hooks are installed, and include exact command/docs pointer.
- Setup/bootstrap auto-refreshes hooks when drift/version mismatch is detected.
- Parity command checks for hook drift on each run and reports drift details to the user.
- Canonical setup docs live in both README and CONTRIBUTING, cross-linked.

### Claude's Discretion

- Exact command names for canonical parity and per-gate shortcuts.
- Exact plain-text/JSON schema details for parity command output, as long as required fields above are preserved.
- Exact warning copy format and placement, as long as warnings remain explicit and actionable.
- Exact implementation of drift detection messaging and optional manual refresh flag naming.

</decisions>

<specifics>
## Specific Ideas

- Push gate scope should remain a fast "pre-merge safety net" (`main` and `release/*` only).
- If `hotfix/*` is introduced, treat it like `release/*` for push enforcement.
- Draft PR checks should surface results early for iteration before formal Ready-for-review enforcement.
- Security model should stay simple for contributors: any secret finding blocks by default.
- Determinism/trust constraint: no auto-fix execution in parity command output.
- Aggregate CI status is acceptable for dashboard visibility, but merge policy remains anchored to individual gate checks.

</specifics>

<deferred>
## Deferred Ideas

Per-gate override labels are intentionally deferred; continue with single `ci-override` unless ambiguity/abuse indicates the need for finer-grained labels in a later phase.

</deferred>

---

_Phase: 20-gate-enforcement-hardening_
_Context gathered: 2026-02-25_
