#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_LLM_TESTS:-0}" != "1" ]]; then
  echo "LLM-assisted tests are disabled by default."
  echo "Set RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=local|budget to run them explicitly."
  exit 0
fi

profile="${TEST_MODEL_PROFILE:-}"
profile="$(printf '%s' "$profile" | tr '[:upper:]' '[:lower:]')"

if [[ "$profile" != "local" && "$profile" != "budget" ]]; then
  echo "Invalid TEST_MODEL_PROFILE: '${TEST_MODEL_PROFILE:-}'" >&2
  echo "Allowed profiles: local, budget" >&2
  echo "Example: RUN_LLM_TESTS=1 TEST_MODEL_PROFILE=local pnpm run test:llm" >&2
  exit 2
fi

echo "Running LLM-assisted tests with TEST_MODEL_PROFILE=$profile"
pnpm --filter @viflo/web run test:llm
