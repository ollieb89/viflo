# Phase 16: CLI Foundation - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Create `bin/lib/paths.cjs` and `bin/lib/writers.cjs` as the shared foundation for all later CLI phases. This phase delivers only the low-level path resolution utilities and file-write primitives — no CLI commands, no user-facing behaviour, no orchestration logic.

</domain>

<decisions>
## Implementation Decisions

### Idempotency signal
- Both writers return a status object: `{ written: boolean, reason: string }` — e.g. `{ written: false, reason: 'unchanged' }`
- When skipping, writers also emit `console.log` with a human-readable skip message (visible during debug/dev)
- "Unchanged" detection: compute what would be written, compare via string equality against current file contents
- Idempotency applies to **both** writers — CLAUDE.md merge and settings.json merge

### CLAUDE.md sentinel behavior
- Sentinel format: HTML comment tags — `<!-- BEGIN VIFLO -->` and `<!-- END VIFLO -->`
- If CLAUDE.md exists but has no sentinel markers: **append** the sentinel block at end (non-destructive)
- If CLAUDE.md does not exist: **create the file** with the sentinel block as its content
- If multiple sentinel blocks detected: **throw an error with a clear message** — do not guess which to update

### settings.json merge strategy
- Conflicting scalar values: **viflo wins** — viflo's value overwrites the existing one
- Unknown/unmanaged keys in existing file: **preserved** — merge is additive for viflo's keys only
- Array values: **union merge with Set-based dedup** — existing items stay, viflo items added if not already present
- Nested objects: **deep merge** — viflo can set `settings.foo.bar` without wiping `settings.foo.baz`

### Path API contract
- `cwd` parameter (for target-project paths): **required** — explicit, avoids silent `process.cwd()` bugs
- Return type: **absolute string paths** — plain strings, no custom objects
- Viflo root resolution: **`__dirname`-based** — resolves upward from the module's own location
- Export style: **individual named exports** — `const { resolveViFloRoot, resolveTargetPath } = require('./paths')`

### Claude's Discretion
- Exact function names beyond the shape described above
- Specific `console.log` message text for skip signals
- Internal helper organisation within each file
- Test fixture structure and temp-dir setup approach

</decisions>

<specifics>
## Specific Ideas

- No `~` literals anywhere in path construction — all paths via `path.join` / `path.resolve` / `__dirname`
- `cwd` must be explicit so callers cannot accidentally inherit the wrong working directory when the CLI is invoked from an arbitrary directory

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 16-cli-foundation*
*Context gathered: 2026-02-24*
