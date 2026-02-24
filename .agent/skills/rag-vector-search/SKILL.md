---
name: rag-vector-search
description: Use when implementing retrieval-augmented generation or semantic search with PostgreSQL. Covers production-safe pgvector schema (HNSW index, model version column), embedding with OpenAI text-embedding-3-small, chunking strategies with token budget math, hybrid search with RRF fusion, retrieval evaluation (recall@k, MRR), and 4 named production Gotchas.
---

# RAG / Vector Search

> See `references/embedding-pipelines.md` for the full TypeScript `chunkText()` function and batch embedding with retry. See `references/retrieval-patterns.md` for RAG prompt assembly and two-stage re-ranking patterns.

## Quick Start

> Assumes Postgres with pgvector extension available. Starting point: `CREATE EXTENSION IF NOT EXISTS vector;`. Install: `npm install openai pgvector`.

The script below is the complete Quick Start artifact. Run it once to set up the schema, embed sample documents, and verify retrieval. No web server needed — just a running Postgres instance.

```typescript
// embed-and-retrieve.ts
// Run: npx tsx embed-and-retrieve.ts
// Time to working output: < 15 minutes
import OpenAI from "openai";
import pgvector from "pgvector/prisma"; // pgvector-node — use toSql(), not JSON.stringify() — different wire format
import { PrismaClient } from "@prisma/client";

const openai = new OpenAI();
const db = new PrismaClient();

// ── 1. Schema (run once — production-safe from day one) ───────────────────────
//
// CREATE EXTENSION IF NOT EXISTS vector;
//
// CREATE TABLE document_chunks (
//   id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
//   source_id              TEXT NOT NULL,
//   content                TEXT NOT NULL,
//   embedding              vector(1536),                           -- text-embedding-3-small dimensions
//   embedding_model_version TEXT NOT NULL,                        -- REQUIRED: enables re-embed on model drift (see Gotcha 2)
//   search_vector          tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
//   created_at             TIMESTAMPTZ DEFAULT NOW()
// );
//
// -- HNSW index: no training step, better recall than IVFFlat, preferred for new schemas
// CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
//
// -- GIN index for the full-text search leg of hybrid search
// CREATE INDEX ON document_chunks USING gin(search_vector);
//
// -- Model version filter index (speeds up WHERE embedding_model_version = '...' scans)
// CREATE INDEX ON document_chunks (embedding_model_version);
//
// ─────────────────────────────────────────────────────────────────────────────

// ── 2. Embed documents ────────────────────────────────────────────────────────

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
      VALUES (
        ${documents[i].sourceId},
        ${documents[i].content},
        ${pgvector.toSql(item.embedding)},  -- pgvector-node — use toSql(), not JSON.stringify() — different wire format
        ${"text-embedding-3-small-v1"}
      )
    `,
  ),
);

console.log(`Embedded ${documents.length} documents.`);

// ── 3. Retrieve ───────────────────────────────────────────────────────────────

const query = "how does approximate nearest neighbor search work?";
const queryEmbedResponse = await openai.embeddings.create({
  model: "text-embedding-3-small",
  input: query,
});
const queryVector = pgvector.toSql(queryEmbedResponse.data[0].embedding);

interface Chunk {
  id: string;
  content: string;
  score: number;
}

const results = await db.$queryRaw<Chunk[]>`
  SELECT
    id::text,
    content,
    1 - (embedding <=> ${queryVector}) AS score
  FROM document_chunks
  WHERE embedding_model_version = 'text-embedding-3-small-v1'
  ORDER BY embedding <=> ${queryVector}
  LIMIT 5
`;

const filtered = results.filter((r) => r.score >= 0.75); // 0.75 threshold: prevents garbage context from reaching LLM

console.log(`\nQuery: "${query}"\n`);
if (filtered.length === 0) {
  console.log("No results above threshold 0.75. Try adding more documents.");
} else {
  filtered.forEach((r, i) => {
    console.log(
      `[${i + 1}] score=${r.score.toFixed(3)}: ${r.content.slice(0, 120)}`,
    );
  });
}

await db.$disconnect();
```

Run: `npx tsx embed-and-retrieve.ts`

You should see 1–3 chunks printed with scores ≥ 0.75.

> Self-hosting path uses Prisma `$executeRaw`. See `references/embedding-pipelines.md` for batch embedding with retry.

---

## 1. Schema

### Table and Index Design

The Quick Start schema is the complete production schema. No retrofitting required.

**Why `embedding_model_version` is NOT OPTIONAL:**

Without this column, switching models (e.g. `text-embedding-3-small` to `text-embedding-3-large`) silently mixes incompatible vectors in the same table. Cosine similarity between vectors from different models is geometrically meaningless — they occupy completely different spaces. Results degrade with no error raised. See Gotcha 2 for the full failure mode.

**HNSW vs IVFFlat — decision table:**

| Situation                                    | Recommendation | Why                                                    |
| -------------------------------------------- | -------------- | ------------------------------------------------------ |
| New schema (default)                         | HNSW           | No training step; better recall; simpler setup         |
| > 1M rows, build time is a constraint        | IVFFlat        | Faster index build (`lists = rows/1000`); lower recall |
| Build time budget limited (hours acceptable) | HNSW           | Higher `ef_construction` cost is a one-time cost       |

**HNSW parameters:**

- `m = 16` — number of bi-directional links per node. Higher values increase recall at the cost of index size and build time. 16 is the balanced default.
- `ef_construction = 64` — candidate list size during index build. Higher values improve recall at the cost of build time. 64 is the balanced default.
- `ef_search` (query-time): Default `ef_search = 40`. **If `LIMIT` exceeds 40, run `SET hnsw.ef_search = N` where `N ≥ LIMIT` before the query.** Otherwise results are silently capped at 40 rows.

```sql
-- Standard HNSW index (new table — run before inserting data)
CREATE INDEX ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- On a live table (CONCURRENTLY avoids write lock — no downtime)
CREATE INDEX CONCURRENTLY ON document_chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

**Why `GENERATED ALWAYS AS ... STORED` for `search_vector`:**

Manually maintaining a `tsvector` column requires updating it on every `INSERT` and `UPDATE`. Generated columns eliminate this sync risk — PostgreSQL handles recomputation automatically. `STORED` means the value is computed at write time and persisted, so reads are fast.

```sql
-- Recreate (for reference) — already in the Quick Start schema
search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
```

---

## 2. Chunking

### Strategy Decision Table

| Strategy   | When to Use                                                        | Chunk Size | Overlap                | Tooling                                         |
| ---------- | ------------------------------------------------------------------ | ---------- | ---------------------- | ----------------------------------------------- |
| Fixed-size | Default; uniform content (articles, docs, prose)                   | 512 tokens | 50–100 tokens (10–20%) | `tiktoken` (exact) or 0.75 chars/token (approx) |
| Semantic   | Structured content (markdown headers, legal sections, code blocks) | Variable   | ~10–15%                | Python: `RecursiveCharacterTextSplitter`        |

### Token Budget Math

```
chunk_tokens × topK + system_prompt_tokens < model_context_limit

Example: 512 × 10 + 1,000 = 6,120 tokens — well within gpt-4o's 128K context
```

> 512 characters ≠ 512 tokens. Use `tiktoken` for exact counts, or approximate at 0.75 tokens/character.

**Overlap rule:** stride = 10–20% of chunk size (e.g. 512-token chunk → 50–100 token overlap). Smaller overlap risks splitting key sentences; larger overlap increases embedding cost.

### Python Aside — Semantic Chunking

```python
# Python ingestion pipeline — semantic boundary awareness
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,    # characters (use tiktoken for token-precise control)
    chunk_overlap=64,  # ~12.5% overlap
    length_function=len,
)
chunks = splitter.split_text(document_text)
```

> Semantic chunking improves recall ~9% for structured documents (Weaviate, 2025). For plain prose, fixed-size is sufficient.

> See `references/embedding-pipelines.md` for the full TypeScript `chunkText()` function and batch embed with retry.

---

## 3. Hybrid Search (RRF Fusion)

Hybrid search combines vector similarity and full-text search. Use RRF (Reciprocal Rank Fusion) — not weighted score addition. Weighted addition (`0.7 × cosine + 0.3 × ts_rank`) conflates incompatible score scales. RRF works on ranks so no normalization is needed.

```sql
-- Hybrid search: vector similarity + full-text, merged via RRF (k=60 from Cormack et al.)
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

> k=60 is the standard RRF constant from Cormack et al. (2009). It generalizes well across datasets and is the community default.

### TypeScript Wrapper

```typescript
import pgvector from "pgvector/prisma";
import { PrismaClient } from "@prisma/client";
import OpenAI from "openai";

const openai = new OpenAI();
const db = new PrismaClient();

interface HybridResult {
  id: string;
  rrf_score: number;
}

async function hybridSearch(query: string, topK = 10): Promise<HybridResult[]> {
  const embedResponse = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: query,
  });
  const queryVector = pgvector.toSql(embedResponse.data[0].embedding);

  const results = await db.$queryRaw<HybridResult[]>`
    WITH vector_search AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> ${queryVector}::vector) AS rank
      FROM document_chunks
      WHERE embedding_model_version = 'text-embedding-3-small-v1'
      LIMIT 20
    ),
    text_search AS (
      SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(search_vector, plainto_tsquery('english', ${query})) DESC) AS rank
      FROM document_chunks
      WHERE search_vector @@ plainto_tsquery('english', ${query})
      LIMIT 20
    )
    SELECT
      COALESCE(v.id, t.id)::text AS id,
      1.0 / (60 + COALESCE(v.rank, 1000)) + 1.0 / (60 + COALESCE(t.rank, 1000)) AS rrf_score
    FROM vector_search v
    FULL OUTER JOIN text_search t ON v.id = t.id
    ORDER BY rrf_score DESC
    LIMIT ${topK}
  `;

  return results;
}
```

> See `references/retrieval-patterns.md` for RAG prompt assembly and two-stage re-ranking patterns.

---

## 4. Evaluation

Before going to production, verify your pipeline meets minimum recall thresholds.

### Metrics

**recall@k** — fraction of expected chunks appearing in top-k results.

Formula: `hits / expected.length` where `hits` = number of expected chunk IDs found in the top-k result set.

Thresholds:

- `recall@5 > 0.8` = production-ready
- `recall@5 < 0.6` = investigate chunking or embedding model choice

**MRR (Mean Reciprocal Rank)** — inverse rank of the first relevant result across queries.

Formula: `mean(1 / rank_of_first_relevant)` per query.

Threshold: `MRR > 0.7` means the first relevant result appears in the top 2 on average.

### Running the Evaluation

```
Run: npx tsx .agent/skills/rag-vector-search/eval.ts
```

`eval.ts` contains a golden set of 3–5 hardcoded queries with expected chunk IDs. No DB seeding required — uses data from the Quick Start. Before metrics are meaningful, complete the Quick Start first and substitute the placeholder chunk IDs in the file with real IDs from your database. Outputs `recall@5` and `MRR` for each query.

> See [.agent/skills/rag-vector-search/eval.ts](.agent/skills/rag-vector-search/eval.ts) for the full runnable evaluation script.

---

## Gotchas / Pitfalls

### Gotcha 1: Missing HNSW Index (Sequential Scan Regression)

Without an HNSW index, every similarity query does a full sequential scan. Tolerable on 10K rows; degrades to >1s on 100K+ rows.

**Why it happens:** Developers prototype with small datasets, ship without the index, miss it until load increases.

**Warning signs:**

- `EXPLAIN ANALYZE` shows `Seq Scan` instead of `Index Scan using hnsw_...`
- Query latency grows linearly with row count
- `\d document_chunks` shows no index on the `embedding` column

**Fix:**

```sql
-- Check existing indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'document_chunks';

-- Add HNSW index on live table (CONCURRENTLY avoids write lock)
CREATE INDEX CONCURRENTLY ON document_chunks
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
```

### Gotcha 2: Embedding Model Drift (Silent Data Corruption)

Switching embedding models (e.g. `text-embedding-3-small` to `text-embedding-3-large`) mixes incompatible vectors in the same table. Similarity searches return nonsense — vectors from different models occupy completely different geometric spaces.

**Why it happens:** The embedding column alone has no metadata about which model produced it. Mixed vectors are indistinguishable at query time.

**Warning signs:**

- Similarity scores cluster around 0.5 (mixed-model vectors produce ~random similarities)
- recall@5 drops suddenly without code changes
- Two developers embed the same document and get different `embedding` values

**Fix:**

```sql
-- Identify stale rows
SELECT embedding_model_version, COUNT(*) FROM document_chunks GROUP BY 1;

-- After re-embedding batch, update version column
UPDATE document_chunks
SET embedding = $1, embedding_model_version = 'text-embedding-3-large-v1'
WHERE id = $2;
```

### Gotcha 3: Chunking Pitfalls (Context Loss and Budget Overrun)

Two common failure modes:

1. **No overlap**: key sentence at chunk boundary is split — neither chunk contains full context. LLM hallucinates from incomplete context.
2. **Chunks too large**: `topK=10` with `chunk_size=1024` tokens = 10,240 tokens of context. With a 16K or 32K context model, or a large system prompt, this silently truncates the prompt.

**Why it happens:** Default splitters use character counts, not token counts. 512 characters ≈ 384 tokens (not 512).

**Warning signs:**

- LLM answers reference half-sentences or cut-off facts
- Token usage per LLM call spikes unexpectedly
- `tiktoken` reveals chunks are 2–3× larger than expected

**Fix:** Use `tiktoken` (Python/npm) for token-precise chunking. Enforce overlap rule: stride = 10–20% of chunk size. Verify budget: `chunk_tokens × topK + system_prompt_tokens < model_context_limit` before embedding.

### Gotcha 4: HNSW Index Fragmentation (Recall Degrades Over Time)

HNSW is a graph structure. Deleted or updated rows leave "dead nodes" in the graph. Over time HNSW traverses abandoned paths during search, silently degrading recall. No error is raised.

**Why it happens:** HNSW indices are not self-healing. Dead tuples accumulate between VACUUM runs.

**Warning signs:**

- recall@5 drifts downward over weeks without schema or code changes
- `pgstattuple` shows high dead-tuple count on `document_chunks`
- After a bulk-delete + re-embed operation, search quality noticeably drops

**Fix:** Run `VACUUM ANALYZE document_chunks` regularly (pg auto-vacuum covers most workloads). After bulk re-embed:

```sql
REINDEX INDEX CONCURRENTLY idx_document_chunks_embedding;
```

---

## Version Context

| Library                         | Version | Notes                                                                                                        |
| ------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------ |
| `pgvector` (Postgres extension) | 0.8.x   | HNSW is the preferred default index (no training step, better recall); IVFFlat valid for >1M rows            |
| `openai` (npm)                  | 4.x     | `text-embedding-3-small` (1536 dims, cost-optimal default); `text-embedding-3-large` (3072 dims, ~6× cost)   |
| `pgvector` (npm, pgvector-node) | latest  | `pgvector/prisma` import — provides `toSql()` for Prisma `$executeRaw`                                       |
| Prisma                          | 5.x     | pgvector requires raw SQL (`$executeRaw` / `$queryRaw`) — Prisma does not natively support the `vector` type |

## See Also

- [Agent Architecture](../agent-architecture/SKILL.md) — episodic memory pattern (pgvector-backed recall for agents)
- [Prompt Engineering](../prompt-engineering/SKILL.md) — system-prompt design for RAG assembly and retrieval context injection
