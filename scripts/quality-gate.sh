#!/usr/bin/env bash
set -u

GATE_FILTER=""
JSON_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --gate)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --gate (expected lint|typecheck|test|build)" >&2
        exit 2
      fi
      case "$2" in
        lint|typecheck|test|build)
          GATE_FILTER="$2"
          ;;
        *)
          echo "Invalid gate: $2 (expected lint|typecheck|test|build)" >&2
          exit 2
          ;;
      esac
      shift 2
      ;;
    --json)
      JSON_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--gate lint|typecheck|test|build] [--json]" >&2
      exit 2
      ;;
  esac
done

RUN_ID="$(date -u +"%Y%m%dT%H%M%SZ")-$$"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

declare -a ORDERED_GATES=("lint" "typecheck" "test" "build")
declare -A COMMANDS=(
  ["lint"]="pnpm run lint"
  ["typecheck"]="pnpm run type-check"
  ["test"]="pnpm run test"
  ["build"]="pnpm run build"
)
declare -A SUGGESTED=(
  ["lint"]="pnpm run lint"
  ["typecheck"]="pnpm run type-check"
  ["test"]="pnpm run test"
  ["build"]="pnpm run build"
)

declare -a EXECUTED_GATES=()
declare -A STATUS_BY_GATE=()
declare -A DURATION_BY_GATE=()
declare -A EXIT_BY_GATE=()
declare -A LOG_BY_GATE=()
HOOK_DRIFT=false
HOOK_DRIFT_DETAILS=""
HOOK_REMEDIATION="bash scripts/setup-security-hooks.sh"

json_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  value="${value//$'\n'/\\n}"
  value="${value//$'\r'/\\r}"
  value="${value//$'\t'/\\t}"
  printf '%s' "$value"
}

run_gate() {
  local gate="$1"
  local command="${COMMANDS[$gate]}"
  local log_file start_ms end_ms duration_ms exit_code status

  log_file="$(mktemp)"
  start_ms="$(date +%s%3N)"
  if bash -lc "$command" >"$log_file" 2>&1; then
    exit_code=0
    status="PASS"
  else
    exit_code=$?
    status="FAIL"
  fi
  end_ms="$(date +%s%3N)"
  duration_ms="$((end_ms - start_ms))"

  EXECUTED_GATES+=("$gate")
  STATUS_BY_GATE["$gate"]="$status"
  DURATION_BY_GATE["$gate"]="$duration_ms"
  EXIT_BY_GATE["$gate"]="$exit_code"
  LOG_BY_GATE["$gate"]="$log_file"
}

detect_hook_drift() {
  local hook_file=".git/hooks/pre-commit"
  local version_marker=".git/hooks/.viflo-pre-commit-version"
  local installed_version=""
  local current_version=""
  local reasons=()

  if [[ ! -d .git ]]; then
    HOOK_DRIFT=true
    HOOK_DRIFT_DETAILS="not running from a git repository root"
    return
  fi

  if [[ ! -f "$hook_file" ]]; then
    reasons+=("hook missing")
  elif ! grep -qi "pre-commit" "$hook_file"; then
    reasons+=("hook content mismatch")
  fi

  if ! command -v pre-commit >/dev/null 2>&1; then
    reasons+=("pre-commit command missing")
  else
    current_version="$(pre-commit --version | awk '{print $2}')"
    if [[ -f "$version_marker" ]]; then
      installed_version="$(cat "$version_marker" 2>/dev/null || true)"
      if [[ "$installed_version" != "$current_version" ]]; then
        reasons+=("version drift ($installed_version -> $current_version)")
      fi
    else
      reasons+=("version marker missing")
    fi
  fi

  if [[ ${#reasons[@]} -gt 0 ]]; then
    HOOK_DRIFT=true
    HOOK_DRIFT_DETAILS="$(IFS='; '; echo "${reasons[*]}")"
  fi
}

cleanup_logs() {
  for gate in "${EXECUTED_GATES[@]}"; do
    rm -f "${LOG_BY_GATE[$gate]}"
  done
}
trap cleanup_logs EXIT

for gate in "${ORDERED_GATES[@]}"; do
  if [[ -n "$GATE_FILTER" && "$GATE_FILTER" != "$gate" ]]; then
    continue
  fi
  run_gate "$gate"
done

if [[ ${#EXECUTED_GATES[@]} -eq 0 ]]; then
  echo "No gates executed." >&2
  exit 2
fi

failed_count=0
for gate in "${EXECUTED_GATES[@]}"; do
  if [[ "${STATUS_BY_GATE[$gate]}" == "FAIL" ]]; then
    failed_count=$((failed_count + 1))
  fi
done

detect_hook_drift

if [[ "$JSON_MODE" == "true" ]]; then
  printf '{\n'
  printf '  "run_id": "%s",\n' "$(json_escape "$RUN_ID")"
  printf '  "timestamp": "%s",\n' "$(json_escape "$TIMESTAMP")"
  printf '  "executed_gates": ['
  for i in "${!EXECUTED_GATES[@]}"; do
    if [[ "$i" -gt 0 ]]; then
      printf ', '
    fi
    printf '"%s"' "$(json_escape "${EXECUTED_GATES[$i]}")"
  done
  printf '],\n'
  printf '  "gates": [\n'
  for i in "${!EXECUTED_GATES[@]}"; do
    gate="${EXECUTED_GATES[$i]}"
    if [[ "${STATUS_BY_GATE[$gate]}" == "FAIL" ]]; then
      suggested_json="\"$(json_escape "${SUGGESTED[$gate]}")\""
    else
      suggested_json="null"
    fi
    printf '    {"gate":"%s","status":"%s","command":"%s","duration_ms":%s,"suggested_command":%s}' \
      "$(json_escape "$gate")" \
      "$(json_escape "${STATUS_BY_GATE[$gate]}")" \
      "$(json_escape "${COMMANDS[$gate]}")" \
      "${DURATION_BY_GATE[$gate]}" \
      "$suggested_json"
    if [[ "$i" -lt $((${#EXECUTED_GATES[@]} - 1)) ]]; then
      printf ','
    fi
    printf '\n'
  done
  printf '  ],\n'
  printf '  "hook_drift": {"detected": %s, "details": "%s", "remediation_command": "%s"},\n' \
    "$HOOK_DRIFT" \
    "$(json_escape "$HOOK_DRIFT_DETAILS")" \
    "$(json_escape "$HOOK_REMEDIATION")"
  printf '  "summary": {"total": %s, "passed": %s, "failed": %s}\n' \
    "${#EXECUTED_GATES[@]}" "$((${#EXECUTED_GATES[@]} - failed_count))" "$failed_count"
  printf '}\n'
else
  echo "== QUALITY GATE RUN =="
  echo "run_id: $RUN_ID"
  echo "timestamp: $TIMESTAMP"
  if [[ -n "$GATE_FILTER" ]]; then
    echo "mode: gate ($GATE_FILTER)"
  else
    echo "mode: full"
  fi
  echo

  if [[ "$HOOK_DRIFT" == "true" ]]; then
    echo "== HOOK DRIFT =="
    echo "status: DRIFT_DETECTED"
    echo "details: $HOOK_DRIFT_DETAILS"
    echo "next_step: Run '$HOOK_REMEDIATION' to repair security hook state."
    echo
  else
    echo "== HOOK DRIFT =="
    echo "status: OK"
    echo
  fi

  for gate in "${EXECUTED_GATES[@]}"; do
    echo "== GATE: $gate =="
    echo "command: ${COMMANDS[$gate]}"
    echo "duration_ms: ${DURATION_BY_GATE[$gate]}"
    echo "status: ${STATUS_BY_GATE[$gate]}"
    echo "output:"
    sed 's/^/  /' "${LOG_BY_GATE[$gate]}"
    if [[ "${STATUS_BY_GATE[$gate]}" == "FAIL" ]]; then
      echo "next_step: Run '${SUGGESTED[$gate]}' to reproduce and fix."
    fi
    echo
  done

  echo "== SUMMARY =="
  echo "executed_gates: ${EXECUTED_GATES[*]}"
  echo "total: ${#EXECUTED_GATES[@]}"
  echo "passed: $((${#EXECUTED_GATES[@]} - failed_count))"
  echo "failed: $failed_count"
fi

if [[ "$failed_count" -gt 0 ]]; then
  exit 1
fi

exit 0
