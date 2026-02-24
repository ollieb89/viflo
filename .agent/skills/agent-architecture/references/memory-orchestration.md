# Memory & Orchestration Patterns

## Memory Types

| Type | Storage | Scope | Use For |
|---|---|---|---|
| In-context | Message array | Single session | Current task state, recent tool results |
| External key-value | Redis / DB | Cross-session | User preferences, session tokens, counters |
| External vector | pgvector / Pinecone | Cross-session | Long-form knowledge, document retrieval |
| Structured state | DB table | Cross-session | Workflow state, checkpoints, audit trail |

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
