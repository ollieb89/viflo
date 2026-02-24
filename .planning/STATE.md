# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.4 milestone started)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** v1.4 Project Tooling — Phase 16 (CLI Foundation) in progress; Plan 01 complete

## Current Position

Phase: 16 (CLI Foundation) — In Progress
Plan: 01 complete (of 4)
Status: INIT-05 satisfied — bin/lib/paths.cjs and bin/lib/writers.cjs created with idempotent write semantics
Last activity: 2026-02-24 — Phase 16 Plan 01 complete (paths.cjs + writers.cjs foundation layer)

Progress: [███░░░░░░░] 30% — v1.4 in progress (1.25/5 phases)

## Performance Metrics

**Velocity:**
- Total plans completed (v1.2): 3
- Average duration: 2.7 min
- Total execution time: 8 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 11-foundation-skills | 3 | 8 min | 2.7 min |

**Recent Trend:**
- Last 3 plans: ~2.7 min each
- Trend: Stable

*Updated after each plan completion*
| Phase 12-rag-vector-search P01 | 4 | 2 tasks | 2 files |
| Phase 12-rag-vector-search P02 | 3 | 2 tasks | 3 files |
| Phase 13-agent-architecture P01 | 4 | 1 tasks | 1 files |
| Phase 13-agent-architecture P02 | 2 | 2 tasks | 2 files |
| Phase 14-stripe-payments P01 | 2 | 1 tasks | 1 files |
| Phase 14-stripe-payments P02 | 3 | 2 tasks | 2 files |
| Phase 15-integration-review P01 | 1 | 1 tasks | 1 files |
| Phase 15-integration-review P02 | 3 | 1 tasks | 3 files |
| Phase 15-integration-review P01 | 1 | 1 tasks | 1 files |
| Phase 15-integration-review P03 | 2 | 1 tasks | 1 files |
| Phase 16-cli-foundation P01 | 2 | 2 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v1.4 roadmap]: Phase 15 (Integration Review) before CLI phases — INDEX.md and cross-refs written only after all skill content is final
- [v1.4 roadmap]: Phase 16 (CLI Foundation) before orchestration — path utilities and write primitives must be tested in isolation before any user-facing flow is wired; the two most dangerous pitfalls (tilde expansion, __dirname confusion) live in this layer
- [v1.4 roadmap]: INIT-05 (idempotency) assigned to Phase 16 — idempotency is a property of the writers layer, not the orchestrator; sentinel merge and JSON merge deduplication belong here
- [v1.4 roadmap]: Phase 17 (--minimal) before Phase 18 (--full) — --full is a superset; confirming the subset is stable and idempotency-tested before adding scaffolding complexity
- [v1.4 roadmap]: bin/viflo.cjs at repo root (not packages/cli/) — matches gsd-tools.cjs precedent; packages/cli/ TypeScript workspace deferred as premature for v1.4
- [v1.4 roadmap]: Sentinel format <!-- viflo:start --> / <!-- viflo:end --> is the shipped contract for CLAUDE.md merge; never overwrite content outside markers
- [v1.4 roadmap]: Write to project-scope .claude/settings.json only — user-scope ~/.claude/settings.json deferred due to active Claude Code bug #5140
- [v1.3 roadmap]: RAG before Agent — pgvector patterns established in Phase 12 so Agent episodic memory section (Phase 13) can make concrete cross-references, not forward references
- [v1.3 roadmap]: Stripe last (Phase 14) — isolated from AI stack; no benefit to building before RAG/Agent in single-author scenario
- [Phase 11-02]: Better Auth replaces Auth.js as self-hosted alternative; auth.api.getSession() reserved for server components needing user data
- [Phase 11-01]: output_config: { format: zodOutputFormat(...) } is the correct Anthropic SDK parameter; response.parsed_output is the correct accessor
- [Phase 12-rag-vector-search]: HNSW as default index over IVFFlat — no training step, better recall
- [Phase 12-rag-vector-search]: RRF rank-based fusion over weighted score addition — no score normalization needed
- [Phase 12-rag-vector-search]: pgvector.toSql() mandatory (not JSON.stringify) — canonical wire format
- [Phase 13-agent-architecture]: Manual tool-use loop over tool_runner() shortcut — guardrail placement is explicit and auditable
- [Phase 13-agent-architecture]: Next.js API route proxy pattern for streaming — avoids CORS, keeps API key server-side
- [Phase 14-stripe-payments]: await req.text() as webhook headline; ON CONFLICT atomic idempotency; API version 2026-01-28.clover
- [Phase 15-integration-review]: See Also sections appended to SKILL.md file bottoms using relative markdown links with named seam annotations at three AI/LLM integration seams
- [Phase 15-integration-review]: agent-architecture flagged ✗ at 503 lines per locked plan decision — phase succeeds with 4/5 skills within limit
- [Phase 16-cli-foundation P01]: Sentinel format confirmed as <!-- BEGIN VIFLO --> / <!-- END VIFLO --> (not the stale viflo:start/end mentioned in earlier STATE.md decisions)
- [Phase 16-cli-foundation P01]: resolveViFloRoot() uses __dirname not process.cwd() — deterministic regardless of invocation directory
- [Phase 16-cli-foundation P01]: indexOf+slice used for sentinel block replacement instead of regex — avoids escaping edge cases
- [Phase 16-cli-foundation P01]: existing-first ordering in Set spread preserves user-added array entries at front

### Pending Todos

- Re-verify Claude Code user-scope permissions.allow bug (#5140) status at Phase 17 implementation time — if resolved, document whether project scope is still the safer default

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-24
Stopped at: Completed 16-01-PLAN.md — bin/lib/paths.cjs and bin/lib/writers.cjs created, INIT-05 satisfied
Resume with: /gsd:execute-phase 16 02 (CLI Foundation, Plan 02)
