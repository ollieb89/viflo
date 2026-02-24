# Stack Research

**Domain:** `viflo init` CLI tool — Node.js bin script wiring new projects to viflo
**Researched:** 2026-02-24
**Confidence:** HIGH (versions verified against npm registry on 2026-02-24)

> **Scope note:** This file covers only the `viflo init` CLI milestone (v1.4). It replaces the v1.3 STACK.md which covered Stripe, RAG, and Agent Architecture skill domains. Those entries remain relevant for skill authors but are not needed for CLI implementation.

---

## Verdict: CJS Workspace Package, Zero Runtime Dependencies

Use a Node.js CJS file at `packages/cli/bin/viflo.cjs`, registered as a pnpm workspace package with a `bin` field. Zero external runtime dependencies — use Node.js built-in `fs`, `path`, and `readline` exclusively. This matches the gsd-tools.cjs pattern already established in the repo's toolchain and satisfies the "no external dependencies beyond standard tools" constraint.

**Why not a shell script:** Shell scripts cannot reliably handle JSON merging, CLAUDE.md section idempotency markers, or cross-platform path construction. The existing `scripts/*.sh` files are setup/telemetry helpers — file manipulation logic belongs in Node.js.

**Why not a proper npm-published bin (yet):** npm publishing requires a public registry account, versioning overhead, and install ceremony (`npm install -g viflo`). At v1.4, the tool only needs to run from the monorepo. The `bin` field and package structure will be npm-publish ready, but actual publishing is deferred.

**Why CJS over ESM:** The workspace root uses `"type": "commonjs"` (package.json has no `"type": "module"` field — default is CJS). The gsd-tools.cjs precedent proves single-file CJS scripts work cleanly with `#!/usr/bin/env node`. ESM in Node requires `.mjs` extension or `"type": "module"` in a separate package, adding friction with no benefit for a CLI with no async module graph.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Node.js | >=20.0.0 (already required by repo) | Runtime | Node 20 includes `fs.cpSync`, `fs.mkdirSync({recursive: true})`, `fs/promises` — all file ops needed for `viflo init` without any external library |
| CommonJS (`.cjs`) | n/a — language mode | Module format | Single-file CJS scripts require no bundling, no compilation step, and work identically on macOS, Linux, and WSL. Matches gsd-tools.cjs precedent. |
| `#!/usr/bin/env node` shebang | n/a | Makes bin executable | Required by npm bin spec — without this, the file runs as a shell script. |
| pnpm workspace package | pnpm >=10.0.0 (already required) | Wires bin into monorepo PATH | Add `packages/cli` to `pnpm-workspace.yaml`; after `pnpm install`, `pnpm --filter @viflo/cli run viflo init` works without a global install. |

### Supporting Libraries

None. The following Node.js built-ins cover all requirements:

| Built-in | Purpose | Node version available |
|----------|---------|----------------------|
| `node:fs` | File existence checks (`existsSync`), reads (`readFileSync`), writes (`writeFileSync`), mkdir (`mkdirSync({recursive:true})`) | All Node 20+ |
| `node:fs/promises` | Async variants for future migration if needed | Node 20+ |
| `node:path` | Cross-platform path construction, `path.join`, `path.resolve` | All |
| `node:os` | `os.homedir()` — for locating `~/.claude/` when writing global Claude Code settings | All |
| `node:readline` | Interactive confirmation prompt (`--dry-run` or overwrite guards) | All |
| `JSON.parse` / `JSON.stringify` | JSON settings merging | Built-in |

**Rationale for zero external dependencies:** `deepmerge@4.3.1` would handle nested JSON merge elegantly, but the `.claude/settings.json` merge is shallow — it only needs to inject an `enabledPlugins` key. A 10-line recursive merge function replaces the library. `fs-extra@11.3.3` would add `ensureDir` and `outputFile` convenience methods, but `fs.mkdirSync({recursive: true})` + `fs.writeFileSync` provide identical behavior in Node 20. Adding any npm dependency to `packages/cli` creates a `node_modules` install requirement for users who `git clone` — the zero-dep approach avoids that entirely.

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Vitest | Unit tests for CLI logic | Already in repo — add test coverage for idempotency guards, JSON merge, CLAUDE.md section injection. Use `node:fs` mock via `vi.mock`. |
| pnpm `--filter` | Run or test the CLI within the workspace | `pnpm --filter @viflo/cli run viflo init ~/my-project` |

---

## Package Structure

### New workspace package: `packages/cli/`

```
packages/cli/
├── package.json        ← defines bin field and package name
├── bin/
│   └── viflo.cjs      ← the CLI implementation (single file, CJS, shebang)
└── tests/
    └── init.test.js   ← Vitest unit tests
```

### `packages/cli/package.json`

```json
{
  "name": "@viflo/cli",
  "version": "1.4.0",
  "description": "viflo init CLI — wires new projects to viflo skills",
  "type": "commonjs",
  "bin": {
    "viflo": "./bin/viflo.cjs"
  },
  "scripts": {
    "viflo": "node ./bin/viflo.cjs",
    "test": "vitest run"
  },
  "engines": {
    "node": ">=20.0.0"
  },
  "files": [
    "bin/"
  ]
}
```

**Why `"bin": { "viflo": "./bin/viflo.cjs" }`:** The `bin` field maps the CLI command name `viflo` to the file. When the package is installed globally (`npm install -g @viflo/cli`), this creates a `viflo` symlink in PATH. When used within the pnpm workspace, `pnpm run viflo` resolves it locally. The `"files"` field ensures only `bin/` is published — no test files or dev artifacts go to npm.

### `pnpm-workspace.yaml` update

```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

`packages/cli` is already covered by the existing `packages/*` glob — no change needed to the workspace file.

### Invocation patterns

| Context | Command | When to use |
|---------|---------|-------------|
| Within monorepo | `pnpm --filter @viflo/cli run viflo -- init ~/my-project` | Development, CI |
| Direct node call | `node packages/cli/bin/viflo.cjs init ~/my-project` | Debugging, no pnpm filter needed |
| After global install | `viflo init ~/my-project` | End-user scenario (post npm publish) |
| npx (no install) | `npx @viflo/cli init ~/my-project` | End-user one-shot (post npm publish) |

---

## Implementation Patterns

### Idempotent file writing (CLAUDE.md stanza injection)

Use sentinel comment markers to make the stanza idempotent. If the markers are already present, skip writing. If they are absent, append. Never overwrite existing content above the markers.

```javascript
const STANZA_START = '<!-- viflo:start -->';
const STANZA_END   = '<!-- viflo:end -->';

function injectStanza(filePath, stanza) {
  const existing = fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : '';
  if (existing.includes(STANZA_START)) {
    return { action: 'skipped', reason: 'stanza already present' };
  }
  const content = existing + (existing.endsWith('\n') ? '' : '\n') +
    STANZA_START + '\n' + stanza + '\n' + STANZA_END + '\n';
  fs.writeFileSync(filePath, content, 'utf8');
  return { action: 'written' };
}
```

### JSON settings merging (`.claude/settings.json`)

Deep merge is overkill — the target key is always `enabledPlugins`. A targeted path-aware write is safer:

```javascript
function mergeSettings(filePath, patch) {
  let existing = {};
  if (fs.existsSync(filePath)) {
    try { existing = JSON.parse(fs.readFileSync(filePath, 'utf8')); }
    catch (_) { /* corrupt file — treat as empty */ }
  }
  // Shallow merge at top level; nested keys under same property are merged 1 level deep
  const merged = { ...existing };
  for (const [k, v] of Object.entries(patch)) {
    if (typeof v === 'object' && !Array.isArray(v) && typeof merged[k] === 'object') {
      merged[k] = { ...merged[k], ...v };
    } else {
      merged[k] = v;
    }
  }
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(merged, null, 2) + '\n', 'utf8');
}
```

**Why not `deepmerge`:** The merge target (`enabledPlugins`) is a flat key-value object. One level of shallow merge is sufficient and avoids a `node_modules` dependency.

### Scaffold directory creation (`.planning/` structure)

```javascript
function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true }); // no-ops if dir exists
}
```

`mkdirSync` with `recursive: true` is idempotent — it does not throw if the directory already exists (Node 20+, verified).

---

## Installation

```bash
# No new dependencies — the CLI uses only Node.js built-ins.
# Workspace registration happens automatically via pnpm-workspace.yaml.

# After adding packages/cli/package.json:
pnpm install

# Run locally:
pnpm --filter @viflo/cli run viflo -- init --minimal /path/to/project
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Zero-dependency CJS single file | `commander@14.0.3` | Use commander when the CLI has 5+ subcommands with complex option parsing, help text generation, or version flags. `viflo init` has 2 flags (`--minimal`, `--full`) — `process.argv.slice(2)` is 10 lines vs adding a dependency. |
| Zero-dependency CJS single file | Shell script (`.sh`) | Use shell scripts for environment setup (as `setup-dev.sh` does), not for file content manipulation or JSON merging. |
| Zero-dependency CJS single file | TypeScript compiled script | TypeScript adds a build step and requires `tsc` or `tsx` at runtime. The CLI is simple enough that type annotations don't justify the compilation overhead. Align with gsd-tools.cjs precedent. |
| CJS `.cjs` | ESM `.mjs` | Use ESM if the package adopts `"type": "module"` later or if the file needs to `import` ESM-only packages. CJS is the safer default for CLI tools that target all Node 20+ environments. |
| Inline JSON merge (10 lines) | `deepmerge@4.3.1` | Use deepmerge if the settings schema becomes deeply nested (3+ levels). For the current `.claude/settings.json` shape (flat top-level keys), inline merge is cleaner. |
| `fs` built-ins | `fs-extra@11.3.3` | Use fs-extra if Node 16 or earlier compatibility is needed. Node 20+ built-ins cover everything: `mkdirSync({recursive})`, `cpSync`, `writeFileSync`. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `commander`, `yargs`, `meow`, `oclif` | Runtime npm dependencies that require `node_modules` present; overkill for 2-flag CLI | `process.argv.slice(2)` with a 15-line arg parser |
| `fs-extra`, `graceful-fs` | Node 20+ built-in `fs` has `mkdirSync({recursive})`, `cpSync` — no gap to fill | `node:fs` |
| `deepmerge`, `lodash.merge`, `merge-deep` | JSON merge needed is shallow (1-level deep) — single for-loop is sufficient | Inline merge function |
| `chalk`, `kleur`, `picocolors` | Color terminal output is nice but adds a dependency; `setup-dev.sh` uses raw ANSI codes | ANSI escape codes directly: `\x1b[32m` for green, `\x1b[0m` to reset |
| TypeScript compilation | Adds `tsc`/`tsx` build step for a file simple enough to write in plain JS | Plain CJS `.cjs` — matches gsd-tools.cjs |
| ESM (`import`/`export`) | CJS interop with existing workspace packages is simpler; CJS is the workspace default | CJS `require`/`module.exports` |
| npm publish at v1.4 | Not yet needed — tool only runs from monorepo; publishing adds versioning overhead | Defer to a dedicated "npm package" milestone |

---

## Stack Patterns by Variant

**If `--minimal` flag:**
- Write CLAUDE.md import stanza (idempotent, marker-based)
- Merge `enabledPlugins` key into `.claude/settings.json` (create file if absent)
- No directory scaffolding

**If `--full` flag:**
- All of `--minimal`
- Create `.planning/` directory structure with GSD template stubs
- Write starter CLAUDE.md template with project-specific placeholder sections

**If target project already has CLAUDE.md with viflo stanza:**
- Detect sentinel markers
- Print "already configured" and exit 0 — do not modify the file

**If target project has `.claude/settings.json` with conflicting `enabledPlugins`:**
- Shallow-merge: existing plugin keys are preserved; viflo entries are added
- Never remove existing plugin entries

---

## Version Compatibility

| Package | Version | Compatible With | Notes |
|---------|---------|-----------------|-------|
| Node.js | >=20.0.0 | `fs.mkdirSync({recursive})`, `fs.cpSync` | Node 20 is already the repo minimum — no new constraint |
| pnpm | >=10.0.0 | workspace package linking, `--filter` | Already required at repo root |
| Vitest | ^1.0.0 | Already in `apps/web` devDependencies | Add to `packages/cli` devDependencies separately; version pin matches existing |

---

## Sources

- npm registry — `commander@14.0.3` confirmed current (2026-02-24, fetched directly from `registry.npmjs.org`); HIGH confidence
- npm registry — `deepmerge@4.3.1` confirmed current (2026-02-24); HIGH confidence
- npm registry — `fs-extra@11.3.3` confirmed current (2026-02-24); HIGH confidence
- [Node.js fs docs](https://nodejs.org/api/fs.html) — `mkdirSync({recursive})`, `cpSync`, `writeFileSync` behavior verified; HIGH confidence
- [npm docs — bin field](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#bin) — `#!/usr/bin/env node` shebang requirement, bin map format; HIGH confidence
- [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) — `.claude/settings.json` `enabledPlugins` format, project-scope path verified; HIGH confidence (fetched directly 2026-02-24)
- [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference) — plugin manifest schema, skills directory structure verified; HIGH confidence (fetched directly 2026-02-24)
- `/home/ollie/.claude/get-shit-done/bin/gsd-tools.cjs` — CJS single-file CLI pattern, zero-dependency approach validated against working production tool; HIGH confidence
- `viflo/package.json` (repo root) — Node `>=20.0.0`, pnpm `>=10.0.0`, default CJS module type confirmed; HIGH confidence
- `viflo/apps/web/package.json` — Vitest `^1.0.0` confirmed as existing test framework version; HIGH confidence

---

*Stack research for: viflo v1.4 — `viflo init` CLI*
*Researched: 2026-02-24*
