# 2. Planning & Architectural Design

## Overview

Before a single line of code is generated, a high-reasoning model establishes a granular system design. This phase translates project requirements into a structured `PLAN.md` that downstream agents and developers can execute without ambiguity.

**Model Selection (from Phase 1):** Use a **Proprietary High Performance** model (Gemini 3 Pro, Claude Opus 4.5, or GPT-5.2) for planning. These models excel at architectural reasoning, long-context analysis, and structured output.

---

## Step 1: Create PLAN.md

Establish a structured planning file in the repository root.

### Template Structure

```markdown
# [Project Name] — System Design

## 1. Project Overview
- One-paragraph summary of the application
- Target users and core value proposition
- Key constraints (budget, timeline, compliance)

## 2. Tech Stack
<!-- Reference the default stack; only deviate with justification -->

## 3. Architecture
- High-level system diagram (monorepo layout, service boundaries)
- Data flow between frontend, API, and database

## 4. Database Schema
- Entity definitions with relationships
- Index strategy
- Migration approach

## 5. API Routes
- Grouped by resource/feature
- HTTP method, path, request/response shape

## 6. Authentication & Authorization
- Auth provider and flow
- Role-based access control (if applicable)
- Token strategy

## 7. Error Handling Strategy
- Client-side error boundaries
- API error response format
- Logging and monitoring approach

## 8. Testing Plan
- Unit, integration, and E2E test scope
- Test tooling
- Coverage targets

## 9. Deployment & CI/CD
- Hosting target
- Pipeline stages
- Environment strategy (dev, staging, prod)
```

### File Convention

- Save to repository root as `PLAN.md`
- Keep under version control
- Update as the design evolves during iterative refinement

---

## Step 2: Provide Context to the Planning Model

Feed the planning model a comprehensive context prompt covering four categories.

### 2.1 Tech Stack Context

Provide the **default stack** so the model generates code-aligned designs:

```yaml
Frontend:
  framework: Next.js 16 (App Router)
  language: TypeScript 5.7+
  styling: Tailwind CSS v4
  state: React 19 Actions / Server Components
  bundler: Turbopack

Backend:
  runtime: Node.js 23
  framework: Next.js API Routes / Hono (for Edge)
  validation: Zod / TypeBox

Database:
  primary: PostgreSQL
  orm: Prisma / Drizzle
  hosting: Supabase / Neon

Auth:
  provider: Auth.js (v5) / Clerk

Monorepo:
  tool: Turborepo 2.0
```

Only deviate from defaults when a specific requirement demands it (e.g., real-time → Supabase Realtime, payments → Stripe, email → Resend).

### 2.2 Infrastructure Constraints

Specify:

-   **Hosting**: Vercel (serverless) vs self-hosted vs edge
-   **Database hosting**: Supabase or Neon (serverless PostgreSQL)
-   **Region / latency requirements**: geographic proximity to users
-   **Scaling expectations**: expected concurrent users, data volume

### 2.3 Budget & Latency Constraints

Specify:

-   **LLM budget ceiling**: monthly API spend cap
-   **Model latency tolerance**: acceptable response time for AI-generated artifacts
-   **Infrastructure budget**: hosting tier, database plan, storage limits
-   **Development timeline**: sprint length, milestone dates

### 2.4 Authentication & Security Requirements

Specify:

-   **Auth flow**: OAuth, email/password, magic link, or SSO
-   **Provider choice**: Auth.js v5 or Clerk (from default stack)
-   **Authorization model**: role-based (RBAC), attribute-based (ABAC), or row-level security (RLS)
-   **Compliance requirements**: GDPR, HIPAA, SOC 2 (if applicable)
-   **Session strategy**: JWT vs server-side sessions

---

## Step 3: Generate Complete System Design

The planning model should produce each of the following artifacts. Below is what "complete" looks like for each.

### 3.1 API Routes

Group by feature/resource. Include:

-   HTTP method and path
-   Request body / query params (with Zod types)
-   Response shape
-   Auth requirement (public, authenticated, admin)
-   Rate limiting (if applicable)

**Format example:**

| Method | Path              | Auth     | Description          |
|--------|-------------------|----------|----------------------|
| GET    | `/api/users/:id`  | Auth     | Fetch user profile   |
| POST   | `/api/users`      | Public   | Create new user      |
| PATCH  | `/api/users/:id`  | Auth     | Update user profile  |
| DELETE | `/api/users/:id`  | Admin    | Delete user account  |

For Next.js API Routes, specify whether each route uses the Edge Runtime or Node.js runtime.

### 3.2 Database Schema

Define entities with:

-   Table name, columns, types
-   Primary keys, foreign keys, unique constraints
-   Indexes (specify type: btree, gin, etc.)
-   Relations (one-to-one, one-to-many, many-to-many)

Use Prisma schema syntax or Drizzle table definitions depending on the chosen ORM. Include the migration strategy (Prisma Migrate or Drizzle Kit).

### 3.3 Authentication Model

Document:

-   Chosen provider (Auth.js v5 or Clerk)
-   Sign-up / sign-in flows
-   Session management (JWT or database sessions)
-   Protected route patterns (Next.js middleware)
-   Role definitions and permission matrix

### 3.4 Monorepo & Service Boundaries

Using Turborepo 2.0, define:

-   `apps/` — deployable applications (e.g., `apps/web`, `apps/api`)
-   `packages/` — shared code (e.g., `packages/ui`, `packages/db`, `packages/shared`)
-   Dependency graph between packages
-   Task definitions in `turbo.json` (build, test, lint, typecheck)

If the project includes a Python backend (FastAPI), define it as a separate service outside the Turborepo workspace with its own dependency management (uv or Pixi).

### 3.5 Error Handling Strategy

-   **Client-side**: React Error Boundaries, toast notifications
-   **API layer**: Standardized error response format
-   **Validation**: Zod schema validation at API boundaries
-   **Logging**: structured logging approach (console in dev, JSON in prod)

Standardized API error format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": []
  }
}
```

### 3.6 Testing Plan

| Layer       | Tool          | Scope                              |
|-------------|---------------|-------------------------------------|
| Unit        | Vitest        | Business logic, utilities, hooks    |
| Integration | Vitest + MSW  | API handlers with mocked externals  |
| E2E         | Playwright    | Critical user flows                 |
| Accessibility | jest-axe    | Component a11y compliance           |

Define:

-   Coverage target (e.g., 80% for business logic)
-   Test file location convention (`__tests__/` or co-located `.test.ts`)
-   CI test execution order

---

## Step 4: Iterative Refinement

A plan is not done on the first pass. Refine until it meets all three criteria.

### Refinement Criteria

**Specific** — Every design element references:
-   Exact file paths (`apps/web/src/app/api/users/route.ts`)
-   Concrete types (TypeScript interfaces, Zod schemas)
-   Named dependencies with versions

**Actionable** — Each section can be directly converted into a task for Phase 3 (Implementation) without requiring additional design decisions.

**Granular** — Complex features are decomposed into single-responsibility units that can be implemented independently.

### Refinement Checklist

- [ ] All API routes have defined request/response shapes
- [ ] Database schema covers all entities with relations and indexes
- [ ] Auth flow is documented end-to-end (sign-up → session → protected route)
- [ ] Monorepo structure is defined with clear package boundaries
- [ ] Error handling is standardized across all layers
- [ ] Testing plan covers unit, integration, and E2E
- [ ] No ambiguous references ("add validation" → specify what, where, how)
- [ ] No technologies outside the default stack unless justified

### Refinement Process

1.  **First pass** — Generate initial design with a High Performance model
2.  **Self-review** — Check against the refinement checklist above
3.  **Gap analysis** — Identify missing sections or vague descriptions
4.  **Targeted refinement** — Use a Code Execution model (e.g., Gemini 3 Flash, Claude Sonnet 4.5) for quick targeted fixes rather than regenerating the full plan
5.  **Human review** — Developer validates the plan against project requirements
6.  **Final lock** — Commit the finalized `PLAN.md` before proceeding to Phase 3

### Done Criteria

The plan is ready for implementation when:

-   Every section of the template (Step 1) is fully populated
-   A developer can read any section and begin coding without asking questions
-   The plan has been reviewed and approved by the team lead or project owner
