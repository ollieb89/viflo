Completed /sc:reflect implementation bundle in viflo repo.

Implemented assets:
- prompts/sc-reflect.md + prompts/sc-reflect.toml
- commands/sg/reflect.md
- features/sc/{commands/research.md,agents/deep-research-agent.md,modes/MODE_DeepResearch.md,core/RESEARCH_CONFIG.md}
- INDEX.md entry for /sc:reflect
- scripts/validate-sc-prompts.sh
- scripts/benchmark-sc-reflect.sh
- test: bin/lib/__tests__/sc-prompts-scripts.test.js

Validation status:
- pnpm test:cli: pass (58 tests)
- validate-sc-prompts.sh: pass
- benchmark-sc-reflect.sh: pass, core_p95_ms=10 (<=200), checkpoint_p95_ms=10 (<=1000)

Notable constraint:
- Existing worktree edits in .planning/config.json and .serena/project.yml were intentionally left untouched.