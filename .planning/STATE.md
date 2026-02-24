# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.5 milestone)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** Planning next milestone — run `/gsd:new-milestone` to define v1.6

## Current Position

Phase: —
Plan: —
Status: v1.5 milestone complete — all phases shipped, archived, git tagged
Last activity: 2026-02-24 — v1.5 milestone archived: viflo init CLI (Phases 17–19), 55/55 tests, all requirements satisfied

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

- Re-verify Claude Code user-scope permissions.allow bug (#5140) for next milestone

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-24
Stopped at: v1.5 milestone complete and archived
Resume with: `/gsd:new-milestone` to start v1.6 planning
