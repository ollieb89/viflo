# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.3 milestone start)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** v1.3 — Phase 14 (Stripe Payments) — Complete (2 of 2 plans done)

## Current Position

Phase: 14 of 15 (Stripe Payments)
Plan: 02 complete (2 of 2 plans) — Phase 14 complete
Status: Phase Complete — Resume Phase 15 (Integration Review)
Last activity: 2026-02-24 — 14-02 stripe-payments reference files updated to 2026-01-28.clover and stripe@20.x

Progress: [████████░░] 75% (historical — v1.3 phases at 0%)

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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v1.3 roadmap]: RAG before Agent — pgvector patterns established in Phase 12 so Agent episodic memory section (Phase 13) can make concrete cross-references, not forward references
- [v1.3 roadmap]: Stripe last (Phase 14) — isolated from AI stack; no benefit to building before RAG/Agent in single-author scenario
- [v1.3 roadmap]: Integration Review (Phase 15) last — INDEX.md and cross-refs written only after all skill content is final, preventing description drift
- [Phase 11-02]: Better Auth replaces Auth.js as self-hosted alternative; auth.api.getSession() reserved for server components needing user data
- [Phase 11-01]: output_config: { format: zodOutputFormat(...) } is the correct Anthropic SDK parameter; response.parsed_output is the correct accessor
- [Phase 12-rag-vector-search]: HNSW as default index over IVFFlat — no training step, better recall
- [Phase 12-rag-vector-search]: RRF rank-based fusion over weighted score addition — no score normalization needed
- [Phase 12-rag-vector-search]: pgvector.toSql() mandatory (not JSON.stringify) — canonical wire format
- [Phase 12-rag-vector-search]: HNSW as default pgvector index — no training required, better recall than IVFFlat
- [Phase 12-rag-vector-search]: RRF rank-based fusion as primary hybrid search — no score normalization needed vs weighted addition
- [Phase 12-rag-vector-search]: recall@5 > 0.80 production threshold, MRR > 0.70 secondary threshold for RAG eval.ts
- [Phase 13-agent-architecture]: Manual tool-use loop over tool_runner() shortcut — guardrail placement is explicit and auditable
- [Phase 13-agent-architecture]: Python primary for LangGraph — TypeScript SDK noted but not covered in agent-architecture skill
- [Phase 13-agent-architecture]: Next.js API route proxy pattern for streaming — avoids CORS, keeps API key server-side
- [Phase 13-agent-architecture]: create_react_agent (Option B) recommended over custom StateGraph (Option A) for most LangGraph use cases
- [Phase 13-agent-architecture]: PostgresSaver (Option B) mandatory for production LangGraph — InMemorySaver (Option A) for dev only
- [Phase 13-agent-architecture]: pgvector episodic store (Option B) recommended for >20-turn sessions or cross-session recall — in-context (Option A) for short sessions only
- [Phase 14-stripe-payments]: Stripe Checkout as primary path (SAQ A); await req.text() as webhook headline; ON CONFLICT atomic idempotency; Stripe status strings stored directly; API version 2026-01-28.clover
- [Phase 14-stripe-payments P02]: Replaced Prisma P2002 idempotency with raw SQL INSERT ON CONFLICT; expanded webhook-patterns.md to all four subscription events; subscription-patterns.md rewritten with raw pg.Pool queries

### Pending Todos

None yet.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-02-24
Stopped at: Completed 14-02-PLAN.md — Stripe reference files updated to 2026-01-28.clover and stripe@20.x
Resume with: Phase 15 (Integration Review)
