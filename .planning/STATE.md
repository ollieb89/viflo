# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.6 milestone kickoff)

**Core value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.
**Current focus:** Milestone v1.6 planning and phase kickoff

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-02-24 — Milestone v1.6 started (Infrastructure Hardening & Quality Gates)

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

### Pending Todos

- Re-verify Claude Code user-scope permissions.allow bug (#5140) for future milestone planning

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-24
Stopped at: Milestone v1.6 initialized (requirements + roadmap defined)
Resume with: `/gsd-plan-phase 20` to begin execution
