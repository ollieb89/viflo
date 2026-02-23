# Phase 6: Test Suite - Context

**Gathered:** 2026-02-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Create `apps/web/` as a minimal TypeScript package with Vitest test suite. The package will contain utility functions for validating viflo metadata (skill frontmatter, plan files) and a coverage ratchet script that enforces coverage thresholds.

This is a documentation/tooling monorepo, so `apps/web/` will be a lightweight utilities package rather than a full web application. The key is demonstrating the testing pattern (Vitest + coverage ratchet) that viflo recommends.

</domain>

<decisions>
## Implementation Decisions

### Test Framework
- **Vitest** as the test runner (standard in viflo's frontend-dev-guidelines skill)
- Tests co-located with source files (`*.test.ts` pattern)
- Coverage via `@vitest/coverage-v8`

### Package Structure
- `apps/web/` — New directory for the utilities package
- `apps/web/src/` — Source files with utility functions
- `apps/web/src/validation/` — Skill metadata validation utilities
- `apps/web/src/parsing/` — Plan file parsing utilities
- `apps/web/package.json` — Package config with Vitest scripts
- `apps/web/vitest.config.ts` — Vitest configuration

### Utility Functions to Test
1. `validateSkillFrontmatter()` — Parse and validate SKILL.md YAML frontmatter
2. `parsePlanFile()` — Parse PLAN.md XML structure
3. `extractTasks()` — Extract tasks from plan files

### Coverage Ratchet
- Custom script: `scripts/coverage-ratchet.ts`
- Stores baseline in `.coverage/baseline.json`
- Fails if coverage decreases from baseline
- Command: `pnpm run test:coverage:ratchet`

### CI Integration
- Update root `package.json` test script to run `pnpm --filter web test`
- Coverage check runs in CI after tests
- Failing tests or coverage regression fails the pipeline

</decisions>

<specifics>
## Specific Ideas

Test examples:

```typescript
// validateSkillFrontmatter.test.ts
expect(validateSkillFrontmatter('---\nname: test\n---')).toBeValid();
expect(validateSkillFrontmatter('no frontmatter')).toHaveError('missing');
```

Coverage ratchet workflow:
1. Run tests with coverage
2. Compare against `.coverage/baseline.json`
3. If coverage >= baseline → pass, update baseline
4. If coverage < baseline → fail with message

</specifics>

<deferred>
## Deferred Ideas

- Full web application (unnecessary for tooling repo)
- E2E tests (Playwright) — out of scope, covered in skills
- Integration tests against live services — not applicable

</deferred>

---

*Phase: 06-test-suite*
*Context gathered: 2026-02-23*
