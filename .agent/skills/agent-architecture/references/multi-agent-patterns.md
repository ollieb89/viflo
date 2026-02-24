# Multi-Agent Patterns

## Full Orchestrator Loop (Claude)

```typescript
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic();

interface AgentState {
  messages: Anthropic.MessageParam[];
  depth: number;
  maxDepth: number;
}

async function runAgentLoop(userMessage: string, tools: Anthropic.Tool[]): Promise<string> {
  const state: AgentState = {
    messages: [{ role: 'user', content: userMessage }],
    depth: 0,
    maxDepth: 10,
  };

  while (true) {
    if (state.depth >= state.maxDepth) {
      throw new Error(`Agent loop exceeded max depth of ${state.maxDepth}`);
    }

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 8096,
      tools,
      messages: state.messages,
    });

    state.depth++;

    if (response.stop_reason === 'end_turn') {
      const textBlock = response.content.find((b) => b.type === 'text');
      return textBlock?.text ?? '';
    }

    if (response.stop_reason === 'tool_use') {
      const toolUses = response.content.filter((b): b is Anthropic.ToolUseBlock => b.type === 'tool_use');
      state.messages.push({ role: 'assistant', content: response.content });

      const toolResults: Anthropic.ToolResultBlockParam[] = await Promise.all(
        toolUses.map(async (toolUse) => ({
          type: 'tool_result' as const,
          tool_use_id: toolUse.id,
          content: await executeTool(toolUse.name, toolUse.input),
        }))
      );

      state.messages.push({ role: 'user', content: toolResults });
    }
  }
}

async function executeTool(name: string, input: unknown): Promise<string> {
  // Dispatch to your tool implementations
  switch (name) {
    case 'search_documents': return await searchDocuments(input as { query: string });
    default: throw new Error(`Unknown tool: ${name}`);
  }
}
```

## Orchestrator → Subagent Handoff

```typescript
interface HandoffContext {
  taskDescription: string;
  priorDecisions: string[];
  constraints: string[];
  outputFormat: string;
}

async function handoffToSubagent(context: HandoffContext): Promise<string> {
  const systemPrompt = `You are a specialist subagent. Complete only the assigned task.

Prior decisions:
${context.priorDecisions.map((d) => `- ${d}`).join('\n')}

Constraints:
${context.constraints.map((c) => `- ${c}`).join('\n')}

Return output as: ${context.outputFormat}`;

  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 4096,
    system: systemPrompt,
    messages: [{ role: 'user', content: context.taskDescription }],
  });

  return response.content[0].type === 'text' ? response.content[0].text : '';
}
```
