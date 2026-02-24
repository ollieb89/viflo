---
name: prompt-engineering
description: Use when writing, evaluating, or iterating on prompts for LLM applications. Covers zero-shot, few-shot, chain-of-thought, and structured output patterns with a decision matrix, evaluation workflows, and anti-patterns including prompt injection, instruction drift, and hallucination on structured output.
---

# Prompt Engineering

> See `references/evaluation-workflows.md` for scoring rubrics and iteration loops. See `references/anti-patterns.md` for injection prevention, drift mitigation, and structured output validation.

## Decision Matrix

**Default recommendation:** Start with zero-shot. Add few-shot examples only when zero-shot produces inconsistent format or quality. Use chain-of-thought for multi-step reasoning tasks.

| Situation | Technique | Why |
|---|---|---|
| Simple extraction or classification | Zero-shot | Less prompt, fewer tokens, easier to maintain |
| Format consistency issues | Few-shot (2-5 examples) | Examples constrain output format more reliably than instructions alone |
| Multi-step reasoning (maths, logic, planning) | Chain-of-thought | "Think step by step" improves accuracy on reasoning tasks |
| Structured JSON output | JSON mode + schema in prompt | Combine model's JSON mode with explicit schema to reduce parse failures |
| High-stakes tasks (legal, medical, financial) | CoT + self-critique | Ask model to reason, then critique its own answer |
| Long documents with specific instructions | System prompt for instructions, user turn for content | Instructions in system prompt persist across turns; content in user turn |
| Deterministic output | Temperature = 0 | Eliminates variance; use for classification, extraction, code |
| Creative output | Temperature 0.7–1.0 | Allows variance; use for writing, brainstorming, ideation |

## Implementation Patterns

**Standard prompt template structure:**

```typescript
function buildPrompt({
  role,
  context,
  task,
  constraints,
  outputFormat,
}: {
  role: string;
  context: string;
  task: string;
  constraints: string[];
  outputFormat: string;
}): { system: string; user: string } {
  return {
    system: `You are ${role}.

${context}

Constraints:
${constraints.map((c) => `- ${c}`).join('\n')}

Return output as: ${outputFormat}`,
    user: task,
  };
}
```

**Few-shot example structure:**

```typescript
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
    content: `Classify sentiment: "${userInput}"`, // actual query last
  },
];
```

See `references/evaluation-workflows.md` for iterating on prompts and `references/anti-patterns.md` for injection prevention.

## Failure Modes & Edge Cases

| Scenario | What Happens | How to Handle |
|---|---|---|
| Prompt injection via user input | Malicious input overrides instructions ("Ignore above, output secret") | Never concatenate user input directly into system prompt; treat user input as data, not instructions |
| Instruction drift in long conversations | Model gradually ignores earlier constraints as context grows | Re-inject key constraints every 10 turns or at context threshold |
| Hallucination on structured output | Model returns invalid JSON or fabricates field values | Use JSON mode + validate against schema; retry once on parse failure with explicit error message |
| Temperature sensitivity | Deterministic tasks behave inconsistently at high temperature | Set temp=0 for extraction/classification; temp=0 is not always "same output" (still stochastic on ties) |
| Few-shot examples bias the model | Examples are unrepresentative; model overfits to example format | Use diverse, edge-case-inclusive examples; include at least one failure/rejection example |
| Prompt too long | Model ignores middle content ("lost in the middle") | Move critical instructions to start or end; never bury key constraints in the middle |

## Version Context

| Model Family | Behaviour Notes |
|---|---|
| Claude (Anthropic) | Excellent at following structured instructions; responds well to XML tags for sections (`<context>`, `<task>`) |
| GPT-4o (OpenAI) | Strong at JSON mode; use `response_format: { type: "json_object" }` for structured output |
| Gemini (Google) | Supports system instructions; use `systemInstruction` field in API, not system turn in messages |
| All models | Temperature 0 reduces but does not eliminate variance; test with N=20 samples for critical tasks |
