# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.6 milestone kickoff)

**Core value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.
**Current focus:** Milestone v1.6 planning and phase kickoff

## Current Position

Phase: 21-test-reliability-and-budget-guards
Plan: Context gathered (pre-planning)
Status: Ready for planning
Last activity: 2026-02-25 — Captured 21-CONTEXT.md with reliability, coverage, and LLM cost-control decisions

## Accumulated Context

### Key Decisions (summary — full log in PROJECT.md)

- [v1.4]: Sentinel format `<!-- BEGIN VIFLO -->` / `<!-- END VIFLO -->` — locked, not the stale viflo:start/end format
- [v1.4]: resolveViFloRoot() uses `__dirname` not `process.cwd()` — deterministic regardless of invocation directory
- [v1.4]: Write to project-scope `.claude/settings.json` only — user-scope deferred due to active Claude Code bug #5140
- [v1.4]: vitest installed at workspace root for CLI tests; web app tests remain unaffected
- [v1.5]: scanSkills accepts rootDir explicitly — pure function, testable with any temp directory
- [v1.5]: writePlanningScaffold uses fs.existsSync (skip-if-exists) — planning files preserve user edits
- [v1.5]: `merged` label at CLI call-site, not in writers — writers return `updated`, CLI maps context
- [v1.5]: No shebang required — npm bin wiring via package.json `bin` field is sufficient for .cjs files
- [v1.6 / 20-01]: Canonical gate execution path is `scripts/quality-gate.sh`; CI and local scripts route through it
- [v1.6 / 20-01]: Required checks remain individual jobs: `lint`, `typecheck`, `test`, `build`; aggregate job is visibility-only
- [v1.6 / 20-01]: Phase executed with `git commit --no-verify` per explicit user instruction due unrelated pre-existing hook failures
- [v1.6 / 20-01]: `rg`-based fallback verification used where `yq` is unavailable in environment
- [v1.6 / 20-02]: Override path uses single `ci-override` label with fail-closed validation for mandatory evidence (reason/scope/tracking/expiry/approver evidence) and authorized team membership checks.
- [v1.6 / 20-02]: Deterministic hook lifecycle path is `bash scripts/setup-security-hooks.sh`; `setup-dev.sh` auto-attempts and continues with explicit CI-impact warning + remediation command on failure.
- [v1.6 / 20-02]: `scripts/quality-gate.sh` reports hook drift on every run with exact remediation command and no auto-fix behavior.
- [v1.6 / 20-02]: `.secrets.baseline` and `.gitleaks.toml` are CODEOWNERS-protected; baseline/allowlist changes require auditable PR rationale and standard owner review.

### Pending Todos

- Re-verify Claude Code user-scope permissions.allow bug (#5140) for future milestone planning

### Blockers/Concerns

- `yq` is not installed locally, so YAML-query verification commands require fallback tooling.
- `pre-commit` is not installed in this environment and cannot be installed due restricted network access; secret-scan hook verification depth is limited to script/path checks.
- Husky pre-commit currently fails on unrelated pre-existing CLI test failures; plan task commits required `--no-verify` per user instruction.

## Session Continuity

Last session: 2026-02-25
Stopped at: Phase 21 context gathered
Resume with: `/gsd-plan-phase 21`
