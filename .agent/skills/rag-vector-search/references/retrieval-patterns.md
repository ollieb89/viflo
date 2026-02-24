# Retrieval Patterns

## Hybrid Search (Vector + Keyword)

Combine pgvector similarity with Postgres full-text search for better precision:

```sql
SELECT
  text,
  source_id,
  (1 - (embedding <=> $1::vector)) * 0.7
    + ts_rank(to_tsvector('english', text), plainto_tsquery('english', $2)) * 0.3 AS score
FROM embeddings
WHERE model_version = 'text-embedding-3-small-v1'
  AND to_tsvector('english', text) @@ plainto_tsquery('english', $2)
ORDER BY score DESC
LIMIT 10;
```

Weights: 70% semantic similarity, 30% keyword relevance. Adjust based on your query patterns.

## RAG Prompt Assembly

```typescript
async function buildRagPrompt(userQuery: string): Promise<string> {
  const results = await search(userQuery, 5, 0.75);

  if (results.length === 0) {
    return userQuery; // fall back to direct LLM — no context injected
  }

  const context = results.map((r, i) => `[${i + 1}] ${r.text}`).join('\n\n');

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
const results = await db.$queryRaw<{ text: string; score: number }[]>`
  SELECT text, 1 - (embedding <=> ${queryVector}::vector) AS score
  FROM embeddings ORDER BY score DESC LIMIT 20
`;

console.table(results.map((r) => ({ score: r.score.toFixed(3), preview: r.text.slice(0, 80) })));
// Start at 0.75; lower if too few results, raise if results are irrelevant
```
