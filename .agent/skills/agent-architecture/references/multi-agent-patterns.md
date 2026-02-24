# Multi-Agent Patterns

> **Version context:** LangGraph 1.x (stable since October 2025, zero breaking changes). `create_react_agent` in `langgraph.prebuilt` is the recommended entry point. LangChain `AgentExecutor` / `initialize_agent()` are deprecated — do not use.
>
> **TypeScript note:** `@langchain/langgraph` exists for TypeScript but patterns here are Python-only (primary ecosystem). See SKILL.md for TypeScript Anthropic SDK patterns.

## LangGraph Agent Patterns

### Option A: Custom StateGraph (not recommended for most cases)

Use only when the prebuilt `create_react_agent` is insufficient — for example, when you need to inject arbitrary nodes between tool calls or define non-standard edge conditions.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

MAX_TURNS = 10  # REQUIRED: passed as recursion_limit

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def call_model(state: AgentState):
    # ... call LLM, return updated state
    pass

def should_continue(state: AgentState):
    # ... decide whether to call tools or end
    return "tools" if needs_tool_call(state) else END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_conditional_edges("agent", should_continue)
graph.set_entry_point("agent")

app = graph.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "session-1"}, "recursion_limit": MAX_TURNS}
result = app.invoke({"messages": [...]}, config)
```

### Option B: `create_react_agent` from `langgraph.prebuilt` (recommended)

Handles the tool-use loop, state management, and checkpointing for you. Use this unless you have a concrete reason to build a custom graph.

```python
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver        # dev/test only
# from langgraph.checkpoint.postgres import PostgresSaver    # production

MAX_TURNS = 10  # REQUIRED: passed as recursion_limit

model = ChatAnthropic(model="claude-sonnet-4-6")

def fetch_url(url: str) -> str:
    """Fetch web content from a URL (first 2000 chars)."""
    import urllib.request
    with urllib.request.urlopen(url) as r:
        return r.read().decode()[:2000]

# Dev: InMemorySaver — state is lost on server restart
agent = create_react_agent(model, tools=[fetch_url], checkpointer=InMemorySaver())

# Production: PostgresSaver — state persists across restarts
# with PostgresSaver.from_conn_string("postgresql://...") as cp:
#     agent = create_react_agent(model, tools=[fetch_url], checkpointer=cp)

config = {"configurable": {"thread_id": "session-1"}, "recursion_limit": MAX_TURNS}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Fetch https://example.com and summarise it"}]},
    config,
)
print(result["messages"][-1].content)
```

## Checkpointing

### Option A: InMemorySaver (dev/test only, not recommended for production)

```python
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()
```

State is lost on server restart. Suitable only for development and testing.

### Option B: PostgresSaver (recommended for production)

```python
from langgraph.checkpoint.postgres import PostgresSaver

with PostgresSaver.from_conn_string("postgresql://user:pass@host/db") as checkpointer:
    agent = create_react_agent(model, tools=tools, checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "session-1"}, "recursion_limit": MAX_TURNS}
    result = agent.invoke({"messages": [...]}, config)
```

Install: `pip install langgraph-checkpoint-postgres`

`PostgresSaver` persists state across server restarts and supports concurrent sessions. Use `InMemorySaver` only in dev. The `thread_id` in `configurable` scopes each conversation — pass a unique value per user session.

## Human-in-the-Loop (Interrupt)

LangGraph 1.x provides `interrupt()` for mid-graph human approval gates. Call `interrupt()` inside any node to pause execution and surface a value to the caller. Resume by invoking the graph again with a `Command(resume=...)`.

```python
from langgraph.types import interrupt, Command
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver

MAX_TURNS = 10  # REQUIRED: passed as recursion_limit

def human_approval_node(state):
    """Pause execution and request human approval before running a destructive tool."""
    pending_action = state["messages"][-1].content
    # interrupt() suspends the graph and returns the value to the caller
    approved = interrupt({"action": pending_action, "prompt": "Approve? (yes/no)"})
    if approved != "yes":
        raise ValueError("Action rejected by human reviewer")
    return state

# Use PostgresSaver so interrupt state persists across HTTP requests
with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
    # For custom graphs with interrupt nodes:
    # graph.add_node("human_approval", human_approval_node)
    # app = graph.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])

    config = {"configurable": {"thread_id": "session-1"}, "recursion_limit": MAX_TURNS}
    # First invocation — runs until interrupt()
    result = app.invoke({"messages": [...]}, config)

    # Resume after human provides input
    result = app.invoke(Command(resume="yes"), config)
```

`interrupt_before` pauses before named nodes; `interrupt_after` pauses after. Use `interrupt()` inside a node body for dynamic, condition-dependent pauses.

## Full Orchestrator Loop (Anthropic SDK — TypeScript)

For TypeScript projects using the Anthropic SDK directly (without LangGraph), the manual tool-use loop below is the standard pattern. Note `recursion_limit` equivalent is `maxDepth`.

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
    maxDepth: 10,  // REQUIRED: equivalent to recursion_limit
  };

  while (true) {
    if (state.depth >= state.maxDepth) {
      throw new Error(`Agent loop exceeded max depth of ${state.maxDepth}`);
    }

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 8192,
      tools,
      messages: state.messages,
    });

    state.depth++;

    if (response.stop_reason === 'end_turn') {
      const textBlock = response.content.find((b) => b.type === 'text');
      return textBlock?.text ?? '';
    }

    if (response.stop_reason === 'max_tokens') {
      // Output was truncated — push partial content and ask model to continue
      state.messages.push({ role: 'assistant', content: response.content });
      state.messages.push({ role: 'user', content: 'Continue.' });
      continue;
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

## When to Use Each Pattern

| Situation | Pattern |
|---|---|
| Task fits in one context window | Single agent + tools |
| Requires parallelism | Orchestrator + parallel subagents |
| Exceeds context window | Orchestrator + sequential subagents |
| Long-running with human checkpoints | LangGraph with `PostgresSaver` + `interrupt()` |
| Custom graph logic required | `StateGraph` (Option A) |
| Standard tool-use agent | `create_react_agent` (Option B) |
