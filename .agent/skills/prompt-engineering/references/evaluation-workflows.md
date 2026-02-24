# Prompt Evaluation Workflows

## The Eval Loop

```
Write prompt → Sample N outputs → Score with rubric → Identify failure pattern → Fix prompt → Repeat
```

Never iterate on a prompt based on a single output. Sample at least 10, preferably 50.

## Scoring Rubric Design

```typescript
interface EvalResult {
  promptVersion: string;
  sample: string;
  scores: {
    correctness: number;   // 0-1: is the answer factually correct?
    format: number;        // 0-1: does output match expected format?
    completeness: number;  // 0-1: does it cover all required elements?
    safety: number;        // 0-1: no harmful, biased, or injected content?
  };
  notes: string;
}

function averageScore(results: EvalResult[]): Record<string, number> {
  const keys = ['correctness', 'format', 'completeness', 'safety'] as const;
  return Object.fromEntries(
    keys.map((k) => [k, results.reduce((sum, r) => sum + r.scores[k], 0) / results.length])
  );
}
```

## Automated Scoring with LLM-as-Judge

```typescript
async function scoreOutput(
  prompt: string,
  output: string,
  rubric: string
): Promise<{ score: number; reasoning: string }> {
  const response = await anthropic.messages.create({
    model: 'claude-haiku-4-5-20251001', // cheap judge model
    max_tokens: 512,
    messages: [
      {
        role: 'user',
        content: `Evaluate this output against the rubric. Return JSON only.

Prompt: ${prompt}
Output: ${output}
Rubric: ${rubric}

Return: {"score": 0-1, "reasoning": "one sentence"}`,
      },
    ],
  });

  const text = response.content[0].type === 'text' ? response.content[0].text : '{}';
  return JSON.parse(text);
}
```

## Version Tracking

Track each prompt version with its eval results:

```typescript
interface PromptVersion {
  version: string;      // e.g., "v1.0", "v1.1"
  systemPrompt: string;
  changesFrom: string;  // what changed and why
  evalResults: {
    sampleSize: number;
    averageScores: Record<string, number>;
    failurePatterns: string[];
  };
}
```
