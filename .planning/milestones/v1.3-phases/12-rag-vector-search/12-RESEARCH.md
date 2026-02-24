# Phase 12: RAG / Vector Search - Research

**Researched:** 2026-02-24
**Domain:** pgvector, OpenAI embeddings, hybrid search (RRF), RAG evaluation
**Confidence:** HIGH

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Quick Start:**

- Assumes Postgres + pgvector installed (`CREATE EXTENSION vector` is the starting point — no Docker compose, no managed DB setup)
- Schema setup (HNSW index creation, `embedding_model_version` column) is IN the Quick Start — production-safe from the first commit, not a retrofit
- Quick Start ends with **console output of retrieved chunks** — developer runs the script and sees results printed, no web server needed
- Similarity threshold filter (`score >= 0.75`) is included in the Quick Start — prevents garbage-in-garbage-out from day one
- 15-minute target is the constraint

**Code Language & Style:**

- **TypeScript primary** using Prisma `$executeRaw` (matches existing skill and viflo's Neon/Prisma stack)
- **Python snippets** for chunking-specific patterns where Python tooling dominates (e.g. LangChain splitters)
- **Complete, copy-pasteable functions** — includes imports, types, error handling. No incomplete snippets
- OpenAI model hardcoded to `text-embedding-3-small` (no configurable param — opinionated default, model choice belongs in decision matrix)

**Chunking Strategies:**

- Coverage: fixed-size vs semantic (two fundamentals only — not recursive character or document-aware)
- Presentation: **decision table with tradeoffs + rule-of-thumb formulas** (no full code for the chunking logic itself — that goes in references/)
- Python snippet for LangChain RecursiveCharacterTextSplitter shown as a practical aside (Python is dominant for chunking tooling)
- **Token budget math included**: concrete numbers showing chunk size × topK must fit in model context (e.g. 512 tokens × 10 chunks = 5,120 tokens of context used)
- Overlap rule: stride = 10–20% of chunk size (e.g. 512-token chunk → 50–100 token overlap)

**Hybrid Search (RRF Fusion):**

- Required per RAG-03 — RRF fusion combining vector similarity and full-text search
- SQL query shown inline in SKILL.md main body (not only in references/) per success criteria requirement

**Evaluation Patterns (RAG-05 + EVAL-01 acceleration):**

- **Full `eval.ts`** as a standalone runnable file at `.agent/skills/rag-vector-search/eval.ts`
- Golden set: hardcoded test queries + expected chunk IDs (3–5 queries, no DB seeding required)
- SKILL.md links to eval.ts and explains how to run it
- Includes benchmark guidance: recall@5 > 0.8 = good for production RAG; below 0.6 signals chunking or embedding issues
- Covers both recall@k and MRR metrics with explanation

**Claude's Discretion:**

- Exact formatting of the decision matrix (rows, columns, table style)
- Specific RRF SQL query implementation details (weights, normalization)
- How existing `references/` files are updated or extended (researcher should investigate current state)
- Gotchas section format — follow auth-systems pattern unless a better fit emerges

### Deferred Ideas (OUT OF SCOPE)

- EVAL-01 is technically listed as a future requirement, but user explicitly chose to include the full eval.ts in this phase — treated as in-scope for Phase 12
- Pinecone escape-hatch documentation (ADV-01) — future phase
- Multimodal RAG patterns (ADV-02) — future phase
- LangChain deep dives — explicitly out of scope (500-line budget)
  </user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID     | Description                                                                                                                 | Research Support                                                                                                                                                     |
| ------ | --------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RAG-01 | User can follow a Quick Start to embed and retrieve documents with pgvector in under 15 minutes                             | Schema + HNSW index + embed + retrieve code patterns fully verified; pgvector-node toSql() confirmed as standard approach                                            |
| RAG-02 | Skill documents chunking strategies (fixed-size vs semantic, overlap rules, token budgets)                                  | Fixed-size and semantic chunking tradeoffs researched; LangChain RecursiveCharacterTextSplitter confirmed as Python standard; token budget math formula documented   |
| RAG-03 | Skill includes HNSW index setup and hybrid search with RRF fusion (vector + full-text)                                      | HNSW index SQL (vector_cosine_ops) verified from pgvector official docs; RRF CTE pattern verified from pgvector official docs and multiple community implementations |
| RAG-04 | Skill documents 3 named Gotchas with warning signs and fixes (chunking pitfalls, missing HNSW index, embedding model drift) | All 3 named pitfalls researched and documented with production evidence; HNSW maintenance gotcha (index fragmentation) is an additional verified production concern  |
| RAG-05 | Skill includes embedding model version column schema and retrieval evaluation patterns (recall@k, MRR)                      | `embedding_model_version` column already in existing references/; recall@k and MRR definitions, formulas, and threshold benchmarks researched and verified           |

</phase_requirements>

---

## Summary

Phase 12 upgrades the existing 92-line RAG skill to auth-systems depth (~437 lines). The existing skill already has the right structural skeleton and correct code patterns — the upgrade is about promotion of reference material into the main body, adding production-safe schema from the Quick Start, documenting chunking strategy tradeoffs with concrete math, implementing proper RRF hybrid search SQL inline, and delivering a runnable `eval.ts` file alongside the skill.

The technical stack is well-understood and stable: OpenAI `text-embedding-3-small` (1536 dimensions), pgvector 0.8.x with HNSW indexing, Prisma `$executeRaw`/`$queryRaw` with `pgvector-node` for TypeScript type safety, and native PostgreSQL `tsvector` for the full-text search leg of hybrid search. All core patterns are verified from Context7 (pgvector official docs) and official OpenAI Node.js library docs.

The key architectural decisions are locked: production-safe schema (HNSW index + `embedding_model_version` column) lives in the Quick Start so developers cannot regress to a schema-free prototype, the similarity threshold filter (`score >= 0.75`) is mandatory from day one, and evaluation (recall@5 > 0.8) gives developers an objective signal within minutes of setting up their pipeline.

**Primary recommendation:** Write the SKILL.md as a series of numbered sections following the auth-systems structure: Quick Start (schema + embed + retrieve in one pass) → 1. Schema → 2. Chunking → 3. Hybrid Search → 4. Evaluation → Gotchas. Promote the RRF SQL CTE pattern and the production schema from references/ into the main body. Extend (do not replace) references/ files.

---

## Standard Stack

### Core

| Library                           | Version | Purpose                                                                        | Why Standard                                                                                                             |
| --------------------------------- | ------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `pgvector` (Postgres extension)   | 0.8.x   | Vector storage, ANN indexing (HNSW/IVFFlat), cosine/L2/inner-product operators | Native Postgres — zero extra infrastructure; SQL joins with metadata; tsvector hybrid search in same query               |
| `openai` (npm)                    | 4.x     | `text-embedding-3-small` embeddings (1536 dims)                                | Project already uses OpenAI; `text-embedding-3-small` is cost-optimal at 1536 dims; batch API supports up to 2048 inputs |
| `pgvector` (npm, `pgvector-node`) | latest  | `toSql()` / `fromSql()` helpers for Prisma `$executeRaw`                       | Handles PostgreSQL vector literal format; prevents serialization bugs; TypeScript-friendly                               |
| Prisma                            | 5.x     | ORM; raw SQL via `$executeRaw` / `$queryRaw` for vector operations             | Prisma does not natively support `vector` type — raw SQL is required; `pgvector-node` bridges the gap                    |

### Supporting

| Library                             | Version | Purpose                                                                          | When to Use                                                                                                 |
| ----------------------------------- | ------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `langchain-text-splitters` (Python) | latest  | `RecursiveCharacterTextSplitter` — the de-facto standard Python chunking utility | Use in Python ingestion pipelines; referenced as a practical aside in SKILL.md chunking section             |
| `tiktoken` (Python/npm)             | latest  | Token-accurate chunk size measurement                                            | When exact token counts matter (vs. character-based approximations); mention in SKILL.md as "for precision" |

### Alternatives Considered

| Instead of                      | Could Use                                                      | Tradeoff                                                                                                                                                                                                                          |
| ------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| pgvector HNSW                   | IVFFlat                                                        | IVFFlat requires training (`lists` parameter, typically `rows/1000`); HNSW has no training step, better recall, preferred for new schemas. IVFFlat only wins on build time for very large datasets (>1M rows).                    |
| `pgvector-node` toSql()         | `JSON.stringify(array)::vector`                                | JSON.stringify approach works but produces non-standard format; `pgvector-node` uses the native bracket format `[1,2,3]` which is the pgvector canonical wire format                                                              |
| RRF fusion (CTE approach)       | Weighted score addition (`0.7 * vector_score + 0.3 * ts_rank`) | Weighted addition requires normalizing incompatible score scales; RRF works on ranks (not scores) so no normalization needed. Existing retrieval-patterns.md uses weighted addition — this should be upgraded to RRF in Phase 12. |
| OpenAI `text-embedding-3-small` | `text-embedding-3-large`                                       | 3-large produces 3072 dims (higher quality) but costs ~6x more; 3-small is correct default for production RAG at scale                                                                                                            |

**Installation:**

```bash
npm install openai pgvector
```

```python
# Python ingestion pipeline (chunking)
pip install langchain-text-splitters tiktoken
```

---

## Architecture Patterns

### Recommended Project Structure

```
.agent/skills/rag-vector-search/
├── SKILL.md                    # Main skill — ~437 lines (upgraded from 92)
├── eval.ts                     # Runnable evaluation script (new)
└── references/
    ├── embedding-pipelines.md  # Chunking code, batch embed with retry (extend, not replace)
    └── retrieval-patterns.md   # Hybrid search, re-ranking, threshold calibration (extend)
```

### Pattern 1: Production-Safe Quick Start Schema

**What:** The Quick Start creates the full production schema in one pass — extension, table with `embedding_model_version`, HNSW index, GIN index for full-text. No retrofitting required.

**When to use:** This is the ONLY schema introduced in Phase 12. The developer runs this once and is production-safe from commit 1.

**Example:**

```sql
-- Source: https://github.com/pgvector/pgvector/blob/master/README.md + pgvector Context7 docs
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id             TEXT NOT NULL,
  content               TEXT NOT NULL,
  embedding             vector(1536),           -- text-embedding-3-small dimensions
  embedding_model_version TEXT NOT NULL,        -- REQUIRED: enables re-embed on model drift
  search_vector         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index: no training step, better recall than IVFFlat, preferred for new schemas
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- GIN index for the full-text search leg of hybrid search
CREATE INDEX ON document_chunks USING gin(search_vector);

-- Model version filter index (speeds up WHERE embedding_model_version = '...' scans)
CREATE INDEX ON document_chunks (embedding_model_version);
```

### Pattern 2: Embed-and-Store with pgvector-node

**What:** TypeScript embed + upsert using `pgvector.toSql()` for correct vector serialization.

**When to use:** All embedding ingestion. The `pgvector-node` library is required — `JSON.stringify` produces a different format that is technically valid but non-idiomatic.

**Example:**

```typescript
// Source: https://github.com/pgvector/pgvector-node (Prisma section)
import OpenAI from "openai";
import pgvector from "pgvector/prisma";
import { db } from "@/lib/db"; // Prisma client

const openai = new OpenAI();

async function embedAndStore(
  chunks: { content: string; sourceId: string }[],
): Promise<void> {
  const response = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: chunks.map((c) => c.content),
  });

  await db.$transaction(
    response.data.map(
      (item, i) =>
        db.$executeRaw`
        INSERT INTO document_chunks (source_id, content, embedding, embedding_model_version)
        VALUES (
          ${chunks[i].sourceId},
          ${chunks[i].content},
          ${pgvector.toSql(item.embedding)},
          ${"text-embedding-3-small-v1"}
        )
      `,
    ),
  );
}
```

### Pattern 3: Similarity Search with Threshold Filter

**What:** Query embedding → cosine similarity search → filter by `score >= 0.75` to prevent garbage context from reaching the LLM.

**When to use:** Every retrieval call. The threshold is mandatory (per CONTEXT.md locked decision).

**Example:**

```typescript
// Source: verified against pgvector Context7 docs (cosine distance operator <=>)
import pgvector from "pgvector/prisma";

interface Chunk {
  id: string;
  content: string;
  score: number;
}

async function retrieve(
  query: string,
  topK = 5,
  minScore = 0.75,
): Promise<Chunk[]> {
  const response = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: query,
  });
  const queryVector = pgvector.toSql(response.data[0].embedding);

  const results = await db.$queryRaw<Chunk[]>`
    SELECT
      id,
      content,
      1 - (embedding <=> ${queryVector}) AS score
    FROM document_chunks
    WHERE embedding_model_version = 'text-embedding-3-small-v1'
    ORDER BY embedding <=> ${queryVector}
    LIMIT ${topK}
  `;

  const filtered = results.filter((r) => r.score >= minScore);
  filtered.forEach((r, i) =>
    console.log(
      `[${i + 1}] score=${r.score.toFixed(3)}: ${r.content.slice(0, 120)}`,
    ),
  );
  return filtered;
}
```

### Pattern 4: Hybrid Search with RRF Fusion

**What:** CTE-based RRF — vector search and full-text search each return 20 candidates, merged by `1/(60 + rank)` formula. k=60 comes from Cormack et al. (2009) and generalizes well across datasets.

**When to use:** Main body of SKILL.md (not only in references/). This is the production retrieval pattern.

**Example:**

```sql
-- Source: https://github.com/pgvector/pgvector (pgvector Context7 official docs)
-- and verified by DEV.to hybrid search implementation
WITH vector_search AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) AS rank
  FROM document_chunks
  WHERE embedding_model_version = 'text-embedding-3-small-v1'
  LIMIT 20
),
text_search AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(search_vector, plainto_tsquery('english', $2)) DESC) AS rank
  FROM document_chunks
  WHERE search_vector @@ plainto_tsquery('english', $2)
  LIMIT 20
)
SELECT
  COALESCE(v.id, t.id) AS id,
  1.0 / (60 + COALESCE(v.rank, 1000)) + 1.0 / (60 + COALESCE(t.rank, 1000)) AS rrf_score
FROM vector_search v
FULL OUTER JOIN text_search t ON v.id = t.id
ORDER BY rrf_score DESC
LIMIT 10;
```

Note: Existing `references/retrieval-patterns.md` uses weighted score addition (0.7 × vector + 0.3 × ts_rank). This approach conflates incompatible score scales. Phase 12 should upgrade to the RRF CTE pattern in the main body and update references/ accordingly.

### Pattern 5: Chunking — Fixed-Size vs Semantic Decision

**What:** Decision table with concrete formulas. Code lives in references/ per locked decision.

**Fixed-size (default):**

- Chunk: 512 tokens, overlap: 50–100 tokens (10–20% of chunk size — verified by multiple sources)
- Rule: `stride = chunk_size × 0.85` (advance 85% per window)
- Token budget: `chunk_tokens × topK ≤ model_context_limit − system_prompt_tokens`
- Example with gpt-4o (128K context, ~1K system prompt): 512 × 10 = 5,120 tokens used — well within budget

**Semantic (when to upgrade):**

- Use when documents have strong structural boundaries (markdown headers, legal paragraphs, code blocks)
- LangChain `RecursiveCharacterTextSplitter` is the Python standard — respects `\n\n`, `\n`, ` ` hierarchy
- Adds complexity: requires sentence boundary detection or header parsing
- Recall improvement: ~9% over fixed-size in independent tests (Weaviate blog, 2025)

```python
# Source: LangChain official docs — RecursiveCharacterTextSplitter
# Python — used for ingestion pipelines; semantic boundary awareness
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,       # in characters (not tokens) — use tiktoken for token-precise control
    chunk_overlap=64,     # ~12.5% overlap
    length_function=len,
)
chunks = splitter.split_text(document_text)
```

### Anti-Patterns to Avoid

- **Using IVFFlat for new schemas:** Requires tuning the `lists` parameter and re-training as row count grows. HNSW has no training step and maintains recall better over time.
- **Inserting vectors without `embedding_model_version`:** Makes re-embedding on model change impossible without full-table scans.
- **Weighted score fusion (0.7 × vector + 0.3 × ts_rank):** Normalizing cosine similarity (0–1) against ts_rank (unbounded) produces arbitrary weights. Use RRF ranks instead.
- **No GIN index on tsvector column:** Full-text search falls back to sequential scan; hybrid search latency degrades as table grows.
- **Setting `ef_search` below topK:** If `ef_search = 40` (default) and `LIMIT 100`, the query can only return 40 results. Always `SET hnsw.ef_search` ≥ topK for your query.
- **Building HNSW index before bulk load:** Build is significantly slower when done row-by-row during inserts. Bulk load first, then `CREATE INDEX`.

---

## Don't Hand-Roll

| Problem                               | Don't Build                               | Use Instead                                                                      | Why                                                                                                                                                     |
| ------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Vector serialization for Prisma       | Custom `toSql()` / JSON stringify helper  | `pgvector-node` (`pgvector/prisma`)                                              | Vector literal format `[1,2,3]` vs JSON `[1,2,3]` — both work today but `pgvector-node` is the canonical library and handles edge cases (NaN, infinity) |
| Chunking logic from scratch           | Custom word-splitting with manual overlap | `RecursiveCharacterTextSplitter` (Python) or existing `chunkText` in references/ | Sentence boundary edge cases (abbreviations, quoted strings) are numerous; LangChain handles them                                                       |
| Token counting                        | `text.length / 4` approximation           | `tiktoken`                                                                       | Approximation error compounds over long documents; tiktoken is the exact tokenizer for OpenAI models                                                    |
| Batch embed retry                     | Custom exponential backoff                | Pattern already in `references/embedding-pipelines.md`                           | Extend what exists — batch-of-100 with 3-attempt backoff is already documented and correct                                                              |
| Score normalization for hybrid search | Normalize cosine to ts_rank scale         | RRF (rank-based fusion)                                                          | Normalization requires knowing min/max scores at query time — impractical; RRF works on ordinal rank                                                    |

**Key insight:** The existing `references/` files already cover batch embedding and the chunking function. Phase 12 promotes patterns into the main body and adds the production schema + eval — it does not start from scratch.

---

## Common Pitfalls

### Pitfall 1: Missing HNSW Index (Sequential Scan Regression)

**What goes wrong:** Without an HNSW index, every similarity query does a full sequential scan. On 10K rows this is tolerable; on 100K+ rows query times exceed 1 second and degrade proportionally.

**Why it happens:** Developers prototype with small datasets where the scan is fast, ship without creating the index, and don't notice until load increases.

**How to avoid:** Create HNSW index in the Quick Start schema — before any data is inserted. This is the core principle of "production-safe from the first commit."

**Warning signs:**

- `EXPLAIN ANALYZE` on a similarity query shows `Seq Scan` instead of `Index Scan using hnsw`
- Query latency grows linearly with row count
- pgvector was installed but `\d document_chunks` shows no index on the `embedding` column

**Fix:**

```sql
-- Check existing indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'document_chunks';
-- Create HNSW index if missing (CONCURRENTLY to avoid table lock on live tables)
CREATE INDEX CONCURRENTLY ON document_chunks
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

### Pitfall 2: Embedding Model Drift (Silent Data Corruption)

**What goes wrong:** Developer switches from `text-embedding-3-small` to `text-embedding-3-large` (or any other model change). Old and new vectors live in the same table. Similarity searches return nonsense because vectors from different models are not comparable — their geometry is completely different.

**Why it happens:** The embedding column has no metadata about which model produced each row. Mixed vectors are indistinguishable at query time.

**How to avoid:** The `embedding_model_version` column is mandatory in the Quick Start schema. Every query includes `WHERE embedding_model_version = 'text-embedding-3-small-v1'`. When changing models, re-embed all rows and update `embedding_model_version`.

**Warning signs:**

- Similarity scores cluster around 0.5 (mixed-model vectors produce random similarities)
- Recall@5 drops suddenly without code changes
- Two developers embed the same document and get different `embedding` vectors

**Fix:**

```sql
-- Identify how many rows need re-embedding
SELECT embedding_model_version, COUNT(*) FROM document_chunks GROUP BY 1;
-- Re-embed old rows (batch job) then update model_version
UPDATE document_chunks SET embedding_model_version = 'text-embedding-3-large-v1'
WHERE id IN (/* re-embedded batch IDs */);
```

### Pitfall 3: Chunking Pitfalls (Context Loss and Budget Overrun)

**What goes wrong:** Two common failure modes:

1. **No overlap**: A key sentence at a chunk boundary gets split — neither chunk contains the full context. The LLM retrieves a chunk that ends mid-thought and produces a hallucinated answer.
2. **Chunks too large**: `topK=10` with `chunk_size=1024` tokens = 10,240 tokens of context. With a 4K context model (or large system prompt), this blows the budget and truncates the prompt silently.

**Why it happens:** Default splitters often use character counts, not token counts. 512 characters ≠ 512 tokens.

**How to avoid:**

- Use token-precise chunking: `tiktoken` for OpenAI models, or approximate at 0.75 tokens/character
- Enforce overlap rule: stride = 10–20% of chunk size
- Token budget check before embedding: `chunk_tokens × topK + system_prompt_tokens < model_context_limit`

**Warning signs:**

- LLM answers reference half-sentences or cut-off facts from retrieved context
- Token usage per LLM call spikes unexpectedly
- Retrieved chunks contain complete sentences in isolation but answers lack coherence

### Pitfall 4: HNSW Index Fragmentation (Recall Degrades Over Time)

**What goes wrong:** HNSW is a graph structure. When rows are updated or deleted, the old nodes remain in the graph as "dead tuples." Over time, the graph develops abandoned paths that HNSW traverses during search but that point to deleted rows. Recall silently drops; no error is raised.

**Why it happens:** HNSW indices are not self-healing. Dead tuples accumulate until `VACUUM` (or `REINDEX`) is run.

**How to avoid:** Run `VACUUM ANALYZE document_chunks` regularly (pg auto-vacuum covers this for most workloads). If re-embedding a large fraction of rows, `REINDEX INDEX CONCURRENTLY` afterward.

**Warning signs:**

- Recall@5 drifts downward over weeks without schema or code changes
- `pgstattuple` shows high dead-tuple count on `document_chunks`
- After a bulk-delete + re-embed operation, search quality drops noticeably

---

## Code Examples

Verified patterns from official sources:

### Quick Start Console Script (RAG-01 target)

```typescript
// Source: patterns verified from pgvector Context7 docs + openai-node Context7 docs
// Run: npx tsx embed-and-retrieve.ts
import OpenAI from "openai";
import pgvector from "pgvector/prisma";
import { PrismaClient } from "@prisma/client";

const openai = new OpenAI();
const db = new PrismaClient();

// --- 1. Schema (run once) ---
// CREATE EXTENSION IF NOT EXISTS vector;
// CREATE TABLE document_chunks (
//   id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   source_id TEXT NOT NULL,
//   content TEXT NOT NULL,
//   embedding vector(1536),
//   embedding_model_version TEXT NOT NULL,
//   search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
//   created_at TIMESTAMPTZ DEFAULT NOW()
// );
// CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64);
// CREATE INDEX ON document_chunks USING gin(search_vector);

// --- 2. Embed documents ---
const documents = [
  {
    sourceId: "doc-1",
    content: "pgvector enables vector similarity search inside PostgreSQL.",
  },
  {
    sourceId: "doc-1",
    content:
      "HNSW indexes provide approximate nearest-neighbor search with high recall.",
  },
  {
    sourceId: "doc-2",
    content:
      "Hybrid search combines vector similarity with full-text search for better precision.",
  },
];

const embedResponse = await openai.embeddings.create({
  model: "text-embedding-3-small",
  input: documents.map((d) => d.content),
});

await db.$transaction(
  embedResponse.data.map(
    (item, i) =>
      db.$executeRaw`
      INSERT INTO document_chunks (source_id, content, embedding, embedding_model_version)
      VALUES (${documents[i].sourceId}, ${documents[i].content}, ${pgvector.toSql(item.embedding)}, ${"text-embedding-3-small-v1"})
    `,
  ),
);

// --- 3. Retrieve ---
const query = "how does approximate nearest neighbor search work?";
const queryEmbedding = (
  await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: query,
  })
).data[0].embedding;

interface Chunk {
  content: string;
  score: number;
}

const results = await db.$queryRaw<Chunk[]>`
  SELECT content, 1 - (embedding <=> ${pgvector.toSql(queryEmbedding)}) AS score
  FROM document_chunks
  WHERE embedding_model_version = 'text-embedding-3-small-v1'
  ORDER BY embedding <=> ${pgvector.toSql(queryEmbedding)}
  LIMIT 5
`;

const filtered = results.filter((r) => r.score >= 0.75);
console.log(`Query: "${query}"\n`);
filtered.forEach((r, i) =>
  console.log(`[${i + 1}] score=${r.score.toFixed(3)}: ${r.content}`),
);

await db.$disconnect();
```

### eval.ts Structure (RAG-05 target)

```typescript
// .agent/skills/rag-vector-search/eval.ts
// Run: npx tsx .agent/skills/rag-vector-search/eval.ts
//
// Golden set: 3–5 hardcoded queries with expected chunk IDs.
// No DB seeding required — expects data from the Quick Start to already be inserted.
//
// Metrics:
//   recall@k  — fraction of expected chunks found in top-k results
//   MRR       — mean reciprocal rank of first relevant result

const GOLDEN_SET = [
  {
    query: "how does approximate nearest neighbor search work?",
    expectedChunkIds: ["<UUID from Quick Start insert>"],
  },
  // ... 2–4 more
];

// recall@k: did expected chunks appear in top-k?
function recallAtK(retrieved: string[], expected: string[], k: number): number {
  const topK = retrieved.slice(0, k);
  const hits = expected.filter((id) => topK.includes(id)).length;
  return hits / expected.length;
}

// MRR: inverse rank of first relevant result
function reciprocalRank(retrieved: string[], expected: string[]): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (expected.includes(retrieved[i])) return 1 / (i + 1);
  }
  return 0;
}

// Benchmark thresholds:
// recall@5 > 0.8 — production-ready
// recall@5 < 0.6 — chunking or embedding issue; investigate
// MRR > 0.7 — relevant result in top 2 on average
```

### HNSW Index Creation (Verified)

```sql
-- Source: https://github.com/pgvector/pgvector/blob/master/README.md (Context7)
-- Minimal (default parameters)
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);

-- Production recommended (explicit parameters)
CREATE INDEX ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- On live table (avoids write lock)
CREATE INDEX CONCURRENTLY ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Tune query-time recall (session-scoped; default is 40)
SET hnsw.ef_search = 100;  -- must be >= LIMIT value for full recall
```

---

## State of the Art

| Old Approach                                         | Current Approach                           | When Changed                                        | Impact                                                                                                              |
| ---------------------------------------------------- | ------------------------------------------ | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| IVFFlat as default index                             | HNSW as preferred default                  | pgvector 0.5.0 (May 2023)                           | HNSW has no training step, better recall, simpler setup; IVFFlat still valid for >1M rows where build time matters  |
| Weighted score fusion (0.7 × cosine + 0.3 × ts_rank) | RRF CTE (rank-based fusion)                | Community adoption accelerated 2024–2025            | RRF requires no score normalization; more principled; existing `references/retrieval-patterns.md` should be updated |
| No model version column                              | `embedding_model_version` column mandatory | Production lessons from 2023–2024                   | Model drift is now considered a critical production concern; versioning enables clean re-embed workflows            |
| Similarity search without threshold                  | `score >= 0.75` filter required            | Widespread adoption ~2024                           | Prevents garbage context from reaching LLM; fail-fast is preferable to confident wrong answers                      |
| Chunking by character count                          | Token-precise chunking (tiktoken)          | As context windows and pricing became critical 2024 | Character estimates (÷4 approximation) break token budget math; tiktoken is exact                                   |

**Deprecated/outdated:**

- **IVFFlat as default recommendation:** Still valid for datasets >1M rows for faster index builds, but HNSW is now the default in pgvector docs and community practice for new schemas.
- **Weighted score hybrid search in `references/retrieval-patterns.md`:** The existing file uses `(1 - (embedding <=> $1::vector)) * 0.7 + ts_rank(...) * 0.3`. This should be extended to include the RRF CTE pattern as the recommended production approach. The weighted approach can remain as a simpler alternative.

---

## Existing Skill Analysis

Current state of files to upgrade:

| File                                | Lines | Gap to Close                                                                                        |
| ----------------------------------- | ----- | --------------------------------------------------------------------------------------------------- |
| `SKILL.md`                          | 92    | Missing Quick Start, numbered sections, Gotchas, eval section — all core content in references/     |
| `references/embedding-pipelines.md` | 93    | Good batch embed + chunking patterns; schema uses IVFFlat (outdated); should note HNSW preferred    |
| `references/retrieval-patterns.md`  | 69    | Hybrid search uses weighted addition (not RRF); RRF CTE should be added; re-ranking pattern is good |

**Strategy:**

1. SKILL.md gets a full rewrite from ~92 lines to ~437 lines
2. `references/embedding-pipelines.md` — update schema to HNSW, note IVFFlat as fallback; keep chunking code
3. `references/retrieval-patterns.md` — add RRF CTE as primary pattern, demote weighted addition to "simpler alternative"

---

## Open Questions

1. **pgvector-node import path for Prisma**
   - What we know: GitHub README shows `import pgvector from 'pgvector/prisma'` for the Prisma-specific adapter
   - What's unclear: Whether this subpath export exists in all published versions (npm page was less clear than the GitHub README)
   - Recommendation: Include `import pgvector from 'pgvector/prisma'` and add a note to verify with `node -e "require('pgvector/prisma')"` — or use the generic `pgvector` import if the subpath fails

2. **`ef_search` default and SKILL.md guidance**
   - What we know: Default `ef_search` is 40 (Crunchy Data blog, verified). If `LIMIT` > 40, results are capped at 40 rows.
   - What's unclear: Whether the Quick Start's `LIMIT 5` would be impacted by the default (it would not — 5 < 40). But a Gotcha note is warranted for anyone increasing topK.
   - Recommendation: Add a note in the HNSW section: "If LIMIT exceeds 40, increase with `SET hnsw.ef_search = N` where N ≥ LIMIT."

3. **`generated always as (to_tsvector(...)) stored` — Postgres version requirement**
   - What we know: Generated columns for tsvector are supported from Postgres 12+. Neon (viflo's platform) runs Postgres 16.
   - What's unclear: Whether to document the version requirement or assume it.
   - Recommendation: No special note needed — Neon is Postgres 16; the schema is safe.

---

## Sources

### Primary (HIGH confidence)

- `/pgvector/pgvector` (Context7) — HNSW index SQL, RRF CTE hybrid search pattern, cosine distance operator
- `/openai/openai-node` (Context7) — `embeddings.create()` API, batch embedding, `text-embedding-3-small` 1536 dims
- https://github.com/pgvector/pgvector-node — `pgvector.toSql()` / `pgvector/prisma` import path
- https://neon.com/blog/understanding-vector-search-and-hnsw-index-with-pgvector — HNSW parameters (m, ef_construction, ef_search defaults)
- https://www.crunchydata.com/blog/hnsw-indexes-with-postgres-and-pgvector — ef_search=40 default, index memory requirements, build timing

### Secondary (MEDIUM confidence — verified with official sources or multiple sources)

- https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk — RRF SQL with FULL OUTER JOIN, k=60 citation from Cormack et al.
- https://weaviate.io/blog/chunking-strategies-for-rag — fixed-size vs semantic comparison, 9% recall improvement for semantic
- https://www.firecrawl.dev/blog/best-chunking-strategies-rag-2025 — 512-token chunk, 50–100 token overlap as default
- https://langcopilot.com/posts/2025-09-17-rag-evaluation-101-from-recall-k-to-answer-faithfulness — recall@k vs MRR definitions and use cases

### Tertiary (LOW confidence — WebSearch, single source)

- Medium blog (Engineering @ Layers, Dec 2025) — HNSW index fragmentation / dead tuple issue. Pattern is logical and consistent with HNSW graph theory, but the specific "signal-driven monitoring" implementation detail should not be prescriptive in SKILL.md.

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — verified from Context7 (pgvector official, openai-node official) and official GitHub
- Architecture patterns: HIGH — HNSW SQL and RRF SQL directly from Context7 pgvector docs; Prisma pattern from official pgvector-node repo
- Pitfalls: HIGH for Pitfalls 1–3 (verified from multiple sources); MEDIUM for Pitfall 4 (HNSW fragmentation — logical but fewer authoritative sources)
- Chunking: MEDIUM — community consensus across multiple 2025 articles; LangChain docs are official

**Research date:** 2026-02-24
**Valid until:** 2026-03-24 (pgvector is stable; OpenAI embedding API is stable; 30-day window appropriate)
