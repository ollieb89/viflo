## Backlog checkpoint: G-02, G-03, G-04 complete

Completed:
- G-02 local secret-prevention wiring:
  - Added root scripts: `prepare` (husky) and `precommit:secrets`.
  - Added executable `scripts/precommit-secrets.sh` with `gitleaks protect --staged --config .gitleaks.toml`.
  - Added `.husky/pre-commit` to run lint, CLI tests, and secrets scan.
  - Added `.gitleaks.toml` with baseline allowlist for placeholders/docs.
  - Added/updated CLI tests asserting hook/config/script wiring.
- G-03 expanded apps/web live test suite:
  - Added `apps/web/src/live/sc-reflect-live.ts` for repo-root discovery and artifact marker validation.
  - Added `apps/web/src/live/sc-reflect-live.test.ts` with success and error-path coverage.
- G-04 coverage ratchet hardening:
  - Added `apps/web/src/live/coverage-ratchet.test.ts` with script-level behavior tests.
  - Updated `apps/web/scripts/coverage-ratchet.ts`:
    - CI now fails when baseline is missing.
    - Check mode no longer auto-updates baseline on improvement.
    - Baseline updates remain explicit via `test:coverage:update`.

Validation evidence:
- `pnpm run validate:sc-prompts` PASS
- `pnpm run bench:sc-reflect` PASS
- `pnpm run test:cli` PASS
- `pnpm --filter @viflo/web run test` PASS
- `pnpm --filter @viflo/web run test:coverage:ratchet` PASS (coverage improved above baseline)

Notes:
- Coverage baseline is intentionally not auto-updated in check mode; run update command when intentionally ratcheting baseline.
- GitHub-side required-check configuration remains branch protection/ruleset settings, outside repository files.