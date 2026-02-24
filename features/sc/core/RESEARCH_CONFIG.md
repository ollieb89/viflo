# SC Research Configuration

Canonical configuration for SC research/reflect command families.

## MCP Servers

- `serena` (required): reflection analysis, task adherence checks, memory ops
- `context7` (optional): library doc grounding during research-heavy flows

## Serena Reflection Tools

- `think_about_task_adherence`
- `think_about_collected_information`
- `think_about_whether_you_are_done`

## Serena Memory Tools

- `list_memories`
- `read_memory`
- `write_memory`

## Performance Targets

- Core reflection operation p95: `< 200ms`
- Checkpoint/memory path p95: `< 1s`

## Consistency Rule

Any `features/sc/commands/*` or `commands/sg/*` prompt that references reflection/research tooling must align with this file.
