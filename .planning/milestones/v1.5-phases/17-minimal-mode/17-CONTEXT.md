# Phase 17: Minimal Mode - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire up `bin/viflo.cjs` as the CLI entry point and implement the `--minimal` flag end-to-end. Running `viflo init --minimal` in any project writes a sentinel-wrapped `@`-import block into CLAUDE.md (all viflo skills) and deep-merges safe default permissions into `.claude/settings.json`. Idempotent on re-run. The `--full` flag, `--dry-run`, labelled output, and `package.json` bin wiring are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Skill selection

- Import ALL skills found in `.agent/skills/` — no curated subset
- Discovery via **filesystem scan** at runtime (enumerate directories in `.agent/skills/`), not INDEX.md or a hardcoded list. New skills added to viflo are automatically included without code changes.
- `@`-import paths use the **absolute path to viflo's install location** (resolved via `__dirname` at runtime, same pattern as Phase 16's `resolveViFloRoot()`). Paths must work from the target project, not relative to it.
- On re-run when sentinel block already exists: **re-scan and add missing `@` lines**. Existing lines are preserved, newly discovered skills are appended inside the sentinel block, manually removed lines are left as-is. Block grows but never loses entries.

### Target path behaviour

- Default target is **`process.cwd()`** — standard Unix tool behaviour. User `cd`s to their project, then runs `viflo init --minimal`.
- An **optional positional argument** is accepted after the flag: `viflo init --minimal [path]`. Falls back to cwd if omitted. Useful for scripting.
- Argument position: `viflo init --minimal [path]` — path comes after the flag.
- If the target path does not exist: **error with clear message** (`Directory not found: /abs/path`) and exit non-zero. Do not silently create it.

### Claude's Discretion

- Exact console output format for Phase 17 (Phase 19 formalises labelled output — Phase 17 just needs something reasonable)
- The specific `permissions.allow` entries that constitute "safe defaults" for `.claude/settings.json`
- How `bin/viflo.cjs` parses flags (`process.argv`, minimist, etc.)
- Error handling for read-only files or missing write permissions

</decisions>

<specifics>
## Specific Ideas

- The sentinel block pattern and merge logic already exist in `bin/lib/writers.cjs` (Phase 16). Phase 17 wires these into the CLI — the heavy lifting is done.
- `resolveViFloRoot()` from `bin/lib/paths.cjs` should be used to build absolute skill paths — consistent with existing patterns.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

_Phase: 17-minimal-mode_
_Context gathered: 2026-02-24_
