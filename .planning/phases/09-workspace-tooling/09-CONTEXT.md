# Phase 9: Workspace & Developer Tooling - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Ensure CI clones work reliably with explicit workspace topology and developer onboarding automates pre-commit hook installation. Delivers `pnpm-workspace.yaml`, CI pipeline simplification (single install), and a `make setup` target for new contributors.

</domain>

<decisions>
## Implementation Decisions

### Pre-commit automation method
- Use a **Makefile target** (`make setup`) as the automation mechanism
- `make setup` runs: `pnpm install` + `pre-commit install` — complete onboarding in one command
- Check if Makefile exists first — add the target if it does, create a new Makefile if it doesn't
- No guard for `pre-commit` being installed — fail naturally with the tool's own error message

### Claude's Discretion
- Onboarding documentation placement (README vs CONTRIBUTING.md) and depth
- CI pipeline restructuring specifics (how the workflow file is modified for single `pnpm install`)
- `pnpm-workspace.yaml` exact scope (success criteria specify `apps/*` and `packages/*`)
- Any additional Makefile targets (e.g., `make help`, `make lint`)

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for CI restructuring and docs placement.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-workspace-tooling*
*Context gathered: 2026-02-24*
