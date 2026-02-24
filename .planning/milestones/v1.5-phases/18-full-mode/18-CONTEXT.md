# Phase 18: Full Mode - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

`viflo init --full` creates a GSD planning scaffold (`.planning/` directory with four stub files) and a richer starter CLAUDE.md template for new projects. It is a superset of `--minimal` — it runs all of `--minimal`'s logic (sentinel block injection + settings.json wiring) and additionally creates the `.planning/` scaffold and a project-context CLAUDE.md template. New capabilities (e.g. additional flags, restore/migrate commands) belong in other phases.

</domain>

<decisions>
## Implementation Decisions

### Scaffold file contents
- **PROJECT.md**: Minimal section headers only (`# Project`, `## Goals`, `## Stack`, etc.) — empty, ready to fill in. No placeholder text or instructions.
- **ROADMAP.md**: Minimal milestone scaffold with a commented example phase entry showing the expected GSD format — enough for the user to see the structure and fill in their own phases.
- **config.json**: Valid JSON with GSD defaults pre-populated (e.g. `profile: "balanced"`, `commit_docs: true`). Works out of the box without any manual editing.
- **STATE.md**: Minimal valid STATE.md that GSD tools can parse — empty decisions/blockers arrays, null current_phase. Not a completely empty file.

### CLAUDE.md template (when created fresh by --full)
- Includes the viflo sentinel block (`<!-- BEGIN VIFLO -->` / `<!-- END VIFLO -->` with skill imports) — `--full` delivers a fully wired CLAUDE.md in one step.
- Contains GSD-oriented project sections above the sentinel block: `# Project`, `## Tech Stack`, `## Development Workflow` with a pointer to `/gsd:` commands.
- This is richer than `--minimal`'s output: `--minimal` only injects the sentinel block into an existing or new file; `--full` creates a fuller starter template with project sections + sentinel.

### Relationship to --minimal
- `--full` is a **superset** of `--minimal`: it executes all `--minimal` logic plus the `.planning/` scaffold and CLAUDE.md template.
- Fully **idempotent**: running `--full` on a project that already had `--minimal` applied is safe — sentinel block unchanged, settings.json unchanged, `.planning/` files skipped if they already exist.
- No special "already have --minimal applied" messaging — per-file status lines communicate what was done vs skipped.
- **Mental model for docs/help text**: `--full` = new project setup; `--minimal` = add viflo to an existing project.

### Per-file output behavior
- Same labelled per-file format as `--minimal`: one line per file showing action and path.
  - `  created  .planning/PROJECT.md`
  - `  skipped  .planning/STATE.md (already exists)`
- Skipped files show a simple `(already exists)` suffix — no verbose explanation needed.
- Summary line at the end: `Done. 3 files created, 2 skipped.`
- On first-time run (all files created), a brief instructional nudge at the end: e.g. `Next: edit .planning/PROJECT.md and run /gsd:new-project to plan your first milestone.`
- No nudge when files are skipped (not a first-time run scenario).

### If CLAUDE.md already exists when --full is run
- Same behavior as `--minimal`: only the viflo sentinel block is injected/updated. Existing content outside the block is never touched.

### Claude's Discretion
- Exact section headers and wording inside the PROJECT.md/ROADMAP.md stubs
- Exact wording of the GSD-oriented CLAUDE.md template sections
- Exact wording of the "what next" nudge message
- Implementation structure for composing --full from --minimal logic

</decisions>

<specifics>
## Specific Ideas

- The `--full` flag is the recommended entry point for brand new projects — help text and README should make this clear
- The labelled output style (`  created  path`, `  skipped  path (already exists)`) was established in Phase 17 and Phase 18 continues that pattern

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 18-full-mode*
*Context gathered: 2026-02-24*
