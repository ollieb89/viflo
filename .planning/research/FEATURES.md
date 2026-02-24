# Feature Research

**Domain:** CLI Init Tool for Agentic Development Environment (viflo init)
**Researched:** 2026-02-24
**Confidence:** HIGH (CLAUDE.md @ import syntax and settings.json schema verified against official Claude Code docs; init CLI patterns cross-referenced against docker init, nuxt init, arc init, npm init behaviour)

---

## Context: What "Wired to Viflo" Actually Means

Before listing features, it is worth being precise about what `viflo init` needs to produce.

**A project "wired to viflo" needs two things:**

1. **CLAUDE.md with an import stanza** — The file Claude Code reads on session start. It must contain `@` import lines pointing to the viflo skills the project wants available. Claude Code's `@` import is a literal file inclusion: the referenced file's content is injected at that position. Skills live at the viflo install path (resolved at run time). The import stanza needs to use absolute or home-relative paths (`~/.viflo/skills/...`) that Claude Code can resolve at session start.

2. **`.claude/settings.json` with safe project permissions** — This is checked into version control and shared across the team. It should allow the common Bash and file operations used in viflo workflows (git, pnpm/npm, test runners) without granting blanket `bypassPermissions`. Minimal is better: a project can always add more.

The `--minimal` mode writes only these two artifacts into an existing project. The `--full` mode also scaffolds the `.planning/` directory (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md stubs) and writes a starter CLAUDE.md with project-specific sections beyond just the import stanza.

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = tool feels broken or dangerous.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Detect existing CLAUDE.md and refuse to silently overwrite | Developers have custom content; silent overwrite destroys it. Every mature init tool (docker init, nuxt init) warns before overwrite | LOW | Check file existence before writing; use sentinel block pattern rather than wholesale replacement |
| Detect existing `.claude/settings.json` and merge, not replace | Project may already have project-specific allow/deny rules. Replacing loses them | MEDIUM | Deep merge the `permissions.allow` and `permissions.deny` arrays; do not replace the entire JSON object. Skip write if no change |
| Idempotent re-runs — safe to run twice with identical output | Users re-run inits when updating viflo. If output differs each run, re-running becomes risky | MEDIUM | Compare new content against existing before writing; emit "already up to date" for unchanged files |
| `--minimal` flag that writes only CLAUDE.md stanza + settings.json | Matches the stated v1.4 requirement (INIT-01). Users with existing projects want surgical injection, not full scaffolding | LOW | Two file operations: inject sentinel block into CLAUDE.md (or create it), create/merge settings.json |
| `--full` flag that also scaffolds `.planning/` directory | Matches the stated v1.4 requirement (INIT-02, INIT-03). New projects need GSD artifact stubs to start planning | MEDIUM | Create dir tree if absent; write stub files; skip files that already exist rather than overwriting |
| Human-readable output — show what was written, what was skipped, what was merged | All polished init CLIs (create-next-app, docker init) print a clear file list. Silent success = confusion | LOW | Log each file with a status: created / updated / skipped / merged |
| Error on missing viflo install path when generating import stanzas | Generating an `@/path/that/does/not/exist` import silently produces a broken CLAUDE.md that Claude Code cannot resolve | LOW | Resolve skill paths before writing; bail with a clear message if viflo cannot be located |
| Correct `.claude/settings.json` schema output | Must be valid JSON matching the Claude Code schema. Wrong JSON breaks Claude Code startup | LOW | Include `$schema` key for editor autocomplete; validate before write |

### Differentiators (Competitive Advantage)

Features that set the init apart. Not required to ship, but add clear value.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Append-only CLAUDE.md stanza with sentinel comments | Rather than rewriting the entire CLAUDE.md, inject a delimited block that can be found and replaced on re-run. Preserves all user content above and below the block | MEDIUM | Parse existing file for sentinel start/end markers; replace block content on re-run; insert at end if block absent. This is the primary idempotency mechanism for CLAUDE.md |
| `--dry-run` flag to preview changes without writing | Reduces anxiety for users running on existing projects with custom configs | LOW | Print would-write diff without touching files; makes init safe to explore |
| `--force` flag to replace sentinel block content without prompt | Power users who want a clean re-scaffold after manual edits corrupted the block | LOW | Replace only the sentinel-bounded region; never touch content outside it |
| Verification pass after writing — confirm injected paths resolve | Read back the written files; verify `@` import paths exist on disk; report broken references | LOW | Simple `fs.existsSync` checks on each injected path; emits a warning (not a failure) for missing optional skills |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems. Explicitly decline these.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Interactive wizard prompting for project name, stack, author | Familiar from create-next-app and vue create; feels polished | Adds significant complexity for minimal payoff. viflo init's job is config injection, not project bootstrapping. Interactive prompts slow CI/automation usage | Accept `--name` as a CLI argument for non-interactive use; default to current directory name |
| Full package.json or monorepo scaffolding | Seems logical as an extension of `--full` | Far out of scope. viflo init wires AI config; it does not bootstrap project structure | Explicitly document this boundary; point to create-next-app for project bootstrapping |
| Automatically detecting and installing viflo if not installed | Convenient if viflo is not yet installed | Creates a circular dependency: init needs viflo to know where skills are. Installing in the middle of init creates unreliable state | Fail fast with a clear install instruction instead |
| Semantic merge of two CLAUDE.md files (section matching) | Users want smart merge that combines their sections with viflo's | Semantic merge of Markdown is fragile and unpredictable. Claude Code reads CLAUDE.md literally; merged content order matters | Sentinel block pattern: user sections are never touched, viflo sections are bounded and replaceable |
| Writing `.claude/settings.local.json` | Local settings file feels like a natural output | `settings.local.json` is gitignored by convention and is personal. viflo init should only touch the shared project settings | Write only `.claude/settings.json`; document that users can add local overrides themselves |
| Generating CLAUDE.md content from codebase analysis | Makes the file more immediately useful for new users | Requires reading the codebase, which is out of scope for a config injection tool and creates a heavyweight dependency | `--full` writes a clearly-labelled starter template with `[TODO: fill in]` placeholders rather than attempting inference |
| Skill selection wizard (which skills do you need?) | Tailored import stanzas are more useful than all-skills import | High complexity for v1; adds a skill taxonomy and detection heuristics | Default to importing all skills; users trim the stanza manually |

---

## Feature Dependencies

```
[Resolve viflo install path]
    └──required by──> [Write CLAUDE.md sentinel block with skill imports]
                          └──required by──> [--minimal mode output]
                          └──required by──> [--full mode output]

[Detect existing CLAUDE.md]
    └──required by──> [Sentinel block append-or-replace logic]
    └──required by──> [Idempotent re-run for CLAUDE.md]

[Detect existing settings.json]
    └──required by──> [Merge permissions arrays]
    └──required by──> [Idempotent re-run for settings.json]

[Write abstraction layer]
    └──required by──> [--dry-run flag]
    └──required by──> [Change detection before write]

[--minimal mode]
    └──subset of──> [--full mode]

[Sentinel block pattern]
    └──enables──> [--force flag for block replacement]
    └──enables──> [Idempotent CLAUDE.md re-runs]

[.planning/ stub scaffolding]
    └──part of──> [--full mode only]
    └──uses──> [skip-if-exists per file]
```

### Dependency Notes

- **Resolve viflo install path must happen before any file write:** Init cannot generate valid `@` import paths without knowing where viflo skills live on disk. This means init must be a post-install command, not a standalone bootstrap. The path resolution strategy (environment variable, config file, or binary location) needs to be decided before implementation.
- **Sentinel block format is a shipped contract:** Once users have sentinel comments in their CLAUDE.md, changing the comment format breaks idempotency for everyone. Choose the sentinel format before v1 and document it as stable. Proposed: `<!-- viflo:skills:start -->` and `<!-- viflo:skills:end -->` (HTML comments are ignored by markdown renderers).
- **`--minimal` is a strict subset of `--full`:** Full mode does everything minimal does, then adds `.planning/` scaffolding and a richer CLAUDE.md starter. Implement minimal correctly first; full composes on top of it.
- **`--dry-run` requires the write layer to be abstracted from the start:** All file writes must go through a single function that can be swapped for a no-op print. Retrofitting this after implementation is painful. Design it in from day one.
- **settings.json merge requires JSON schema awareness:** The merge must not blindly concat arrays (creates duplicates) or overwrite the entire file (loses user keys). Use deduplicated array union for `allow` and `deny`; leave all other keys untouched.

---

## MVP Definition

### Launch With (v1 — this milestone, INIT-01 through INIT-04)

Minimum viable product — what is needed to satisfy the four active requirements.

- [ ] **Resolve viflo install path** — detect where skills live (from a config file, environment variable, or the calling binary's location); fail with clear message if not found
- [ ] **Write CLAUDE.md import stanza using sentinel block pattern** — append block to existing file or create new file; replace block content on re-run (idempotent); never touch content outside sentinels
- [ ] **Write `.claude/settings.json`** — create with minimal safe permissions if absent; deep-merge permissions arrays (deduplicated union) if file already exists
- [ ] **`--minimal` flag** — the two operations above only
- [ ] **`--full` flag** — additionally scaffold `.planning/` directory with PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md stubs (skip-if-exists per file); write or update starter CLAUDE.md sections
- [ ] **Idempotent re-runs** — compare new content against existing state before writing; emit "already up to date" for unchanged files
- [ ] **Human-readable output** — log each file action (created / updated / skipped / merged) with the file path
- [ ] **Fail fast on missing viflo path** — clear error message with install instructions, not a silent broken import

### Add After Validation (v1.x)

Features to add once core is working and tested on real projects.

- [ ] **`--dry-run` flag** — implement once write abstraction is confirmed clean; low cost if designed in from day one
- [ ] **`--force` flag** — replace sentinel block content without change detection; useful when manual edits corrupted the block
- [ ] **Verification pass** — after writing, check that all injected `@` import paths resolve on disk; emit warnings for missing references

### Future Consideration (v2+)

Features to defer until the init command has real user feedback.

- [ ] **Stack-aware skill selection** — detect Node/Python/framework stack and inject a subset of skills; requires defining a skill taxonomy and detection heuristics; HIGH complexity
- [ ] **Interactive wizard mode** — only if users report that the flag-based API is confusing
- [ ] **Plugin registry for third-party skills** — viflo skills are the only target for v1; defer extensibility

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Sentinel block CLAUDE.md injection | HIGH | MEDIUM | P1 |
| settings.json create with safe defaults | HIGH | LOW | P1 |
| settings.json deep merge (existing file) | HIGH | MEDIUM | P1 |
| Idempotent re-runs (change detection) | HIGH | LOW | P1 |
| `--minimal` / `--full` flags | HIGH | LOW | P1 |
| Human-readable per-file output | HIGH | LOW | P1 |
| Fail fast on bad install path | HIGH | LOW | P1 |
| `.planning/` stub scaffolding (--full) | MEDIUM | LOW | P1 |
| Starter CLAUDE.md template sections (--full) | MEDIUM | LOW | P1 |
| `--dry-run` flag | MEDIUM | LOW | P2 |
| `--force` flag | MEDIUM | LOW | P2 |
| Verification pass after writing | MEDIUM | LOW | P2 |
| Stack-aware skill selection | MEDIUM | HIGH | P3 |
| Interactive wizard | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for this milestone (INIT-01 through INIT-04)
- P2: Should have, add when core is stable
- P3: Nice to have, future milestone

---

## Analogous Tool Behavior

How comparable init CLIs handle the patterns this feature set requires.

| Behavior | docker init | nuxt init | arc init | npm init | Our Approach |
|----------|-------------|-----------|----------|----------|--------------|
| Existing file detection | Warns, prompts user to overwrite all or nothing | Prompts to overwrite or skip the target directory | Skip-if-exists by design; fully idempotent | Reads existing fields, strictly additive | Sentinel block for CLAUDE.md; array union merge for settings.json |
| Re-run behaviour | Not idempotent — prompts again each time | Not idempotent — prompts again | Idempotent — no-op if file exists | Additive — never removes existing values | Idempotent via sentinel block detection + settings diff |
| Minimal vs full modes | Single mode (all Docker files generated) | Single mode (full project scaffold) | Not applicable | Not applicable | Explicit `--minimal` / `--full` flags; minimal is the safe default |
| Output verbosity | Lists each generated file with icon | Minimal output, sparse | Silent on skips | Question prompts + summary | List each file with action verb and absolute path |
| Custom content preservation | No (user must back up Dockerfile manually) | No (overwrite is all-or-nothing) | Yes (never touches existing files) | Yes (additive only, never removes) | Yes — sentinel block never touches content outside its markers |

**Key insight from analogues:** The most common complaint about init CLIs is accidental overwrite of custom content. The sentinel block pattern (used in Ansible's `# BEGIN ANSIBLE MANAGED BLOCK` / `# END ANSIBLE MANAGED BLOCK` convention and similar config management systems) solves this cleanly: viflo owns the region between the sentinels, the user owns everything else.

**The arc init precedent is the closest model:** It generates files only if they do not already exist and is documented as safe to re-run. For CLAUDE.md specifically, viflo cannot use skip-if-exists because the file will usually already exist with user content — hence the sentinel block extension of this pattern.

---

## What Goes in CLAUDE.md vs settings.json

This distinction is critical for getting the output of `viflo init` correct.

### CLAUDE.md contains (knowledge, conventions, instructions)

Per official Claude Code documentation: "CLAUDE.md controls what Claude should know." This includes:

- `@` import lines pointing to viflo skills the project uses
- Project-specific coding conventions (added by user, not by init)
- Architectural decisions Claude should know about
- Which files or directories are off-limits for editing

**The viflo-generated sentinel block (minimal mode):**

```markdown
<!-- viflo:skills:start -->
<!-- Managed by viflo init — edit this block by running: viflo init --minimal -->
@~/.viflo/skills/gsd-workflow/SKILL.md
@~/.viflo/skills/frontend/SKILL.md
@~/.viflo/skills/backend-dev-guidelines/SKILL.md
@~/.viflo/skills/database-design/SKILL.md
<!-- viflo:skills:end -->
```

**The viflo-generated CLAUDE.md starter template (full mode only) adds:**

```markdown
# [Project Name]

## Project Overview

[TODO: 2-3 sentence description of this project]

## Common Commands

[TODO: fill in build, test, and lint commands]

## Architecture Notes

[TODO: key architectural decisions Claude should know]

<!-- viflo:skills:start -->
<!-- Managed by viflo init — edit this block by running: viflo init --minimal -->
@~/.viflo/skills/gsd-workflow/SKILL.md
...
<!-- viflo:skills:end -->
```

### settings.json contains (permissions and behaviour)

Per official Claude Code documentation: "settings.json controls what Claude can do." Project settings at `.claude/settings.json` are committed to version control and apply to all collaborators.

**The viflo-generated minimal settings.json:**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(pnpm *)",
      "Bash(npm *)",
      "Bash(node *)",
      "Bash(python3 *)",
      "Bash(pytest *)",
      "WebSearch",
      "WebFetch(domain:github.com)"
    ],
    "defaultMode": "acceptEdits"
  }
}
```

**What init must NOT write to settings.json:** `bypassPermissions` mode, deny rules (too project-specific), MCP server definitions, sensitive env vars, `skipDangerousModePermissionPrompt: true`.

**What init adds when merging into an existing settings.json:** Union of the above allow patterns into the existing `permissions.allow` array, deduplicated. All other existing keys are left unchanged.

---

## Idempotency Implementation Patterns

Based on the arc init and npm init precedents, these are the correct approaches per artifact:

**CLAUDE.md (sentinel block):**
1. Search for `<!-- viflo:skills:start -->` in existing file
2. If found: replace everything between start and end sentinels with new skill list; leave content outside sentinels unchanged
3. If not found: append the full block (start sentinel + imports + end sentinel) to the end of the file
4. If file does not exist: create it with the sentinel block only (minimal) or with the full starter template (full)
5. Before writing: compare new block against existing block; if identical, emit "already up to date" and skip

**settings.json (deep merge):**
1. Read existing file if present; parse as JSON
2. Compute union of existing `permissions.allow` + viflo defaults, deduplicated
3. Compute union of existing `permissions.deny` + viflo defaults (empty for v1), deduplicated
4. Set `permissions.defaultMode` to `acceptEdits` if not already set (do not override if user has set it)
5. Leave all other top-level keys unchanged
6. Before writing: compare merged result against existing file; if identical, emit "already up to date" and skip

**`.planning/` stubs (skip-if-exists):**
1. For each stub file (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md): check if it already exists
2. If it exists: emit "skipped (already exists)" and do not touch it
3. If it does not exist: write the template stub

---

## Sources

- [Claude Code Permissions Docs](https://code.claude.com/docs/en/permissions) — permissions system, settings.json schema, allow/deny/ask rules; HIGH confidence (official docs, fetched 2026-02-24)
- [Claude Code Settings Docs](https://code.claude.com/docs/en/settings) — full settings.json key reference, precedence hierarchy; HIGH confidence (official docs, fetched 2026-02-24)
- [CLAUDE.md @ import syntax](https://github.com/anthropics/claude-code/issues/6321) — confirmed `@path/to/file` literal inclusion, no heading adjustment, recursive imports supported; MEDIUM confidence (GitHub issue, consistent with official overview)
- [docker init behavior](https://spacelift.io/blog/docker-init) — warns on existing files, prompts for overwrite decision, no --force flag; MEDIUM confidence (blog consistent with official Docker docs)
- [arc init idempotency](https://arc.codes/docs/en/reference/cli/init) — explicit "generates files only if they do not already exist" design; HIGH confidence (official arc docs)
- [npm init additive behavior](https://docs.npmjs.com/cli/init) — strictly additive, keeps existing fields; HIGH confidence (official npm docs)
- [nuxt init existing project handling](https://github.com/vuejs/vue-cli/issues/267) — confirms prompts on existing project but does not do semantic merge; MEDIUM confidence (GitHub issue)
- Developer guide to Claude Code settings.json, eesel.ai — project vs user scope distinction, example structures; MEDIUM confidence (blog, consistent with official docs)

---

*Feature research for: viflo init CLI (v1.4 milestone)*
*Researched: 2026-02-24*
