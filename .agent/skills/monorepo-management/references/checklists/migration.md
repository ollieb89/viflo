# Multi-Repo to Monorepo Migration Checklist

Extracted from [SKILL.md](../SKILL.md)

## Pre-Migration Planning

- [ ] Audit existing repositories for dependencies and conflicts
- [ ] Choose monorepo tool (Turborepo recommended for most, Nx for complex needs)
- [ ] Plan directory structure (apps/, packages/, tools/)
- [ ] Identify shared code candidates for extraction
- [ ] Set up CI/CD strategy for monorepo workflows

## Repository Setup

- [ ] Create new monorepo root with pnpm workspaces
- [ ] Configure root package.json with workspace definitions
- [ ] Set up shared configuration packages (TypeScript, ESLint, Prettier)
- [ ] Initialize git repository with proper .gitignore

## Code Migration

- [ ] Migrate applications to apps/ directory
- [ ] Extract shared UI components to packages/ui/
- [ ] Extract shared utilities to packages/utils/
- [ ] Extract shared types to packages/types/
- [ ] Update all import paths to use workspace protocol
- [ ] Consolidate duplicate dependencies across packages

## Build & Tooling Configuration

- [ ] Configure turbo.json with proper task pipeline
- [ ] Set up build caching with correct inputs/outputs
- [ ] Configure remote caching (optional but recommended)
- [ ] Set up shared ESLint and TypeScript configurations
- [ ] Configure changesets for versioning (if publishing packages)

## CI/CD Migration

- [ ] Update GitHub Actions for monorepo structure
- [ ] Configure affected/changed detection for efficient builds
- [ ] Set up proper dependency installation with pnpm
- [ ] Configure deployment for affected apps only
- [ ] Add monorepo-aware test runs

## Post-Migration

- [ ] Verify all applications build and run correctly
- [ ] Test workspace linking and dependency resolution
- [ ] Update documentation and README files
- [ ] Train team on new monorepo workflows
- [ ] Archive old repositories after transition period

## Common Migration Pitfalls

- **Circular Dependencies**: Check for A depends on B, B depends on A patterns
- **Phantom Dependencies**: Ensure all used dependencies are in package.json
- **Incorrect Cache Inputs**: Verify Turborepo inputs capture all relevant files
- **Over-Sharing**: Don't share code that should remain package-specific
- **Under-Sharing**: Consolidate genuinely duplicated code
