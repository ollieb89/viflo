# Phase 9: Workspace & Developer Tooling — Context

## Overview

**Phase Goal**: Fresh CI clones work reliably without workarounds, and developer onboarding automates pre-commit hook installation  
**Requirements**: CI-02 (gap closure), QUAL-01, QUAL-02 (gap closure)  
**Depends on**: Phase 8

## Current State Analysis

### CI Issue (WORKAROUND EXISTS)

Current `.github/workflows/ci.yml` has a workaround:

```yaml
- run: pnpm install --frozen-lockfile
- run: cd apps/web && pnpm install --frozen-lockfile # WORKAROUND
```

**Root Cause**: `pnpm-workspace.yaml` doesn't properly declare workspace topology.

**Target**: Single `pnpm install` at root should install all workspace dependencies.

### Pre-commit Hook Installation (MANUAL)

Current state: Developers must manually run `pre-commit install` after cloning.

**Target**: Automated via setup script or Makefile target.

## Success Criteria

1. ✅ `pnpm-workspace.yaml` declares `apps/*` and `packages/*`
2. ✅ CI pipeline uses single `pnpm install` (no separate `apps/web` step)
3. ✅ `pre-commit install` automated via setup script
4. ✅ `README.md` or `CONTRIBUTING.md` references onboarding command

## Proposed Plans

Based on the 4 success criteria, I expect **2 plans**:

### 09-01: Workspace Configuration (CI-02 gap closure)

- Fix `pnpm-workspace.yaml` to properly declare workspaces
- Update CI to use single `pnpm install`
- Verify workspace dependencies are linked correctly
- Test CI pipeline end-to-end

### 09-02: Developer Onboarding Automation (QUAL-01, QUAL-02 gap closure)

- Create `scripts/setup-dev.sh` or Makefile target for setup
- Automate `pre-commit install` in setup script
- Update `CONTRIBUTING.md` with onboarding instructions
- Test fresh clone → setup → dev ready workflow

## Open Questions

1. **Setup script vs Makefile**:
   - Option A: `scripts/setup-dev.sh` (consistent with existing scripts)
   - Option B: Makefile (common convention)
   - **Decision**: Option A — consistent with existing script structure

2. **Workspace glob patterns**:
   - Should use `apps/*` and `packages/*` for future extensibility
   - Currently only have `apps/web/`

## Dependencies

- pnpm 10.6.5 (already installed)
- pre-commit (already configured)

## Verification Strategy

1. Clean clone test: `git clone && pnpm install && pnpm test` (should work)
2. CI test: Push to branch, verify single install step
3. Fresh dev test: New clone → setup script → pre-commit hooks active
