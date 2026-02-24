# Phase 16: CLI Foundation - Research

**Researched:** 2026-02-24
**Domain:** Node.js CommonJS path utilities and idempotent file writers
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Idempotency signal:** Both writers return `{ written: boolean, reason: string }`. When skipping, also emit `console.log` with a human-readable skip message. "Unchanged" detection: compute what would be written, compare via string equality against current file contents.
- **CLAUDE.md sentinel behavior:**
  - Sentinel format: `<!-- BEGIN VIFLO -->` and `<!-- END VIFLO -->` (HTML comment tags)
  - If CLAUDE.md exists, no sentinels: **append** sentinel block at end (non-destructive)
  - If CLAUDE.md does not exist: **create** the file with the sentinel block as its content
  - If multiple sentinel blocks detected: **throw an error with a clear message** — do not guess
- **settings.json merge strategy:**
  - Conflicting scalar values: **viflo wins** — viflo's value overwrites existing
  - Unknown/unmanaged keys in existing file: **preserved** — additive for viflo's keys only
  - Array values: **union merge with Set-based dedup** — existing items stay, viflo items added if not present
  - Nested objects: **deep merge** — viflo can set `settings.foo.bar` without wiping `settings.foo.baz`
- **Path API contract:**
  - `cwd` parameter (for target-project paths): **required** — explicit, avoids silent `process.cwd()` bugs
  - Return type: **absolute string paths** — plain strings, no custom objects
  - Viflo root resolution: **`__dirname`-based** — resolves upward from the module's own location
  - Export style: **individual named exports** — `const { resolveViFloRoot, resolveTargetPath } = require('./paths')`

### Claude's Discretion

- Exact function names beyond the shape described above
- Specific `console.log` message text for skip signals
- Internal helper organisation within each file
- Test fixture structure and temp-dir setup approach

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INIT-05 | Re-running `viflo init` on an existing project does not overwrite customized content (CLAUDE.md outside sentinel block, existing `.planning/` files, existing settings.json entries) | Idempotency patterns: string-equality check before write, sentinel-aware merge, Set-based JSON array dedup |
</phase_requirements>

---

## Summary

Phase 16 creates two CommonJS library modules — `bin/lib/paths.cjs` and `bin/lib/writers.cjs` — that form the stable, tested foundation for all subsequent `viflo init` CLI phases. The path module provides deterministic, absolute-path resolution: viflo's own root via `__dirname` traversal, and any target-project path via an explicit `cwd` argument. The writers module encodes the idempotency contract (compute-then-compare, return status object) and the two merge strategies — sentinel-block splice for CLAUDE.md and deep-merge-with-Set-dedup for settings.json.

This phase intentionally delivers zero user-facing behaviour. There is no CLI entry point, no `bin/viflo.cjs`, no command parsing. The only artefacts are the two library files, their Vitest unit tests, and the test scaffold (vitest.config.cjs or equivalent) needed to run those tests from a temp directory that is outside the viflo repo.

The existing codebase already uses Vitest 1.x (locked at `^1.0.0` in apps/web/package.json) and the `gsd-tools.cjs` precedent in `/home/ollie/.claude/get-shit-done/bin/` demonstrates the exact CommonJS style — `require`, `module.exports`, no TypeScript compilation step. Tests for this phase must mock `os.homedir()` and must run from a temp directory because `__dirname`-based resolution must not silently depend on the current working directory.

**Primary recommendation:** Create `bin/lib/paths.cjs` and `bin/lib/writers.cjs` as pure CommonJS with Node.js built-ins only (no third-party deps), and place tests in `bin/lib/__tests__/` using Vitest's `vi.mock` for `os` and `fs` — matching the apps/web pattern.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Node.js built-ins (`path`, `fs`, `os`) | Node >= 20 (engine constraint in package.json) | Path construction, file I/O, home dir | Zero deps; `path.join`/`path.resolve` handle cross-platform separators; `fs.readFileSync`/`writeFileSync` sufficient for synchronous CLI ops |
| Vitest | ^1.0.0 (already installed in apps/web) | Unit test runner | Already in monorepo; `vi.mock` covers `os.homedir()` mocking; runs from any directory |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `os` (built-in) | Node >= 20 | `os.homedir()` — only for path context in tests, NOT in production path logic | Only in tests to mock and verify `~` never appears |
| `v8` coverage provider | via `@vitest/coverage-v8` | Test coverage reports | Already configured in apps/web; reuse same provider config for bin/lib tests |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Node built-in `path` | `pathe` (in node_modules already) | `pathe` is ESM-first; `.cjs` files use CommonJS `require`; built-in `path` is the correct choice |
| Vitest | Jest | Vitest already present in the monorepo; Jest would be redundant |
| Hand-rolled deep merge | `lodash.merge` | No third-party deps in `bin/lib/`; deep merge for a two-level JSON object is 20 lines — acceptable to write |

**Installation:**

```bash
# No new dependencies — Node.js built-ins + Vitest already present
# If running tests from bin/lib/ needs a local vitest config:
# vitest is available at repo root via pnpm workspaces
```

## Architecture Patterns

### Recommended Project Structure

```
bin/
├── lib/
│   ├── paths.cjs          # Path resolution utilities
│   ├── writers.cjs        # CLAUDE.md + settings.json writers
│   └── __tests__/
│       ├── paths.test.js  # Vitest unit tests for paths.cjs
│       └── writers.test.js # Vitest unit tests for writers.cjs
└── vitest.config.cjs      # Vitest config for bin/lib tests (CommonJS)
```

Note: `bin/viflo.cjs` is NOT created in this phase. This phase is library-only.

### Pattern 1: `__dirname`-based Viflo Root Resolution

**What:** The `paths.cjs` module uses `__dirname` (the directory containing `paths.cjs` itself) and traverses upward a known number of levels to reach the viflo repo root. Since `paths.cjs` lives at `bin/lib/paths.cjs`, `path.resolve(__dirname, '..', '..')` reaches the repo root reliably regardless of the caller's working directory.

**When to use:** Whenever a CLI module needs to locate viflo's own assets (skills directory, templates, etc.)

**Example:**

```javascript
// bin/lib/paths.cjs
'use strict';

const path = require('path');

/**
 * Resolve the viflo installation root.
 * paths.cjs lives at bin/lib/paths.cjs → two levels up = repo root.
 * Never uses process.cwd() or os.homedir().
 */
function resolveViFloRoot() {
  return path.resolve(__dirname, '..', '..');
}

/**
 * Resolve a path within the target project.
 * @param {string} cwd - Explicit working directory of the target project (required)
 * @param {...string} segments - Path segments relative to cwd
 * @returns {string} Absolute path string
 */
function resolveTargetPath(cwd, ...segments) {
  if (!cwd || typeof cwd !== 'string') {
    throw new Error('resolveTargetPath: cwd is required and must be a string');
  }
  return path.resolve(cwd, ...segments);
}

module.exports = { resolveViFloRoot, resolveTargetPath };
```

### Pattern 2: Compute-then-Compare Idempotency

**What:** Before writing any file, compute the full string that would be written, read the current file content (if it exists), and compare. Only write if they differ. Return `{ written: boolean, reason: string }`.

**When to use:** Both `writeCLAUDEmd` and `writeSettingsJson` must implement this.

**Example:**

```javascript
// Inside writers.cjs — generic idempotency wrapper
function writeIfChanged(filePath, newContent) {
  let existing = null;
  try {
    existing = fs.readFileSync(filePath, 'utf-8');
  } catch {
    // File does not exist — will be created
  }

  if (existing === newContent) {
    console.log(`[viflo] skipped (unchanged): ${filePath}`);
    return { written: false, reason: 'unchanged' };
  }

  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, newContent, 'utf-8');
  return { written: true, reason: existing === null ? 'created' : 'updated' };
}
```

### Pattern 3: Sentinel-Aware CLAUDE.md Merge

**What:** Locate `<!-- BEGIN VIFLO -->` and `<!-- END VIFLO -->` markers. Replace the content between them with new content. If markers are absent, append the entire sentinel block. If markers appear more than once, throw.

**When to use:** `writeCLAUDEmd(cwd, sentinelContent)` in writers.cjs.

**Example:**

```javascript
const SENTINEL_START = '<!-- BEGIN VIFLO -->';
const SENTINEL_END = '<!-- END VIFLO -->';

function mergeCLAUDEmd(existingContent, sentinelContent) {
  const startCount = (existingContent.match(/<!-- BEGIN VIFLO -->/g) || []).length;
  const endCount   = (existingContent.match(/<!-- END VIFLO -->/g) || []).length;

  if (startCount > 1 || endCount > 1) {
    throw new Error(
      '[viflo] CLAUDE.md contains multiple sentinel blocks. ' +
      'Remove duplicates manually before running viflo init.'
    );
  }

  const block = `${SENTINEL_START}\n${sentinelContent}\n${SENTINEL_END}`;

  if (startCount === 0) {
    // Append — non-destructive
    return existingContent.trimEnd() + '\n\n' + block + '\n';
  }

  // Replace existing block
  const startIdx = existingContent.indexOf(SENTINEL_START);
  const endIdx   = existingContent.indexOf(SENTINEL_END) + SENTINEL_END.length;
  return existingContent.slice(0, startIdx) + block + existingContent.slice(endIdx);
}
```

### Pattern 4: Deep Merge with Set-based Array Dedup for settings.json

**What:** Recursively merge viflo's settings object into the existing object. Arrays use union (Set-dedup). Scalars: viflo wins. Unknown existing keys are preserved.

**Example:**

```javascript
function deepMerge(existing, incoming) {
  const result = Object.assign({}, existing);
  for (const [key, value] of Object.entries(incoming)) {
    if (Array.isArray(value) && Array.isArray(result[key])) {
      // Union merge with dedup
      result[key] = [...new Set([...result[key], ...value])];
    } else if (
      value !== null &&
      typeof value === 'object' &&
      !Array.isArray(value) &&
      result[key] !== null &&
      typeof result[key] === 'object' &&
      !Array.isArray(result[key])
    ) {
      // Recurse for nested objects
      result[key] = deepMerge(result[key], value);
    } else {
      // Scalar: viflo wins
      result[key] = value;
    }
  }
  return result;
}
```

### Anti-Patterns to Avoid

- **Using `process.cwd()` in path resolution:** The CLI will be invoked from arbitrary directories. `process.cwd()` silently returns the wrong path. Use `__dirname` for viflo's own paths and explicit `cwd` for target-project paths.
- **Using `~` or `os.homedir()` in path construction:** Tilde expansion is a shell feature; Node.js `path.resolve('~/foo')` does NOT expand it. Always use `os.homedir()` + `path.join` when a home-relative path is genuinely needed, but the locked decisions prohibit `~` literals entirely.
- **Writing without checking:** Writing unconditionally means idempotency fails — a re-run diffs as "changed" in git even when content is identical.
- **Overwriting content outside sentinel markers:** The sentinel-aware merge MUST only replace the block between markers. Content before `<!-- BEGIN VIFLO -->` and after `<!-- END VIFLO -->` is user-owned.
- **Requiring `cwd` to default to `process.cwd()`:** The locked decision says `cwd` is **required**. Do not add a default. Callers must be explicit.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Recursive directory creation before write | Custom mkdir loop | `fs.mkdirSync(dir, { recursive: true })` | Built-in since Node 10.12; handles race conditions |
| JSON pretty-printing on write | Custom serialiser | `JSON.stringify(obj, null, 2) + '\n'` | Consistent 2-space indent; trailing newline avoids POSIX lint warnings |
| Cross-platform path joins | String concatenation with `/` | `path.join()` or `path.resolve()` | Windows compatibility future-proofing; avoids double-slash bugs |

**Key insight:** The entire `bin/lib/` layer needs zero third-party dependencies. Node's built-ins (`path`, `fs`, `os`) handle every requirement. Adding npm packages to the bin layer would complicate the eventual global install story (Phase PLAT-02).

## Common Pitfalls

### Pitfall 1: `__dirname` Confusion When Tests Run

**What goes wrong:** Tests import `paths.cjs` from a test file in `bin/lib/__tests__/`. `__dirname` inside `paths.cjs` still refers to `bin/lib/` (the module's own directory), which is correct. But if a test tries to assert that `resolveViFloRoot()` returns the current temp directory, it will fail because `__dirname` is fixed at module load time based on the file's location on disk.

**Why it happens:** Developers confuse the test runner's `cwd` with `__dirname`. Vitest may run tests from a temp directory but the imported module's `__dirname` stays tied to its real disk path.

**How to avoid:** Test `resolveViFloRoot()` by asserting the returned path ends with `/viflo` (or contains `bin/lib`'s parent). Do NOT mock `__dirname` — it's not a function. Only mock `os.homedir()` and `fs` operations.

**Warning signs:** Test assertions that compare `resolveViFloRoot()` output to `process.cwd()`.

### Pitfall 2: Sentinel Regex Overmatch

**What goes wrong:** Using a greedy regex to find the sentinel block captures content between an outer and inner occurrence when multiple blocks exist, silently mangling the file.

**Why it happens:** Using `.+` (greedy) between start and end markers.

**How to avoid:** Count occurrences first (throw if > 1), then use `indexOf` for positional extraction — not a regex replace.

**Warning signs:** A test with two sentinel blocks that "merges" without throwing.

### Pitfall 3: Set-Dedup Loses Order Unexpectedly

**What goes wrong:** `[...new Set([...existing, ...incoming])]` preserves insertion order (existing first), which is correct. But if the caller passes `incoming` first, new items appear before existing ones.

**Why it happens:** Array spread order matters in Set construction.

**How to avoid:** Always spread existing array first: `new Set([...existingArray, ...incomingArray])`. Document this in the function comment. Test with existing items that overlap partially.

**Warning signs:** Tests that don't verify item order in merged arrays.

### Pitfall 4: JSON Write Without Trailing Newline

**What goes wrong:** `JSON.stringify(obj, null, 2)` produces no trailing newline. POSIX tools and git report the file as "no newline at end of file", creating spurious diff noise.

**Why it happens:** `JSON.stringify` is spec-correct — JSON has no trailing newline requirement. But files on disk should.

**How to avoid:** Always write `JSON.stringify(obj, null, 2) + '\n'`. The idempotency check then correctly compares this format on re-run.

**Warning signs:** Git showing `\ No newline at end of file` on settings.json changes.

### Pitfall 5: Sentinel Format Inconsistency (STATE.md vs CONTEXT.md)

**What goes wrong:** STATE.md (written during roadmap) records `<!-- viflo:start --> / <!-- viflo:end -->` as the sentinel format. CONTEXT.md (the locked design, gathered 2026-02-24) specifies `<!-- BEGIN VIFLO --> / <!-- END VIFLO -->`. These are different strings.

**Why it happens:** The sentinel format was refined during the discuss-phase session after the roadmap was written.

**How to avoid:** Use CONTEXT.md as the authoritative source. The sentinel strings are `<!-- BEGIN VIFLO -->` and `<!-- END VIFLO -->`. STATE.md entry is stale for this detail.

**Warning signs:** Any code or test that references `viflo:start` or `viflo:end`.

## Code Examples

Verified patterns from Node.js built-ins (HIGH confidence — Node.js 20 LTS docs):

### Absolute path resolution with `__dirname`

```javascript
// bin/lib/paths.cjs
// __dirname = /path/to/viflo/bin/lib
const path = require('path');

function resolveViFloRoot() {
  // bin/lib -> bin -> repo root
  return path.resolve(__dirname, '..', '..');
}
// Returns: /path/to/viflo  (absolute, regardless of process.cwd())
```

### Recursive directory creation before write

```javascript
// Node.js 20 built-in — no external dep needed
const fs = require('fs');
const path = require('path');

fs.mkdirSync(path.dirname(filePath), { recursive: true });
fs.writeFileSync(filePath, content, 'utf-8');
```

### Vitest mock of `os.homedir()` (CJS test file)

```javascript
// bin/lib/__tests__/paths.test.js
const { describe, it, expect, vi, beforeEach } = require('vitest');

vi.mock('os', () => ({
  homedir: vi.fn(() => '/mock/home'),
}));

// In tests: import paths AFTER mock is set up
const { resolveTargetPath } = require('../paths.cjs');

describe('resolveTargetPath', () => {
  it('requires explicit cwd', () => {
    expect(() => resolveTargetPath()).toThrow('cwd is required');
  });

  it('returns absolute path from cwd + segments', () => {
    const result = resolveTargetPath('/tmp/my-project', '.claude', 'settings.json');
    expect(result).toBe('/tmp/my-project/.claude/settings.json');
  });
});
```

### Vitest config for CommonJS bin/lib tests

```javascript
// bin/vitest.config.cjs  (CommonJS — vitest supports cjs config files)
const { defineConfig } = require('vitest/config');

module.exports = defineConfig({
  test: {
    include: ['bin/lib/__tests__/**/*.test.{js,cjs}'],
    environment: 'node',
  },
});
```

Or run directly without a config file:

```bash
npx vitest run --config bin/vitest.config.cjs
# or from repo root via pnpm:
pnpm exec vitest run bin/lib/__tests__
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `__filename` globals in CJS | `__dirname` + `path.resolve` | Always best practice | `__dirname` gives directory, not file — correct for upward traversal |
| Regex-based sentinel replace | `indexOf` position + slice | This phase's design | Safer; throws on ambiguity; no greedy overmatch |
| Shallow `Object.assign` for JSON merge | Recursive deep merge with Set arrays | This phase's design | Preserves nested keys; deduplicates arrays correctly |

**Deprecated/outdated:**

- `~` in path strings: Shell shorthand, not a Node.js path primitive — never use in Node code.
- `path.join(os.homedir(), ...)` as a default in library functions: Makes functions non-pure and harder to test; the locked design requires explicit `cwd` instead.

## Open Questions

1. **Vitest config placement for CJS tests**
   - What we know: Vitest 1.x supports `vitest.config.cjs` but documentation primarily shows ESM config files. The monorepo root `package.json` has `"test": "pnpm --filter @viflo/web test"` which only runs the web app's tests.
   - What's unclear: Whether to put `bin/vitest.config.cjs` at repo root or under `bin/`. Running `pnpm test` at root currently only runs `@viflo/web` tests.
   - Recommendation: Create `bin/vitest.config.cjs` under `bin/` and add a `"test:cli"` script to the root `package.json` that runs `pnpm exec vitest run --config bin/vitest.config.cjs`. This keeps CLI tests separate from web tests and avoids modifying the existing test pipeline.

2. **CJS `require` vs dynamic `vi.mock` in Vitest**
   - What we know: Vitest's `vi.mock` is hoisted to the top of the test file in ESM. In CJS test files, hoisting works differently — `vi.mock('os', ...)` must appear before the `require` of the module under test.
   - What's unclear: Exact Vitest 1.x CJS hoisting behaviour (it generally works but has edge cases with CommonJS require caching).
   - Recommendation: Use `vi.resetModules()` in `beforeEach` and use `require` inside test cases (not at top level) to ensure fresh module loads after mocks are applied. Alternatively, structure `paths.cjs` to accept injected dependencies for `os.homedir` to make testing simpler without mock hoisting concerns.

## Sources

### Primary (HIGH confidence)

- Node.js 20 LTS docs — `path.resolve`, `path.join`, `__dirname`, `fs.mkdirSync({ recursive })`, `fs.readFileSync`, `fs.writeFileSync`
- Vitest 1.x docs — `vi.mock`, `vi.resetModules`, `defineConfig`, CJS support
- `/home/ollie/.claude/get-shit-done/bin/lib/core.cjs` — direct precedent for CommonJS style: `'use strict'`, `require`, `module.exports`, `path.resolve`, `fs.readFileSync`
- `/home/ollie/Development/Tools/viflo/apps/web/vitest.config.ts` — confirmed Vitest 1.x with v8 coverage provider in use
- `/home/ollie/Development/Tools/viflo/apps/web/package.json` — confirmed `vitest: "^1.0.0"`, Node `">=20.0.0"` engine constraint
- `/home/ollie/Development/Tools/viflo/.planning/phases/16-cli-foundation/16-CONTEXT.md` — locked decisions (authoritative over STATE.md for sentinel format)

### Secondary (MEDIUM confidence)

- `Set`-based array dedup pattern (`[...new Set([...a, ...b])]`) — standard JS idiom, verified against MDN Set documentation behaviour

### Tertiary (LOW confidence)

- Vitest CJS `vi.mock` hoisting edge cases — known from Vitest issue tracker patterns but not verified against Vitest 1.x release notes for this specific scenario. Flag for validation when writing tests.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — Node.js built-ins confirmed, Vitest version confirmed from package.json, gsd-tools.cjs CJS pattern directly verified
- Architecture: HIGH — `__dirname` traversal is deterministic; sentinel logic is algorithmic not library-dependent; deep merge is standard JS
- Pitfalls: HIGH for pitfalls 1-4 (derived from first-principles analysis of the locked decisions); MEDIUM for pitfall 5 (sentinel name inconsistency — directly observed in STATE.md vs CONTEXT.md)

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 (Node.js built-ins and Vitest 1.x are stable; no fast-moving dependencies)
