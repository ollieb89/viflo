---
phase: 12-rag-vector-search
plan: "01"
subsystem: agent-skills
tags: [rag, pgvector, embeddings, hybrid-search, evaluation]
dependency_graph:
  requires: []
  provides: [rag-vector-search-skill]
  affects: [phase-13-agent-episodic-memory]
tech_stack:
  added: [pgvector-node, tiktoken]
  patterns: [hnsw-index, rrf-fusion, recall-at-k, mrr-evaluation]
key_files:
  created:
    - .agent/skills/rag-vector-search/eval.ts
  modified:
    - .agent/skills/rag-vector-search/SKILL.md
key_decisions:
  - "HNSW as default index over IVFFlat — no training step, better recall, preferred for new schemas"
  - "pgvector.toSql() mandatory (not JSON.stringify) — canonical wire format for pgvector-node"
  - "score >= 0.75 similarity threshold in Quick Start — prevents garbage context from reaching LLM from day one"
  - "RRF rank-based fusion over weighted score addition — no score normalization needed across incompatible scales"
  - "embedding_model_version column mandatory in Quick Start schema — model drift is a production correctness concern"
metrics:
  duration: "4 min"
  completed: "2026-02-24"
  tasks_completed: 2
  files_modified: 2
---

# Phase 12 Plan 01: RAG SKILL.md Rewrite Summary

**One-liner:** Production-safe pgvector RAG skill with HNSW schema, RRF hybrid search SQL inline, 4 named Gotchas, and runnable eval.ts — expanded from 92 to 416 lines at auth-systems depth.

## What Was Built

The existing 92-line RAG skill was a thin shell pointing to `references/` files. This plan promoted production-essential patterns into the main body and added a complete Quick Start that gets a developer to working embed-and-retrieve in under 15 minutes.

**SKILL.md (416 lines) — complete structure:**

- **Quick Start** — Full production-safe schema (HNSW + GIN + model version indexes) as commented SQL inside a TypeScript script. Embed using `pgvector.toSql()`, retrieve with `score >= 0.75` threshold, `console.log` output. Run: `npx tsx embed-and-retrieve.ts`.
- **Section 1: Schema** — HNSW vs IVFFlat decision table, `ef_search` note, `GENERATED ALWAYS AS` explanation for `tsvector`, `CREATE INDEX CONCURRENTLY` variant.
- **Section 2: Chunking** — Fixed-size vs semantic decision table, token budget math formula, Python `RecursiveCharacterTextSplitter` aside, overlap rule.
- **Section 3: Hybrid Search** — Full RRF CTE SQL inline (not only in references/), TypeScript `hybridSearch()` wrapper using `pgvector.toSql()` + `$queryRaw`.
- **Section 4: Evaluation** — `recall@k` and `MRR` metric explanations with production thresholds, `eval.ts` run command.
- **Gotchas (4)** — Missing HNSW Index, Embedding Model Drift, Chunking Pitfalls, HNSW Fragmentation — each with Warning signs and Fix code blocks.
- **Version Context table** — pgvector 0.8.x, openai 4.x, pgvector-node, Prisma 5.x.

**eval.ts** — Standalone runnable evaluation script with 3 golden set queries, `recallAtK()` and `reciprocalRank()` functions, pass/warn/fail output, no DB seeding required.

## Verification Results

| Check | Expected | Result | Status |
|-------|----------|--------|--------|
| Line count | >= 380 | 416 | PASS |
| HNSW index SQL | present | 4 occurrences | PASS |
| pgvector.toSql() | present | 3 occurrences | PASS |
| score >= 0.75 filter | present | 1 occurrence | PASS |
| rrf_score inline | present | 5 occurrences | PASS |
| Gotcha count | 4 | 4 | PASS |
| recall@5 > 0.8 threshold | present | 1 occurrence | PASS |
| chunk_tokens budget math | present | 2 occurrences | PASS |

## Commits

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Rewrite SKILL.md to 416 lines | e208d2d | `.agent/skills/rag-vector-search/SKILL.md` |
| 2 | Create eval.ts evaluation script | 45f53f7 | `.agent/skills/rag-vector-search/eval.ts` |

## Deviations from Plan

### Auto-added Missing Critical Functionality

**[Rule 2 - Missing] Created eval.ts referenced in SKILL.md**
- **Found during:** Post-Task 1 verification
- **Issue:** SKILL.md contains a markdown link to `eval.ts` and a run command (`npx tsx .agent/skills/rag-vector-search/eval.ts`). The plan's `key_links` frontmatter explicitly requires this link to resolve. The file did not exist.
- **Fix:** Created `.agent/skills/rag-vector-search/eval.ts` with golden set, `recallAtK()`, `reciprocalRank()`, pass/warn/fail output, and `$disconnect()` at end. Matches the eval.ts structure specified in RESEARCH.md.
- **Files modified:** `.agent/skills/rag-vector-search/eval.ts` (new)
- **Commit:** 45f53f7

### Tasks Merged

**Task 1 + Task 2 executed as single write** — The plan called for Task 2 to "append" Sections 3-4 and Gotchas after Task 1. Writing and then appending to the same file would produce the same result as writing the complete document in one pass. Both tasks are complete and individually committed (SKILL.md as Task 1, eval.ts creation as Task 2).

## Requirements Addressed

| Requirement | Description | Status |
|-------------|-------------|--------|
| RAG-01 | Quick Start embed-and-retrieve in under 15 minutes with console output | Complete |
| RAG-02 | Chunking strategies with fixed-size vs semantic table and token budget math | Complete |
| RAG-03 | HNSW index setup and hybrid search with RRF fusion SQL inline | Complete |
| RAG-04 | 4 named Gotchas with warning signs and fixes | Complete |
| RAG-05 | embedding_model_version column schema and recall@k / MRR evaluation patterns | Complete |

## Self-Check: PASSED

- FOUND: `.agent/skills/rag-vector-search/SKILL.md` (416 lines)
- FOUND: `.agent/skills/rag-vector-search/eval.ts` (runnable evaluation script)
- FOUND: `.planning/phases/12-rag-vector-search/12-01-SUMMARY.md`
- FOUND: commit e208d2d (SKILL.md rewrite)
- FOUND: commit 45f53f7 (eval.ts creation)
