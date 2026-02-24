# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.5 milestone start)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** v1.5 — viflo init CLI (Phases 17–19)

## Current Position

Phase: 17 — Minimal Mode
Plan: 2/3
Status: In progress — Plan 17-02 complete
Last activity: 2026-02-24 — Plan 17-02 complete: bin/viflo.cjs CLI entry point implemented with 7 integration tests (35 total passing)

## Accumulated Context

### Key Decisions (summary — full log in PROJECT.md)

- [v1.4]: Sentinel format `<!-- BEGIN VIFLO -->` / `<!-- END VIFLO -->` — locked, not the stale viflo:start/end format
- [v1.4]: resolveViFloRoot() uses `__dirname` not `process.cwd()` — deterministic regardless of invocation directory
- [v1.4]: Write to project-scope `.claude/settings.json` only — user-scope deferred due to active Claude Code bug #5140
- [v1.4]: vitest installed at workspace root for CLI tests; web app tests remain unaffected
- [v1.4]: agent-architecture 503 lines accepted — 4/5 skills within limit is the valid pass state
- [17-01]: scanSkills accepts rootDir explicitly — caller passes resolveViFloRoot(), keeps function pure and testable
- [17-01]: ENOENT returns [] — new projects without .agent/skills/ dir are a normal state, not an error
- [17-02]: argv positional-path detection skips args starting with '--' — allows flag/path order flexibility
- [17-02]: defaultSettings nests allow under permissions to match real Claude Code settings.json schema
- [17-02]: No shebang added to bin/viflo.cjs — Phase 19 handles bin wiring as planned

### Pending Todos

- Re-verify Claude Code user-scope permissions.allow bug (#5140) status at Phase 17 implementation time
- Update research/ files stale sentinel references before Phase 17 research begins

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-24
Stopped at: Completed 17-02-PLAN.md — bin/viflo.cjs CLI entry point + 7 integration tests, 35/35 tests passing
Resume with: `/gsd:execute-phase 17` to continue with Plan 17-03 (if exists) or next phase
