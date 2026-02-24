# Pitfalls Research

**Domain:** CLI init tool that writes config files (CLAUDE.md, settings.json, .planning/ stubs) to wire new projects to viflo
**Researched:** 2026-02-24
**Confidence:** HIGH for path resolution and JSON merge issues (verified against official Claude Code docs and real codebase); MEDIUM for cross-platform specifics (Linux/macOS confirmed, WSL2 scenarios partially inferred); HIGH for idempotency patterns (verified from GSD existing code patterns and community sources)

---

## Critical Pitfalls

### Pitfall 1: Tilde Expansion Failure — `~/.claude/` Treated as a Literal Path

**What goes wrong:**
When `viflo init` writes the user-scope `settings.json` at `~/.claude/settings.json`, naively constructing the path as the string `~/.claude/settings.json` and passing it to `fs.writeFileSync` results in Node.js looking for a directory literally named `~` in the working directory. Node.js does NOT expand `~`. The write silently fails with `ENOENT` or writes to a wrong location if a `~` directory happens to exist.

**Why it happens:**
Shell expansion of `~` to `$HOME` happens at the shell parsing layer before the process receives arguments. Inside a Node.js process, `~` is a literal character. Developers test from a shell where typing `cat ~/.claude/settings.json` works fine (shell expanded), assume the path "works," and don't verify the actual file system path the Node.js code uses.

**How to avoid:**
Always construct user-home paths with `os.homedir()`:

```javascript
const os = require("os");
const path = require("path");

// CORRECT
const claudeSettingsPath = path.join(os.homedir(), ".claude", "settings.json");

// WRONG — do not do this
const claudeSettingsPath = "~/.claude/settings.json";
const claudeSettingsPath = path.join("~", ".claude", "settings.json");
```

`os.homedir()` reads `$HOME` (Linux/macOS) or the appropriate Windows registry key. It is the only reliable cross-platform home directory resolver in Node.js. The GSD codebase already uses this pattern correctly in `config.cjs` and `init.cjs` — viflo's CLI must follow the same convention.

**Warning signs:**

- Any string in the implementation containing a literal `~` passed to `fs.*` functions.
- `path.join('~', ...)` anywhere in the CLI code.
- A test that only verifies success when run from the user's shell but doesn't mock `os.homedir()`.

**Phase to address:**
Implementation phase (INIT-01 / INIT-02) — path construction utilities must be written and unit-tested before any file-writing code is added.

---

### Pitfall 2: Symlinked Home Directory Causes Double-Write or Wrong Target

**What goes wrong:**
On systems where `$HOME` is a symlink (NFS-mounted home directories in enterprise Linux environments, some macOS setups with `/Users` symlinked to another volume, some Docker-in-Docker configurations), `os.homedir()` returns the symlink path (e.g., `/home/user`), while `fs.realpathSync(os.homedir())` returns the real target (e.g., `/nfs/homes/user`). If the CLI checks for existing files using the real path but writes using the symlink path (or vice versa), the idempotency check (`if file already exists, skip`) produces a false negative and the file is written twice or to the wrong location.

**Why it happens:**
The file-exists check uses one path, the write uses a differently-resolved path. This is an order-of-operations error compounded by symlink resolution differences between `fs.existsSync` and `fs.realpathSync`.

**How to avoid:**
Use a single path variable derived from `os.homedir()` without any `realpathSync` call for user-facing config writes. Do not mix resolved and unresolved paths in the same check-then-write sequence. Store the path once at the top of the operation:

```javascript
const CLAUDE_DIR = path.join(os.homedir(), ".claude");
const SETTINGS_PATH = path.join(CLAUDE_DIR, "settings.json");

// Use SETTINGS_PATH for both existsSync check and writeFileSync
```

**Warning signs:**

- Code that calls `fs.realpathSync` on user home paths before writing.
- Separate variables derived from `os.homedir()` and `process.env.HOME` in the same function.

**Phase to address:**
Implementation phase (INIT-01) — single path derivation pattern enforced in the file-writing utility layer.

---

### Pitfall 3: `process.cwd()` vs. `__dirname` Confusion for Project-Relative Paths

**What goes wrong:**
`viflo init` must write files relative to the **user's current project directory** (e.g., `./CLAUDE.md`, `./.claude/settings.json`, `./.planning/`). Using `__dirname` instead of `process.cwd()` resolves paths relative to the viflo binary's installation directory (inside `node_modules` or the global npm prefix), not the user's project. Files land in the wrong directory, the user sees no error, and the project is not wired to viflo.

**Why it happens:**
`__dirname` is used in library code to locate bundled assets. Developers who write viflo's file-writing logic by copying patterns from internal module code accidentally use `__dirname` for user-facing output paths. The error is invisible in development if the developer runs the CLI from within the viflo repo itself (where `__dirname` and `process.cwd()` happen to coincide).

**How to avoid:**
Establish a strict convention at the module boundary: all project-relative paths are computed from `process.cwd()` passed as a `cwd` parameter. This is already the established pattern in GSD's `gsd-tools.cjs` — every command function accepts `cwd` as its first argument. Follow the same pattern in viflo's CLI:

```javascript
function writeClaudeMdStanza(cwd, vifloSkillsPath) {
  const targetPath = path.join(cwd, "CLAUDE.md");
  // ...
}
```

**Warning signs:**

- Any `path.join(__dirname, ...)` that produces an output file (as opposed to reading a bundled template from the package).
- CLI tests that only pass when run from the viflo repo root.

**Phase to address:**
Implementation phase (INIT-01) — enforced by code review and a CLI integration test that runs from a temp directory.

---

### Pitfall 4: Non-Idempotent settings.json Write — Clobbering User Permissions

**What goes wrong:**
`viflo init` writes a project-scoped `.claude/settings.json` containing a `permissions.allow` array of tool rules for viflo skill referencing. If the user has already added their own allow rules (e.g., `"Bash(git *)"`, `"WebSearch"`) and re-runs `viflo init`, a naive `fs.writeFileSync(path, JSON.stringify(VIFLO_DEFAULTS))` overwrites their customizations. The user's existing Claude Code workflow breaks. Re-running `viflo init` to upgrade viflo settings destroys user content.

**Why it happens:**
The happy path is tested (first run, no existing file). Re-run behaviour is either not tested or tested only with an identical file. The failure is discovered after a user reports lost configuration.

**How to avoid:**
Read-modify-write with a deep array merge:

1. If the file does not exist: write the default template.
2. If the file exists: parse it, merge viflo's entries into the existing arrays (additive for `permissions.allow`; do not remove existing entries), write back.
3. Use a sentinel comment or viflo-specific key to detect which entries viflo manages, so they can be updated on re-run without touching user entries.

```javascript
function mergeSettingsJson(existingPath, viFloEntries) {
  let existing = {};
  if (fs.existsSync(existingPath)) {
    existing = JSON.parse(fs.readFileSync(existingPath, "utf-8"));
  }
  const existingAllow = existing?.permissions?.allow ?? [];
  const merged = {
    ...existing,
    permissions: {
      ...existing.permissions,
      allow: [
        ...new Set([...existingAllow, ...viFloEntries.permissions.allow]),
      ],
    },
  };
  fs.writeFileSync(existingPath, JSON.stringify(merged, null, 2), "utf-8");
}
```

**Warning signs:**

- `fs.writeFileSync(settingsPath, JSON.stringify(FULL_DEFAULT_SETTINGS))` without an existence check.
- No test case for "run viflo init twice" or "run viflo init on a project with existing `.claude/settings.json`".
- `--force` flag added as a shortcut to skip the merge (removes the safety net).

**Phase to address:**
Implementation phase (INIT-01 / INIT-04) — idempotency is a hard requirement per INIT-04 and must be tested before the feature is marked complete.

---

### Pitfall 5: Invalid JSON Written to settings.json — Silent Claude Code Failure

**What goes wrong:**
Claude Code silently ignores a malformed `settings.json` (invalid JSON, trailing comma, unquoted key). The user sees no error on `viflo init` completion, but Claude Code falls back to its defaults, ignoring the viflo skill references. The user's Claude Code sessions have no viflo skill awareness. The bug is difficult to diagnose because Claude Code does not display a settings parse error at startup.

**Why it happens:**
String interpolation or manual JSON construction produces invalid JSON (trailing comma after the last array element, missing closing bracket). Template literals with conditionally-included entries are especially prone to this. The issue also appears when the read-modify-write merge produces a corrupt file if the existing settings.json is malformed (parse error on read followed by a write of an empty object).

**How to avoid:**

- Never construct JSON by string concatenation. Always build a JavaScript object and call `JSON.stringify(obj, null, 2)`.
- If reading an existing file, wrap `JSON.parse` in a try/catch and abort (do not overwrite) if the existing file is malformed. Surface the error to the user: "Existing `.claude/settings.json` is not valid JSON. Fix it manually and re-run `viflo init`."
- Validate the outgoing JSON by parsing it before writing: `JSON.parse(JSON.stringify(result))` — any object that survives this round-trip is valid JSON.

**Warning signs:**

- Template literals used to build JSON output.
- No `try/catch` around `JSON.parse` when reading existing settings.json.
- No post-write validation step.

**Phase to address:**
Implementation phase (INIT-01) — JSON handling utilities must validate on both read and write. Integration test: corrupt the existing settings.json and verify `viflo init` errors gracefully rather than writing over it.

---

### Pitfall 6: Overwriting User-Customized CLAUDE.md Content

**What goes wrong:**
Users who have already customized their project's `CLAUDE.md` (added project-specific context, team conventions, toolchain notes) lose their customizations when `viflo init --full` runs in full mode and writes a starter CLAUDE.md template. This is the most user-visible destructive failure mode. Unlike settings.json (which is JSON-mergeable), CLAUDE.md is freeform Markdown, making programmatic merge-without-clobber harder.

**Why it happens:**
The `--full` flag is associated with "write everything," and the initial implementation writes the full starter template unconditionally. The developer testing the tool tests from a blank directory where no CLAUDE.md exists. The destructive re-run case is not in the test matrix.

**How to avoid:**
Use a block-based update strategy rather than full-file replacement:

1. If CLAUDE.md does not exist: write the full starter template.
2. If CLAUDE.md exists: scan for a viflo-managed block delimited by sentinel markers:

   ```markdown
   <!-- viflo:start -->

   @.agent/skills/... (import stanza content)

   <!-- viflo:end -->
   ```

3. If the sentinel markers are present: replace only the content between them with the updated viflo import stanza. Leave everything outside the markers untouched.
4. If CLAUDE.md exists but has no sentinel markers: append the viflo import stanza at the end with the sentinels, never modify existing content.

This is the same pattern used by tools like `mise`, `direnv`, and shell profile managers that add entries to `.bashrc` / `.zshrc`.

**Warning signs:**

- `fs.writeFileSync(claudeMdPath, FULL_TEMPLATE)` without an existence check.
- No test case for "CLAUDE.md already exists with user content."
- `--force` flag that skips sentinel detection (acceptable for explicit user opt-in, but must be clearly documented as destructive).

**Phase to address:**
Implementation phase (INIT-03 for `--full` mode CLAUDE.md write; INIT-04 for idempotency contract). The sentinel strategy must be designed before writing any CLAUDE.md output code.

---

### Pitfall 7: Claude Code settings.json Scope Confusion — User vs. Project vs. Local

**What goes wrong:**
Claude Code has three settings file scopes:

- `~/.claude/settings.json` — user scope (applies to all projects)
- `.claude/settings.json` in the project root — project scope (should be committed)
- `.claude/settings.local.json` in the project root — local scope (gitignored)

`viflo init --minimal` is intended to wire Claude Code to viflo skills globally (user scope). Writing to `.claude/settings.json` (project scope) instead writes a file that will be committed to the user's repo — possibly exposing internal Claude Code configuration in a public repository, and also requiring every collaborator to re-run `viflo init` to get the same setup.

Writing to `~/.claude/settings.json` at user scope means the viflo skill references apply globally to all of the user's projects — which is the desired behavior for `--minimal` (viflo is a personal toolkit) but may surprise users who wanted project-scoped setup.

**Why it happens:**
The distinction between user scope and project scope is easy to miss. New developers building on top of Claude Code assume "settings.json" means one canonical file. The Claude Code docs do not prominently feature the scope hierarchy.

**How to avoid:**
Make the target scope explicit in the CLI's design and documentation:

- `viflo init --minimal` → writes to `~/.claude/settings.json` (user scope). Warn the user: "This will apply viflo skill references to all your Claude Code projects."
- `viflo init --full` → writes to `.claude/settings.json` (project scope). Warn the user: "This file will be committed to your repository."

Add a `--scope user|project` flag if both modes need to support both scopes. Never infer the scope silently.

**Warning signs:**

- Documentation or code that refers to "settings.json" without specifying which scope.
- `--minimal` mode that writes to project scope.
- No user-facing message explaining which file was written and what scope it applies to.

**Phase to address:**
Design phase (before implementation starts) — scope decision must be documented in the CLI design spec. Implementation phase (INIT-01) — must be validated by integration tests that check the written file path.

---

### Pitfall 8: Broken permissions.allow Merge Due to Unknown Merge Behavior

**What goes wrong:**
Claude Code's `permissions.allow` merge behavior across scopes is not fully documented. Community evidence and an open bug (#5140 in the anthropics/claude-code repo) indicates that user-scope `permissions.allow` may not be enforced in some Claude Code versions, requiring entries to be duplicated at the project scope to work reliably. If `viflo init --minimal` writes only to user scope, users on affected Claude Code versions will see their viflo skill references silently not applied.

Additionally, the merge strategy for hooks at different scopes is undocumented. There is an open bug where user-level permissions in `~/.claude/settings.json` are shown as "loaded" in `/permissions` but have no effect during command execution.

**Why it happens:**
The Claude Code settings system is evolving. Documentation lags implementation. Community workarounds (write to project scope) work but are not official.

**How to avoid:**

- Verify the permissions.allow scope behavior against the installed Claude Code version before writing to user scope only.
- At minimum, document the known limitation in `viflo init`'s output: "Note: user-scope permission rules may require Claude Code ≥ [version]. If Claude Code still prompts for tool approval after running `viflo init`, re-run with `--scope project`."
- Consider writing to `.claude/settings.local.json` (project local) for `--minimal` mode as a pragmatic workaround — this is gitignored, so it doesn't pollute the user's repo, and project scope is reliably enforced.

**Warning signs:**

- No mention of the scope bug in the CLI's README or output.
- No test that actually invokes Claude Code and verifies permissions are applied.
- Implementation assumes user-scope permissions always work.

**Phase to address:**
Implementation phase (INIT-01) — document the scope limitation in the CLI output; consider project-local scope as the default until the user-scope bug is resolved upstream.

---

### Pitfall 9: WSL2 Path Assumptions — Linux Home vs. Windows Path

**What goes wrong:**
Under WSL2, `os.homedir()` returns the WSL Linux home (e.g., `/home/username`). Claude Code for Windows stores its config at `C:\Users\username\.claude\` — accessible in WSL at `/mnt/c/Users/username/.claude/`. A user running `viflo init` inside WSL2 while using the Windows Claude Code installation will have the tool write to `/home/username/.claude/settings.json` (WSL Linux home) instead of `/mnt/c/Users/username/.claude/settings.json` (Windows Claude Code config). The Windows Claude Code never sees the viflo configuration.

**Why it happens:**
Most developers test on native Linux or macOS. The WSL2 split between Linux home and Windows home is a niche case that requires deliberate detection. `os.homedir()` correctly returns the Linux home from within WSL — it cannot know that the user intends to target the Windows Claude Code installation.

**How to avoid:**

- Detect WSL2 by checking `process.env.WSL_DISTRO_NAME` or reading `/proc/version` for `Microsoft`.
- If WSL2 is detected, check whether `~/.claude/settings.json` exists in the Linux home AND whether `/mnt/c/Users/*/. claude/settings.json` exists.
- If only the Windows path exists, warn the user: "WSL2 detected. Your Claude Code installation appears to be on Windows at `/mnt/c/Users/...`. Run `viflo init` from the Windows terminal or specify `--claude-dir /mnt/c/Users/<you>/.claude`."
- Document the WSL2 constraint in the README.

**Warning signs:**

- No WSL2 detection code in the CLI.
- Tests that pass on Linux but are never run in a WSL2 environment.
- No `--claude-dir` escape hatch for non-standard Claude Code installation paths.

**Phase to address:**
Implementation phase (INIT-01) — WSL2 detection is a first-class concern given that the PROJECT.md constraint explicitly states "Scripts must work on macOS, Linux, and WSL."

---

### Pitfall 10: .planning/ Scaffold Overwrites Existing Phase Structure

**What goes wrong:**
`viflo init --full` scaffolds a `.planning/` directory with template stubs (STATE.md, ROADMAP.md, PROJECT.md, etc.). On an existing project that is already mid-milestone using GSD methodology, writing these stubs overwrites the live planning documents. Existing roadmap phases, state tracking, and requirements are deleted. This is catastrophic — the project loses its planning history.

**Why it happens:**
The `--full` mode is tested on fresh directories. The brownfield case (existing `.planning/` with live content) is not in the test matrix. The failure mode mirrors the CLAUDE.md clobber pitfall but is worse because `.planning/` files are not easily reconstructed.

**How to avoid:**

- Check for existing `.planning/` before writing any scaffold files.
- If `.planning/` exists, default to "skip all existing files, write only missing ones." Log each skipped file: "Skipped `.planning/STATE.md` — already exists."
- If a file exists that conflicts with a required scaffold stub, surface a clear message: "`.planning/ROADMAP.md` already exists. To overwrite, use `viflo init --full --force`."
- The `--force` flag must require explicit confirmation or a `--yes` non-interactive flag to prevent accidents.

```
$ viflo init --full
.planning/ already exists with 5 files.
Writing only missing scaffold files...
  + Created: .planning/todos/pending/ (new directory)
  ~ Skipped: .planning/STATE.md (exists)
  ~ Skipped: .planning/ROADMAP.md (exists)
```

**Warning signs:**

- `fs.mkdirSync` + `fs.writeFileSync` for every scaffold file without existence checks.
- No test case for "run `viflo init --full` on a project already using GSD methodology."
- `--full` documentation that doesn't explicitly state which files are safe to re-run.

**Phase to address:**
Implementation phase (INIT-02 / INIT-04) — scaffold write loop must be existence-aware by design, not as a retrofit.

---

### Pitfall 11: Scope Creep in `--full` Mode — "Full" Becomes a Moving Target

**What goes wrong:**
`--full` mode starts with a clear spec: scaffold `.planning/` + write starter CLAUDE.md. During implementation, it grows to also: run `git init`, install a pre-commit hook, add a `.gitignore` entry, create a `scripts/` directory, write a Makefile target. Each addition seems logical in isolation. The result is a `--full` mode that modifies the user's project structure beyond what was designed, causes unexpected side effects in brownfield projects, and is harder to make idempotent because each additional artifact adds a new failure mode.

**Why it happens:**
Tooling authors optimise for the "magic one command" experience. Every additional thing `--full` does seems to reduce setup friction. The accumulation is not visible as scope creep because each individual addition is small.

**How to avoid:**
Lock the `--full` spec before implementation starts and treat it as a hard boundary:

```
--minimal: write ~/.claude/settings.json (user scope, permissions.allow for viflo skills)
           write CLAUDE.md import stanza (sentinel-based, non-destructive)

--full: everything --minimal does, PLUS:
        scaffold .planning/ directory (write only missing files)
        write starter CLAUDE.md template (if no CLAUDE.md exists; append stanza if exists)
```

Nothing else. Any additional behavior requires a new flag or a separate command. If a feature is requested during implementation that doesn't fit either mode, add it to the `v1.5` backlog, not to `--full`.

**Warning signs:**

- Implementation PR description includes "also added X because it seemed useful."
- `--full` mode that runs `git` commands or modifies files outside `CLAUDE.md`, `.claude/`, and `.planning/`.
- No explicit written spec for what `--full` does and doesn't do before implementation begins.

**Phase to address:**
Design phase (before implementation starts) — write a one-paragraph "what --full does and does NOT do" section in the CLI design doc and treat it as an acceptance criterion.

---

## Technical Debt Patterns

| Shortcut                                                                                                           | Immediate Benefit                | Long-term Cost                                                   | When Acceptable                                                                     |
| ------------------------------------------------------------------------------------------------------------------ | -------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Use hardcoded string `"~/.claude"` instead of `os.homedir()`                                                       | Simpler code                     | Silently writes to wrong path; `ENOENT` in Node.js               | Never                                                                               |
| Skip the read-modify-write for settings.json; just overwrite                                                       | Simpler code                     | Destroys user's existing Claude Code permissions on re-run       | Never                                                                               |
| Write full CLAUDE.md template unconditionally                                                                      | Simpler code                     | Destroys user's project-specific CLAUDE.md customizations        | Never                                                                               |
| Skip WSL2 detection; document as "run from Windows terminal"                                                       | Saves dev time                   | Users run from WSL2 terminal, report "viflo init doesn't work"   | Acceptable as v1.4 cut if clearly documented with a workaround                      |
| Write to `.claude/settings.json` (project scope) instead of `~/.claude/settings.json` (user scope) for `--minimal` | Avoids user-scope permission bug | File gets committed to user repos; not the intent of `--minimal` | Acceptable as a workaround for the user-scope bug if communicated                   |
| Add `--force` to skip all safety checks                                                                            | Easy escape hatch                | Users accidentally destroy existing config                       | Acceptable only with `--yes` confirmation flag and clear destructive-action warning |
| Scaffold all `.planning/` files without checking existence                                                         | Simpler loop                     | Clobbers live planning documents on re-run                       | Never                                                                               |

---

## Integration Gotchas

| Integration               | Common Mistake                                                                                | Correct Approach                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Claude Code settings.json | Writing to wrong scope (`~/.claude/` vs `.claude/`) for the intended use case                 | `--minimal` targets user scope; `--full` targets project scope; document both clearly    |
| Claude Code settings.json | Assuming `permissions.allow` entries from user scope are enforced in all Claude Code versions | Check for the open scope enforcement bug; offer `--scope project` or `.local` workaround |
| Claude Code settings.json | String-building JSON with template literals                                                   | Build JS objects, call `JSON.stringify(obj, null, 2)` always                             |
| CLAUDE.md                 | Full file overwrite on re-run                                                                 | Sentinel marker strategy — only update the viflo-managed block                           |
| .planning/ scaffold       | Writing all stub files unconditionally                                                        | Check existence of each file; skip existing files and report what was skipped            |
| WSL2                      | `os.homedir()` returns Linux home but user's Claude Code is the Windows installation          | Detect `WSL_DISTRO_NAME`; warn if Windows Claude Code config path exists                 |
| Existing viflo project    | Running `viflo init --full` after the project already uses GSD methodology                    | Existence-check every file before writing; never clobber planning documents              |

---

## Performance Traps

Not applicable at the scale of a CLI init tool — the tool runs once (or occasionally on re-run), writes a handful of small files, and exits. Performance is not a concern. Correctness and safety are.

---

## Security Mistakes

| Mistake                                                                        | Risk                                                                                    | Prevention                                                                                                                                         |
| ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Writing to paths derived from user-supplied CLI arguments without sanitization | Path traversal: `viflo init --claude-dir ../../../../etc/` writes to system directories | Validate `--claude-dir` is an absolute path inside the user's home directory; reject paths containing `..`                                         |
| Committing `.claude/settings.local.json` to the user's repo                    | Exposes local Claude Code permissions, API keys set via `env` key                       | Use project scope (`.claude/settings.json`) for commitable config; document that `settings.local.json` should be in `.gitignore`                   |
| Writing viflo skill paths as absolute paths in settings.json                   | If viflo moves or the user's home directory changes, all skill references break         | Write paths relative to `~` using a `$HOME`-based pattern, or write the `@` import stanza in CLAUDE.md rather than absolute paths in settings.json |

---

## "Looks Done But Isn't" Checklist

- [ ] **Path resolution:** `os.homedir()` used for all user-home-relative paths — verify no `~` literals in `fs.*` calls.
- [ ] **Idempotency:** Running `viflo init` twice on the same project produces the same result — verify with a test that runs the command twice and compares file content.
- [ ] **settings.json merge:** Existing `permissions.allow` entries are preserved on re-run — verify with a test that seeds a settings.json with user entries before running `viflo init`.
- [ ] **CLAUDE.md sentinel:** Re-run on a project with a customized CLAUDE.md only updates the viflo-managed block — verify the content outside the sentinel markers is unchanged.
- [ ] **Malformed settings.json guard:** Running `viflo init` on a project with an invalid `settings.json` errors with a human-readable message instead of writing a corrupt file — verify with a test that seeds an invalid JSON file.
- [ ] **Scope clarity:** CLI output explicitly states which file was written and at which scope — verify the success message includes the full resolved path.
- [ ] **WSL2 warning:** WSL2 environments get a warning if `os.homedir()` returns a Linux home while a Windows Claude Code installation is detected — verify detection logic exists.
- [ ] **`.planning/` safety:** Running `viflo init --full` on an existing GSD project skips existing files and reports what was skipped — verify no planning documents are overwritten.
- [ ] **`--full` scope:** The implementation does not include any behavior not in the written `--full` spec — verify against the spec before marking INIT-02 complete.
- [ ] **Integration test from temp dir:** At least one integration test runs the CLI from a temporary directory (not the viflo repo root) — verify `process.cwd()` vs `__dirname` distinction is exercised.

---

## Recovery Strategies

| Pitfall                                                       | Recovery Cost | Recovery Steps                                                                                                                                              |
| ------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User's `~/.claude/settings.json` overwritten                  | MEDIUM        | Check `~/.claude/` for backup created by viflo (if implemented); restore from git if user has `~/.claude/` in a dotfiles repo; manually re-add lost entries |
| User's `CLAUDE.md` overwritten                                | MEDIUM        | Restore from `git diff HEAD~1 CLAUDE.md` if project is under git; if not, user must re-add customizations manually                                          |
| User's `.planning/` documents overwritten                     | HIGH          | Restore from git history (`git log --oneline -- .planning/`); if no git, files may be unrecoverable                                                         |
| Files written to wrong path (tilde not expanded)              | LOW           | Delete the `~` directory that was created; re-run after fix                                                                                                 |
| Invalid JSON written to settings.json                         | LOW           | Delete the file; re-run `viflo init`; Claude Code resumes using defaults                                                                                    |
| WSL2 user writes to Linux home instead of Windows Claude path | LOW           | Manually copy `~/.claude/settings.json` to `/mnt/c/Users/<username>/.claude/settings.json`                                                                  |

---

## Pitfall-to-Phase Mapping

| Pitfall                            | Prevention Phase                                      | Verification                                                                            |
| ---------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------- |
| Tilde expansion failure            | INIT-01 implementation — path utilities               | Unit test: mock `os.homedir()` to a temp dir; verify no `~` in written paths            |
| Symlinked home directory confusion | INIT-01 implementation — single path variable pattern | Code review: one path variable per target file, never re-derived                        |
| `process.cwd()` vs `__dirname`     | INIT-01 implementation — cwd parameter convention     | Integration test run from a temp directory outside the viflo repo                       |
| settings.json clobber on re-run    | INIT-04 idempotency — read-modify-write with merge    | Test: run twice; assert user's existing `allow` entries survive the second run          |
| Invalid JSON write                 | INIT-01 implementation — JSON utilities               | Test: corrupt existing settings.json; assert CLI errors, not overwrites                 |
| CLAUDE.md clobber                  | INIT-03 + INIT-04 — sentinel marker strategy          | Test: run with pre-existing CLAUDE.md; assert only sentinel block updated               |
| settings.json scope confusion      | Design phase before INIT-01                           | Documentation + CLI output review: output must state which file path was written        |
| permissions.allow scope bug        | INIT-01 implementation — scope workaround             | Manual test: verify Claude Code applies the written permissions                         |
| WSL2 home path mismatch            | INIT-01 implementation — WSL2 detection               | Test in WSL2 environment or mock `WSL_DISTRO_NAME`                                      |
| .planning/ scaffold clobber        | INIT-02 + INIT-04                                     | Test: run `--full` on a project with existing `.planning/`; assert no files overwritten |
| Scope creep in `--full` mode       | Design phase — written spec before INIT-02            | Acceptance: INIT-02 completion review checks implementation against spec                |

---

## Sources

**Official Claude Code Documentation**

- [Claude Code Settings Reference](https://code.claude.com/docs/en/settings) — Scope hierarchy, all valid top-level keys, managed settings paths (verified 2026-02-24)

**Known Bugs and Limitations**

- [User-level permissions in `~/.claude/settings.json` not enforced (GitHub #5140)](https://github.com/anthropics/claude-code/issues/5140) — Active bug: user-scope `permissions.allow` shown as loaded but not enforced; workaround is project scope

**Path Handling in Node.js**

- [Node.js `os.homedir()` Method](https://www.geeksforgeeks.org/node-js/node-js-os-homedir-method/) — Cross-platform home directory resolution
- [Tilde Expansion Fails in Environment Variables in Shell Scripts](https://linuxvox.com/blog/tilde-expansion-in-environment-variable/) — Why `~` is not expanded outside shell parsing layer
- [Symlink Resolution in Node.js (nodejs/node #3402)](https://github.com/nodejs/node/issues/3402) — Node.js resolves symlinks in `require` but not in user-supplied paths

**WSL2 Path Considerations**

- [Install Node.js on WSL2 (Microsoft Docs)](https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-wsl) — `os.homedir()` behavior in WSL2 Linux context
- [wsl-path npm package](https://www.npmjs.com/package/wsl-path) — Utility for converting WSL POSIX paths to Windows paths

**Idempotency Patterns**

- [How to Write Idempotent Bash Scripts](https://arslan.io/2019/07/03/how-to-write-idempotent-bash-scripts/) — Check-then-act patterns; grep-based sentinel detection
- GSD codebase `config.cjs` — `cmdConfigEnsureSection` demonstrates the correct read-check-write pattern for config files in this repo

**Claude Code settings.json Schema**

- [claude-code-settings-schema.json (community gist)](https://gist.github.com/xdannyrobertsx/0a395c59b1ef09508e52522289bd5bf6) — Community-documented schema reference
- [A developer's guide to settings.json in Claude Code](https://www.eesel.ai/blog/settings-json-claude-code) — Array merge behavior, scope precedence

---

_Pitfalls research for: viflo init CLI — config file writing, idempotency, cross-platform path resolution_
_Researched: 2026-02-24_
