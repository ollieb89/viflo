---
phase: 16-cli-foundation
plan: "01"
subsystem: infra
tags:
  [nodejs, commonjs, path-resolution, idempotency, file-writing, sentinel-merge]

requires: []
provides:
  - "resolveViFloRoot(): returns absolute path to viflo repo root via __dirname (never process.cwd)"
  - "resolveTargetPath(cwd, ...segments): throws on missing/non-string cwd; otherwise path.resolve"
  - "writeCLAUDEmd(targetCwd, sentinelContent): idempotent sentinel-block merge into CLAUDE.md"
  - "writeSettingsJson(targetCwd, incomingSettings): idempotent deep-merge into .claude/settings.json"
affects:
  - phase-17-minimal-init
  - phase-18-full-init
  - phase-19-update

tech-stack:
  added: []
  patterns:
    - "sentinel-merge: indexOf+slice (not regex) replaces <!-- BEGIN VIFLO --> / <!-- END VIFLO --> block"
    - "writeIfChanged: compute-then-compare prevents unnecessary disk writes and preserves idempotency"
    - "deepMerge: existing-first Set spread for array deduplication preserves stable ordering"
    - "CommonJS-only bin/lib layer: no build step, no external deps, directly require()-able"

key-files:
  created:
    - bin/lib/paths.cjs
    - bin/lib/writers.cjs
  modified: []

key-decisions:
  - "Sentinel format is <!-- BEGIN VIFLO --> / <!-- END VIFLO --> (plan specified this; not the stale viflo:start/end format noted in STATE.md)"
  - "resolveViFloRoot() uses __dirname not process.cwd() — deterministic regardless of where node is invoked from"
  - "resolveTargetPath has no default for cwd — required argument, throws immediately on falsy or non-string"
  - "indexOf+slice used for sentinel replacement instead of regex — avoids regex escaping pitfalls on marker text"
  - "existing-first in Set spread ([...existing, ...incoming]) — stable deduplication order preserves user entries"
  - "Trailing newline added to JSON output (JSON.stringify + '\\n') — avoids POSIX lint noise"

patterns-established:
  - "writeIfChanged pattern: all writes go through single helper that returns { written, reason } and skips unchanged content"
  - "ENOENT-as-null pattern: fs.readFileSync wrapped in try/catch, ENOENT returns null (not throw)"
  - "Two-level __dirname resolution: bin/lib/paths.cjs -> __dirname/../.. = repo root"

requirements-completed:
  - INIT-05

duration: 2min
completed: 2026-02-24
---

# Phase 16 Plan 01: CLI Foundation Summary

**CommonJS path utilities and idempotent file writers for viflo init — resolveViFloRoot/\_\_dirname-based root detection, sentinel-merge CLAUDE.md, and Set-dedup deep-merge settings.json**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-24T12:42:13Z
- **Completed:** 2026-02-24T12:44:13Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `bin/lib/paths.cjs` delivers deterministic repo-root and target-path resolution using `__dirname` — no `process.cwd()`, no `~` literals
- `bin/lib/writers.cjs` provides fully idempotent CLAUDE.md sentinel merge (indexOf+slice) and settings.json deep merge (Set dedup, existing-first order)
- Both functions return `{ written: boolean, reason: string }` and log a skip message when content is unchanged
- INIT-05 (idempotency requirement) satisfied at the library level: sentinel merge and Set-dedup prevent content destruction on re-run

## Task Commits

Each task was committed atomically:

1. **Task 1: Create bin/lib/paths.cjs** - `abe7610` (feat)
2. **Task 2: Create bin/lib/writers.cjs** - `be80ac0` (feat)

## Files Created/Modified

- `bin/lib/paths.cjs` - resolveViFloRoot() and resolveTargetPath(cwd, ...segments) — Node.js built-ins only
- `bin/lib/writers.cjs` - writeCLAUDEmd and writeSettingsJson — idempotent writers using paths.cjs

## Decisions Made

- Sentinel format confirmed as `<!-- BEGIN VIFLO -->` / `<!-- END VIFLO -->` per plan (not the stale `viflo:start`/`viflo:end` mentioned in STATE.md decisions log)
- `indexOf` + `slice` used for sentinel block replacement instead of regex — avoids escaping edge cases
- Existing-first ordering in `[...new Set([...existing, ...incoming])]` ensures user-added array entries are preserved at the front

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The shell escaped `!` characters in Node.js `-e` one-liners, so verification was run via a temporary script file; script was deleted before commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `bin/lib/paths.cjs` and `bin/lib/writers.cjs` are ready for Phase 17 (--minimal init) and Phase 18 (--full init) to require directly
- No blockers or concerns

---

_Phase: 16-cli-foundation_
_Completed: 2026-02-24_
