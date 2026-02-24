---
phase: 11-foundation-skills
plan: "01"
subsystem: skills
tags:
  [
    prompt-engineering,
    anthropic-sdk,
    chain-of-thought,
    few-shot,
    structured-output,
    evaluation,
    golden-set,
  ]

# Dependency graph
requires: []
provides:
  - "prompt-engineering skill at v1.2 depth standard with quick-start, numbered sections, applies-to schema"
  - "anti-patterns catalogue with 5 Before/After TypeScript code blocks"
  - "golden-set eval architecture with 3 .md test cases and runnable eval.ts"
  - "evaluation-workflows.md with golden set architecture, prompt versioning, LLM-as-judge patterns"
affects: [12-agent-architecture, 13-auth-systems, 14-stripe-payments]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "applies-to frontmatter schema for model-specific pattern tagging"
    - "golden-set eval architecture: .md test cases + TypeScript runner + LLM-as-judge"
    - "Before/After anti-pattern documentation format"
    - "prompt versioning via file-per-variant with last-verified-against frontmatter"

key-files:
  created:
    - ".agent/skills/prompt-engineering/references/golden-set/chain-of-thought.md"
    - ".agent/skills/prompt-engineering/references/golden-set/few-shot.md"
    - ".agent/skills/prompt-engineering/references/golden-set/output-format.md"
    - ".agent/skills/prompt-engineering/references/golden-set/eval.ts"
  modified:
    - ".agent/skills/prompt-engineering/SKILL.md"
    - ".agent/skills/prompt-engineering/references/anti-patterns.md"
    - ".agent/skills/prompt-engineering/references/evaluation-workflows.md"

key-decisions:
  - "applies-to schema uses exact model IDs (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001) not family names — prevents ambiguity when new models release"
  - "eval.ts uses LLM-as-judge (claude-haiku-4-5-20251001) against bullet criteria rather than exact string matching — handles natural language output variance"
  - "golden-set .md test cases use human-readable Input Prompt and Expected Output Criteria sections parsed by eval.ts — keeps test cases editable without changing runner"

patterns-established:
  - "applies-to frontmatter: every prompt pattern document declares which model IDs it has been verified against"
  - "golden-set eval: .md test cases + eval.ts runner lives in skill references/ for zero-platform prompt evaluation"
  - "anti-pattern format: Before/After TypeScript code blocks with // BEFORE — anti-pattern and // AFTER — corrected labels"

requirements-completed: [PROMPT-01, PROMPT-02, PROMPT-03, PROMPT-04, PROMPT-05]

# Metrics
duration: 4min
completed: 2026-02-24
---

# Phase 11 Plan 01: Prompt Engineering Skill v1.2 Summary

**Prompt-engineering skill rewritten to v1.2 depth: copy-paste quick-start, applies-to model schema, Before/After anti-patterns, and runnable golden-set eval architecture using LLM-as-judge**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-24T03:42:25Z
- **Completed:** 2026-02-24T03:45:49Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- SKILL.md rewritten with Quick Start block, numbered sections 1-4, and applies-to frontmatter schema — developer can make a structured Claude API call within 2 minutes of reading
- anti-patterns.md upgraded to exactly 5 entries each with Before/After TypeScript code blocks covering prompt injection, instruction drift, hallucination on structured output, constraint overload, and lost-in-the-middle
- Golden-set eval architecture created: 3 .md test cases (chain-of-thought, few-shot, output-format) plus eval.ts runner that calls Claude and judges output with LLM-as-judge — runnable with `npx ts-node eval.ts`
- evaluation-workflows.md rewritten to explain golden set architecture, test case format, running instructions, and prompt versioning by file

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite SKILL.md with quick-start, numbered sections, applies-to schema** - `3d9697c` (feat)
2. **Task 2: Upgrade anti-patterns.md, create golden-set files and eval.ts** - `af4347b` (feat)

**Plan metadata:** _(docs commit follows)_

## Files Created/Modified

- `.agent/skills/prompt-engineering/SKILL.md` — Rewritten with Quick Start, sections 1-4, applies-to schema, CoT/few-shot/output-format patterns with real SDK calls (281 lines, under 500)
- `.agent/skills/prompt-engineering/references/anti-patterns.md` — 5 anti-patterns in Before/After TypeScript format (197 lines)
- `.agent/skills/prompt-engineering/references/evaluation-workflows.md` — Golden set architecture, test case format, running instructions, prompt versioning, scoring rubrics
- `.agent/skills/prompt-engineering/references/golden-set/chain-of-thought.md` — CoT test case with applies-to frontmatter
- `.agent/skills/prompt-engineering/references/golden-set/few-shot.md` — Few-shot test case with applies-to frontmatter
- `.agent/skills/prompt-engineering/references/golden-set/output-format.md` — Structured output test case with applies-to frontmatter
- `.agent/skills/prompt-engineering/references/golden-set/eval.ts` — TypeScript eval runner with LLM-as-judge, exit code 1 on failure (131 lines)

## Decisions Made

- **applies-to schema uses exact model IDs** — `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` rather than family names. Prevents ambiguity when new models release.
- **eval.ts uses LLM-as-judge (claude-haiku-4-5-20251001)** — evaluates output against bullet criteria rather than exact string matching, which handles natural language output variance without brittleness.
- **Test cases use human-readable .md format** — Input Prompt and Expected Output Criteria sections are parsed by eval.ts, keeping test cases editable by developers without changing the runner.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. Eval.ts requires `ANTHROPIC_API_KEY` in environment, which is standard for any Claude API usage.

## Next Phase Readiness

- prompt-engineering skill is complete and shippable at v1.2 standard
- All 5 PROMPT-0x requirements satisfied (PROMPT-01 through PROMPT-05)
- Phase 11 Plan 02 (auth-systems) can proceed independently — no dependency on prompt-engineering
- Phase 12 (agent-architecture) has declared dependency on prompt-engineering skill — that dependency is now satisfied

## Self-Check: PASSED

All 7 files confirmed present on disk. Both task commits confirmed in git log (3d9697c, af4347b).

---

_Phase: 11-foundation-skills_
_Completed: 2026-02-24_
