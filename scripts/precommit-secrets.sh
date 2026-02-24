#!/usr/bin/env bash
set -euo pipefail

if [[ "${SKIP_GITLEAKS:-}" == "1" ]]; then
  echo "SKIP: gitleaks check bypassed via environment variable."
  exit 0
fi

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "ERROR: gitleaks is not installed. Install from https://github.com/gitleaks/gitleaks and retry." >&2
  exit 1
fi

gitleaks protect --staged --config .gitleaks.toml --redact --verbose
