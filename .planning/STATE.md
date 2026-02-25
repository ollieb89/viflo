# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.6 milestone kickoff)

**Core value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.
**Current focus:** Milestone v1.6 planning and phase kickoff

## Current Position

Phase: 20-gate-enforcement-hardening
Plan: 20-01 complete (1/2)
Status: In progress
Last activity: 2026-02-25 — Executed 20-01 (quality-gate runner + CI gate jobs + gate policy note)

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

### Pending Todos

- Re-verify Claude Code user-scope permissions.allow bug (#5140) for future milestone planning

### Blockers/Concerns

- `pnpm run gate:test` and full `pnpm run quality-gate` timed out in this environment (exit 124); follow-up needed in phase 20-02 or dedicated debug pass.
- `yq` is not installed locally, so YAML-query verification commands from plan require fallback tooling.

## Session Continuity

Last session: 2026-02-25
Stopped at: Completed 20-01-PLAN.md
Resume with: `/gsd-execute-phase 20` to execute 20-02-PLAN.md
