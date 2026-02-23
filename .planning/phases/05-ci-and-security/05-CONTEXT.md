# Phase 5: CI & Security - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up GitHub Actions CI pipeline (install → lint → type-check → test → build) that runs automatically on push and pull_request events, with branch protection on `main` enforcing passing checks, plus pre-commit secret scanning using `gitleaks` and `detect-secrets` to block any committed secrets.

</domain>

<decisions>
## Implementation Decisions

### Pre-commit tooling

- Use the Python `pre-commit` framework with `.pre-commit-config.yaml` as the authoritative config
- Run both `gitleaks` and `detect-secrets` — overlapping coverage is intentional
- Secrets scanning only — no lint or type-check in pre-commit (those run in CI)
- No existing Makefile or package.json `prepare` script; developer installation documented in README/CONTRIBUTING (Claude decides exact format — likely `pip install pre-commit && pre-commit install`)

### CI pipeline structure

- Single job with sequential steps: install → lint → type-check → test → build
- Fails fast when any step fails (GitHub Actions default)
- Targets Node 20 LTS (no `.nvmrc` or engines constraint in repo; pnpm lockfile v9 requires Node 18+)
- pnpm store caching enabled via `actions/setup-node` or `actions/cache`
- Triggers on both `push` (to main) and `pull_request` events

### Branch protection

- Not explicitly discussed — Claude decides based on standard practice: protect `main`, require the CI status check to pass, no admin bypass

### Claude's Discretion

- Exact `actions/cache` vs `actions/setup-node` pnpm caching approach
- Whether to pin action versions (e.g. `actions/checkout@v4`) — standard to pin
- `detect-secrets` baseline file management (`.secrets.baseline` — standard)
- Branch protection settings beyond requiring the CI check
- Node version file (`.nvmrc`) — may add for consistency
- Developer onboarding documentation format in CONTRIBUTING.md

</decisions>

<specifics>
## Specific Ideas

No specific references — open to standard approaches. Requirements (CI-01, CI-02, CI-03, QUAL-01, QUAL-02) are the authoritative spec.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

_Phase: 05-ci-and-security_
_Context gathered: 2026-02-23_
