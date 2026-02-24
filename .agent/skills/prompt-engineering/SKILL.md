---
name: prompt-engineering
description: Use when writing, evaluating, or iterating on prompts for Claude API calls. Covers quick-start setup, role/context/task/output anatomy, applies-to model schema, chain-of-thought, few-shot, and structured output patterns with a decision matrix, evaluation workflows, and anti-patterns. v1.2 standard — includes golden-set eval tooling.
---

# Prompt Engineering

> See `references/anti-patterns.md` for top-5 output-degrading patterns with Before/After examples. See `references/evaluation-workflows.md` for golden-set scoring and eval.ts runner.

## Quick Start

Copy-paste ready — only requirement is `ANTHROPIC_API_KEY` in your environment.

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic(); // reads ANTHROPIC_API_KEY from env

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 1024,
  system: 'You are a geography expert. Return only the capital city name, nothing else.',
  messages: [
    { role: 'user', content: 'What is the capital of France?' },
  ],
});

console.log(response.content[0].type === 'text' ? response.content[0].text : '');
// Output: Paris
```

---

## 1. Setup

### Installation

```bash
npm install @anthropic-ai/sdk
```

Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or in `.env` (with `dotenv`):

```
ANTHROPIC_API_KEY=sk-ant-...
```

### Model Selection

| Model | Best For | Notes |
|---|---|---|
| `claude-opus-4-6` | Complex reasoning, multi-step planning, extended thinking | Most capable; use for CoT tasks requiring deep reasoning |
| `claude-sonnet-4-6` | Balanced quality and speed — **recommended default** | Handles nearly all production workloads |
| `claude-haiku-4-5-20251001` | Fast classification, eval judges, high-volume tasks | Cheapest; use for structured output and eval scoring |

**Model-specific behavior:** All Claude models are instruction-tuned and respond well to XML section delimiters (`<context>`, `<task>`, `<critical>`). This is Claude-specific — GPT-4o uses plain text sections, Gemini uses `systemInstruction` field.

---

## 2. Configuration

### Prompt Anatomy (role/context/task/output)

The `buildPrompt()` function encodes the four-part anatomy every production prompt needs:

```typescript
interface PromptParams {
  role: string;
  context: string;
  task: string;
  constraints: string[];
  outputFormat: string;
}

function buildPrompt(params: PromptParams): { system: string; user: string } {
  return {
    system: `You are ${params.role}.

${params.context}

Constraints:
${params.constraints.map((c) => `- ${c}`).join('\n')}

Return output as: ${params.outputFormat}`,
    user: params.task,
  };
}

// Usage
const { system, user } = buildPrompt({
  role: 'a customer support agent for Acme Inc.',
  context: 'You help customers with billing and account questions only.',
  task: 'The user message is below.',
  constraints: [
    'Do not discuss competitors',
    'Escalate to human if the issue involves refunds over $500',
    'Always end with an offer to help further',
  ],
  outputFormat: 'plain conversational English, 2-3 sentences max',
});
```

### applies-to Frontmatter Schema (PROMPT-02)

Every prompt pattern file must carry this frontmatter block to declare which models it has been tested against:

```yaml
---
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
---
```

**Field meanings:**

| Field | Purpose | Valid values |
|---|---|---|
| `applies-to` | Models where this pattern works reliably | Any subset of: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001` |
| `last-verified-against` | Specific model used in last test run | One of the above model IDs |
| `verified-date` | ISO date of last verification | `YYYY-MM-DD` |

**Why this matters:** A chain-of-thought pattern tested on `claude-opus-4-6` may produce lower-quality reasoning on `claude-haiku-4-5-20251001`. Tagging prevents silently broken patterns when you switch models.

---

## 3. Patterns

Each pattern below carries `applies-to` frontmatter — check it before choosing a model.

### Chain-of-Thought (CoT)

```yaml
applies-to: [claude-opus-4-6, claude-sonnet-4-6]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
```

Ask the model to reason step-by-step before giving the final answer. Improves accuracy on math, logic, and multi-step planning tasks.

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 2048, // CoT needs space — give it at least 2x your expected output
  system: 'You are a math tutor. Think through this step by step before giving your final answer. Show your reasoning.',
  messages: [
    {
      role: 'user',
      content: 'A train travels 120 miles in 2 hours. A car travels the same distance in 1.5 hours. How much faster is the car, in mph?',
    },
  ],
});

console.log(response.content[0].type === 'text' ? response.content[0].text : '');
```

**Extended thinking (claude-opus-4-6 only):** For complex multi-step reasoning, `claude-opus-4-6` supports a `thinking` parameter that enables internal extended reasoning before the response. See the Anthropic SDK docs for `thinking: { type: 'enabled', budget_tokens: 5000 }`.

### Few-Shot

```yaml
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
```

Provide 2–5 input/output example pairs before the real request. Use when zero-shot produces inconsistent format or quality.

```typescript
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// Note: do NOT wrap userInput in quotes — allows escape attacks via `"`
const userInput = 'The packaging was a bit dented but the item inside was perfect.';

const messages: Anthropic.MessageParam[] = [
  {
    role: 'user',
    content: 'Classify sentiment: "The product arrived broken and customer service was useless."',
  },
  { role: 'assistant', content: '{"sentiment": "negative", "confidence": 0.97}' },
  {
    role: 'user',
    content: 'Classify sentiment: "Fast shipping and exactly what I ordered."',
  },
  { role: 'assistant', content: '{"sentiment": "positive", "confidence": 0.95}' },
  {
    role: 'user',
    content: `Classify the sentiment of the following text.\n\nText: ${userInput}`,
  },
];

const response = await client.messages.create({
  model: 'claude-sonnet-4-6',
  max_tokens: 256,
  messages,
});

console.log(response.content[0].type === 'text' ? response.content[0].text : '');
```

### Output Format Specification (Structured Output)

```yaml
applies-to: [claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
```

Use `client.messages.parse` with `zodOutputFormat` for reliable structured output. This handles schema validation automatically.

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod';
import { z } from 'zod';

const client = new Anthropic();

const SentimentSchema = z.object({
  sentiment: z.enum(['positive', 'negative', 'neutral']),
  confidence: z.number().min(0).max(1),
});

const response = await client.messages.parse({
  model: 'claude-haiku-4-5-20251001',
  max_tokens: 256,
  messages: [
    {
      role: 'user',
      content: 'Classify the sentiment: "The product arrived broken and customer service was useless."',
    },
  ],
  response_format: zodOutputFormat(SentimentSchema, 'sentiment'),
});

const result = response.choices[0].message.parsed;
// result.sentiment => 'negative'
// result.confidence => 0.97
```

**Alternative:** If Zod is not in your project, use `jsonSchemaOutputFormat` from `@anthropic-ai/sdk/helpers/json-schema`.

**Key distinction:** Use `client.messages.parse` (not `messages.create`) for structured output — it handles parsing and throws on schema mismatch automatically.

### Decision Matrix

**Default:** Start with zero-shot. Add few-shot only when zero-shot produces inconsistent format or quality. Use CoT for multi-step reasoning.

| Situation | Technique | Why |
|---|---|---|
| Simple extraction or classification | Zero-shot | Less prompt, fewer tokens, easier to maintain |
| Format consistency issues | Few-shot (2-5 examples) | Examples constrain output format more reliably than instructions alone |
| Multi-step reasoning (maths, logic, planning) | Chain-of-thought | "Think step by step" improves accuracy on reasoning tasks |
| Structured JSON output | `messages.parse` + `zodOutputFormat` | Combine schema validation with automatic parsing |
| High-stakes tasks (legal, medical, financial) | CoT + self-critique | Ask model to reason, then critique its own answer |
| Long documents with specific instructions | System for instructions, user for content | Instructions in system prompt persist; content in user turn |
| Deterministic output | Temperature = 0 | Eliminates variance; use for classification, extraction, code |
| Creative output | Temperature 0.7–1.0 | Allows variance; use for writing, brainstorming |

---

## 4. Gotchas / Pitfalls

**1. Anti-Patterns** — See `references/anti-patterns.md` for the top-5 output-degrading patterns with Before/After TypeScript examples: prompt injection, instruction drift, hallucination on structured output, constraint overload, and lost-in-the-middle.

**2. Prompt Versioning Without Structure** — Each prompt variant should be a file. Git history is version history. Tag each file with `last-verified-against:` frontmatter to lock it to a model snapshot. Warning sign: a single `prompts.ts` file with inline string edits — no audit trail, no rollback.

**3. Missing applies-to Tags** — A pattern that works on `claude-opus-4-6` may not work as well on `claude-haiku-4-5-20251001`. Always tag patterns with `applies-to` frontmatter. Warning sign: pattern documented without `applies-to:` field.

**4. Temperature Sensitivity** — Deterministic tasks (extraction, classification) must use temperature 0. Temperature 0 reduces but does not eliminate variance — test with N=20 samples for critical tasks before treating a prompt as production-ready.
