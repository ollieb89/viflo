---
phase: 11-foundation-skills
plan: "03"
subsystem: skills
tags: [prompt-engineering, anthropic-sdk, structured-output, zod, gap-closure]

# Dependency graph
requires:
  - phase: 11-01
    provides: prompt-engineering SKILL.md v1.2 with structured output pattern
  - phase: 11-02
    provides: auth-systems SKILL.md v1.2 (sibling plan, dependency ordering)
provides:
  - Correct Anthropic SDK API surface in prompt-engineering structured output code blocks
  - SKILL.md output_config and parsed_output replacing OpenAI-compatible response_format and choices[0]
  - anti-patterns.md anti-pattern #3 AFTER block with correct Anthropic SDK surface
affects: [agent-architecture, any phase consuming prompt-engineering skill]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Anthropic SDK structured output: output_config: { format: zodOutputFormat(...) } parameter + .parsed_output accessor"

key-files:
  created: []
  modified:
    - .agent/skills/prompt-engineering/SKILL.md
    - .agent/skills/prompt-engineering/references/anti-patterns.md

key-decisions:
  - "output_config: { format: zodOutputFormat(...) } is the correct Anthropic SDK parameter (not response_format:)"
  - "response.parsed_output is the correct accessor on the object returned by client.messages.parse (not response.choices[0].message.parsed)"

patterns-established:
  - "Gap closure: four targeted line replacements to eliminate OpenAI-compatible API surface from Anthropic SDK examples"

requirements-completed: [PROMPT-03, PROMPT-04]

# Metrics
duration: 1min
completed: 2026-02-24
---

# Phase 11 Plan 03: Fix Structured Output API Surface Summary

**Corrected four lines across two files — replacing OpenAI-compatible `response_format` and `choices[0].message.parsed` with Anthropic SDK `output_config: { format: ... }` and `.parsed_output`**

## Performance

- **Duration:** 1 min
- **Started:** 2026-02-24T03:58:37Z
- **Completed:** 2026-02-24T03:59:12Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments

- Fixed SKILL.md structured output code block to use correct Anthropic SDK `output_config` parameter and `response.parsed_output` accessor
- Fixed anti-patterns.md anti-pattern #3 AFTER block to use the same correct Anthropic SDK surface
- Both files now contain zero instances of `response_format:` or `choices[0]` — a developer copying either block will not get a runtime error

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix structured output API surface in SKILL.md and anti-patterns.md** - `eb0a98a` (fix)

**Plan metadata:** (see final docs commit)

## Files Created/Modified

- `.agent/skills/prompt-engineering/SKILL.md` - Line 244: `response_format:` → `output_config: { format: ... }`, Line 247: `response.choices[0].message.parsed` → `response.parsed_output`
- `.agent/skills/prompt-engineering/references/anti-patterns.md` - Line 111: same `output_config` fix, Line 114: same `parsed_output` fix

## Decisions Made

None - mechanical gap closure executed exactly as specified. The correct API surface (`output_config` + `parsed_output`) was pre-verified in 11-RESEARCH.md.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- PROMPT-03 and PROMPT-04 are now fully satisfied (previously partial)
- Phase 11 (Foundation Skills) is fully complete — all three plans done
- Ready for Phase 12 (agent-architecture) via `/gsd:plan-phase 12`

## Self-Check: PASSED

All files present and commit eb0a98a verified.

---

_Phase: 11-foundation-skills_
_Completed: 2026-02-24_
