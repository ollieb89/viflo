# Telemetry

LLM usage telemetry for the viflo project.

## Purpose

Track LLM usage to understand:

- Token consumption by model and task type
- Task success rates
- Duration patterns
- Cost analysis

## Schema

| Field               | Type     | Description                                     |
| ------------------- | -------- | ----------------------------------------------- |
| `timestamp`         | ISO 8601 | When the task was completed (UTC)               |
| `model`             | string   | LLM model name (e.g., "claude-3-opus", "gpt-4") |
| `prompt_tokens`     | integer  | Tokens in the prompt                            |
| `completion_tokens` | integer  | Tokens in the completion                        |
| `task_success`      | boolean  | Whether the task completed successfully         |
| `task_type`         | enum     | plan \| execute \| verify \| discuss \| quick   |
| `duration_ms`       | integer  | Task duration in milliseconds                   |
| `notes`             | string   | Optional context or notes                       |

## Usage

### Log a Task

```bash
./scripts/log-telemetry.sh \
  "claude-3-opus" \
  1500 \
  3200 \
  true \
  "execute" \
  45000 \
  "Phase 6 tests"
```

Arguments:

1. Model name
2. Prompt tokens
3. Completion tokens
4. Success (true/false)
5. Task type (plan/execute/verify/discuss/quick)
6. Duration in milliseconds
7. Notes (optional)

### Generate Report

```bash
# Markdown report (default)
./scripts/telemetry-report.sh

# JSON format
./scripts/telemetry-report.sh --format json
```

## Storage

- **File**: `usage.csv`
- **Format**: CSV with headers
- **Backup**: Automatic backup when file exceeds 10MB
- **Retention**: Committed to git for historical analysis

## Privacy

- No user-identifiable information
- No code snippets or proprietary content
- Only aggregate metrics and task metadata

## Retention Policy

Data is retained indefinitely for historical analysis. Backups are created automatically when the main file exceeds 10MB.
