#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"
ITERATIONS="${ITERATIONS:-25}"
CORE_THRESHOLD_MS="${CORE_THRESHOLD_MS:-200}"
CHECKPOINT_THRESHOLD_MS="${CHECKPOINT_THRESHOLD_MS:-1000}"
MCP_PROBE_THRESHOLD_MS="${MCP_PROBE_THRESHOLD_MS:-1000}"
MCP_PROBE_CMD="${MCP_PROBE_CMD:-}"
ALLOW_FLAKY_PROBES="${ALLOW_FLAKY_PROBES:-}"

core_samples=()
checkpoint_samples=()
mcp_samples=()

measure_ms() {
  local start end
  start="$(date +%s%3N)"
  "$@" >/dev/null 2>&1
  end="$(date +%s%3N)"
  echo $((end - start))
}

p95() {
  # shellcheck disable=SC2206
  local arr=($*)
  local count="${#arr[@]}"
  if [[ "${count}" -eq 0 ]]; then
    echo "0"
    return
  fi
  IFS=$'\n' arr=($(printf '%s\n' "${arr[@]}" | sort -n))
  unset IFS
  local idx=$(( (95 * count + 99) / 100 - 1 ))
  if [[ "${idx}" -lt 0 ]]; then
    idx=0
  fi
  if [[ "${idx}" -ge "${count}" ]]; then
    idx=$((count - 1))
  fi
  echo "${arr[$idx]}"
}

for _ in $(seq 1 "${ITERATIONS}"); do
  core_ms="$(measure_ms bash -lc "rg -q '^## Behavioral Flow' '${ROOT}/prompts/sc-reflect.md' && rg -q '^\\[validation\\]' '${ROOT}/prompts/sc-reflect.toml'")"
  checkpoint_ms="$(measure_ms bash -lc "mkdir -p '${ROOT}/.tmp-benchmark' && printf 'checkpoint\n' > '${ROOT}/.tmp-benchmark/reflect-checkpoint.tmp' && rg -q 'think_about_whether_you_are_done' '${ROOT}/features/sc/core/RESEARCH_CONFIG.md'")"
  core_samples+=("${core_ms}")
  checkpoint_samples+=("${checkpoint_ms}")
  if [[ -n "${MCP_PROBE_CMD}" ]]; then
    if [[ -n "${CI:-}" && -z "${ALLOW_FLAKY_PROBES}" ]]; then
      continue
    fi
    mcp_ms="$(measure_ms bash -lc "${MCP_PROBE_CMD}")"
    mcp_samples+=("${mcp_ms}")
  fi
done

core_p95="$(p95 "${core_samples[*]}")"
checkpoint_p95="$(p95 "${checkpoint_samples[*]}")"

echo "core_p95_ms=${core_p95} threshold=${CORE_THRESHOLD_MS}"
echo "checkpoint_p95_ms=${checkpoint_p95} threshold=${CHECKPOINT_THRESHOLD_MS}"
if [[ "${#mcp_samples[@]}" -gt 0 ]]; then
  mcp_p95="$(p95 "${mcp_samples[*]}")"
  echo "mcp_probe_p95_ms=${mcp_p95} threshold=${MCP_PROBE_THRESHOLD_MS}"
elif [[ -n "${MCP_PROBE_CMD}" ]]; then
  echo "mcp_probe=skipped (CI deterministic mode; set ALLOW_FLAKY_PROBES=1 to enable)"
fi

rm -rf "${ROOT}/.tmp-benchmark"

if (( core_p95 > CORE_THRESHOLD_MS )); then
  echo "core reflection p95 exceeds threshold" >&2
  exit 1
fi

if (( checkpoint_p95 > CHECKPOINT_THRESHOLD_MS )); then
  echo "checkpoint path p95 exceeds threshold" >&2
  exit 1
fi

if [[ "${#mcp_samples[@]}" -gt 0 ]] && (( mcp_p95 > MCP_PROBE_THRESHOLD_MS )); then
  echo "mcp probe p95 exceeds threshold" >&2
  exit 1
fi

echo "SC reflect benchmark passed."
