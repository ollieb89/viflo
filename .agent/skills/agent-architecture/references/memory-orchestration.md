# Memory & Orchestration Patterns

## Memory Types

| Type | Storage | Scope | Use For |
|---|---|---|---|
| In-context | Message array | Single session | Current task state, recent tool results |
| External key-value | Redis / DB | Cross-session | User preferences, session tokens, counters |
| External vector | pgvector | Cross-session | Long-form episodic memory, semantic recall |
| Structured state | DB table | Cross-session | Workflow state, checkpoints, audit trail |

## Episodic Memory via pgvector

### Option A: In-context memory (simple, not recommended beyond ~20 turns)

Pass all prior messages in the `messages` array. Simple and requires no infrastructure, but context overflow is a real risk beyond ~20 turns. At 20+ turns the context window fills, forcing truncation or summarisation — and cross-session recall is impossible.

Use only for short, contained sessions where no cross-session memory is needed.

### Option B: pgvector episodic store (recommended for sessions > 20 turns or cross-session recall)

Store each agent message as a vector embedding in the `agent_episodes` table. At recall time, embed the query and retrieve the top-k semantically relevant episodes. Agents can recall past interactions across sessions with sub-10ms query times.

For full HNSW index setup, chunking strategies, and eval patterns, see the `rag-vector-search` skill.

#### Schema

```sql
-- Enable pgvector extension (run once per database)
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE agent_episodes (
  id          BIGSERIAL PRIMARY KEY,
  session_id  TEXT NOT NULL,
  role        TEXT NOT NULL,          -- 'user' or 'assistant'
  content     TEXT NOT NULL,
  embedding   VECTOR(1536),
  embedding_model_version TEXT NOT NULL,  -- e.g. 'text-embedding-3-small-v1'
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- B-tree index for session lookups
CREATE INDEX ON agent_episodes (session_id);

-- HNSW index for fast ANN search (no training required, better recall than IVFFlat)
CREATE INDEX ON agent_episodes USING hnsw (embedding vector_cosine_ops);
-- For >1M rows: CREATE INDEX ON agent_episodes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

`embedding_model_version` is mandatory. Without it, embeddings from different model versions are silently compared, producing garbage recall scores — the same pattern as `document_chunks` in the RAG skill.

See the `rag-vector-search` skill for HNSW index tuning (`ef_construction`, `m` parameters) and eval patterns.

#### store_episode / recall_episodes

```python
# Python — store and recall agent episodes
import openai
import pgvector

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_MODEL_VERSION = f"{EMBEDDING_MODEL}-v1"
openai_client = openai.OpenAI()

def store_episode(db, session_id: str, role: str, content: str) -> None:
    """Embed and store a single agent turn."""
    raw_vector = openai_client.embeddings.create(
        model=EMBEDDING_MODEL, input=content
    ).data[0].embedding
    db.execute(
        "INSERT INTO agent_episodes (session_id, role, content, embedding, embedding_model_version) "
        "VALUES (%s, %s, %s, %s, %s)",
        (session_id, role, content, pgvector.encode(raw_vector), EMBEDDING_MODEL_VERSION),
    )

def recall_episodes(db, query: str, top_k: int = 5) -> list[dict]:
    """Retrieve top-k semantically relevant episodes for the query."""
    query_vector = pgvector.encode(
        openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding
    )
    return db.fetchall(
        "SELECT role, content, 1 - (embedding <=> %s) AS score "
        "FROM agent_episodes "
        "WHERE embedding_model_version = %s "
        "ORDER BY embedding <=> %s LIMIT %s",
        (query_vector, EMBEDDING_MODEL_VERSION, query_vector, top_k),
    )
```

Key points:
- `pgvector.encode(vector)` — not `JSON.stringify` or raw list. This produces the correct binary wire format for pgvector.
- `embedding_model_version` filter in recall query — prevents cross-model result contamination.
- `1 - (embedding <=> %s) AS score` — cosine similarity score (0 = unrelated, 1 = identical).

## Checkpointing Long Tasks

```typescript
interface TaskCheckpoint {
  taskId: string;
  step: number;
  state: Record<string, unknown>;
  completedSubtasks: string[];
  updatedAt: Date;
}

async function saveCheckpoint(checkpoint: TaskCheckpoint): Promise<void> {
  await db.taskCheckpoint.upsert({
    where: { taskId: checkpoint.taskId },
    create: checkpoint,
    update: { step: checkpoint.step, state: checkpoint.state, completedSubtasks: checkpoint.completedSubtasks, updatedAt: new Date() },
  });
}

async function resumeFromCheckpoint(taskId: string): Promise<TaskCheckpoint | null> {
  return db.taskCheckpoint.findUnique({ where: { taskId } });
}
```

> **LangGraph note:** If using LangGraph, prefer `PostgresSaver` over a manual checkpoint table — it handles state serialisation and thread scoping automatically. See `references/multi-agent-patterns.md` for the `PostgresSaver` setup.

## Context Window Budget Management

```typescript
const TOKEN_BUDGET = 150_000; // leave headroom below model max
const SUMMARISE_THRESHOLD = 0.8; // summarise when 80% full

function estimateTokens(messages: { content: string }[]): number {
  return messages.reduce((sum, m) => sum + Math.ceil(m.content.length / 4), 0);
}

async function maybeCompressContext(
  messages: Anthropic.MessageParam[],
  currentTokens: number
): Promise<Anthropic.MessageParam[]> {
  if (currentTokens < TOKEN_BUDGET * SUMMARISE_THRESHOLD) return messages;

  // Summarise all but the last 4 messages
  const toSummarise = messages.slice(0, -4);
  const recent = messages.slice(-4);

  const summary = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 1024,
    messages: [
      ...toSummarise,
      { role: 'user', content: 'Summarise the conversation above in 200 words, preserving key decisions and facts.' },
    ],
  });

  const summaryText = summary.content[0].type === 'text' ? summary.content[0].text : '';

  return [
    { role: 'user', content: `[Context summary]: ${summaryText}` },
    { role: 'assistant', content: 'Understood. Continuing from where we left off.' },
    ...recent,
  ];
}
```
