/sc:reflect completion checkpoint after CI-required-checks work.

Completed scope:
- Added package scripts: validate:sc-prompts, bench:sc-reflect
- Added CI jobs: sc-prompts-validate, sc-reflect-benchmark
- build job now depends on both checks
- Added deterministic CI behavior for MCP probe in benchmark script (skip in CI unless ALLOW_FLAKY_PROBES is set)

Validation evidence:
- pnpm run validate:sc-prompts: PASS
- pnpm run bench:sc-reflect: PASS (core_p95_ms=11 <=200, checkpoint_p95_ms=10 <=1000)
- pnpm test:cli: PASS (58/58 tests)

Open operational step:
- GitHub branch protection/ruleset must mark sc-prompts-validate and sc-reflect-benchmark as required status checks (settings-side action).

Notes:
- Existing unrelated local modifications in .planning/config.json and .serena/project.yml remain untouched by design.