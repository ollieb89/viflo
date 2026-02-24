---
name: agent-architecture
description: Use when designing or implementing AI agent systems. Covers single-agent-with-tools, orchestrator-subagent, and event-driven pipeline patterns with memory types, handoff protocols, and production failure modes including agent loops, context overflow, and parallel resource conflicts.
---

# Agent Architecture

> See `references/multi-agent-patterns.md` for orchestrator and subagent implementation. See `references/memory-orchestration.md` for memory types, context management, and state persistence.

## Decision Matrix

**Default recommendation:** Start with a single agent + tools. Add orchestration only when tasks exceed a single context window or require genuine parallelism.

| Situation | Pattern | Why |
|---|---|---|
| Task fits in one context window | Single agent with tools | Simplest, fastest, least failure surface |
| Task requires parallelism (independent subtasks) | Orchestrator + parallel subagents | Subagents work concurrently; orchestrator merges results |
| Task exceeds context window | Orchestrator + sequential subagents | Summarise and hand off context between agents |
| Long-running workflow with human checkpoints | Event-driven pipeline | Persist state between steps; resume after human input |
| Specialised expertise per subtask | Orchestrator + specialist subagents | Each subagent has focused system prompt; higher quality per domain |
| Cost-sensitive with mixed task complexity | Orchestrator (large model) + subagents (small model) | Reserve expensive models for planning; cheap models for execution |

## Implementation Patterns

**Tool definition (Anthropic Claude):**

```typescript
const tools: Anthropic.Tool[] = [
  {
    name: 'search_documents',
    description: 'Search the document store for relevant content. Use when the user asks about specific topics.',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'The search query' },
        limit: { type: 'number', description: 'Max results to return (default: 5)' },
      },
      required: ['query'],
    },
  },
];
```

**Orchestrator dispatch pattern:**

```typescript
async function dispatchSubagent(task: string, contextSummary: string): Promise<string> {
  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001', // use cheaper model for execution
    max_tokens: 4096,
    system: `You are a specialist agent. Complete only the assigned task. 
Context from orchestrator: ${contextSummary}`,
    messages: [{ role: 'user', content: task }],
  });

  return response.content[0].type === 'text' ? response.content[0].text : '';
}
```

See `references/multi-agent-patterns.md` for full orchestrator loop and `references/memory-orchestration.md` for state management.

## Failure Modes & Edge Cases

| Scenario | What Happens | How to Handle |
|---|---|---|
| Agent loop (tool calls itself repeatedly) | Infinite loop, runaway API costs | Add call depth counter; abort after 10 iterations; log the loop for debugging |
| Context overflow mid-task | Agent loses early context; quality degrades silently | Checkpoint state to external store every N steps; summarise before window fills |
| Handoff information loss | Subagent lacks context from orchestrator | Always include full task context in handoff, not just the delta; include prior decisions |
| Parallel agents conflict on shared resource | Database race condition, corrupted state | Use optimistic locking or a task queue; never allow parallel agents to write same record |
| Subagent hallucinates tool output | Fabricates results instead of calling tool | Validate tool results against schema; never trust agent self-report of tool success |
| Prompt injection via tool result | Malicious content in tool output hijacks agent | Sanitise tool results before injecting into context; treat tool output as untrusted |

## Version Context

| Library | Last Verified | Notes |
|---|---|---|
| `@anthropic-ai/sdk` | 0.37.x | `tool_use` content block for tool calls; `tool_result` for responses |
| `openai` (npm) | 4.x | `function_calling` (legacy) vs `tool_choice` (current) — use `tool_choice` |
| Claude models | claude-sonnet-4-6, claude-haiku-4-5 | Opus for planning/orchestration; Haiku for high-volume execution tasks |
| GPT models | gpt-4o, gpt-4o-mini | gpt-4o-mini for execution; gpt-4o for complex reasoning |
