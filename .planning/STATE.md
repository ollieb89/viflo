# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 — v1.2 milestone started)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** v1.2 Skills Expansion — Phase 11: Foundation Skills (Prompt Engineering + Auth Systems)

## Current Position

Phase: 11 of 14 (Foundation Skills)
Plan: 03 complete (Phase 11 done)
Status: Phase 11 complete — ready for Phase 12
Last activity: 2026-02-24 — Completed 11-03 (structured output API surface gap closure)

Progress: [██░░░░░░░░] 20% (3 plans complete)

## Performance Metrics

**Velocity:**
- Total plans completed (v1.2): 3
- Average duration: 2.7 min
- Total execution time: 8 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 11-foundation-skills | 3 | 8 min | 2.7 min |

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Phase 10]: Gap-closure pattern — explicit commit-and-verify phase prevents disk/committed drift
- [v1.2 planning]: Auth.js is maintenance-mode (team joined Better Auth Sept 2025) — auth skill leads with Clerk (managed) + Better Auth (self-hosted); Auth.js covered as "migrating from" only
- [v1.2 planning]: Dependency order: prompt-engineering → agent-architecture; auth-systems → stripe-payments
- [11-01]: applies-to schema uses exact model IDs (claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001) not family names — prevents ambiguity when new models release
- [11-01]: eval.ts uses LLM-as-judge (claude-haiku-4-5-20251001) against bullet criteria — handles natural language output variance without brittle string matching
- [11-01]: golden-set .md test cases use human-readable sections parsed by eval.ts — keeps test cases editable without changing runner
- [11-02]: Better Auth replaces Auth.js as self-hosted alternative — authjs-patterns.md replaced with deprecation stub
- [11-02]: Better Auth middleware uses getSessionCookie() fast path (Approach A) as recommended default; auth.api.getSession() reserved for server components needing user data
- [11-02]: CVE-2025-29927 documented as Next.js App Router framework-level pitfall — applies to Clerk and Better Auth users equally; requires Next.js 15.2.3+
- [Phase 11-foundation-skills]: output_config: { format: zodOutputFormat(...) } is the correct Anthropic SDK parameter; response.parsed_output is the correct accessor (not OpenAI-compatible response_format/choices[0])

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 12]: Hybrid search (pgvector + tsvector RRF) — specific SQLAlchemy 2.0 implementation needs verification during authoring; consider /gsd:research-phase if patterns feel thin
- [Phase 12]: Agent token budget enforcement — verify which SDK surfaces max_turns/max_tokens_per_run controls during authoring

## Session Continuity

Last session: 2026-02-24
Stopped at: Completed 11-03-PLAN.md (structured output API surface gap closure — PROMPT-03 and PROMPT-04 fully satisfied)
Resume with: `/gsd:plan-phase 12` for Phase 12 (agent-architecture)
