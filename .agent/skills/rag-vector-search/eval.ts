// .agent/skills/rag-vector-search/eval.ts
// Run: npx tsx .agent/skills/rag-vector-search/eval.ts
//
// Evaluates RAG retrieval quality using a golden set of hardcoded queries.
// No DB seeding required — expects data from the Quick Start to already be inserted.
//
// Metrics:
//   recall@k  — fraction of expected chunks found in top-k results (threshold: recall@5 > 0.8)
//   MRR       — mean reciprocal rank of first relevant result (threshold: MRR > 0.7)
//
// Prerequisites:
//   1. Run the Quick Start: npx tsx embed-and-retrieve.ts
//   2. Copy the UUIDs printed by the insert step into GOLDEN_SET below
//   3. Run: npx tsx .agent/skills/rag-vector-search/eval.ts

import OpenAI from 'openai';
import pgvector from 'pgvector/prisma';
import { PrismaClient } from '@prisma/client';

const openai = new OpenAI();
const db = new PrismaClient();

// ── Golden Set ────────────────────────────────────────────────────────────────
// Replace placeholder UUIDs with actual IDs from your Quick Start insert.
// Each entry: a natural language query + the IDs of chunks that should appear in top-5.

const GOLDEN_SET = [
  {
    query: 'how does approximate nearest neighbor search work?',
    expectedChunkIds: [
      '<UUID of HNSW chunk from Quick Start>',
    ],
  },
  {
    query: 'what is vector similarity search in postgres?',
    expectedChunkIds: [
      '<UUID of pgvector chunk from Quick Start>',
    ],
  },
  {
    query: 'how does hybrid search combine semantic and keyword search?',
    expectedChunkIds: [
      '<UUID of hybrid search chunk from Quick Start>',
    ],
  },
];
// ─────────────────────────────────────────────────────────────────────────────

// ── Metrics ───────────────────────────────────────────────────────────────────

/**
 * recall@k: fraction of expected chunks appearing in top-k results.
 * Formula: hits / expected.length
 * Thresholds: > 0.8 = production-ready; < 0.6 = investigate chunking or embedding
 */
function recallAtK(retrieved: string[], expected: string[], k: number): number {
  const topK = retrieved.slice(0, k);
  const hits = expected.filter((id) => topK.includes(id)).length;
  return hits / expected.length;
}

/**
 * Reciprocal Rank: 1 / rank_of_first_relevant (0 if no relevant result found).
 * MRR is the mean of this across all queries.
 * Threshold: MRR > 0.7 means the first relevant result appears in the top 2 on average.
 */
function reciprocalRank(retrieved: string[], expected: string[]): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (expected.includes(retrieved[i])) return 1 / (i + 1);
  }
  return 0;
}

// ── Retrieval ─────────────────────────────────────────────────────────────────

interface ChunkRow {
  id: string;
  score: number;
}

async function retrieve(query: string, topK = 5): Promise<string[]> {
  const embedResponse = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: query,
  });
  const queryVector = pgvector.toSql(embedResponse.data[0].embedding);

  const results = await db.$queryRaw<ChunkRow[]>`
    SELECT
      id::text,
      1 - (embedding <=> ${queryVector}) AS score
    FROM document_chunks
    WHERE embedding_model_version = 'text-embedding-3-small-v1'
    ORDER BY embedding <=> ${queryVector}
    LIMIT ${topK}
  `;

  return results.map((r) => r.id);
}

// ── Main ──────────────────────────────────────────────────────────────────────

const K = 5;
let totalRecall = 0;
let totalMRR = 0;

console.log(`\nRAG Evaluation — recall@${K} and MRR\n${'─'.repeat(50)}`);

for (const item of GOLDEN_SET) {
  const retrieved = await retrieve(item.query, K);
  const recall = recallAtK(retrieved, item.expectedChunkIds, K);
  const rr = reciprocalRank(retrieved, item.expectedChunkIds);

  totalRecall += recall;
  totalMRR += rr;

  const recallLabel = recall >= 0.8 ? 'PASS' : recall >= 0.6 ? 'WARN' : 'FAIL';
  const mrrLabel = rr > 0.7 ? 'PASS' : 'WARN';

  console.log(`Query:    "${item.query}"`);
  console.log(`recall@${K}: ${recall.toFixed(2)} [${recallLabel}]`);
  console.log(`RR:       ${rr.toFixed(2)} [${mrrLabel}]`);
  console.log('');
}

const avgRecall = totalRecall / GOLDEN_SET.length;
const avgMRR = totalMRR / GOLDEN_SET.length;

console.log('─'.repeat(50));
console.log(`Mean recall@${K}: ${avgRecall.toFixed(2)} (threshold: > 0.8 for production-ready)`);
console.log(`Mean MRR:        ${avgMRR.toFixed(2)} (threshold: > 0.7 = relevant result in top 2 on average)`);
console.log('');

if (avgRecall >= 0.8) {
  console.log('Status: PRODUCTION-READY (recall@5 > 0.8)');
} else if (avgRecall >= 0.6) {
  console.log('Status: BORDERLINE — consider tuning chunking strategy or topK');
} else {
  console.log('Status: NOT READY — recall@5 < 0.6. Investigate chunking or embedding model.');
}

await db.$disconnect();
