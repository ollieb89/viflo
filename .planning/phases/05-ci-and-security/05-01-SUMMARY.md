# Phase 5, Plan 1: GitHub Actions CI + Branch Protection — Summary

**Completed:** 2026-02-23  
**Status:** ✅ Complete

---

## Files Created

| File | Purpose |
|------|---------|
| `package.json` | Root workspace config with CI scripts |
| `.nvmrc` | Node version pin (20) |
| `.github/workflows/ci.yml` | GitHub Actions pipeline definition |

---

## CI Scripts (package.json)

```json
{
  "lint": "prettier --check \"**/*.{md,yaml,yml,json}\" --ignore-path .gitignore",
  "lint:fix": "prettier --write \"**/*.{md,yaml,yml,json}\" --ignore-path .gitignore",
  "type-check": "echo 'type-check: no TS sources at root (documentation repo)' && exit 0",
  "test": "echo 'test: no test suite yet (Phase 6)' && exit 0",
  "build": "echo 'build: documentation repo — no build step' && exit 0"
}
```

- **lint**: Runs Prettier on markdown, YAML, and JSON files
- **type-check**: Placeholder (exits 0) — no TypeScript at root
- **test**: Placeholder (exits 0) — Vitest suite coming in Phase 6
- **build**: Placeholder (exits 0) — documentation repo has no build

All scripts exit 0 in a clean CI environment without secrets.

---

## Workflow Configuration

**Job ID:** `build` (this is the required status check name)

**Triggers:**
- `push` to `main`
- `pull_request` to `main`

**Steps (sequential, fail-fast):**
1. Checkout repository (`actions/checkout@v4`)
2. Setup pnpm (`pnpm/action-setup@v4`)
3. Setup Node.js (`actions/setup-node@v4` with pnpm caching)
4. `pnpm install --frozen-lockfile`
5. `pnpm run lint`
6. `pnpm run type-check`
7. `pnpm run test`
8. `pnpm run build`

**Pinned action versions:**
- `actions/checkout@v4`
- `pnpm/action-setup@v4`
- `actions/setup-node@v4`

---

## Branch Protection Settings

Set via GitHub CLI (`gh api`):

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["build"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
```

- Requires the `build` status check to pass before merging
- Strict mode: requires branches to be up-to-date before merging
- No admin enforcement (admins can bypass if needed)

---

## Prettier Formatting

Applied `pnpm run lint:fix` to fix all existing formatting issues:
- 146 markdown files reformatted
- YAML/JSON files normalized
- All files now pass `prettier --check`

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Single job vs parallel jobs | Per 05-CONTEXT.md: "single job with sequential steps" for simplicity |
| pnpm caching | `actions/setup-node@v4` with `cache: pnpm` for efficient installs |
| Placeholder scripts | Documentation repo has no app to build; Phase 6 adds real test suite |
| Prettier for linting | Standard formatter for markdown/YAML/JSON in documentation repos |
| `lint:fix` script | Convenience for fixing formatting without manual `prettier --write` |

---

## Verification

```bash
# Verify package.json scripts
node -e "const p = require('./package.json'); console.log(Object.keys(p.scripts))"

# Verify CI workflow
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('valid')"

# Verify .nvmrc
cat .nvmrc  # → 20

# Verify branch protection
gh api repos/ollieb89/viflo/branches/main/protection
```

---

## Requirements Closed

- ✅ **CI-01**: Push/PR triggers GitHub Actions workflow automatically
- ✅ **CI-02**: Pipeline runs install → lint → type-check → test → build with fail-fast
- ✅ **CI-03**: Branch protection enforces passing `build` check before merge
