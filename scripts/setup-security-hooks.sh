#!/usr/bin/env bash
# Deterministic setup/refresh for security pre-commit hooks.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HOOK_FILE=".git/hooks/pre-commit"
VERSION_MARKER=".git/hooks/.viflo-pre-commit-version"

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    fail "Missing required command '$1'."
  fi
}

require_cmd pre-commit

if [[ ! -d .git ]]; then
  fail "This script must run from a git repository root."
fi

PRE_COMMIT_VERSION="$(pre-commit --version | awk '{print $2}')"
if [[ -z "${PRE_COMMIT_VERSION:-}" ]]; then
  fail "Unable to determine pre-commit version."
fi

needs_refresh=false
refresh_reasons=()

if [[ ! -f "$HOOK_FILE" ]]; then
  needs_refresh=true
  refresh_reasons+=("hook missing")
elif ! grep -qi "pre-commit" "$HOOK_FILE"; then
  needs_refresh=true
  refresh_reasons+=("hook content mismatch")
fi

if [[ -f "$VERSION_MARKER" ]]; then
  INSTALLED_VERSION="$(cat "$VERSION_MARKER" 2>/dev/null || true)"
  if [[ "$INSTALLED_VERSION" != "$PRE_COMMIT_VERSION" ]]; then
    needs_refresh=true
    refresh_reasons+=("pre-commit version drift ($INSTALLED_VERSION -> $PRE_COMMIT_VERSION)")
  fi
else
  needs_refresh=true
  refresh_reasons+=("missing version marker")
fi

if [[ "$needs_refresh" == true ]]; then
  log "Refreshing pre-commit hooks: ${refresh_reasons[*]}"
else
  log "Pre-commit hook install appears current; running deterministic refresh."
fi

pre-commit install --hook-type pre-commit --overwrite
pre-commit install-hooks

printf '%s\n' "$PRE_COMMIT_VERSION" > "$VERSION_MARKER"

if [[ ! -f "$HOOK_FILE" ]]; then
  fail "pre-commit hook was not installed at $HOOK_FILE."
fi

if ! grep -qi "pre-commit" "$HOOK_FILE"; then
  fail "Installed hook at $HOOK_FILE does not look like a pre-commit hook."
fi

log "Security hooks are installed and refreshed."
exit 0
