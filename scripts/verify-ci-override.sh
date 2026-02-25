#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/verify-ci-override.sh [options]

Validate audited ci-override usage on pull requests.

Options:
  --event-path PATH       GitHub event payload path (default: $GITHUB_EVENT_PATH)
  --repo OWNER/REPO       Repository slug (default: $GITHUB_REPOSITORY)
  --token TOKEN           GitHub token (default: $GITHUB_TOKEN)
  --api-url URL           GitHub API URL (default: $GITHUB_API_URL or https://api.github.com)
  --team-slug SLUG        Authorized team slug (default: $CI_OVERRIDE_AUTHORIZED_TEAM or maintainers)
  --help                  Show this help and exit
EOF
}

EVENT_PATH="${GITHUB_EVENT_PATH:-}"
REPO="${GITHUB_REPOSITORY:-}"
TOKEN="${GITHUB_TOKEN:-}"
API_URL="${GITHUB_API_URL:-https://api.github.com}"
TEAM_SLUG="${CI_OVERRIDE_AUTHORIZED_TEAM:-maintainers}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --event-path)
      EVENT_PATH="${2:-}"
      shift 2
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    --token)
      TOKEN="${2:-}"
      shift 2
      ;;
    --api-url)
      API_URL="${2:-}"
      shift 2
      ;;
    --team-slug)
      TEAM_SLUG="${2:-}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command '$1' is not available." >&2
    exit 2
  fi
}

require_cmd jq
require_cmd curl

if [[ -z "$EVENT_PATH" || ! -f "$EVENT_PATH" ]]; then
  echo "ERROR: event payload file not found. Set --event-path or GITHUB_EVENT_PATH." >&2
  exit 2
fi

if [[ -z "$REPO" || "$REPO" != */* ]]; then
  echo "ERROR: invalid repository slug. Set --repo or GITHUB_REPOSITORY (OWNER/REPO)." >&2
  exit 2
fi

if [[ -z "$TOKEN" ]]; then
  echo "ERROR: missing GitHub token. Set --token or GITHUB_TOKEN." >&2
  exit 1
fi

if [[ -z "$TEAM_SLUG" ]]; then
  echo "ERROR: authorized team slug is empty." >&2
  exit 1
fi

OWNER="${REPO%%/*}"
PR_NUMBER="$(jq -r '.pull_request.number // empty' "$EVENT_PATH")"

if [[ -z "$PR_NUMBER" ]]; then
  echo "ERROR: pull_request.number missing in event payload." >&2
  exit 1
fi

mapfile -t LABELS < <(jq -r '.pull_request.labels[]?.name // empty' "$EVENT_PATH")

has_override_label=false
for label in "${LABELS[@]}"; do
  if [[ "$label" == "ci-override" ]]; then
    has_override_label=true
    break
  fi
done

if [[ "$has_override_label" != "true" ]]; then
  echo "No ci-override label present; skipping audit."
  exit 0
fi

echo "ci-override label detected on PR #$PR_NUMBER. Running audited override checks."

pr_body="$(jq -r '.pull_request.body // ""' "$EVENT_PATH")"
event_sender="$(jq -r '.sender.login // empty' "$EVENT_PATH")"
label_applier="$event_sender"
action="$(jq -r '.action // empty' "$EVENT_PATH")"

api_get() {
  local path="$1"
  local code
  local body_file

  body_file="$(mktemp)"
  code="$(curl -sS -L \
    -H "Authorization: Bearer $TOKEN" \
    -H "Accept: application/vnd.github+json" \
    -w "%{http_code}" \
    "$API_URL$path" \
    -o "$body_file")"

  if [[ "$code" -lt 200 || "$code" -ge 300 ]]; then
    echo "ERROR: GitHub API request failed ($code) for $path" >&2
    cat "$body_file" >&2 || true
    rm -f "$body_file"
    exit 1
  fi

  cat "$body_file"
  rm -f "$body_file"
}

issue_comments_json="$(api_get "/repos/$REPO/issues/$PR_NUMBER/comments?per_page=100")"
reviews_json="$(api_get "/repos/$REPO/pulls/$PR_NUMBER/reviews?per_page=100")"

issue_comment_text="$(echo "$issue_comments_json" | jq -r '.[].body // ""')"

evidence_text="$(printf '%s\n%s' "$pr_body" "$issue_comment_text")"

required_field() {
  local field_regex="$1"
  local field_name="$2"

  if ! printf '%s\n' "$evidence_text" | grep -Eiq "$field_regex[[:space:]]*[:\-][[:space:]]*[^[:space:]].+"; then
    echo "ERROR: Missing or empty override evidence field: $field_name" >&2
    exit 1
  fi
}

required_field 'reason' 'reason'
required_field 'scope' 'scope'
required_field 'tracking( link)?' 'tracking link'
required_field 'expiry' 'expiry'
required_field 'approver evidence' 'approver evidence'

scope_line="$(printf '%s\n' "$evidence_text" | grep -Ei 'scope[[:space:]]*[:\-]' | head -n1 || true)"
scope_value="$(printf '%s' "$scope_line" | sed -E 's/^[[:space:]]*[^: -]+([[:space:]][^: -]+)*[[:space:]]*[:\-][[:space:]]*//')"

if ! printf '%s\n' "$scope_value" | grep -Eiq '(lint|typecheck|test|build)'; then
  echo "ERROR: Scope must include at least one gate: lint|typecheck|test|build." >&2
  exit 1
fi

if ! printf '%s\n' "$scope_value" | grep -Eiq '(skip|fail)'; then
  echo "ERROR: Scope must include condition: skip or fail." >&2
  exit 1
fi

tracking_line="$(printf '%s\n' "$evidence_text" | grep -Ei 'tracking( link)?[[:space:]]*[:\-]' | head -n1 || true)"
if ! printf '%s\n' "$tracking_line" | grep -Eiq 'https?://'; then
  echo "ERROR: Tracking link must include an http(s) URL." >&2
  exit 1
fi

approver_line="$(printf '%s\n' "$evidence_text" | grep -Ei 'approver evidence[[:space:]]*[:\-]' | head -n1 || true)"
approver_login="$(printf '%s\n' "$approver_line" | grep -Eo '@[A-Za-z0-9-]+' | head -n1 | sed 's/^@//' || true)"

if [[ -z "$approver_login" ]]; then
  echo "ERROR: Approver evidence must include a GitHub username mention (for example @maintainer)." >&2
  exit 1
fi

if [[ "$action" != "labeled" && -z "$label_applier" ]]; then
  label_applier="$(echo "$issue_comments_json" | jq -r '.[] | select((.body // "") | test("ci-override"; "i")) | .user.login // empty' | head -n1)"
fi

if [[ -z "$label_applier" ]]; then
  echo "ERROR: Unable to determine ci-override label applier from event/comment context." >&2
  exit 1
fi

check_team_membership() {
  local username="$1"
  local membership_json
  local state

  membership_json="$(api_get "/orgs/$OWNER/teams/$TEAM_SLUG/memberships/$username")"
  state="$(echo "$membership_json" | jq -r '.state // empty')"
  if [[ "$state" != "active" ]]; then
    echo "ERROR: User @$username is not an active member of @$OWNER/$TEAM_SLUG." >&2
    exit 1
  fi
}

check_team_membership "$label_applier"
check_team_membership "$approver_login"

approved_review_login="$(echo "$reviews_json" | jq -r '.[] | select(.state == "APPROVED") | .user.login // empty' | sort -u | head -n1)"
if [[ -z "$approved_review_login" ]]; then
  echo "ERROR: Override requires at least one APPROVED review." >&2
  exit 1
fi

check_team_membership "$approved_review_login"

echo "Override audit checks passed."
echo "Label applier: @$label_applier"
echo "Approver evidence: @$approver_login"
echo "Approved reviewer: @$approved_review_login"
