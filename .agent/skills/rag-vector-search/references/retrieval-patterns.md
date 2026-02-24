# Retrieval Patterns

## Hybrid Search (Vector + Keyword)

Combine pgvector similarity with Postgres full-text search for better precision:

> **Prefer RRF (below) for production.** The weighted approach (`0.7 × vector + 0.3 × ts_rank`) conflates incompatible score scales. RRF is more principled and requires no normalization.

### Option A: Weighted Score (simple, not recommended for production)

```sql
SELECT
  content,
  source_id,
  (1 - (embedding <=> $1::vector)) * 0.7
    + ts_rank(search_vector, plainto_tsquery('english', $2)) * 0.3 AS score
FROM document_chunks
WHERE embedding_model_version = 'text-embedding-3-small-v1'
-- No keyword filter: allow pure semantic matches to rank via score weighting
ORDER BY score DESC
LIMIT 10;
```

Weights: 70% semantic similarity, 30% keyword relevance. Adjust based on your query patterns.

### Option B: RRF Fusion (recommended)

```sql
-- RRF (Reciprocal Rank Fusion) — rank-based, no score normalization needed
-- Source: Cormack et al. (2009); k=60 generalizes well across datasets
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

## RAG Prompt Assembly

```typescript
async function buildRagPrompt(userQuery: string): Promise<string> {
  const results = await search(userQuery, 5, 0.75);

  if (results.length === 0) {
    return userQuery; // fall back to direct LLM — no context injected
  }

  const context = results.map((r, i) => `[${i + 1}] ${r.content}`).join('\n\n');

  return `Answer the question using only the context below. If the answer is not in the context, say "I don't know."

Context:
${context}

Question: ${userQuery}`;
}
```

## Re-ranking (Two-Stage Retrieval)

For higher precision, use a cross-encoder to re-rank top-k results:

```typescript
// Stage 1: fast ANN retrieval (top 20)
const candidates = await search(query, 20, 0.6);

// Stage 2: cross-encoder re-ranking (top 5)
// Using a lightweight model like cross-encoder/ms-marco-MiniLM-L-6-v2 via HuggingFace
const reranked = await rerankWithCrossEncoder(query, candidates, 5);
```

Re-ranking significantly improves precision for long documents but adds latency. Use only when answer quality matters more than response speed.

## Similarity Threshold Calibration

```typescript
// Log scores during development to find your threshold
const results = await db.$queryRaw<{ content: string; score: number }[]>`
  SELECT content, 1 - (embedding <=> ${queryVector}::vector) AS score
  FROM document_chunks ORDER BY score DESC LIMIT 20
`;

console.table(results.map((r) => ({ score: r.score.toFixed(3), preview: r.content.slice(0, 80) })));
// Start at 0.75; lower if too few results, raise if results are irrelevant
```
