# Embedding Pipelines

## Chunking Strategy

```typescript
// Note: chunkSize is in words. For token-precise control, use tiktoken (Python) or approximate: 1 word ≈ 1.3 tokens.
// chunkSize=512 words ≈ 665 tokens. Adjust down to ~390 for 512-token chunks.
function chunkText(text: string, chunkSize = 512, overlap = 128): string[] {
  const words = text.split(/\s+/);
  const chunks: string[] = [];

  for (let i = 0; i < words.length; i += chunkSize - overlap) {
    const chunk = words.slice(i, i + chunkSize).join(" ");
    if (chunk.trim()) chunks.push(chunk);
    if (i + chunkSize >= words.length) break;
  }

  return chunks;
}
```

**Chunking rules:**

- Target 256–512 tokens per chunk (not characters — use a tokeniser like `tiktoken` for precision)
- Use 25–50% overlap to preserve context at boundaries
- Never split mid-sentence if possible — split on paragraph breaks first
- Include metadata (document ID, page number, section heading) alongside each chunk

## Batch Embedding with Retry

```typescript
import OpenAI from "openai";

const openai = new OpenAI();
const BATCH_SIZE = 100;

async function embedBatch(texts: string[]): Promise<number[][]> {
  const response = await openai.embeddings.create({
    model: "text-embedding-3-small",
    input: texts,
  });
  return response.data.map((d) => d.embedding);
}

async function embedAll(texts: string[], retries = 3): Promise<number[][]> {
  const results: number[][] = [];

  for (let i = 0; i < texts.length; i += BATCH_SIZE) {
    const batch = texts.slice(i, i + BATCH_SIZE);
    let attempt = 0;

    while (attempt < retries) {
      try {
        const embeddings = await embedBatch(batch);
        results.push(...embeddings);
        break;
      } catch (err) {
        attempt++;
        if (attempt === retries) throw err;
        await new Promise((r) => setTimeout(r, Math.pow(2, attempt) * 1000));
      }
    }
  }

  return results;
}
```

// For upsert pattern with pgvector.toSql(), see SKILL.md Quick Start.

## pgvector Schema (Prisma + raw SQL extension)

```sql
-- Run once to enable the extension
CREATE EXTENSION IF NOT EXISTS vector;

-- document_chunks table (matches SKILL.md Quick Start)
CREATE TABLE document_chunks (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id             TEXT NOT NULL,
  content               TEXT NOT NULL,
  search_vector         tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
  embedding             vector(1536),  -- match your model's output dimensions
  embedding_model_version TEXT NOT NULL,
  created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON document_chunks (embedding_model_version); -- speeds up model_version filter

-- GIN index for full-text search
CREATE INDEX ON document_chunks USING gin(search_vector);

-- HNSW index for approximate nearest-neighbour search (no training required, better recall)
CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- IVFFlat alternative for >1M rows (requires training): CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```
