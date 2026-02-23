# 4. Testing & Continuous Integration

## Overview

This phase establishes the **automated verification layer** that ensures every artifact produced in Phase 3 (Implementation) meets quality, correctness, and security standards before reaching production. It defines test generation strategies, code quality gates, CI/CD pipelines, and monitoring systems that provide continuous feedback to the development loop.

**Inputs:** Working, human-reviewed code from Phase 3, with co-located or adjacent test stubs.

**Outputs:** A fully automated quality pipeline where every commit is verified, every PR is gated, and every deployment is traceable.

**Model Selection (from Phase 1):** Use **Code Execution Cheap** models (Gemini 3 Flash, GPT-5 Mini) for test generation and boilerplate quality tasks. Reserve **Code Execution Mid** models (Claude Sonnet 4.5) for complex integration test design or debugging flaky tests.

---

## 4.1 Test Strategy & Architecture

### Purpose

Define the overall testing pyramid, tooling, and organizational conventions. This section operationalizes the **Testing Plan** defined in Phase 2's `PLAN.md` (§ 3.6) — it specifies _how_ to implement the test architecture that was _designed_ during planning.

### The Testing Pyramid

Apply the standard testing pyramid. The majority of tests should be fast, cheap unit tests. Integration and E2E tests should be fewer but cover critical paths.

```
         ╱  E2E  ╲           ← Few: critical user journeys only
        ╱ Integr. ╲          ← Moderate: API + DB + Auth flows
       ╱   Unit    ╲         ← Many: business logic, utils, hooks
      ╱──────────────╲
```

### Test Tooling by Ecosystem

Select test tools based on the project's tech stack. The table below covers common ecosystems:

| Ecosystem        | Unit / Integration      | E2E              | Accessibility | Coverage      |
| ---------------- | ----------------------- | ---------------- | ------------- | ------------- |
| JS/TS (Node)     | Vitest                  | Playwright       | jest-axe      | v8 / istanbul |
| JS/TS (React)    | Vitest + Testing Lib    | Playwright       | jest-axe      | v8 / istanbul |
| JS/TS (Vue)      | Vitest + Vue Test Utils | Playwright       | jest-axe      | v8 / istanbul |
| Python (FastAPI) | pytest + httpx          | Playwright (API) | —             | coverage.py   |
| Python (Django)  | pytest-django           | Playwright       | —             | coverage.py   |
| Mobile (RN)      | Jest + Testing Lib      | Detox / Maestro  | —             | istanbul      |

### Test File Organization

Use **co-located tests** as the default convention. Tests live next to the code they verify:

```
src/
  services/
    user.service.ts
    user.service.test.ts        ← Unit test
  routes/
    users/
      route.ts
      route.test.ts             ← Integration test
tests/
  e2e/
    user-profile.spec.ts        ← E2E test (separate directory)
  fixtures/
    users.ts                    ← Shared test data
```

**Convention Rules:**

- Unit and integration tests: co-located as `<filename>.test.ts` or `test_<filename>.py`
- E2E tests: separate `tests/e2e/` directory (they test flows, not files)
- Test fixtures and factories: shared `tests/fixtures/` directory
- Mock definitions: co-located or in `tests/mocks/`

### Coverage Targets

Define minimum coverage thresholds per layer:

| Layer                     | Target | Rationale                                   |
| ------------------------- | ------ | ------------------------------------------- |
| Business logic / services | 85%    | Core value; most bugs hide here             |
| API route handlers        | 80%    | Entry points; must handle errors correctly  |
| UI components             | 70%    | Test behavior, not visual layout            |
| Utilities / helpers       | 90%    | Pure functions; easy and cheap to test      |
| Configuration / infra     | 50%    | Smoke tests; verified by CI pipeline itself |

**Important:** Coverage is a floor, not a goal. 100% coverage with bad assertions is worse than 80% coverage with meaningful tests.

---

## 4.2 AI-Assisted Test Generation

### Purpose

Leverage LLMs to generate the bulk of test boilerplate, then refine with human review. Test generation is one of the highest-ROI uses of AI agents — tests are formulaic, well-defined, and easily verified by running them.

### Model Selection for Test Generation

| Test Type          | Recommended Model Tier | Reasoning                                                     |
| ------------------ | ---------------------- | ------------------------------------------------------------- |
| Unit tests         | Code Execution Cheap   | Formulaic, one function → one test. Gemini Flash excels here. |
| Integration tests  | Code Execution Mid     | Requires understanding of request/response flows.             |
| E2E test skeletons | Code Execution Mid     | Needs understanding of UI flows and selectors.                |
| Edge case tests    | Code Execution Mid     | Requires reasoning about failure modes.                       |
| Fuzz / property    | High Performance       | Requires deep understanding of domain invariants.             |

### Test Generation Prompting Template

Every test generation prompt must include:

```
Generate: [unit test / integration test / E2E test]
For: [exact path to source file being tested]
Test file: [exact path for the test file]
Framework: [Vitest / pytest / Jest / Playwright]
Source code: [paste the function/class/module being tested]
Dependencies to mock: [list external dependencies to stub]
Test cases to cover:
  1. Happy path — [describe expected input → output]
  2. Edge case — [describe boundary conditions]
  3. Error case — [describe failure modes]
Assertions: Use [expect / assert] with specific matchers
Naming convention: [describe("ModuleName", () => { it("should ...") })]
```

### Test Quality Criteria

AI-generated tests must pass these checks before acceptance:

- [ ] **Runs green** — The test actually passes when run
- [ ] **Fails correctly** — Remove the implementation; the test should fail
- [ ] **Tests behavior, not implementation** — No assertions on internal state
- [ ] **Meaningful assertions** — No `expect(result).toBeDefined()` without further checks
- [ ] **Descriptive names** — Test name describes the expected behavior
- [ ] **Independent** — Tests don't depend on execution order
- [ ] **Deterministic** — No flakiness from timing, randomness, or shared state
- [ ] **Covers the contract** — Tests the public interface, not private methods

### Anti-Patterns in Generated Tests

| Anti-Pattern                  | Why It Fails                               | Correct Approach                                 |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------ |
| `expect(result).toBeTruthy()` | Passes on any truthy value; proves nothing | `expect(result).toEqual(expectedValue)`          |
| Testing mock return values    | Tests the mock, not the code               | Assert on the _effect_ of calling the mocked dep |
| One giant test per function   | Hard to diagnose failures                  | One behavior per test case                       |
| No negative tests             | Misses error handling paths                | Always test at least one error/edge case         |
| Snapshot tests for logic      | Brittle; break on any change               | Use snapshots for UI rendering only              |
| Hardcoded dates/times         | Flaky in different timezones / over time   | Use deterministic time mocking                   |

---

## 4.3 Local Code Quality Enforcement

### Purpose

Ensure every developer (and agent) commits code that meets project standards. Quality enforcement happens **locally before push**, catching issues before they reach CI and waste pipeline minutes.

### Linting & Formatting

Configure linting and formatting per ecosystem. The goal is **zero-config enforcement** — developers and agents should never have to think about style.

#### JavaScript / TypeScript

| Tool       | Purpose            | Config File        |
| ---------- | ------------------ | ------------------ |
| ESLint     | Code quality rules | `eslint.config.js` |
| Prettier   | Formatting         | `.prettierrc`      |
| TypeScript | Type checking      | `tsconfig.json`    |

#### Python

| Tool | Purpose              | Config File                     |
| ---- | -------------------- | ------------------------------- |
| Ruff | Linting + formatting | `ruff.toml` or `pyproject.toml` |
| mypy | Static type checking | `mypy.ini` or `pyproject.toml`  |

**Note:** Ruff replaces Black, flake8, and isort in a single tool with 10–100x faster execution. Prefer Ruff for all new Python projects.

### Pre-Commit Hooks

Use pre-commit hooks to enforce quality gates before code reaches the remote:

#### Setup with Husky (JS/TS Projects)

```bash
# Install
npx husky init

# .husky/pre-commit
npx lint-staged
```

#### Setup with pre-commit (Python Projects)

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.x
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.x.x
    hooks:
      - id: mypy
```

### Lint-Staged Configuration

Only run checks on staged files to keep commits fast:

```json
// package.json or .lintstagedrc
{
  "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
  "*.{json,md,yml}": ["prettier --write"]
}
```

### Quality Gate Checklist

Before any code is pushed:

- [ ] All lint rules pass (`eslint .` / `ruff check .`)
- [ ] All formatting is applied (`prettier --check .` / `ruff format --check .`)
- [ ] Type checking passes (`tsc --noEmit` / `mypy .`)
- [ ] Related unit tests pass (`vitest run --changed` / `pytest --last-failed`)

---

## 4.4 CI/CD Pipeline Architecture

### Purpose

Define the automated pipeline that runs on every push and PR. The CI pipeline is the **final quality gate** before code reaches production. Nothing merges without a green pipeline.

### Recommended Platform

**GitHub Actions** — free for public repos, generous free minutes for private repos, native GitHub integration for branch protection and PR checks.

### Pipeline Stages

Design the pipeline in sequential stages. Each stage must pass before the next begins:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Install  │───►│   Lint   │───►│   Build  │───►│   Test   │───►│  Deploy  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                     │
                                              ┌──────┴──────┐
                                              │  Coverage   │
                                              │  Report     │
                                              └─────────────┘
```

### Stage Definitions

#### Stage 1: Install

- Install dependencies with lockfile (`npm ci` / `pnpm install --frozen-lockfile` / `uv sync --frozen`)
- Cache dependency directories for faster subsequent runs
- Fail-fast if lockfile is out of sync

#### Stage 2: Lint & Type Check

- Run linter across all packages (`pnpm -r lint` / `ruff check .`)
- Run type checking (`pnpm -r typecheck` / `mypy .`)
- Run formatting check (`prettier --check .` / `ruff format --check .`)
- **This stage runs on all PRs and pushes**

#### Stage 3: Build

- Build all packages in dependency order (`turbo build` or equivalent)
- Verify the production build completes without errors
- Cache build outputs for downstream stages
- **This stage runs on all PRs and pushes**

#### Stage 4: Test

- Run unit tests with coverage reporting
- Run integration tests with test database (if applicable)
- Generate coverage report and fail if below threshold
- **This stage runs on all PRs and pushes**

#### Stage 5: E2E Tests

- Run Playwright / Cypress tests against the built application
- This stage is heavier; run on PRs to `main` / `develop` only, not on every push
- If using Turborepo, leverage `turbo test:e2e` with caching

#### Stage 6: Deploy

- Deploy to preview/staging on PR (Vercel preview, Railway preview)
- Deploy to production on merge to `main`
- **Only runs after all previous stages pass**

### GitHub Actions Workflow Template

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 23
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm -r lint
      - run: pnpm -r typecheck
      - run: pnpm -r build

  test:
    needs: quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 23
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm -r test -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/

  e2e:
    needs: test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 23
          cache: "pnpm"
      - run: pnpm install --frozen-lockfile
      - run: pnpm -r build
      - run: npx playwright install --with-deps
      - run: pnpm -r test:e2e
```

### Branch Protection Rules

Configure GitHub branch protection on `main` (and optionally `develop`):

- [ ] Require status checks to pass before merging (`quality`, `test`)
- [ ] Require branches to be up-to-date before merging
- [ ] Require at least 1 PR review
- [ ] Dismiss stale reviews on new pushes
- [ ] Do not allow bypassing the above rules

---

## 4.5 Test Coverage Monitoring

### Purpose

Track test coverage over time to ensure the codebase doesn't regress. Coverage monitoring is a **guard rail**, not a performance metric — the goal is preventing decline, not gamifying a number.

### Coverage Collection

#### JavaScript / TypeScript

```json
// vitest.config.ts → test.coverage
{
  "provider": "v8",
  "reporter": ["text", "json-summary", "lcov"],
  "thresholds": {
    "lines": 80,
    "branches": 75,
    "functions": 80,
    "statements": 80
  }
}
```

#### Python

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Coverage Enforcement in CI

1. **Fail the build** if coverage drops below the configured threshold
2. **Report coverage diff** on PRs (use a GitHub Action or bot)
3. **Track trends** — use a service like Codecov or Coveralls, or store JSON summaries as CI artifacts

### Ratcheting Strategy

Instead of setting a fixed global target, use **ratcheting** — the coverage threshold is always set to the current coverage level. Coverage can only go up:

1. Run coverage, record the current value
2. Set the threshold to `current_value - 1%` (small buffer for refactoring)
3. On every CI run, fail if coverage drops below this threshold
4. Periodically update the threshold to reflect the new baseline

---

## 4.6 Performance & Cost Monitoring

### Purpose

Track the operational costs and performance of the AI-assisted development workflow. This data feeds directly into Phase 5 (Iteration & Continuous Improvement) for ongoing optimization.

### Metrics to Track

#### Agent Performance Metrics

| Metric                   | Definition                                         | Target |
| ------------------------ | -------------------------------------------------- | ------ |
| First-pass acceptance    | % of AI-generated code that passes human review    | > 70%  |
| Refinement rounds        | Average prompt iterations before acceptance        | < 2.5  |
| Test generation accuracy | % of AI-generated tests that run green immediately | > 85%  |
| Build break rate         | % of commits that break CI                         | < 5%   |
| Flaky test rate          | % of test runs with non-deterministic failures     | < 2%   |

#### Cost Metrics

| Metric               | How to Track                                          | Review Cadence |
| -------------------- | ----------------------------------------------------- | -------------- |
| Token usage per task | Log API usage per agent session                       | Per sprint     |
| Cost per feature     | Aggregate token cost across all tasks for a feature   | Per feature    |
| Model cost breakdown | Cost distribution across model tiers (cheap/mid/high) | Monthly        |
| CI minutes consumed  | GitHub Actions usage dashboard                        | Monthly        |

#### Latency Metrics

| Metric               | Definition                                  | Target          |
| -------------------- | ------------------------------------------- | --------------- |
| Agent response time  | Time from prompt to first output            | < 30s for cheap |
| CI pipeline duration | Total time from push to green/red           | < 10 min        |
| Time to review       | Time from PR creation to first human review | < 4 hours       |
| MTTR                 | Mean time to resolve a broken build         | < 30 min        |

### Monitoring Implementation

#### Option A: Lightweight (Spreadsheet / JSON)

For small teams or early-stage projects:

- Log metrics to a JSON file or spreadsheet after each sprint
- Review trends in sprint retrospectives
- Adjust model selection and agent routing based on data

#### Option B: Automated Dashboard

For larger teams or production projects:

- Use an observability tool (Grafana, Datadog, or a simple Next.js dashboard)
- Instrument agent calls to log token usage, latency, and success/failure
- Set up alerts for anomalous cost spikes or coverage drops
- Publish weekly automated reports

### Cost Optimization Triggers

Take action when any of these thresholds are crossed:

| Trigger                            | Action                                            |
| ---------------------------------- | ------------------------------------------------- |
| Monthly API spend > budget ceiling | Shift more tasks to cheaper models or open-source |
| First-pass acceptance < 60%        | Improve prompting templates or switch models      |
| CI pipeline > 15 min               | Add caching, parallelize stages, reduce E2E scope |
| Flaky test rate > 5%               | Quarantine flaky tests, fix root causes           |
| Coverage dropping for 3+ sprints   | Mandate test-first development for new features   |

---

## 4.7 Handling CI Failures & Flaky Tests

### Purpose

Define procedures for when the pipeline breaks. Unresolved CI failures block the entire team; flaky tests erode trust in the pipeline.

### CI Failure Protocol

1. **Build break on `main`** — Highest priority. Revert the offending commit or hotfix within 30 minutes.
2. **Build break on feature branch** — The PR author is responsible. Fix before requesting review.
3. **Intermittent failure** — Investigate for flakiness. If confirmed flaky, quarantine (see below).

### Flaky Test Management

```
Flaky test identified
  ├── Is the flakiness reproducible locally?
  │     ├── Yes → Fix the root cause (timing, shared state, ordering)
  │     └── No → Likely CI environment issue (resource limits, parallelism)
  │
  ├── Can it be fixed within 1 hour?
  │     ├── Yes → Fix immediately
  │     └── No → Quarantine
  │
  └── Quarantine process:
        1. Mark test with @flaky / @skip annotation
        2. Create a tracked issue with reproduction steps
        3. Move to a separate CI job (non-blocking)
        4. Fix within the current sprint
        5. Un-quarantine and return to blocking pipeline
```

### Common Flakiness Root Causes

| Root Cause                 | Solution                                              |
| -------------------------- | ----------------------------------------------------- |
| Timing / race conditions   | Use explicit waits, deterministic ordering            |
| Shared test state          | Isolate tests; reset state in beforeEach/setUp        |
| Date/time sensitivity      | Mock the clock; use frozen timestamps                 |
| Network calls in tests     | Mock all external calls (MSW, responses, httpx mocks) |
| Parallel test interference | Run conflicting tests sequentially                    |
| Database state leaks       | Use transactions with rollback, or per-test databases |

---

## 4.8 Done Criteria

Phase 4 is complete when all of the following are true:

### Infrastructure

- [ ] **Linting & formatting** are configured and enforced via pre-commit hooks
- [ ] **CI pipeline** runs on every push and PR (lint → build → test)
- [ ] **Branch protection** is enabled on `main` with required status checks
- [ ] **Coverage reporting** is integrated into CI and PRs

### Test Coverage

- [ ] All features from `PLAN.md` have corresponding unit tests
- [ ] Critical paths have integration tests (API + DB + Auth)
- [ ] At least 3 E2E tests cover the core user journeys
- [ ] Coverage meets or exceeds the per-layer targets (§ 4.1)

### Monitoring

- [ ] Agent performance metrics are being collected (§ 4.6)
- [ ] Cost tracking is in place (token usage, CI minutes)
- [ ] Flaky test management process is documented and followed

### Quality

- [ ] All tests pass deterministically in CI (zero flaky tests in blocking pipeline)
- [ ] The pipeline completes in under 15 minutes
- [ ] No critical or major lint violations remain
- [ ] Ready to proceed to Phase 5 (Iteration & Continuous Improvement)
