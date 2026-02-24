# Phase 13: Agent Architecture - Research

**Researched:** 2026-02-24
**Domain:** Claude agent tool use, guardrails, SSE streaming, LangGraph, episodic memory, MCP
**Confidence:** HIGH

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Quick Start structure**: Step 1 is a running agent with no tools. By end of Quick Start, developer has a tool-using agent with hard `MAX_TURNS` guardrail wired in. `MAX_TURNS` and `MAX_TOKENS_PER_RUN` are present as named constants in every code example from the first tool example onward — no example ships without them.
- **Quick Start tool example**: Web search / fetch URL — demonstrates real agent value (accessing external data).
- **Code example language**: Python and TypeScript side-by-side throughout (tab-switcher or paired blocks). Both must be complete and equivalent.
- **Gotchas section**: All 3 required pitfalls get full depth — warning signs, why it happens, how to fix it:
  1. Runaway costs — agent loops without termination
  2. Untyped sub-agent handoffs — data contract failures between agents
  3. Bag-of-agents error multiplication — errors compound across agent chains
- Each pitfall includes code: anti-pattern side-by-side with the corrected version.
- Tone: direct and opinionated — "Don't do this" framing.
- **When NOT to use agents**: Visually distinct callout box at top of gotchas section (or its own section). Brief explanation of criteria, not a full decision tree.
- **Streaming stack**: FastAPI `StreamingResponse` → Next.js client via Vercel AI SDK v6. Stack is locked.

### Claude's Discretion

- Exact visual structure of tab-switcher / code pairing (inline, fenced blocks, MDX tabs, etc.)
- Streaming section depth of frontend wiring (FastAPI + Next.js stack is specified but depth is Claude's call)
- Number of additional gotchas beyond the required 3 (more are fine if real)
- Exact formatting of the "When NOT to use agents" callout

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID       | Description                                                                                                    | Research Support                                                                                                                                                                                               |
| -------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AGENT-01 | User can follow a Quick Start to build a tool-using agent with Anthropic SDK in under 15 minutes               | Anthropic SDK tool use loop documented — both Python and TypeScript patterns verified via Context7 and official docs                                                                                           |
| AGENT-02 | Skill documents max_turns and max_tokens guardrails as required (not optional), with cost runaway context      | Pattern exists: manual loop counter + `max_tokens` on every `messages.create` call; named constants `MAX_TURNS`/`MAX_TOKENS_PER_RUN` enforced by convention                                                    |
| AGENT-03 | Skill covers streaming output via SSE (FastAPI StreamingResponse) and Vercel AI SDK v6 (Next.js client)        | FastAPI async generator + `StreamingResponse(media_type="text/event-stream")` → `useChat` hook via `@ai-sdk/react`. Vercel AI SDK v6 (6.0.97) confirmed current.                                               |
| AGENT-04 | Skill covers LangGraph stateful multi-agent graphs with v1.1.5 stability note                                  | LangGraph 1.0 released October 2025 — stable, zero breaking changes. Current PyPI version is in 1.x series. `create_react_agent`, `StateGraph`, `InMemorySaver`/`PostgresSaver` all verified.                  |
| AGENT-05 | Skill covers episodic memory via pgvector (cross-reference to RAG skill) and includes 1-paragraph MCP overview | pgvector episodic memory: pattern maps directly to RAG skill. MCP: open standard introduced November 2024, now Linux Foundation/AAIF-governed, 97M+ monthly downloads, universal AI-tool integration protocol. |

</phase_requirements>

---

## Summary

Phase 13 produces a SKILL.md covering Claude agent patterns — not a production agent system. The deliverable is a developer skill document (~500-line cap per INFRA-02) that teaches tool-using agents, guardrails, streaming, multi-agent graphs, episodic memory, and when agents are the wrong tool.

The core Anthropic tool-use loop is extremely stable: define tools with JSON schema, call `messages.create()`, check `stop_reason === 'tool_use'`, execute the tool, append `tool_result` to messages, loop. This pattern is identical in Python and TypeScript, and both SDKs now offer high-level abstractions (`tool_runner()` / `beta.messages.toolRunner()`) that handle the loop automatically. For the skill doc, the manual loop is the better teaching tool because it makes guardrails explicit.

The biggest research flag from STATE.md was: _"LangGraph 1.1.5 checkpointing and human-in-the-loop patterns may have shifted from 0.x to 1.0 (released October 2025)."_ This is now resolved: LangGraph 1.0 shipped October 2025 with zero breaking changes. Core graph primitives (`StateGraph`, `add_node`, `add_edge`, `compile`) are unchanged. The `prebuilt` module (`create_react_agent`) is confirmed available. For production checkpointing, `PostgresSaver` is the correct recommendation (not `InMemorySaver`). The stability note in the SKILL.md should reference "LangGraph 1.x (stable since October 2025)."

Vercel AI SDK v6 (6.0.97 as of February 2026) is the current version. The streaming pattern uses `useChat` from `@ai-sdk/react` on the Next.js client. For the FastAPI → Next.js SSE bridge: FastAPI produces `text/event-stream` via async generator, and the Next.js route proxies it (or calls FastAPI directly from the API route). The CONTEXT.md stack is correct and current.

**Primary recommendation:** Write SKILL.md using the manual tool-use loop as the Quick Start core (makes guardrails explicit), the `tool_runner()` as the "shortcut" callout, FastAPI SSE → Next.js AI SDK v6 for the streaming section, and LangGraph `create_react_agent` with `PostgresSaver` for the multi-agent section.

---

## Standard Stack

### Core

| Library                         | Version                     | Purpose                                                                | Why Standard                                                                  |
| ------------------------------- | --------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `@anthropic-ai/sdk`             | 0.37.x                      | Anthropic API access, tool use loop, streaming                         | Official SDK; `tool_use` stop reason pattern is the canonical agent primitive |
| `anthropic` (Python)            | 0.40.x                      | Python equivalent                                                      | Official SDK; identical tool-use semantics                                    |
| `fastapi`                       | 0.115+                      | SSE streaming server                                                   | Async-native; `StreamingResponse` + async generator = idiomatic SSE           |
| `@ai-sdk/anthropic`             | latest                      | Vercel AI SDK Anthropic provider                                       | `createAnthropic` is the standard import; required with Vercel AI SDK v6      |
| `ai`                            | 6.x (6.0.97 current)        | Vercel AI SDK core — `streamText`, `useChat`, `convertToModelMessages` | Current stable version; AI SDK 6 is the active major version                  |
| `@ai-sdk/react`                 | 6.x                         | Next.js client hooks — `useChat`                                       | Required for Next.js client streaming                                         |
| `langgraph`                     | 1.x (1.0 released Oct 2025) | Stateful multi-agent graphs                                            | 1.0 is first stable major release; no breaking changes until 2.0              |
| `langgraph-checkpoint-postgres` | 1.x                         | Production checkpointing                                               | `PostgresSaver` for production; `InMemorySaver` for development only          |

### Supporting

| Library               | Version | Purpose                                   | When to Use                                                 |
| --------------------- | ------- | ----------------------------------------- | ----------------------------------------------------------- |
| `zod`                 | 3.x     | Tool input schema validation (TypeScript) | When using `betaZodTool` / `toolRunner` shortcut            |
| `langchain-anthropic` | latest  | Anthropic model provider for LangGraph    | Required when using LangGraph with Claude (`ChatAnthropic`) |
| `uvicorn`             | 0.30+   | ASGI server for FastAPI                   | FastAPI production server                                   |

### Alternatives Considered

| Instead of    | Could Use                               | Tradeoff                                                                                           |
| ------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Manual loop   | `tool_runner()` / `betaZodTool`         | High-level helper eliminates boilerplate but hides the guardrail logic — bad for teaching          |
| LangGraph     | LangChain agents                        | LangGraph is the graph-first approach; LangChain agents are deprecated in favour of LangGraph      |
| FastAPI SSE   | Next.js API route + AI SDK `streamText` | All-Next.js approach is simpler if not using Python backend; FastAPI is locked by CONTEXT.md       |
| Vercel AI SDK | Raw `fetch` + SSE                       | AI SDK v6 `useChat` handles reconnection, message state, and part rendering — worth the dependency |

**Installation:**

```bash
# TypeScript (Next.js client)
npm install ai @ai-sdk/anthropic @ai-sdk/react @anthropic-ai/sdk

# Python (FastAPI server + LangGraph)
pip install anthropic fastapi uvicorn langgraph langchain-anthropic langgraph-checkpoint-postgres
```

---

## Architecture Patterns

### Recommended Project Structure (for SKILL.md examples)

```
agent-quickstart/
├── agent.ts              # Quick Start — TypeScript tool-using agent
├── agent.py              # Quick Start — Python equivalent
├── streaming/
│   ├── server.py         # FastAPI SSE endpoint
│   └── client/
│       ├── app/api/chat/route.ts   # Next.js API route (proxies FastAPI or calls direct)
│       └── app/page.tsx            # useChat client component
└── multi-agent/
    └── graph.py          # LangGraph create_react_agent example
```

### Pattern 1: Manual Tool-Use Loop with Guardrails

**What:** The core agent loop. Call Claude → check `stop_reason` → execute tool → append `tool_result` → repeat. Hard `MAX_TURNS` counter aborts runaway loops.

**When to use:** Always for the teaching example. Makes guardrails explicit and auditable.

**TypeScript:**

```typescript
// Source: Context7 /anthropics/anthropic-sdk-typescript + official docs
import Anthropic from "@anthropic-ai/sdk";

const MAX_TURNS = 10; // REQUIRED: hard limit on agent iterations
const MAX_TOKENS_PER_RUN = 4096; // REQUIRED: caps per-call output tokens

const client = new Anthropic();

const tools: Anthropic.Tool[] = [
  {
    name: "fetch_url",
    description: "Fetch the content of a URL and return the text",
    input_schema: {
      type: "object",
      properties: {
        url: { type: "string", description: "The URL to fetch" },
      },
      required: ["url"],
    },
  },
];

async function runAgent(userMessage: string): Promise<string> {
  const messages: Anthropic.MessageParam[] = [
    { role: "user", content: userMessage },
  ];

  for (let turn = 0; turn < MAX_TURNS; turn++) {
    const response = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: MAX_TOKENS_PER_RUN,
      tools,
      messages,
    });

    if (response.stop_reason === "end_turn") {
      const textBlock = response.content.find((b) => b.type === "text");
      return textBlock?.text ?? "";
    }

    if (response.stop_reason === "tool_use") {
      messages.push({ role: "assistant", content: response.content });

      const toolResults: Anthropic.ToolResultBlockParam[] = await Promise.all(
        response.content
          .filter((b): b is Anthropic.ToolUseBlock => b.type === "tool_use")
          .map(async (toolUse) => ({
            type: "tool_result" as const,
            tool_use_id: toolUse.id,
            content: await executeTool(
              toolUse.name,
              toolUse.input as { url: string },
            ),
          })),
      );

      messages.push({ role: "user", content: toolResults });
    }
  }

  throw new Error(
    `Agent exceeded MAX_TURNS (${MAX_TURNS}). Aborting to prevent runaway costs.`,
  );
}

async function executeTool(
  name: string,
  input: { url: string },
): Promise<string> {
  if (name === "fetch_url") {
    const res = await fetch(input.url);
    const text = await res.text();
    return text.slice(0, 2000); // truncate to avoid context bloat
  }
  throw new Error(`Unknown tool: ${name}`);
}
```

**Python:**

```python
# Source: Context7 /anthropics/anthropic-sdk-python + official docs
import anthropic
import urllib.request

MAX_TURNS = 10            # REQUIRED: hard limit on agent iterations
MAX_TOKENS_PER_RUN = 4096  # REQUIRED: caps per-call output tokens

client = anthropic.Anthropic()

tools = [
    {
        "name": "fetch_url",
        "description": "Fetch the content of a URL and return the text",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch"},
            },
            "required": ["url"],
        },
    }
]

def execute_tool(name: str, input_data: dict) -> str:
    if name == "fetch_url":
        with urllib.request.urlopen(input_data["url"]) as response:
            return response.read().decode("utf-8")[:2000]
    raise ValueError(f"Unknown tool: {name}")

def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    for turn in range(MAX_TURNS):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=MAX_TOKENS_PER_RUN,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text_block = next((b for b in response.content if b.type == "text"), None)
            return text_block.text if text_block else ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(f"Agent exceeded MAX_TURNS ({MAX_TURNS}). Aborting to prevent runaway costs.")
```

### Pattern 2: FastAPI SSE → Next.js via Vercel AI SDK v6

**What:** FastAPI async generator yields SSE chunks from the Anthropic streaming SDK. Next.js `useChat` from `@ai-sdk/react` consumes the stream.

**When to use:** Python backend + Next.js frontend architecture.

**Server (Python FastAPI):**

```python
# Source: Anthropic official streaming docs + FastAPI async generator pattern
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import anthropic
import json

app = FastAPI()
client = anthropic.AsyncAnthropic()

MAX_TOKENS_PER_RUN = 4096  # REQUIRED

async def stream_agent_response(user_message: str):
    """Async generator yielding SSE-formatted text chunks."""
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=MAX_TOKENS_PER_RUN,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            # SSE format: each chunk must end with \n\n
            yield f"data: {json.dumps({'text': text})}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/api/chat")
async def chat(request: dict):
    return StreamingResponse(
        stream_agent_response(request["message"]),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

**Client (Next.js + Vercel AI SDK v6):**

```typescript
// Source: Context7 /vercel/ai — useChat hook pattern (AI SDK v6)
'use client';

import { useChat } from '@ai-sdk/react';
import { TextStreamChatTransport } from 'ai';
import { useState } from 'react';

export default function AgentChat() {
  const [input, setInput] = useState('');

  // useChat points at a Next.js API route that proxies FastAPI
  const { messages, sendMessage } = useChat({
    transport: new TextStreamChatTransport({ api: '/api/chat' }),
  });

  return (
    <div>
      {messages.map((m) => (
        <div key={m.id}>
          <strong>{m.role}:</strong>{' '}
          {m.parts.map((part, i) =>
            part.type === 'text' ? <span key={i}>{part.text}</span> : null
          )}
        </div>
      ))}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage({ text: input });
          setInput('');
        }}
      >
        <input value={input} onChange={(e) => setInput(e.target.value)} />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```

**Next.js API route (proxy to FastAPI):**

```typescript
// app/api/chat/route.ts — Source: AI SDK v6 streamText pattern
import { streamText, convertToModelMessages, UIMessage } from "ai";
import { createAnthropic } from "@ai-sdk/anthropic";

const anthropic = createAnthropic();
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: anthropic("claude-sonnet-4-6"),
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

> Note: The Next.js API route approach (using AI SDK `streamText` with `@ai-sdk/anthropic`) is simpler and avoids the proxy complexity. Use the FastAPI server pattern when the backend is Python-only. Both are valid — FastAPI is the locked choice per CONTEXT.md for the streaming section.

### Pattern 3: LangGraph `create_react_agent` (Multi-Agent)

**What:** LangGraph 1.x prebuilt ReAct agent with `PostgresSaver` for production checkpointing. Stateful, resumable, supports human-in-the-loop via `interrupt()`.

**When to use:** Multi-step workflows that exceed a single context window, require parallel execution, or need resumability after server restart.

**Python:**

```python
# Source: Context7 /langchain-ai/langgraph — LangGraph 1.x (stable since October 2025)
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres import PostgresSaver  # production
# from langgraph.checkpoint.memory import InMemorySaver  # dev/test only

MAX_TURNS = 10  # REQUIRED: LangGraph agents support recursion_limit

model = ChatAnthropic(model="claude-sonnet-4-6")

def search_web(query: str) -> str:
    """Search the web and return results."""
    # Your implementation here
    return f"Results for: {query}"

tools = [search_web]

# Production: PostgresSaver (persists state across server restarts)
# with PostgresSaver.from_conn_string("postgresql://...") as checkpointer:
#     agent = create_react_agent(model, tools, checkpointer=checkpointer)

# Dev/test: InMemorySaver
from langgraph.checkpoint.memory import InMemorySaver
agent = create_react_agent(
    model,
    tools,
    checkpointer=InMemorySaver(),
    # recursion_limit limits the max number of node traversals (guards against loops)
)

config = {
    "configurable": {"thread_id": "session-1"},
    "recursion_limit": MAX_TURNS,  # REQUIRED: hard loop limit
}

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Search for recent news about AI agents"}]},
    config,
)
```

### Anti-Patterns to Avoid

- **No MAX_TURNS guard**: Agent loop runs until API error or budget exhaustion. Even with a generous limit, the constant MUST be defined and named — not hardcoded inline.
- **No `max_tokens` on every call**: Default `max_tokens` varies by client version. Always set it explicitly. `MAX_TOKENS_PER_RUN` as a named constant.
- **Untyped tool outputs**: Returning `any` or `dict` from tool execution. Downstream agents can't validate the result. Use typed interfaces / dataclasses.
- **`InMemorySaver` in production**: State is lost on server restart. Always use `PostgresSaver` (or `SqliteSaver` for single-machine dev) in production.
- **`tool_runner()` in teaching examples**: Hides the loop and makes guardrail placement non-obvious. Teach the manual loop first.

---

## Don't Hand-Roll

| Problem                           | Don't Build                                 | Use Instead                                                                          | Why                                                                                                           |
| --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Automatic tool execution loop     | Custom `while True` dispatcher              | `client.beta.messages.toolRunner()` (TS) / `client.beta.messages.tool_runner()` (Py) | SDK handles tool dispatch, message accumulation, and loop termination — use after teaching the manual pattern |
| ReAct agent graph                 | Custom `StateGraph` with tool router        | `create_react_agent` from `langgraph.prebuilt`                                       | LangGraph 1.x prebuilt handles the ReAct loop, tool calling, and streaming natively                           |
| SSE serialization                 | Manual `f"data: {text}\n\n"` for everything | Anthropic SDK `client.messages.stream()` context manager                             | SDK handles `content_block_delta` event types, partial JSON accumulation for tool inputs, ping events         |
| Checkpoint serialization          | Custom DB schema for agent state            | `PostgresSaver` from `langgraph-checkpoint-postgres`                                 | Handles state graph snapshots, thread IDs, and time-travel debugging                                          |
| Token counting for context budget | Character-count heuristics                  | `response.usage.input_tokens + response.usage.output_tokens`                         | Anthropic API returns exact token counts in every response — no estimation needed                             |

**Key insight:** The Anthropic tool-use protocol has two layers: the raw API (check `stop_reason`, parse `tool_use` blocks, return `tool_result`) and SDK helpers (`tool_runner`). Teach the raw API first so guardrails are explicit, then mention the shortcut.

---

## Common Pitfalls

### Pitfall 1: Runaway Costs (Agent Loop Without Termination)

**What goes wrong:** Agent calls a tool → gets a result → calls another tool → no terminal condition → API calls accumulate unboundedly. At $3–15 per million output tokens, a 100-turn loop can cost hundreds of dollars before anyone notices.

**Why it happens:** Developers test with small prompts that terminate in 1–2 turns. The loop never runs long in dev, so no one adds a guard.

**Warning signs:**

- API cost spikes on dashboards with no corresponding feature launch
- Agent "spinning" — same or similar tool calls repeated across turns
- Response to simple queries takes many seconds / minutes

**Anti-pattern:**

```python
# BAD: no termination guard
while True:
    response = client.messages.create(...)
    if response.stop_reason == "end_turn":
        break
    # What if it never reaches "end_turn"?
```

**Fix:**

```python
# GOOD: hard named constant, throws on breach
MAX_TURNS = 10
for turn in range(MAX_TURNS):
    response = client.messages.create(max_tokens=MAX_TOKENS_PER_RUN, ...)
    if response.stop_reason == "end_turn":
        return extract_text(response)
    # handle tool_use...

raise RuntimeError(f"Exceeded MAX_TURNS ({MAX_TURNS}). Check tool logic for infinite loops.")
```

### Pitfall 2: Untyped Sub-Agent Handoffs

**What goes wrong:** Orchestrator agent passes a result to a sub-agent as a raw string. Sub-agent expects a structured object. Sub-agent either hallucinates the missing fields or fails silently.

**Why it happens:** Multi-agent systems are prototyped with string handoffs because it's easy. When the output format changes (even a field rename), downstream agents break without raising an exception.

**Warning signs:**

- Sub-agent returns answers that reference fields not in the original task
- Different runs of the same pipeline produce structurally different outputs
- Adding a new orchestrator output breaks one sub-agent but not others

**Anti-pattern:**

```typescript
// BAD: untyped string handoff
const result = await orchestratorAgent(task); // returns string
const subResult = await subAgent(result); // what schema does subAgent expect?
```

**Fix:**

```typescript
// GOOD: typed contract at the handoff boundary
interface SearchHandoff {
  query: string;
  maxResults: number;
  requiredFields: string[];
}

function validateHandoff(raw: unknown): SearchHandoff {
  // Use zod or manual validation
  if (typeof (raw as SearchHandoff).query !== "string") {
    throw new Error("Invalid handoff: missing query field");
  }
  return raw as SearchHandoff;
}

const rawHandoff = await orchestratorAgent(task);
const handoff = validateHandoff(JSON.parse(rawHandoff)); // throws on bad schema
const subResult = await subAgent(handoff);
```

### Pitfall 3: Bag-of-Agents Error Multiplication

**What goes wrong:** A pipeline of 5 agents, each with 90% reliability, has a combined reliability of 0.9^5 = 59%. Each agent that runs on a flawed predecessor output amplifies the error — by the final agent, the hallucination is presented as fact.

**Why it happens:** Developers treat agent accuracy as an additive property ("5 agents, each good at their task"). It's multiplicative. Errors compound.

**Warning signs:**

- Final output quality is worse than a single-agent approach on the same task
- Early-stage agent errors appear in final outputs with greater confidence
- Removing an agent from the pipeline improves output quality

**Anti-pattern:**

```python
# BAD: no output validation between agents
result_1 = agent_1(user_input)    # 90% reliable
result_2 = agent_2(result_1)      # 90% × 90% = 81%
result_3 = agent_3(result_2)      # 73%
result_4 = agent_4(result_3)      # 66%
final    = agent_5(result_4)      # 59% — worse than single agent
```

**Fix:**

```python
# GOOD: validate at each stage; abort early if confidence drops
result_1 = agent_1(user_input)
if not validate_stage(result_1, schema=SearchResultSchema):
    raise ValueError("Stage 1 output failed validation — aborting pipeline")

result_2 = agent_2(result_1)
# ... repeat for each stage
```

> **Rule of thumb:** If a single capable model can do the task, use one agent. Add agents only when tasks require genuine parallelism or exceed a single context window.

---

## Code Examples

Verified patterns from official sources:

### Step 1 Quick Start: Agent with No Tools (< 5 min to working output)

```python
# Source: Anthropic official docs — simplest working agent
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.content[0].text)
```

```typescript
// Source: Anthropic official docs
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "What is the capital of France?" }],
});

console.log(
  response.content[0].type === "text" ? response.content[0].text : "",
);
```

### SSE Event Flow (for streaming section reference)

From official Anthropic docs, a streamed response produces events in this order:

1. `message_start` — message object with empty content
2. `content_block_start` — new content block begins
3. `content_block_delta` (`text_delta` or `input_json_delta` for tools)
4. `content_block_stop` — block complete
5. `message_delta` — top-level changes (stop_reason, usage)
6. `message_stop` — stream complete

For tool use: `stop_reason` in `message_delta` will be `"tool_use"`. The `input_json_delta` events carry partial JSON that must be accumulated to reconstruct the tool input.

### Vercel AI SDK v6 — Next.js API Route

```typescript
// Source: Context7 /vercel/ai — AI SDK v6 confirmed current (6.0.97, Feb 2026)
// app/api/chat/route.ts
import { streamText, convertToModelMessages, UIMessage } from "ai";
import { createAnthropic } from "@ai-sdk/anthropic";

const anthropic = createAnthropic(); // reads ANTHROPIC_API_KEY from env
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: anthropic("claude-sonnet-4-6"),
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
```

### LangGraph ReAct Agent

```python
# Source: Context7 /langchain-ai/langgraph — v1.x (stable since October 2025)
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import InMemorySaver

MAX_TURNS = 10  # REQUIRED: recursion_limit enforces this

model = ChatAnthropic(model="claude-sonnet-4-6")

def fetch_url(url: str) -> str:
    """Fetch web content from a URL."""
    import urllib.request
    with urllib.request.urlopen(url) as r:
        return r.read().decode()[:2000]

agent = create_react_agent(
    model,
    tools=[fetch_url],
    checkpointer=InMemorySaver(),
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Fetch https://example.com and summarise it"}]},
    config={"configurable": {"thread_id": "t1"}, "recursion_limit": MAX_TURNS},
)
```

### MCP Overview (1-paragraph for AGENT-05)

MCP (Model Context Protocol) is an open standard introduced by Anthropic in November 2024, now governed by the Linux Foundation / AAIF. It standardizes how AI models connect to external tools and data sources — defining a client-server protocol built on JSON-RPC 2.0 so any AI host (Claude, ChatGPT, Cursor) can invoke any MCP server without custom connectors. Where the tool-use patterns in this skill cover tools you build and host yourself, MCP defines how to expose those tools (or any existing service) as a reusable server that any compliant AI client can call. If you're building agents that need to connect to third-party services or share tool implementations across multiple AI systems, MCP is the integration layer to reach for.

### Episodic Memory via pgvector (cross-reference to RAG skill)

Episodic memory stores agent conversation history as searchable vector embeddings — enabling agents to recall past interactions rather than relying solely on in-context messages.

```python
# Store a turn as an episode
import openai
import pgvector

EMBEDDING_MODEL = "text-embedding-3-small"
openai_client = openai.OpenAI()

def store_episode(db, session_id: str, role: str, content: str) -> None:
    embed = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=content)
    vector = embed.data[0].embedding
    db.execute(
        """
        INSERT INTO agent_episodes (session_id, role, content, embedding, embedding_model_version)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (session_id, role, content, pgvector.encode(vector), f"{EMBEDDING_MODEL}-v1"),
    )

def recall_episodes(db, query: str, top_k: int = 5) -> list[dict]:
    embed = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    vector = pgvector.encode(embed.data[0].embedding)
    return db.fetchall(
        """
        SELECT role, content, 1 - (embedding <=> %s) AS score
        FROM agent_episodes
        WHERE embedding_model_version = %s
        ORDER BY embedding <=> %s
        LIMIT %s
        """,
        (vector, f"{EMBEDDING_MODEL}-v1", vector, top_k),
    )
```

> Schema: `agent_episodes` table requires `embedding_model_version` column — same pattern as the RAG skill's `document_chunks` table. See `references/embedding-pipelines.md` for the full chunking and batch-embed pipeline. HNSW index recommended; see RAG skill for index setup.

---

## State of the Art

| Old Approach                      | Current Approach                                      | When Changed  | Impact                                                                                                                       |
| --------------------------------- | ----------------------------------------------------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| LangGraph 0.x (prebuilt unstable) | LangGraph 1.x (stable, production-ready)              | October 2025  | Zero breaking changes; `create_react_agent` confirmed stable; `PostgresSaver` is the production checkpointing recommendation |
| Vercel AI SDK v4/v5               | Vercel AI SDK v6 (current: 6.0.97)                    | 2025          | New `ToolLoopAgent`, human-in-the-loop tool approval, `useChat` with `parts` API, `convertToModelMessages`                   |
| `new Anthropic()` (AI SDK)        | `createAnthropic()` from `@ai-sdk/anthropic`          | AI SDK v4.0   | Breaking change already shipped — use `createAnthropic`                                                                      |
| LangChain agents (deprecated)     | LangGraph `create_react_agent`                        | 2024–2025     | LangChain agents are superseded; LangGraph is the current recommendation                                                     |
| MCP (niche/beta)                  | MCP (Linux Foundation / AAIF, 97M+ monthly downloads) | December 2025 | MCP is now mainstream; ChatGPT, Claude, Cursor all support it                                                                |

**Deprecated/outdated:**

- LangChain `initialize_agent()` / `AgentExecutor`: Replaced by LangGraph `create_react_agent`. Do not teach.
- Vercel AI SDK `experimental_StreamData`: Replaced by `toUIMessageStreamResponse()` and parts API in v5+.
- `new Anthropic()` constructor in `@ai-sdk/anthropic`: Replaced by `createAnthropic()`.

---

## Open Questions

1. **`@ai-sdk/react` `useChat` with FastAPI as the backend (not Next.js route)**
   - What we know: `TextStreamChatTransport` in AI SDK v6 accepts a custom `api` URL. FastAPI can be pointed at directly from the browser.
   - What's unclear: Whether `TextStreamChatTransport` parses Anthropic's raw SSE format or expects AI SDK's own stream format. If the latter, the FastAPI server needs to produce AI SDK-compatible SSE (not raw Anthropic SSE).
   - Recommendation: For the skill doc, show the Next.js API route approach (using `@ai-sdk/anthropic` + `streamText`) as the primary pattern. For the FastAPI backend, show raw Anthropic streaming — then note that wiring it to `useChat` requires either a proxy route or producing AI SDK-compatible SSE from the FastAPI endpoint. This is the natural "depth" limit the CONTEXT.md gives Claude discretion on.

2. **LangGraph TypeScript support**
   - What we know: LangGraph has a JavaScript/TypeScript SDK (`@langchain/langgraph`). Context7 results showed Python examples only.
   - What's unclear: Whether the TypeScript API is at parity with Python for `create_react_agent` and `PostgresSaver` in 1.x.
   - Recommendation: For AGENT-04 (LangGraph), show Python only (LangGraph is primarily a Python framework). Note that `@langchain/langgraph` exists for TypeScript but is not covered in this skill.

3. **LangGraph version to cite: 1.x vs 1.1.5**
   - What we know: STATE.md mentioned "v1.1.5" specifically. PyPI shows 1.x as current. The October 2025 LangGraph 1.0 release blog confirms stable major version. The exact latest patch version was not retrieved.
   - What's unclear: Whether 1.1.5 specifically has been released.
   - Recommendation: Cite "LangGraph 1.x (stable since October 2025)" in the SKILL.md, not a specific patch. This avoids stale version pins.

---

## Sources

### Primary (HIGH confidence)

- Context7 `/anthropics/anthropic-sdk-typescript` — tool use loop, toolRunner, stop_reason handling
- Context7 `/anthropics/anthropic-sdk-python` — Python tool use, streaming, @beta_tool decorator
- Context7 `/langchain-ai/langgraph` (version 1.0.3) — StateGraph, create_react_agent, InMemorySaver, PostgresSaver, human-in-the-loop interrupt
- Context7 `/vercel/ai` — useChat hook, streamText, TextStreamChatTransport, convertToModelMessages, @ai-sdk/anthropic provider
- [Anthropic official streaming docs](https://platform.claude.com/docs/en/build-with-claude/streaming) — SSE event types, tool_use streaming, message_delta stop_reason

### Secondary (MEDIUM confidence)

- [LangGraph 1.0 release blog — LangChain](https://blog.langchain.com/langchain-langgraph-1dot0/) — confirmed October 2025 stable release, zero breaking changes
- [Medium: LangGraph 1.0 summary](https://medium.com/@romerorico.hugo/langgraph-1-0-released-no-breaking-changes-all-the-hard-won-lessons-8939d500ca7c) — confirms backward compatibility and stability guarantees
- [Vercel AI SDK 6 blog](https://vercel.com/blog/ai-sdk-6) — ToolLoopAgent, human-in-the-loop, current version confirmed 6.0.97
- [Anthropic MCP announcement](https://www.anthropic.com/news/model-context-protocol) — MCP origins, November 2024 introduction
- [MCP spec (Nov 2025)](https://modelcontextprotocol.io/specification/2025-11-25) — current spec version, Linux Foundation governance

### Tertiary (LOW confidence)

- WebSearch result: "FastAPI + Anthropic SSE streaming" — pattern confirmed as viable; specific implementation verified via official Anthropic streaming docs and FastAPI docs

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — verified via Context7 (Anthropic SDK, LangGraph, Vercel AI SDK), official docs
- Architecture: HIGH — manual tool-use loop is canonical and stable; LangGraph 1.x confirmed stable
- Pitfalls: HIGH — all 3 required pitfalls verified against known failure modes; error multiplication is well-documented
- LangGraph version: MEDIUM — 1.x stable confirmed, specific patch version not pinned (intentional)
- Vercel AI SDK v6 + FastAPI bridge: MEDIUM — `streamText` pattern verified; FastAPI-to-`useChat` bridge has an open question on stream format compatibility

**Research date:** 2026-02-24
**Valid until:** 2026-04-01 (AI SDK v6 and LangGraph 1.x are stable — 5-week window is conservative)
