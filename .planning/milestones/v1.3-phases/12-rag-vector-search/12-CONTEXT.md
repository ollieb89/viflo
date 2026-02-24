# Phase 12: RAG / Vector Search - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Upgrade the existing 92-line RAG skill to auth-systems depth (~437 lines). Output is `.agent/skills/rag-vector-search/SKILL.md` — a technical documentation file developers READ and FOLLOW to embed documents into pgvector, retrieve them with hybrid search, and avoid production pitfalls. Schema is production-safe (HNSW index, model_version column) from the first commit.

Covers requirements: RAG-01, RAG-02, RAG-03, RAG-04, RAG-05.

</domain>

<decisions>
## Implementation Decisions

### Quick Start
- Assumes Postgres + pgvector installed (`CREATE EXTENSION vector` is the starting point — no Docker compose, no managed DB setup)
- Schema setup (HNSW index creation, `embedding_model_version` column) is IN the Quick Start — production-safe from the first commit, not a retrofit
- Quick Start ends with **console output of retrieved chunks** — developer runs the script and sees results printed, no web server needed
- Similarity threshold filter (`score >= 0.75`) is included in the Quick Start — prevents garbage-in-garbage-out from day one
- 15-minute target is the constraint

### Code Language & Style
- **TypeScript primary** using Prisma `$executeRaw` (matches existing skill and viflo's Neon/Prisma stack)
- **Python snippets** for chunking-specific patterns where Python tooling dominates (e.g. LangChain splitters)
- **Complete, copy-pasteable functions** — includes imports, types, error handling. No incomplete snippets
- OpenAI model hardcoded to `text-embedding-3-small` (no configurable param — opinionated default, model choice belongs in decision matrix)

### Chunking Strategies
- Coverage: fixed-size vs semantic (two fundamentals only — not recursive character or document-aware)
- Presentation: **decision table with tradeoffs + rule-of-thumb formulas** (no full code for the chunking logic itself — that goes in references/)
- Python snippet for LangChain RecursiveCharacterTextSplitter shown as a practical aside (Python is dominant for chunking tooling)
- **Token budget math included**: concrete numbers showing chunk size × topK must fit in model context (e.g. 512 tokens × 10 chunks = 5,120 tokens of context used)
- Overlap rule: stride = 10–20% of chunk size (e.g. 512-token chunk → 50–100 token overlap)

### Hybrid Search (RRF Fusion)
- Required per RAG-03 — RRF fusion combining vector similarity and full-text search
- SQL query shown inline in SKILL.md main body (not only in references/) per success criteria requirement

### Evaluation Patterns (RAG-05 + EVAL-01 acceleration)
- **Full `eval.ts`** as a standalone runnable file at `.agent/skills/rag-vector-search/eval.ts`
- Golden set: hardcoded test queries + expected chunk IDs (3–5 queries, no DB seeding required)
- SKILL.md links to eval.ts and explains how to run it
- Includes benchmark guidance: recall@5 > 0.8 = good for production RAG; below 0.6 signals chunking or embedding issues
- Covers both recall@k and MRR metrics with explanation

### Claude's Discretion
- Exact formatting of the decision matrix (rows, columns, table style)
- Specific RRF SQL query implementation details (weights, normalization)
- How existing `references/` files are updated or extended (researcher should investigate current state)
- Gotchas section format — follow auth-systems pattern unless a better fit emerges

</decisions>

<specifics>
## Specific Ideas

- Goal phrasing from roadmap: "production-safe schema in place from the first commit" — this is THE guiding principle for Quick Start scope
- Auth-systems skill (~437 lines) is the depth benchmark — Quick Start + numbered sections + Gotchas
- Existing references/embedding-pipelines.md and references/retrieval-patterns.md should be reviewed; update or extend rather than replace
- eval.ts lives alongside the skill as a runnable file (not documentation) — `.agent/skills/rag-vector-search/eval.ts`

</specifics>

<deferred>
## Deferred Ideas

- EVAL-01 is technically listed as a future requirement, but user explicitly chose to include the full eval.ts in this phase — treated as in-scope for Phase 12
- Pinecone escape-hatch documentation (ADV-01) — future phase
- Multimodal RAG patterns (ADV-02) — future phase
- LangChain deep dives — explicitly out of scope (500-line budget)

</deferred>

---

*Phase: 12-rag-vector-search*
*Context gathered: 2026-02-24*
