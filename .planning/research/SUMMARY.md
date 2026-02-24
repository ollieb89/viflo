# Project Research Summary

**Project:** viflo — `viflo init` CLI (v1.4)
**Domain:** Node.js CLI tool for wiring projects to an agentic development methodology toolkit
**Researched:** 2026-02-24
**Confidence:** HIGH

## Executive Summary

`viflo init` is a config-injection CLI with a narrow, well-defined job: write two things into a target project — a CLAUDE.md import stanza (pointing to viflo skills via `@` import syntax) and a `.claude/settings.json` with safe default permissions. Research confirms the correct implementation is a zero-dependency CommonJS Node.js script at `bin/viflo.cjs`, following the `gsd-tools.cjs` precedent already established in the ecosystem. No external npm packages are needed; Node 20 built-ins (`fs`, `path`, `os`, `readline`) cover all requirements. The `packages/cli/` TypeScript workspace approach is explicitly deferred — it is premature engineering before the CLI shape is proven.

The feature set is tight and well-bounded. `--minimal` mode writes a CLAUDE.md sentinel block plus a settings.json merge; `--full` mode additionally scaffolds `.planning/` stubs. Both modes must be idempotent by design. The sentinel block pattern (HTML comment markers bounding the viflo-managed section of CLAUDE.md) is the correct and non-negotiable mechanism — it preserves all user content outside the block and is a shipped contract from the first release. Settings.json requires a read-modify-write with array deduplication, never a full overwrite.

The biggest risks are correctness and safety failures, not performance. Three classes of failure must be prevented by design: (1) writing to wrong paths (tilde not expanded; `__dirname` used instead of `process.cwd()`), (2) clobbering user-customized files on re-run (CLAUDE.md, settings.json, `.planning/` documents), and (3) scope confusion between user-level and project-level Claude Code settings. Research also flags an active Claude Code bug (issue #5140) where user-scope `permissions.allow` is not reliably enforced — the documented workaround is writing to project scope instead. All three risk classes are preventable with disciplined path utilities, sentinel-aware writes, and explicit per-file existence checks.

---

## Key Findings

### Recommended Stack

The stack is minimal by design. A single CJS file (`bin/viflo.cjs`) with a `#!/usr/bin/env node` shebang is the entire runtime artifact, decomposed into four lib modules for testability. Zero external npm dependencies are justified and achievable — Node 20's `fs` module handles all file operations including idempotent directory creation (`mkdirSync({recursive: true})`). The `packages/cli/` workspace approach (TypeScript, compilation pipeline, npm publish) is explicitly deferred to a future milestone.

See `.planning/research/STACK.md` for the full version compatibility matrix and package structure.

**Core technologies:**
- **Node.js >=20.0.0**: Runtime — already required by repo; provides all needed `fs` built-ins including `cpSync` and recursive `mkdirSync`
- **CommonJS `.cjs`**: Module format — `__dirname` only works in CJS (needed for self-referential path resolution); matches gsd-tools.cjs precedent; no build step required
- **`node:fs` / `node:path` / `node:os` / `node:readline`**: All file I/O and path construction — zero external dependencies; `os.homedir()` is the only safe cross-platform home directory resolver
- **pnpm workspace (>=10.0.0)**: Already required by repo; `bin/viflo.cjs` sits at repo root outside `packages/*` — simpler than a workspace package for v1.4
- **Vitest**: Testing — already in repo; mock `node:fs` via `vi.mock` for unit tests; integration tests must run from temp directories to validate `process.cwd()` vs `__dirname` separation

**Implementation patterns (from STACK.md):**
- Sentinel-based CLAUDE.md merge: `<!-- viflo:start -->` / `<!-- viflo:end -->` HTML comment markers; detect on read, replace in-place on write
- Settings.json merge: build a JavaScript object, call `JSON.stringify(obj, null, 2)` — never construct JSON by string concatenation; use `Set` for array deduplication
- `.planning/` scaffold: `mkdirSync({recursive: true})` is idempotent; per-file `existsSync` check before each write

**ARCHITECTURE.md vs STACK.md location disagreement:** STACK.md proposes `packages/cli/` as the package home; ARCHITECTURE.md's more detailed analysis explicitly recommends `bin/viflo.cjs` with `bin/lib/` submodules, and rejects `packages/cli/` as premature complexity. **Treat `bin/viflo.cjs` as the canonical location decision for v1.4.**

### Expected Features

`viflo init` writes config files — it does not bootstrap projects. That boundary must be held. The feature set maps directly onto the four active requirements (INIT-01 through INIT-04).

See `.planning/research/FEATURES.md` for the full feature table, dependency graph, idempotency patterns, and comparison with analogous init CLIs.

**Must have (P1 — required for INIT-01 through INIT-04):**
- Resolve viflo install path via `__dirname` — required before any writes; fail fast with clear message if resolution fails
- Write CLAUDE.md sentinel block with `@` import lines pointing to all viflo skills — append-or-replace, idempotent
- Write `.claude/settings.json` with safe default `permissions.allow` — create-if-absent or deep-merge (deduplicated array union) if file exists
- `--minimal` flag — CLAUDE.md stanza + settings.json only
- `--full` flag — everything in minimal plus `.planning/` stub scaffold (skip-if-exists per file) and starter CLAUDE.md template if CLAUDE.md is brand new
- Idempotent re-runs — compare new content against existing state before writing; emit "already up to date" for unchanged files
- Human-readable per-file output — log each file action (`created / updated / skipped / merged`) with the resolved absolute path

**Should have (P2 — add once core is stable):**
- `--dry-run` flag — preview without writing (requires write layer abstracted from day one; low cost if designed in)
- `--force` flag — replace sentinel block without change detection, with explicit `--yes` confirmation
- Verification pass — after writing, confirm all injected `@` import paths resolve on disk; emit warnings for missing references

**Defer (v2+):**
- Stack-aware skill selection — detect project stack and inject a curated skill subset; high complexity, requires skill taxonomy
- Interactive wizard mode — only if flag-based API proves confusing in practice
- npm publish / global install — deferred; tool only needs to run from monorepo at v1.4

**Explicit anti-features (do not build):**
- Full project scaffolding (package.json, git init, Makefile) — out of scope; viflo init is config injection only
- Semantic CLAUDE.md merge (section matching) — fragile and unpredictable; sentinel block is the correct approach
- Writing to `settings.local.json` — gitignored by convention; project writes go to `settings.json`
- Auto-installing viflo if absent — circular dependency; fail fast with install instructions instead
- Skill selection wizard for v1 — default to importing all skills; users trim manually

### Architecture Approach

The CLI decomposes into four single-concern modules with a clear bottom-up dependency order. The entry point (`bin/viflo.cjs`) is thin — argument routing only. Each lib module is independently testable via `require()` without loading the full CLI. The critical boundary between viflo's own directory (`__dirname`) and the user's project directory (`process.cwd()`) must be enforced at the module API level: all writer functions accept `cwd` as an explicit parameter.

See `.planning/research/ARCHITECTURE.md` for the full component diagrams, data flow for `--minimal` and `--full` modes, integration points, anti-patterns, and invocation reference.

**Major components:**
1. `bin/viflo.cjs` — CLI entry point: `process.argv` parsing, routes to `init.cjs`; thin, no business logic
2. `bin/lib/init.cjs` — Orchestrates `--minimal` / `--full` flows; idempotency checks; per-file stdout reporting
3. `bin/lib/paths.cjs` — Self-referential viflo root via `__dirname`; all target-project paths via `process.cwd()` passed as `cwd` parameter; OS-agnostic path construction with `os.homedir()` for user-home paths
4. `bin/lib/writers.cjs` — CLAUDE.md sentinel-aware merge; settings.json JSON merge with `Set`-based array deduplication; `.planning/` scaffold with per-file existence guard

**Files written to target projects:**

| File | Mode | Action |
|------|------|--------|
| `CLAUDE.md` | both | Sentinel append-or-replace; never touches content outside markers |
| `.claude/settings.json` | both | JSON merge; deduplicated `permissions.allow` array |
| `.planning/PROJECT.md` | --full only | Create-if-absent |
| `.planning/ROADMAP.md` | --full only | Create-if-absent |
| `.planning/STATE.md` | --full only | Create-if-absent |
| `.planning/config.json` | --full only | Create-if-absent |

**Files the CLI never modifies:**
- `~/.claude/settings.json` (user scope — out of scope for project init)
- Any CLAUDE.md content outside the `<!-- viflo:start -->` / `<!-- viflo:end -->` sentinel markers
- Any existing `.planning/` file (create-if-absent, never overwrite)

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full descriptions, warning signs, recovery strategies, and the "Looks Done But Isn't" verification checklist.

1. **Tilde expansion failure** — `~/.claude` as a literal string fails silently in Node.js (`ENOENT` or writes to a `~` directory). Use `path.join(os.homedir(), '.claude', ...)` for all user-home paths. Any `~` literal in a `fs.*` call is a bug. Test by mocking `os.homedir()` to a temp directory.

2. **`__dirname` vs `process.cwd()` confusion** — `__dirname` points to the viflo binary location; `process.cwd()` points to the user's project. All project-relative output paths must use `process.cwd()`. Enforce via a `cwd` parameter convention in all writer functions. Integration tests must run from a temp directory outside the viflo repo.

3. **CLAUDE.md full-file overwrite** — Writing the starter template unconditionally destroys user customizations. The sentinel block pattern is the non-negotiable mechanism — design it before writing any CLAUDE.md output code. Test with a pre-existing customized CLAUDE.md.

4. **settings.json clobber on re-run** — `fs.writeFileSync(path, JSON.stringify(FULL_DEFAULTS))` without a read-modify-write destroys user permissions on re-run. Always read, merge (deduplicated `Set` union for `allow` array), write back. Test with a pre-seeded settings.json.

5. **Invalid JSON written to settings.json** — Template literal JSON construction produces trailing commas and breaks Claude Code silently. Always build a JS object and call `JSON.stringify`. Wrap `JSON.parse` of existing files in `try/catch` and surface malformed-file errors to the user rather than overwriting.

6. **Claude Code user-scope permissions bug (issue #5140)** — Active bug: `permissions.allow` in `~/.claude/settings.json` may not be enforced in some Claude Code versions. The safe workaround is writing to project scope (`.claude/settings.json`) for `--minimal`, or documenting the limitation clearly in CLI output.

7. **`.planning/` scaffold clobber** — `viflo init --full` on an existing GSD project must skip all existing files. A scaffold loop without per-file existence checks destroys live planning documents. Recovery from lost `.planning/` is HIGH cost. Never retrofit — design skip-if-exists from the start.

8. **`--full` scope creep** — Lock the `--full` spec to: CLAUDE.md stanza + settings.json + `.planning/` stubs. Any addition touching git, package.json, scripts, or Makefile is out of scope and belongs in a future milestone.

---

## Implications for Roadmap

The implementation maps naturally onto the four active requirements (INIT-01 through INIT-04) with a clear build order driven by module dependencies and safety priorities. The most dangerous pitfalls all live in the path and write utility layer — build and test that layer first before any orchestration code.

### Phase 1: Foundation — Path Utilities and Write Primitives

**Rationale:** All other phases depend on `paths.cjs` and `writers.cjs` being correct and tested. The two most dangerous pitfalls (tilde expansion, `__dirname` confusion) live here. Testing these utilities in isolation — with mocked `os.homedir()` and temp directories — catches the bugs before any user-facing flow is wired. The sentinel merge and JSON merge logic also belong here, enabling Phase 2 to focus on orchestration and idempotency.

**Delivers:** `bin/lib/paths.cjs` with full unit tests; `bin/lib/writers.cjs` with CLAUDE.md sentinel merge and settings.json JSON merge; Vitest setup for the CLI package; integration test harness that runs from a temp directory outside the viflo repo

**Addresses:** INIT-04 (idempotency primitives); all P1 file-handling features from FEATURES.md

**Avoids:** Pitfall 1 (tilde expansion), Pitfall 2 (symlinked home), Pitfall 3 (`__dirname`), Pitfall 5 (invalid JSON write)

**Research flag:** No research needed — standard Node.js built-ins with stable, well-documented behavior.

### Phase 2: Minimal Mode — Core Init Flow (INIT-01 + INIT-04)

**Rationale:** `--minimal` is the strict subset of `--full`. Shipping minimal first proves the two core write operations before adding scaffolding complexity. Idempotency tests for minimal are the acceptance criteria for this phase — re-running twice must produce identical output.

**Delivers:** `bin/lib/init.cjs` with `--minimal` orchestration; `bin/viflo.cjs` entry point with `process.argv` parsing; `viflo init --minimal` working end-to-end; integration test from temp directory verifying both first run and idempotent re-run

**Uses:** `paths.cjs` and `writers.cjs` from Phase 1

**Implements:** Architecture components 1 and 2 (entry point + init orchestrator)

**Addresses:** INIT-01 (CLAUDE.md stanza write); INIT-04 (idempotent re-runs for minimal mode)

**Avoids:** Pitfall 4 (settings.json clobber), Pitfall 6 (CLAUDE.md overwrite)

**Research flag:** No research needed — sentinel block pattern, `process.argv` parsing, settings.json JSON merge are all well-established patterns.

### Phase 3: Full Mode and .planning/ Scaffold (INIT-02 + INIT-03)

**Rationale:** `--full` is a superset of `--minimal`. Implement after minimal is confirmed stable and tested. The scaffold write loop must be existence-aware from the start — skip-if-exists is a design constraint, not a retrofit. Lock the `--full` spec before writing any code for this phase.

**Delivers:** `--full` flag with `.planning/` stub creation (skip-if-exists per file, log each skipped file); starter CLAUDE.md template written only when CLAUDE.md is brand new; `viflo init --full` end-to-end tests against both fresh and existing projects with live `.planning/` content

**Addresses:** INIT-02 (`.planning/` directory scaffold); INIT-03 (starter CLAUDE.md template on `--full`)

**Avoids:** Pitfall 7 (`.planning/` scaffold clobber), Pitfall 8 (`--full` scope creep)

**Research flag:** No research needed — file existence checks and directory creation are trivial Node.js patterns.

### Phase 4: Wiring, Scope Clarification, and Polish

**Rationale:** Wire the `"bin"` field in `package.json`, document the settings.json scope behavior (including the user-scope bug workaround), add human-readable per-file output, and verify Claude Code `@` import approval dialog behavior. Deferred from core phases to avoid distraction during implementation.

**Delivers:** `"bin": { "viflo": "bin/viflo.cjs" }` in `package.json`; user-facing output for every file action with resolved paths and scope labels; documentation of Claude Code `@` import one-time approval dialog in CLI stdout; documented scope limitation for `permissions.allow` bug

**Addresses:** FEATURES.md human-readable output requirement; P2 features (`--dry-run` scaffold if write layer was abstracted in Phase 1 as designed)

**Avoids:** Pitfall 6 (user-scope permissions bug — documented in CLI output); Pitfall 7 (scope confusion — output explicitly states which file path was written)

**Research flag:** Validate at implementation time — re-verify Claude Code user-scope `permissions.allow` bug (#5140) against the installed Claude Code version. Behavior may have changed since research date (2026-02-24).

### Phase Ordering Rationale

- Path utilities and write primitives must precede all file-writing phases — the two most critical pitfalls are in the path layer and must be caught in isolation before any orchestration is wired
- `--minimal` must be complete and idempotency-tested before `--full` begins — `--full` is a superset; confirming the subset first catches core issues without `.planning/` complexity
- `--full` requires a locked written spec before Phase 3 starts — scope creep is a named pitfall and needs an explicit written boundary as the acceptance criterion
- Package.json wiring is deferred to Phase 4 — it has no bearing on correctness and can be done at any time before v1.4 ships

### Research Flags

Phases needing deeper research during planning:
- **Phase 4 (scope clarification):** Re-verify Claude Code user-scope `permissions.allow` bug status (#5140) against the installed version — behavior may have been fixed upstream since research was conducted.

Phases with standard patterns (skip research-phase):
- **Phase 1:** `os.homedir()`, `fs`, `path`, `JSON.parse/stringify` — stable Node.js built-ins, HIGH confidence, no research needed
- **Phase 2:** Sentinel block pattern, `process.argv` parsing, settings.json merge — well-established patterns
- **Phase 3:** File existence checks, directory scaffolding — trivial Node.js patterns

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions verified against npm registry 2026-02-24; CJS pattern validated against working gsd-tools.cjs in production; Node 20 built-ins confirmed sufficient |
| Features | HIGH | CLAUDE.md `@` import syntax and settings.json schema verified against official Claude Code docs; init CLI patterns cross-referenced against docker init, arc init, npm init behavior |
| Architecture | HIGH | Derived from direct codebase inspection of gsd-tools.cjs and viflo repo structure; `__dirname` / `process.cwd()` behaviors are stable Node.js semantics; Claude Code settings paths verified from official docs |
| Pitfalls | HIGH (path/idempotency) / MEDIUM (WSL2, scope bug) | Path and idempotency pitfalls verified from official docs and GSD codebase patterns; WSL2 scenarios partially inferred (Linux/macOS confirmed); user-scope permissions bug is documented but may be version-specific |

**Overall confidence:** HIGH

### Gaps to Address

- **STACK.md vs ARCHITECTURE.md location disagreement:** STACK.md proposes `packages/cli/` workspace; ARCHITECTURE.md recommends `bin/viflo.cjs` with `bin/lib/` modules and explicitly rejects `packages/cli/` as premature. Confirm `bin/viflo.cjs` is the canonical v1.4 decision in requirements before implementation begins.

- **Claude Code user-scope permissions bug (#5140):** Active at research time. Re-verify against the installed Claude Code version before deciding the default write scope for `--minimal`. If the bug is resolved, `~/.claude/settings.json` (user scope) is correct; if still open, project scope (`.claude/settings.json`) is the safe default.

- **Sentinel format as a shipped contract:** Once `<!-- viflo:start -->` / `<!-- viflo:end -->` markers appear in users' CLAUDE.md files, the format cannot change without a migration path. Confirm the exact sentinel strings before any write code is committed; document them as stable in v1.4.

- **WSL2 detection:** Research identifies the WSL2 / Windows Claude Code path mismatch as a known risk (PROJECT.md requires WSL support). Detection via `process.env.WSL_DISTRO_NAME` is documented but not tested. Allocate time in Phase 1 to implement and test detection logic, or explicitly document the WSL2 limitation with a workaround.

---

## Sources

### Primary (HIGH confidence)
- [Claude Code Settings Reference](https://code.claude.com/docs/en/settings) — Settings file scope hierarchy, `permissions.allow` format, project vs user scope paths (verified 2026-02-24)
- [Claude Code Memory / CLAUDE.md docs](https://code.claude.com/docs/en/memory) — `@` import syntax, file inclusion behavior, CLAUDE.md precedence (verified 2026-02-24)
- [Claude Code Permissions docs](https://code.claude.com/docs/en/permissions) — Full permissions system, allow/deny/ask rules, settings.json schema (verified 2026-02-24)
- `/home/ollie/.claude/get-shit-done/bin/gsd-tools.cjs` — CJS single-file CLI pattern, zero-dependency approach, `os.homedir()` usage validated against working production tool
- `viflo/package.json` (repo root) — Node `>=20.0.0`, pnpm `>=10.0.0`, CJS default confirmed (direct inspection)
- [Node.js fs docs](https://nodejs.org/api/fs.html) — `mkdirSync({recursive})`, `cpSync`, `writeFileSync` behavior verified for Node 20+
- [npm docs — bin field](https://docs.npmjs.com/cli/v7/configuring-npm/package-json#bin) — `#!/usr/bin/env node` shebang requirement, bin map format

### Secondary (MEDIUM confidence)
- [arc init idempotency docs](https://arc.codes/docs/en/reference/cli/init) — Skip-if-exists design; closest analogous pattern to viflo's `.planning/` scaffold approach
- [npm init additive behavior](https://docs.npmjs.com/cli/init) — Strictly additive, never removes existing values
- [GitHub issue #5140 — user-scope permissions not enforced](https://github.com/anthropics/claude-code/issues/5140) — Active bug; project-scope workaround documented
- [Node.js `os.homedir()` docs](https://nodejs.org/api/os.html#oshomedir) — Cross-platform home directory resolution behavior
- Developer guide to Claude Code settings.json (eesel.ai) — Project vs user scope distinction, example structures

### Tertiary (LOW confidence / needs validation)
- WSL2 path detection via `process.env.WSL_DISTRO_NAME` — inferred from Microsoft docs; not tested in WSL2 environment
- Claude Code `@` import one-time approval dialog behavior — documented in community sources (GitHub issues), not in official docs

---

*Research completed: 2026-02-24*
*Ready for roadmap: yes*
