---
pattern: chain-of-thought
model: claude-sonnet-4-6
applies-to: [claude-opus-4-6, claude-sonnet-4-6]
last-verified-against: claude-sonnet-4-6
verified-date: 2026-02-24
eval-verified-date: 2026-02-24
---

## Input Prompt

System: You are a math tutor. Think through this step by step before giving your final answer. Show your reasoning.

User: A train travels 120 miles in 2 hours. A car travels the same distance in 1.5 hours. How much faster is the car, in mph?

## Expected Output Criteria

- Contains step-by-step reasoning before the final answer (not just the final number)
- Correctly calculates train speed: 120 ÷ 2 = 60 mph
- Correctly calculates car speed: 120 ÷ 1.5 = 80 mph
- Final answer states the car is 20 mph faster
- Does not skip directly to the answer without showing intermediate steps
