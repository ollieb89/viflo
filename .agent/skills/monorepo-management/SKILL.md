---
name: monorepo-management
description: Master monorepo management with Turborepo, Nx, and pnpm workspaces to build efficient, scalable multi-package repositories with optimized builds and dependency management. Use when setting up monorepos, optimizing builds, or managing shared dependencies.
triggers:
  - Setting up a monorepo
  - Configuring Turborepo or Nx
  - Managing shared dependencies
  - Optimizing build pipelines
  - Sharing code across packages
  - Managing pnpm workspaces
---

# Monorepo Management

Build efficient, scalable monorepos that enable code sharing, consistent tooling, and atomic changes across multiple packages and applications.

## When to Use This Skill

- Setting up new monorepo projects
- Migrating from multi-repo to monorepo
- Optimizing build and test performance
- Managing shared dependencies
- Implementing code sharing strategies
- Setting up CI/CD for monorepos
- Versioning and publishing packages
- Debugging monorepo-specific issues

## Core Concepts

### 1. Why Monorepos?

**Advantages:**

- Shared code and dependencies
- Atomic commits across projects
- Consistent tooling and standards
- Easier refactoring
- Simplified dependency management
- Better code visibility

**Challenges:**

- Build performance at scale
- CI/CD complexity
- Access control
- Large Git repository

### 2. Monorepo Tools Comparison

| Tool                | Best For           | Complexity | Features                                      |
| ------------------- | ------------------ | ---------- | --------------------------------------------- |
| **Turborepo**       | Most projects      | Low        | Task pipelines, remote caching, great DX      |
| **Nx**              | Enterprise/complex | High       | Graph visualization, plugins, code generators |
| **pnpm workspaces** | Package management | Low        | Efficient disk usage, workspace protocol      |

See the [reference guides](./references/guides/) for detailed setup instructions.

## Directory Structure Best Practices

```
my-monorepo/
├── apps/                  # Applications
│   ├── web/              # Next.js web app
│   └── api/              # Backend API
├── packages/             # Shared packages
│   ├── ui/               # Shared UI components
│   ├── utils/            # Shared utilities
│   ├── types/            # Shared TypeScript types
│   ├── tsconfig/         # Shared TS configs
│   └── config/           # Shared ESLint/Prettier configs
├── tools/                # Build tools and scripts
├── pnpm-workspace.yaml   # Workspace configuration
├── turbo.json           # Build orchestration
└── package.json         # Root package.json
```

## Shared Configurations

### TypeScript Configuration

```json
// packages/tsconfig/base.json
{
  "compilerOptions": {
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "declaration": true
  },
  "exclude": ["node_modules"]
}

// packages/tsconfig/react.json
{
  "extends": "./base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}

// apps/web/tsconfig.json
{
  "extends": "@repo/tsconfig/react.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### ESLint Configuration

```javascript
// packages/config/eslint-preset.js
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier",
  ],
  plugins: ["@typescript-eslint", "react", "react-hooks"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: {
      version: "detect",
    },
  },
  rules: {
    "@typescript-eslint/no-unused-vars": "error",
    "react/react-in-jsx-scope": "off",
  },
};

// apps/web/.eslintrc.js
module.exports = {
  extends: ["@repo/config/eslint-preset"],
  rules: {
    // App-specific rules
  },
};
```

## Code Sharing Patterns

### Pattern 1: Shared UI Components

```typescript
// packages/ui/src/button.tsx
import * as React from 'react';

export interface ButtonProps {
  variant?: 'primary' | 'secondary';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ variant = 'primary', children, onClick }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

// packages/ui/src/index.ts
export { Button, type ButtonProps } from './button';
export { Input, type InputProps } from './input';

// apps/web/src/app.tsx
import { Button } from '@repo/ui';

export function App() {
  return <Button variant="primary">Click me</Button>;
}
```

### Pattern 2: Shared Utilities

```typescript
// packages/utils/src/string.ts
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.slice(0, length) + "..." : str;
}

// packages/utils/src/index.ts
export * from "./string";
export * from "./array";
export * from "./date";

// Usage in apps
import { capitalize, truncate } from "@repo/utils";
```

### Pattern 3: Shared Types

```typescript
// packages/types/src/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user";
}

export interface CreateUserInput {
  email: string;
  name: string;
  password: string;
}

// Used in both frontend and backend
import type { User, CreateUserInput } from "@repo/types";
```

## CI/CD Considerations

Key principles for monorepo CI/CD:

1. **Affected Detection**: Only build/test changed packages and their dependents
2. **Caching**: Leverage remote caching to speed up builds
3. **Parallelization**: Run independent tasks in parallel
4. **Workspace-aware**: Use pnpm filters and workspace commands

Example GitHub Actions structure:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0 # For affected commands

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v3
        with:
          node-version: 18
          cache: "pnpm"

      - run: pnpm install --frozen-lockfile
      - run: pnpm turbo run build test lint type-check
```

## Best Practices

1. **Consistent Versioning**: Lock dependency versions across workspace
2. **Shared Configs**: Centralize ESLint, TypeScript, Prettier configs
3. **Dependency Graph**: Keep it acyclic, avoid circular dependencies
4. **Cache Effectively**: Configure inputs/outputs correctly in build tool
5. **Type Safety**: Share types between frontend/backend
6. **Testing Strategy**: Unit tests in packages, E2E in apps
7. **Documentation**: README in each package
8. **Release Strategy**: Use changesets for versioning

## Common Pitfalls

- **Circular Dependencies**: A depends on B, B depends on A
- **Phantom Dependencies**: Using deps not in package.json
- **Incorrect Cache Inputs**: Missing files in build tool inputs
- **Over-Sharing**: Sharing code that should be separate
- **Under-Sharing**: Duplicating code across packages
- **Large Monorepos**: Without proper tooling, builds slow down

## Publishing Packages

```bash
# Using Changesets
pnpm add -Dw @changesets/cli
pnpm changeset init

# Create changeset
pnpm changeset

# Version packages
pnpm changeset version

# Publish
pnpm changeset publish
```

```yaml
# .github/workflows/release.yml
- name: Create Release Pull Request or Publish
  uses: changesets/action@v1
  with:
    publish: pnpm release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## Resources

### Setup Guides

- **[Turborepo Setup Guide](./references/guides/turborepo-setup.md)** - Comprehensive Turborepo configuration and caching
- **[Nx Setup Guide](./references/guides/nx-setup.md)** - Nx monorepo patterns and task running
- **[pnpm Workspaces Guide](./references/guides/pnpm-workspaces.md)** - pnpm workspace features and dependency management

### Checklists

- **[Migration Checklist](./references/checklists/migration.md)** - Multi-repo to monorepo migration steps

### Scripts

- `scripts/dependency-graph.ts` - Visualize package dependencies
