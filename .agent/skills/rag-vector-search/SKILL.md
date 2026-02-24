---
name: rag-vector-search
description: Use when implementing retrieval-augmented generation, semantic search, or embedding-based pipelines. Covers pgvector, Pinecone, and Qdrant with embedding generation, chunking strategies, hybrid search, and production edge cases including embedding model changes, similarity thresholds, and cold-start behaviour.
---

# RAG / Vector Search

> See `references/embedding-pipelines.md` for chunking, embedding, and upsert patterns. See `references/retrieval-patterns.md` for query, hybrid search, and re-ranking.

## Decision Matrix

**Default recommendation:** Start with pgvector if you already have Postgres. Move to a dedicated vector store only when you outgrow it.

| Situation | Choice | Why |
|---|---|---|
| Already using Postgres, < 1M vectors | pgvector | Zero new infrastructure, SQL joins with metadata, free |
| > 1M vectors or need managed scaling | Pinecone | Horizontal scaling, managed infrastructure, fast ANN at scale |
| Self-hosted, need advanced filtering | Qdrant | Rich payload filters, open source, HNSW indexing |
| Multi-tenant, strict data isolation | pgvector (separate schema/table per tenant) | Leverage existing Postgres row-level security |
| Real-time updates (vectors change frequently) | pgvector or Qdrant | Pinecone upserts can lag; prefer stores with immediate consistency |
| Hybrid search (semantic + keyword) | pgvector | Native `tsvector` + vector similarity in one query |

## Implementation Patterns

**Embedding pipeline (OpenAI → pgvector):**

```typescript
import OpenAI from 'openai';
import { db } from '@/lib/db'; // Prisma client with pgvector extension

const openai = new OpenAI();

async function embedAndStore(chunks: { text: string; sourceId: string }[]) {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: chunks.map((c) => c.text),
  });

  await db.$transaction(
    response.data.map((embedding, i) =>
      db.$executeRaw`
        INSERT INTO embeddings (text, source_id, embedding, model_version)
        VALUES (${chunks[i].text}, ${chunks[i].sourceId}, ${JSON.stringify(embedding.embedding)}::vector, ${'text-embedding-3-small-v1'})
      `
    )
  );
}
```

**Similarity search (cosine distance):**

```typescript
async function search(query: string, topK = 5, minScore = 0.75) {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });
  const queryVector = response.data[0].embedding;

  const results = await db.$queryRaw<{ text: string; score: number }[]>`
    SELECT text, 1 - (embedding <=> ${JSON.stringify(queryVector)}::vector) AS score
    FROM embeddings
    WHERE model_version = 'text-embedding-3-small-v1'
    ORDER BY embedding <=> ${JSON.stringify(queryVector)}::vector
    LIMIT ${topK}
  `;

  return results.filter((r) => r.score >= minScore); // drop low-confidence results
}
```

See `references/embedding-pipelines.md` for chunking strategies and `references/retrieval-patterns.md` for hybrid search and re-ranking.

## Failure Modes & Edge Cases

| Scenario | What Happens | How to Handle |
|---|---|---|
| Embedding model version change | Old and new vectors are incompatible; mixed results become garbage | Tag every row with `model_version`; re-embed all rows when changing models |
| Chunk splits mid-sentence | Context is lost at boundary; retrieval returns incomplete answers | Use overlapping chunks (stride = 50% of chunk size); keep chunks 256–512 tokens |
| Top-k returns irrelevant results | LLM answers confidently from bad context | Add similarity score threshold (`score >= 0.75`); return "no results" rather than bad results |
| Cold start (empty index) | Every query returns nothing; RAG adds no value | Seed with representative synthetic examples or disable RAG until N documents indexed |
| Embedding rate limits | Batch embedding jobs fail partway through | Process in batches of 100; retry with exponential backoff; track progress to resume |
| Index grows unbounded | Query latency degrades; storage costs spike | Set TTL or archive policy; re-index periodically rather than accumulating stale vectors |

## Version Context

| Library | Last Verified | Notes |
|---|---|---|
| `pgvector` (Postgres extension) | 0.8.x | `ivfflat` index for approximate search; `hnsw` index for better recall (slower build) |
| `openai` (npm) | 4.x | `text-embedding-3-small` (1536 dims, cheap); `text-embedding-3-large` (3072 dims, higher quality) |
| `@pinecone-database/pinecone` | 3.x | Serverless indexes (default) use different upsert API from pod-based indexes |
| Prisma | 5.x | pgvector requires `prisma-client-py` extension or raw SQL for vector operations |
