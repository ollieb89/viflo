#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(pwd)}"

require_file() {
  local file="$1"
  if [[ ! -f "${ROOT}/${file}" ]]; then
    echo "missing required file: ${file}" >&2
    exit 1
  fi
}

prompts_dir="${ROOT}/prompts"
if [[ ! -d "${prompts_dir}" ]]; then
  echo "missing prompts directory: prompts/" >&2
  exit 1
fi

for md in "${prompts_dir}"/*.md; do
  [[ -e "${md}" ]] || continue
  toml="${md%.md}.toml"
  if [[ ! -f "${toml}" ]]; then
    echo "missing matching .toml for ${md}" >&2
    exit 1
  fi
done

for toml in "${prompts_dir}"/*.toml; do
  [[ -e "${toml}" ]] || continue
  md="${toml%.toml}.md"
  if [[ ! -f "${md}" ]]; then
    echo "missing matching .md for ${toml}" >&2
    exit 1
  fi

  for key in \
    'name = ' \
    'version = ' \
    'description = ' \
    'command = ' \
    'input_mode = ' \
    '[tooling]' \
    '[validation]'; do
    if ! rg -q "^${key}" "${toml}"; then
      echo "missing required key '${key}' in ${toml}" >&2
      exit 1
    fi
  done
done

require_file "prompts/sc-reflect.md"
require_file "prompts/sc-reflect.toml"
require_file "commands/sg/reflect.md"
require_file "features/sc/commands/research.md"
require_file "features/sc/agents/deep-research-agent.md"
require_file "features/sc/modes/MODE_DeepResearch.md"
require_file "features/sc/core/RESEARCH_CONFIG.md"
require_file "INDEX.md"

echo "SC prompt validation passed."
