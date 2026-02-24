# SG Command: /sc:reflect

Mirror of core `/sc:reflect` prompt intent for SG command workflows.

## Command
`/sc:reflect [--type task|session|completion] [--analyze] [--validate]`

## Defaults
- `--type task`
- `--analyze true`
- `--validate true`

## Execution Flow
1. Analyze current state with Serena reflection tools.
2. Validate adherence to goals and quality criteria.
3. Reflect on completeness, risks, and unresolved work.
4. Document cross-session insights in memory when useful.
5. Provide prioritized optimization actions.

## Required Serena Tools
- `think_about_task_adherence`
- `think_about_collected_information`
- `think_about_whether_you_are_done`
- `list_memories`
- `read_memory`
- `write_memory`

## Constraints
- Do not mark a task done without explicit done-check evidence.
- Keep reflection output concise, decision-oriented, and actionable.
- Preserve consistency with `features/sc/core/RESEARCH_CONFIG.md`.
