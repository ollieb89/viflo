# Phase 20: Gate Enforcement Hardening - Research

**Researched:** 2026-02-25
**Domain:** GitHub Actions merge gates, local CI parity commands, and pre-commit secret enforcement
**Confidence:** HIGH

---

## User Constraints (from CONTEXT.md)

### Locked Decisions

- Enforcement runs on both PR and push.
- PR checks run on every PR update (`opened`, `synchronize`, `reopened`) including draft PRs.
- PR checks on draft PRs are informative; merge-required enforcement applies once PR is marked Ready for review.
- Push workflow runs on `main` and `release/*` only as a fast pre-merge safety net.
- If `hotfix/*` is introduced later, it should follow the same push-enforcement policy as `release/*`.
- Skipped checks do not satisfy merge requirements by default.
- Merge blocking keys off individual required checks for `lint`, `typecheck`, `test`, and `build`.
- Combined status is acceptable for visibility but cannot replace individual required checks.
- Override authority is restricted to an authorized team (for example `maintainers` / `release-managers`) via audited override label `ci-override`.
- Override evidence in PR is mandatory: reason, scope (gate(s) + skip/fail), tracking link, expiry, and approver evidence.
- Provide one canonical full parity command path plus optional per-gate commands.
- Full parity execution runs all gates, reports all failures, and exits non-zero.
- Output is sectioned by gate with clear pass/fail status for scanability and deterministic CI mirroring.
- Output supports default plain text plus optional machine-readable JSON mode (for tooling/editor integrations).
- On failure, include concrete actionable next-step hints per gate (example fix command).
- Do not auto-execute fixes.
- Pre-commit secret scanning hard-blocks on any finding.
- Blocking applies immediately for all contributors (no grace commit path).
- False-positive/exception handling uses auditable baseline/allowlist updates with explicit PR rationale.
- Baseline/allowlist files should be owned by security/maintainer CODEOWNERS; normal CODEOWNERS review is sufficient.
- Hook setup uses both auto-attempt and explicit re-run paths.
- If setup fails locally, onboarding continues with loud warning and exact remediation command/docs pointer.
- Setup command auto-refreshes hooks when drift/version mismatch is detected.
- Parity command checks hook drift on every run and reports it.
- Canonical setup docs live in both README and CONTRIBUTING, cross-linked.

### Claude's Discretion

- Exact command names and script naming for full parity vs per-gate entrypoints.
- Exact warning text and remediation copy shown when hook bootstrap fails.
- Exact audited metadata shape for override label usage and where it is recorded.

### Deferred Ideas (OUT OF SCOPE)

- Per-gate override labels are deferred; start with single `ci-override` and revisit only if ambiguity/abuse appears.

---

## Phase Requirements

| ID      | Description                                                             | Research Support                                                                                                            |
| ------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| GATE-01 | Push and PR workflows block merge on lint/typecheck/test/build failures | Use required status checks tied to a deterministic `quality-gates` workflow job set; avoid optional/skipped required checks |
| GATE-02 | Local command path reproduces CI pass/fail                              | Create one canonical script consumed by both CI and local `pnpm` script; per-gate scripts call the same underlying commands |
| SEC-01  | Commits blocked on secret findings (`gitleaks` + `detect-secrets`)      | Enforce via pre-commit hooks with baseline-aware detect-secrets and hard-fail behavior                                      |
| SEC-02  | One bootstrap command installs/refreshes security hooks                 | Keep `./scripts/setup-dev.sh` as bootstrap and add explicit refresh command path + drift-aware reinstall                    |

---

## Summary

Phase 20 should standardize one authoritative quality-gate execution path and use it in both CI and local workflows. The repository already has a CI workflow and pre-commit config, but they are not yet aligned to the phase constraints: branch coverage is limited to `main`, quality gates are split across jobs without a single canonical local mirror command, and override/audit semantics for skipped checks are not formalized.

For merge enforcement, GitHub required status checks and branch/ruleset protections should be the primary control plane. Required checks are strict: if a required check never reports success (including many skipped/misconfigured states), merge is blocked. This aligns with your fail-closed stance and means workflow trigger/path logic must be designed carefully so required checks always produce a definitive status for scoped changes.

For security hooks, pre-commit with `gitleaks` and `detect-secrets` is already in place and should remain the standard stack. Keep blocking behavior hard by default with no grace commit path, and require CODEOWNERS-routed review for baseline edits with explicit PR rationale. Bootstrap should be dual-path: auto-attempt during setup and explicit refresh command for deterministic repair, while parity runs detect/report hook drift.

**Primary recommendation:** implement a single canonical `quality-gate` entrypoint as the source of truth for lint/typecheck/test/build, invoke it from both CI and local `pnpm run` commands, enforce individual required checks on `main` + `release/*` PR/push coverage (with draft PRs reporting but not merge-blocking until Ready), and add audited override mechanics (`ci-override`) with required PR evidence fields.

---

## Standard Stack

### Core

| Library/Platform               | Version                                | Purpose                               | Why Standard                                                  |
| ------------------------------ | -------------------------------------- | ------------------------------------- | ------------------------------------------------------------- |
| GitHub Actions                 | Current hosted platform                | CI execution and required checks      | Native merge enforcement with required status checks/rulesets |
| `actions/checkout`             | `v4`                                   | Checkout source in CI jobs            | Stable official action already used in repo                   |
| `actions/setup-node`           | `v4`                                   | Node runtime + pnpm cache integration | Standard Node setup pattern already used                      |
| `pnpm/action-setup`            | `v4`                                   | pnpm installation in CI               | Standard pnpm action already used                             |
| pre-commit                     | 4.x                                    | Local commit-time hook orchestration  | Canonical multi-hook manager with reproducible config         |
| gitleaks pre-commit hook       | repo `gitleaks/gitleaks`, rev pinned   | Secret scanning on staged changes     | High-signal detector, already integrated                      |
| detect-secrets pre-commit hook | repo `Yelp/detect-secrets`, rev pinned | Baseline-aware secret scanning        | Supports audit/update workflow and baseline gating            |

### Supporting

| Tool                   | Version    | Purpose                          | When to Use                                               |
| ---------------------- | ---------- | -------------------------------- | --------------------------------------------------------- |
| `.gitleaks.toml`       | repo-local | Policy tuning and allow-rules    | Keep false positives manageable without disabling scanner |
| `.secrets.baseline`    | repo-local | Existing-known-findings baseline | Allow rollout that blocks new leaks only                  |
| `scripts/setup-dev.sh` | repo-local | Bootstrap + hook installation    | Canonical contributor onboarding and refresh path         |

### Alternatives Considered

| Instead of                 | Could Use                 | Tradeoff                                                                        |
| -------------------------- | ------------------------- | ------------------------------------------------------------------------------- |
| pre-commit hooks           | Husky-only shell hooks    | Pre-commit provides stronger cross-language hook ecosystem + baseline patterns  |
| Required checks only on PR | Push + PR checks          | PR-only saves CI minutes but reduces early failure signal on protected branches |
| Fail-open skipped checks   | Maintainer override label | Override label keeps explicit, auditable exception path                         |

---

## Architecture Patterns

### Recommended Project Structure

```text
.github/workflows/
  ci.yml                     # quality gates workflow (required checks)
  ci-override-audit.yml      # optional explicit override/audit gate
scripts/
  quality-gate.sh            # canonical full parity command (CI + local)
  quality-gate-lint.sh       # optional thin wrappers (or pnpm scripts only)
  quality-gate-typecheck.sh
  quality-gate-test.sh
  quality-gate-build.sh
  setup-dev.sh               # bootstrap/install/refresh hooks
.pre-commit-config.yaml
.gitleaks.toml
.secrets.baseline
README.md
CONTRIBUTING.md
```

### Pattern 1: Single Source of Truth Gate Runner

**What:** One script runs lint/typecheck/test/build in deterministic order, prints sectioned pass/fail, returns non-zero if any gate fails.

**When to use:** Always. CI jobs and local command both call this same script or same command set.

**Example:**

```bash
#!/usr/bin/env bash
set -euo pipefail

status=0
run_gate() {
  local name="$1"
  local cmd="$2"
  echo "== [${name}] =="
  if eval "$cmd"; then
    echo "PASS: ${name}"
  else
    echo "FAIL: ${name}"
    echo "Hint: run '${cmd}' locally to reproduce"
    status=1
  fi
  echo
}

run_gate "lint" "pnpm run lint"
run_gate "type-check" "pnpm run type-check"
run_gate "test" "pnpm run test"
run_gate "build" "pnpm run build"

exit $status
```

### Pattern 2: Required-Check-Compatible Workflow Triggering

**What:** CI triggers cover required branch targets (`main`, `release/*`) for both push and PR. Avoid path filters that can leave required checks unresolved for merge.

**When to use:** For all merge-blocking gates.

**Example:**

```yaml
on:
  push:
    branches: [main, "release/*"]
  pull_request:
    branches: [main, "release/*"]
  merge_group:
```

### Pattern 3: Audited Override Label Gate

**What:** Keep normal required checks strict; if a check is intentionally bypassed, require explicit authorized-team-applied label (`ci-override`) and required evidence fields in PR.

**When to use:** Exception-only path for skipped/non-applicable checks.

**Implementation shape (recommended):**

- Add lightweight workflow/job that validates label presence + authorized-team authority + required evidence fields.
- Treat this job as required only when skip/override path is invoked.
- Store audit details in PR timeline/comments and merge commit history.

### Pattern 4: Hook Bootstrap + Refresh

**What:** Setup script performs `pre-commit install` and can refresh hooks on drift (`pre-commit install --install-hooks` and `pre-commit autoupdate` via maintainer workflow, not implicit contributor side effects).

**When to use:** Onboarding and explicit refresh command.

---

## Don't Hand-Roll

| Problem                | Don't Build                          | Use Instead                              | Why                                                    |
| ---------------------- | ------------------------------------ | ---------------------------------------- | ------------------------------------------------------ |
| Secret scanning engine | Custom regex scanner script          | `gitleaks` + `detect-secrets` hooks      | Mature detection rules, known baseline/audit workflows |
| Hook dispatcher        | Custom `.git/hooks/pre-commit` logic | `pre-commit` framework                   | Reproducible hook env and pinned revisions             |
| Merge policy logic     | Ad-hoc human convention              | GitHub required checks + branch/rulesets | Enforceable and auditable at platform level            |
| Local-vs-CI parity     | Separate command implementations     | Single shared quality-gate runner        | Prevents drift and “works on my machine” failures      |

**Key insight:** enforce policy at platform boundaries (GitHub checks + pre-commit) and keep command execution centralized to avoid duplicated logic drift.

---

## Common Pitfalls

### Pitfall 1: Required checks + skipped workflows deadlock merges

**What goes wrong:** PR cannot merge because required check never reports success (often due to path filters or mismatched trigger scope).
**Why it happens:** Required checks are strict; skipped/pending states may not satisfy merge requirements.
**How to avoid:** Keep required gate workflow broadly triggered for protected branches and ensure each required job always emits a terminal status.
**Warning signs:** PR shows expected check as pending/skipped forever.

### Pitfall 2: Local parity command diverges from CI over time

**What goes wrong:** Local command passes while CI fails (or vice versa).
**Why it happens:** Different command sets or flags between scripts and workflow YAML.
**How to avoid:** CI runs the same script/entrypoint as local canonical command.
**Warning signs:** Frequent “cannot reproduce CI failure locally” reports.

### Pitfall 3: Baseline updates silently weaken security gate

**What goes wrong:** Secrets stop being flagged due to broad baseline edits.
**Why it happens:** Baseline changed without focused review or rationale.
**How to avoid:** Require CODEOWNERS review + explicit PR explanation for baseline/allowlist changes.
**Warning signs:** Large baseline diffs with no incident/false-positive justification.

### Pitfall 4: Hook setup failures block adoption

**What goes wrong:** Contributors bypass tooling after failed setup attempt.
**Why it happens:** Setup scripts hard-fail without remediation path or retry guidance.
**How to avoid:** Continue onboarding with clear warning and exact remediation command; provide explicit refresh command.
**Warning signs:** Repeated PRs from contributors missing hook-generated checks.

### Pitfall 5: Override label becomes an implicit bypass norm

**What goes wrong:** `ci-override` used routinely rather than exceptionally.
**Why it happens:** Missing approval controls and audit visibility.
**How to avoid:** Restrict label application to authorized team, require rationale template with scope/tracking/expiry, and periodically review override frequency.
**Warning signs:** Growing number of merged PRs with override label and minimal explanation.

---

## Code Examples

### Example: CI job calling canonical parity script

```yaml
jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: ./scripts/quality-gate.sh
```

### Example: Pre-commit config (baseline-aware detect-secrets)

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
```

### Example: pnpm scripts for full parity + per-gate iteration

```json
{
  "scripts": {
    "quality-gate": "./scripts/quality-gate.sh",
    "gate:lint": "pnpm run lint",
    "gate:typecheck": "pnpm run type-check",
    "gate:test": "pnpm run test",
    "gate:build": "pnpm run build"
  }
}
```

---

## Open Questions (for planner to resolve)

1. Should required checks be implemented via branch protection only, rulesets only, or both (migration-safe path)?
2. Where should override-audit logic live: dedicated workflow, protected GitHub app check, or both?
3. Should draft-PR enforcement transition be handled purely by GitHub branch requirements or by conditional job logic?
4. Do we keep `scripts/precommit-secrets.sh` as supplemental/manual command or retire it in favor of pre-commit-only path?

---

## Sources

### Repository Evidence (HIGH)

- `/.github/workflows/ci.yml` (current branch triggers and gate jobs)
- `/.pre-commit-config.yaml` (gitleaks + detect-secrets hooks)
- `/scripts/setup-dev.sh` (hook bootstrap behavior)
- `/scripts/precommit-secrets.sh` (staged gitleaks helper)
- `/package.json` (existing scripts and commands)
- `/.planning/REQUIREMENTS.md` (GATE-01/02, SEC-01/02 mapping)
- `/.planning/phases/20-gate-enforcement-hardening/20-CONTEXT.md` (locked user decisions)

### External References (HIGH/MEDIUM)

- GitHub Docs: About protected branches and required status checks
  - https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Docs: About rulesets
  - https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets
- GitHub Docs: Events that trigger workflows (`push`, `pull_request`, `merge_group`)
  - https://docs.github.com/actions/using-workflows/events-that-trigger-workflows
- pre-commit official docs
  - https://pre-commit.com/
- gitleaks repository and pre-commit hook usage
  - https://github.com/gitleaks/gitleaks
- detect-secrets repository and baseline workflow
  - https://github.com/Yelp/detect-secrets

---

**Valid until:** 2026-03-25 (recheck GitHub rulesets/required-check behavior and hook revisions before implementation if delayed)
