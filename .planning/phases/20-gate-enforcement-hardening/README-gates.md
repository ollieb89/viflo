# Phase 20 Gate Enforcement Policy

This note defines deterministic quality-gate usage and required-check setup for Phase 20.

## Local Gate Commands

- Canonical full run: `pnpm run quality-gate`
- Per-gate shortcuts:
- `pnpm run gate:lint`
- `pnpm run gate:typecheck`
- `pnpm run gate:test`
- `pnpm run gate:build`

All commands route through the canonical runner `scripts/quality-gate.sh`.

## Required Checks for Branch Protection / Rulesets

Configure these exact required status checks:

- `lint`
- `typecheck`
- `test`
- `build`

## Enforcement Notes

- `quality-gates` is an aggregate visibility job only. It must not replace individual required checks.
- Skipped checks do not satisfy required merge gates by default.
- CI trigger policy for this phase:
- `pull_request` on `main` and `release/*` for `opened`, `synchronize`, `reopened`
- `push` on `main` and `release/*`
- `merge_group` enabled for merge queue parity

## Future Branch Policy

If `hotfix/*` is introduced later, apply the same push gate policy used for `release/*`.
