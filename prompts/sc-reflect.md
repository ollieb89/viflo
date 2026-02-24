# /sc:reflect - Task Reflection and Validation

## Purpose

Run structured reflection at task/session/completion checkpoints with Serena tools to verify quality, adherence, and readiness.

## Usage

`/sc:reflect [--type task|session|completion] [--analyze] [--validate]`

## Inputs

- `--type`: `task` (default), `session`, or `completion`
- `--analyze`: enable analysis pass (default: `true`)
- `--validate`: enable validation pass (default: `true`)

## Behavioral Flow

1. Analyze current state and progress with Serena reflection tools.
2. Validate requirement adherence and quality gates.
3. Reflect on gaps, risks, and completion readiness.
4. Document insights into cross-session memory when warranted.
5. Optimize by issuing concrete next-step recommendations.

## Required Tool Coordination

- `think_about_task_adherence`: goal alignment and deviation detection
- `think_about_collected_information`: information completeness and quality
- `think_about_whether_you_are_done`: completion criteria and remaining work
- `list_memories` / `read_memory` / `write_memory`: learning persistence

## Output Contract

- Reflection summary by scope (`task`, `session`, or `completion`)
- Validation outcomes (pass/fail + rationale)
- Explicit remaining work, if any
- 1-3 prioritized optimization recommendations

## Quality and Performance Targets

- Core reflection operations complete within 200ms p95.
- Checkpoint creation / memory-write path completes within 1s p95.
- No completion claim without explicit adherence and done-check signal.
