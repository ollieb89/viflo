# Evaluation Workflows

---

## Golden Set Architecture

A golden set is a folder of `.md` test case files plus a TypeScript runner (`eval.ts`). It gives you a lightweight, platform-free eval suite that lives in your repo alongside your prompts.

```
references/golden-set/
  chain-of-thought.md   # test case: CoT pattern
  few-shot.md           # test case: few-shot pattern
  output-format.md      # test case: structured output pattern
  eval.ts               # runner: reads .md files, calls Claude, judges output
```

**Developer workflow:**

1. Write or edit a prompt pattern file
2. `cd .agent/skills/prompt-engineering/references/golden-set/`
3. `npx ts-node eval.ts`
4. See pass/fail per test case in stdout
5. Fix prompt, repeat until all pass

No external platform needed. No account registration. Just `ANTHROPIC_API_KEY` in your environment.

---

## Test Case Format

Each `.md` file in `golden-set/` follows this structure:

```markdown
---
pattern: chain-of-thought
model: claude-sonnet-4-6
applies-to: [claude-opus-4-6, claude-sonnet-4-6]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
---

## Input Prompt

System: [system prompt text]

User: [user message text]

## Expected Output Criteria

- [criterion 1 — specific, checkable]
- [criterion 2]
- [criterion 3]
```

**Frontmatter fields:**

| Field                   | Required | Purpose                                             |
| ----------------------- | -------- | --------------------------------------------------- |
| `pattern`               | Yes      | Human-readable pattern name (used in runner output) |
| `model`                 | Yes      | Model to call when running this test                |
| `applies-to`            | Yes      | Full list of models this pattern is validated for   |
| `last-verified-against` | Yes      | Model used in last successful run                   |
| `verified-date`         | Yes      | ISO date of last verification                       |

**Criteria writing tips:**

- Make each criterion independently checkable (the LLM judge evaluates each one)
- Prefer specific over vague: "Final answer states the car is 20 mph faster" not "Answer is correct"
- Include format criteria ("Does not wrap JSON in markdown code fences") alongside content criteria

---

## Running the Eval

**One-time setup (if not already installed):**

```bash
npm install -D ts-node @types/node
```

**Run:**

```bash
cd .agent/skills/prompt-engineering/references/golden-set/
npx ts-node eval.ts
```

**Output format:**

```
  Running chain-of-thought... ✓ PASS
  Running few-shot... ✓ PASS
  Running output-format-specification... ✗ FAIL — Output skipped intermediate steps

3/3 passed     # or with failures:
2/3 passed     # exit code 1 on any failure
```

Exit code 0 on all pass, exit code 1 on any failure — suitable for CI integration.

---

## Prompt Versioning

Each prompt variant is a file. Git history is version history.

**File structure:**

```
prompts/
  summarize-v1.md    # last-verified-against: claude-sonnet-4-6, 2026-01-15
  summarize-v2.md    # last-verified-against: claude-sonnet-4-6, 2026-02-10
  classify-v1.md
```

**Rules:**

1. Every prompt file carries `last-verified-against:` frontmatter — locks it to a model snapshot
2. When you change a prompt, commit the change with a message explaining why (don't edit silently)
3. For significant changes, create a new file (`summarize-v3.md`) — preserves rollback
4. When a new model is released, re-run golden set on existing prompts and update `last-verified-against:`

**Warning sign:** A single `prompts.ts` file with inline string edits — no audit trail, no rollback, no model pinning.

---

## The Eval Loop

```
Write prompt → Sample N outputs → Score with rubric → Identify failure pattern → Fix prompt → Repeat
```

Never iterate on a prompt based on a single output. Sample at least 10, preferably 50.

---

## Scoring Rubric Design

```typescript
interface EvalResult {
  promptVersion: string;
  sample: string;
  scores: {
    correctness: number; // 0-1: is the answer factually correct?
    format: number; // 0-1: does output match expected format?
    completeness: number; // 0-1: does it cover all required elements?
    safety: number; // 0-1: no harmful, biased, or injected content?
  };
  notes: string;
}

function averageScore(results: EvalResult[]): Record<string, number> {
  const keys = ["correctness", "format", "completeness", "safety"] as const;
  return Object.fromEntries(
    keys.map((k) => [
      k,
      results.reduce((sum, r) => sum + r.scores[k], 0) / results.length,
    ]),
  );
}
```

---

## Automated Scoring with LLM-as-Judge

```typescript
async function scoreOutput(
  prompt: string,
  output: string,
  rubric: string,
): Promise<{ score: number; reasoning: string }> {
  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001", // cheap judge model
    max_tokens: 512,
    messages: [
      {
        role: "user",
        content: `Evaluate this output against the rubric. Return JSON only.

Prompt: ${prompt}
Output: ${output}
Rubric: ${rubric}

Return: {"score": 0-1, "reasoning": "one sentence"}`,
      },
    ],
  });

  const raw =
    response.content[0].type === "text" ? response.content[0].text : "{}";
  try {
    return JSON.parse(raw);
  } catch {
    return { score: 0, reasoning: "Judge returned invalid JSON" };
  }
}
```

---

## Version Tracking

Track each prompt version with its eval results:

```typescript
interface PromptVersion {
  version: string; // e.g., "v1.0", "v1.1"
  systemPrompt: string;
  changesFrom: string; // what changed and why
  evalResults: {
    sampleSize: number;
    averageScores: Record<string, number>;
    failurePatterns: string[];
  };
}
```
