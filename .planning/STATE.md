# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-24 after v1.3 milestone start)

**Core value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI
**Current focus:** v1.3 — Phase 12 (RAG / Vector Search) — Complete (2 of 2 plans done)

## Current Position

Phase: 12 of 15 (RAG / Vector Search)
Plan: 02 complete (2 of 2 plans)
Status: Phase Complete
Last activity: 2026-02-24 — 12-02 eval.ts + reference file updates (HNSW schema, RRF CTE)

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

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 13 — research flag]: LangGraph 1.1.5 checkpointing and human-in-the-loop patterns may have shifted from 0.x to 1.0 (released October 2025). Validate before writing multi-agent section. Core Anthropic tool-use loop is stable and needs no research.

## Session Continuity

Last session: 2026-02-24
Stopped at: Completed 12-02-PLAN.md — eval.ts finalized, embedding-pipelines.md HNSW schema, retrieval-patterns.md RRF CTE
Resume with: Phase 13 (Agent Memory)
