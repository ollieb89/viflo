#!/bin/bash
# Generate reports from telemetry data
# Usage: ./scripts/telemetry-report.sh [--format markdown|json]

set -e

TELEMETRY_FILE=".telemetry/usage.csv"
FORMAT="${1:-markdown}"

if [ "$FORMAT" = "--format" ]; then
    FORMAT="${2:-markdown}"
fi

if [ ! -f "$TELEMETRY_FILE" ]; then
    echo "Error: Telemetry file not found at $TELEMETRY_FILE"
    exit 1
fi

# Count total entries (excluding header)
TOTAL_ENTRIES=$(tail -n +2 "$TELEMETRY_FILE" | wc -l | tr -d ' ')

if [ "$TOTAL_ENTRIES" -eq 0 ]; then
    echo "No telemetry data found."
    exit 0
fi

# Calculate statistics using awk
STATS=$(tail -n +2 "$TELEMETRY_FILE" | awk -F',' '
BEGIN {
    total_prompt = 0
    total_completion = 0
    total_duration = 0
    success_count = 0
    plan_count = 0
    execute_count = 0
    verify_count = 0
    discuss_count = 0
    quick_count = 0
}
{
    total_prompt += $3
    total_completion += $4
    total_duration += $7
    if ($5 == "true") success_count++
    
    if ($6 == "plan") plan_count++
    else if ($6 == "execute") execute_count++
    else if ($6 == "verify") verify_count++
    else if ($6 == "discuss") discuss_count++
    else if ($6 == "quick") quick_count++
}
END {
    print total_prompt, total_completion, total_duration, success_count, NR, plan_count, execute_count, verify_count, discuss_count, quick_count
}')

read -r TOTAL_PROMPT TOTAL_COMPLETION TOTAL_DURATION SUCCESS_COUNT TOTAL PLAN_COUNT EXECUTE_COUNT VERIFY_COUNT DISCUSS_COUNT QUICK_COUNT <<< "$STATS"

TOTAL_TOKENS=$((TOTAL_PROMPT + TOTAL_COMPLETION))
SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($SUCCESS_COUNT / $TOTAL) * 100}")
AVG_DURATION=$(awk "BEGIN {printf \"%.0f\", $TOTAL_DURATION / $TOTAL}")

if [ "$FORMAT" = "json" ]; then
    cat << EOF
{
  "summary": {
    "total_entries": $TOTAL,
    "total_prompt_tokens": $TOTAL_PROMPT,
    "total_completion_tokens": $TOTAL_COMPLETION,
    "total_tokens": $TOTAL_TOKENS,
    "success_rate_percent": $SUCCESS_RATE,
    "average_duration_ms": $AVG_DURATION
  },
  "by_task_type": {
    "plan": $PLAN_COUNT,
    "execute": $EXECUTE_COUNT,
    "verify": $VERIFY_COUNT,
    "discuss": $DISCUSS_COUNT,
    "quick": $QUICK_COUNT
  }
}
EOF
else
    # Markdown format
    echo "# Telemetry Report"
    echo ""
    echo "Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo ""
    echo "## Summary"
    echo ""
    echo "| Metric | Value |"
    echo "|--------|-------|"
    echo "| Total Entries | $TOTAL |"
    echo "| Total Prompt Tokens | $TOTAL_PROMPT |"
    echo "| Total Completion Tokens | $TOTAL_COMPLETION |"
    echo "| **Total Tokens** | **$TOTAL_TOKENS** |"
    echo "| Success Rate | ${SUCCESS_RATE}% |"
    echo "| Average Duration | ${AVG_DURATION}ms |"
    echo ""
    echo "## By Task Type"
    echo ""
    echo "| Task Type | Count |"
    echo "|-----------|-------|"
    echo "| Plan | $PLAN_COUNT |"
    echo "| Execute | $EXECUTE_COUNT |"
    echo "| Verify | $VERIFY_COUNT |"
    echo "| Discuss | $DISCUSS_COUNT |"
    echo "| Quick | $QUICK_COUNT |"
    echo ""
    echo "---"
    echo ""
    echo "*Data source: $TELEMETRY_FILE*"
fi
