#!/bin/bash
# Telemetry logging script for LLM usage tracking
# Usage: ./scripts/log-telemetry.sh "model-name" prompt_tokens completion_tokens true|false "task_type" duration_ms "notes"

set -e

# Configuration
TELEMETRY_DIR=".telemetry"
USAGE_FILE="$TELEMETRY_DIR/usage.csv"
BACKUP_THRESHOLD=10485760  # 10MB in bytes

# Validate arguments
if [ $# -lt 6 ]; then
    echo "Usage: $0 <model> <prompt_tokens> <completion_tokens> <task_success> <task_type> <duration_ms> [notes]"
    echo ""
    echo "Arguments:"
    echo "  model             - Model name (e.g., 'claude-3-opus', 'gpt-4')"
    echo "  prompt_tokens     - Number of prompt tokens (integer)"
    echo "  completion_tokens - Number of completion tokens (integer)"
    echo "  task_success      - true or false"
    echo "  task_type         - plan|execute|verify|discuss|quick"
    echo "  duration_ms       - Duration in milliseconds (integer)"
    echo "  notes             - Optional notes (quoted string)"
    echo ""
    echo "Example:"
    echo "  $0 \"claude-3-opus\" 1500 3200 true \"execute\" 45000 \"Phase 6 tests\""
    exit 1
fi

MODEL="$1"
PROMPT_TOKENS="$2"
COMPLETION_TOKENS="$3"
TASK_SUCCESS="$4"
TASK_TYPE="$5"
DURATION_MS="$6"
NOTES="${7:-}"

# Validate model name (non-empty)
if [ -z "$MODEL" ]; then
    echo "Error: Model name cannot be empty"
    exit 1
fi

# Validate tokens are integers
if ! [[ "$PROMPT_TOKENS" =~ ^[0-9]+$ ]]; then
    echo "Error: prompt_tokens must be an integer"
    exit 1
fi

if ! [[ "$COMPLETION_TOKENS" =~ ^[0-9]+$ ]]; then
    echo "Error: completion_tokens must be an integer"
    exit 1
fi

# Validate task_success is boolean
if [ "$TASK_SUCCESS" != "true" ] && [ "$TASK_SUCCESS" != "false" ]; then
    echo "Error: task_success must be 'true' or 'false'"
    exit 1
fi

# Validate task_type
if [[ ! "$TASK_TYPE" =~ ^(plan|execute|verify|discuss|quick)$ ]]; then
    echo "Error: task_type must be one of: plan, execute, verify, discuss, quick"
    exit 1
fi

# Validate duration_ms is integer
if ! [[ "$DURATION_MS" =~ ^[0-9]+$ ]]; then
    echo "Error: duration_ms must be an integer"
    exit 1
fi

# Escape notes for CSV (replace commas and newlines)
ESCAPED_NOTES="${NOTES//,/ }"
ESCAPED_NOTES="${ESCAPED_NOTES//$'\n'/ }"

# Ensure telemetry directory exists
mkdir -p "$TELEMETRY_DIR"

# Check if backup needed
if [ -f "$USAGE_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$USAGE_FILE" 2>/dev/null || stat -c%s "$USAGE_FILE" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt "$BACKUP_THRESHOLD" ]; then
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        mv "$USAGE_FILE" "$TELEMETRY_DIR/usage_backup_$TIMESTAMP.csv"
        echo "timestamp,model,prompt_tokens,completion_tokens,task_success,task_type,duration_ms,notes" > "$USAGE_FILE"
        echo "Note: Created backup at $TELEMETRY_DIR/usage_backup_$TIMESTAMP.csv"
    fi
fi

# Create file with headers if it doesn't exist
if [ ! -f "$USAGE_FILE" ]; then
    echo "timestamp,model,prompt_tokens,completion_tokens,task_success,task_type,duration_ms,notes" > "$USAGE_FILE"
fi

# Generate timestamp (RFC 3339 format)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Append to CSV
echo "$TIMESTAMP,$MODEL,$PROMPT_TOKENS,$COMPLETION_TOKENS,$TASK_SUCCESS,$TASK_TYPE,$DURATION_MS,$ESCAPED_NOTES" >> "$USAGE_FILE"

echo "✓ Telemetry logged: $MODEL ($TASK_TYPE) - ${PROMPT_TOKENS}/${COMPLETION_TOKENS} tokens"
