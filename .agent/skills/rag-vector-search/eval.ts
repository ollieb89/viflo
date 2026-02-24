// .agent/skills/rag-vector-search/eval.ts
// Run: npx tsx .agent/skills/rag-vector-search/eval.ts
//
// RAG evaluation script. Requires the Quick Start data to be inserted first
// (see SKILL.md Quick Start section — 3 sample documents are embedded there).
//
// Metrics:
//   recall@k  — fraction of expected chunks in top-k results (threshold: >0.8 for production)
//   MRR       — mean reciprocal rank of first relevant result (threshold: >0.7)
//
// No DB seeding required — uses hardcoded chunk IDs from Quick Start inserts.
// To get the chunk IDs: SELECT id, content FROM document_chunks LIMIT 10;

import OpenAI from 'openai';
import pgvector from 'pgvector/prisma';
import { PrismaClient } from '@prisma/client';

// Replace UUID values with actual IDs after running Quick Start inserts:
//   SELECT id, content FROM document_chunks ORDER BY created_at;
const GOLDEN_SET: Array<{ query: string; expectedChunkIds: string[] }> = [
  {
    query: 'how does approximate nearest neighbor search work?',
    expectedChunkIds: ['<replace-with-chunk-id-from-Quick-Start>'],
  },
  {
    query: 'what is pgvector used for in PostgreSQL?',
    expectedChunkIds: ['<replace-with-chunk-id-from-Quick-Start>'],
  },
  {
    query: 'how does hybrid search combine vector and keyword search?',
    expectedChunkIds: ['<replace-with-chunk-id-from-Quick-Start>'],
  },
];

// recall@k: fraction of expected chunks found in top-k retrieved results
function recallAtK(retrieved: string[], expected: string[], k: number): number {
  const topK = retrieved.slice(0, k);
  const hits = expected.filter((id) => topK.includes(id)).length;
  return hits / expected.length;
}

// MRR: reciprocal rank of the first relevant result (1/rank, or 0 if not found)
function reciprocalRank(retrieved: string[], expected: string[]): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (expected.includes(retrieved[i])) return 1 / (i + 1);
  }
  return 0;
}

async function retrieveIds(
  openai: OpenAI,
  db: PrismaClient,
  query: string,
  topK = 5
): Promise<string[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });
  const queryVector = pgvector.toSql(response.data[0].embedding);

  const results = await db.$queryRaw<{ id: string }[]>`
    SELECT id
    FROM document_chunks
    WHERE embedding_model_version = 'text-embedding-3-small-v1'
    ORDER BY embedding <=> ${queryVector}
    LIMIT ${topK}
  `;

  return results.map((r) => r.id);
}

async function main(): Promise<void> {
  const openai = new OpenAI();
  const db = new PrismaClient();

  console.log('RAG Evaluation\n' + '='.repeat(40));

  let totalRecall = 0;
  let totalMRR = 0;

  for (const { query, expectedChunkIds } of GOLDEN_SET) {
    const retrieved = await retrieveIds(openai, db, query);
    const recall = recallAtK(retrieved, expectedChunkIds, 5);
    const mrr = reciprocalRank(retrieved, expectedChunkIds);

    totalRecall += recall;
    totalMRR += mrr;

    console.log(`\nQuery: "${query}"`);
    console.log(`  recall@5: ${recall.toFixed(2)}  MRR: ${mrr.toFixed(2)}`);
    console.log(`  retrieved: ${retrieved.slice(0, 5).join(', ')}`);
  }

  const avgRecall = totalRecall / GOLDEN_SET.length;
  const avgMRR = totalMRR / GOLDEN_SET.length;

  console.log('\n' + '='.repeat(40));
  console.log(`Average recall@5: ${avgRecall.toFixed(2)}  (threshold: >0.80 for production)`);
  console.log(`Average MRR:      ${avgMRR.toFixed(2)}  (threshold: >0.70)`);

  if (avgRecall < 0.6) {
    console.log('\n⚠ recall@5 < 0.60 — investigate chunking strategy or embedding model');
  } else if (avgRecall >= 0.8) {
    console.log('\n✓ recall@5 ≥ 0.80 — production-ready');
  } else {
    console.log('\n~ recall@5 0.60–0.80 — acceptable; consider tuning chunk size or overlap');
  }

  await db.$disconnect();
}

main().catch(console.error);
