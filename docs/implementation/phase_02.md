# Phase 2 Implementation Plan: Detailed Planning and Architectural Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish the detailed architectural blueprint (`PLAN.md`) and tasks backlog (`TASKS.md`) before execution, focusing on rigorous planning using reasoning models to refine design and catch errors early.

**Architecture:**

- **Planning-First:** Create immutable architectural design before writing code.
- **Blueprint:** Define Schema, API Surface, and Constraints in `PLAN.md`.
- **Validation:** Perform "Mental Compile" and referential integrity checks on design.
- **Handoff:** Break down design into atomic, dependency-aware tasks in `TASKS.md`.

**Tech Stack:** Markdown, Mermaid.js, Zod, SQL (RLS Policies), Prisma/Drizzle Schema.

---

### Task 1: Context Aggregation & Technology Stack Definition

**Files:**

- Create: `docs/planning/PLAN.md`

**Step 1: Create Planning Directory**

Ensure the directory exists.

```bash
mkdir -p docs/planning
```

**Step 2: Initialize PLAN.md**

Create the initial skeleton with Goal, Tech Stack, and System Constraints.

```markdown
# docs/planning/PLAN.md

# Architectural Blueprint

## Goal

[Insert detailed goal from PRD]

## Tech Stack

- Frontend: Next.js 16, TypeScript 5.7+, Tailwind v4
- Backend: Supabase (PostgreSQL), Next.js API Routes (or Python FastAPI if specified)
- Database: PostgreSQL with pgvector
- Auth: Supabase Auth / Clerk
- Deployment: Vercel / Docker

## System Constraints

### Infrastructure

- Deployment Target: Vercel
- Database: Managed PostgreSQL (Supabase)

### Budget

- Latency Target: < 200ms API response
- Token Budget: Cost-Efficient Execution (Gemini Flash)

### Security

- Auth: HttpOnly Cookies / JWT
- RLS: Enabled by default on all tables
```

**Step 3: Commit**

```bash
git add docs/planning/PLAN.md
git commit -m "docs: initialize PLAN.md with constraints and tech stack"
```

---

### Task 2: Schema & API Surface Definition (The "Blueprint")

**Files:**

- Modify: `docs/planning/PLAN.md`

**Step 1: Define Database Schema**

Add Entity-Relationship Diagram (ERD) and Schema definitions.

```markdown
## Database Schema

### ERD (Mermaid)

\`\`\`mermaid
erDiagram
USER ||--o{ POST : writes
USER {
string id PK
string email
}
POST {
string id PK
string content
string user_id FK
}
\`\`\`

### Schema Definitions (Prisma/SQL)

[Insert specific schema code here]
```

**Step 2: Define API Surface**

Add detailed API routes with request/response types.

```markdown
## API Surface

### Endpoints

#### POST /api/v1/resource

- **Auth**: Required (Role: User)
- **Input (Zod)**:
  \`\`\`typescript
  z.object({
  data: z.string().min(1)
  })
  \`\`\`
- **Response**:
  \`\`\`json
  { "id": "uuid", "status": "success" }
  \`\`\`
```

**Step 3: Commit**

```bash
git add docs/planning/PLAN.md
git commit -m "docs: add schema and API definitions to PLAN.md"
```

---

### Task 3: Authentication & Authorization Strategy Design

**Files:**

- Modify: `docs/planning/PLAN.md`

**Step 1: Define Auth Middleware Strategy**

Specify how requests are authenticated.

```markdown
## Security & Authorization

### Middleware Strategy

- Use Next.js Middleware to validate session tokens.
- Public Routes: `/login`, `/register`, `/api/public/*`
- Protected Routes: `/dashboard/*`, `/api/protected/*`
```

**Step 2: Define Row Level Security (RLS) Policies**

Explicitly define SQL policies for data access.

```markdown
### RLS Policies

#### Table: users

- **Select**: Users can select their own data (`auth.uid() = id`).
- **Update**: Users can update their own data.

#### Table: posts

- **Select**: Public (if published) or Owner.
- **Insert**: Authenticated users only.
```

**Step 3: Commit**

```bash
git add docs/planning/PLAN.md
git commit -m "docs: add auth strategy and RLS policies to PLAN.md"
```

---

### Task 4: Task Decomposition (The "Agent Handoff")

**Files:**

- Create: `docs/planning/TASKS.md`

**Step 1: Create TASKS.md**

Break down the architecture into atomic implementation tasks (ACID-T).

```markdown
# docs/planning/TASKS.md

# Implementation Tasks

## Phase 3: Execution Backlog

- [ ] **Task 3.1: Monorepo Scaffold**
  - Context: `PLAN.md#Tech Stack`
  - Action: Initialize Turbo/Nx, setup TSConfig, ESLint.

- [ ] **Task 3.2: Database Setup**
  - Context: `PLAN.md#Database Schema`
  - Action: Write Prisma schema, run migration, generate client.

- [ ] **Task 3.3: Auth Integration**
  - Context: `PLAN.md#Security`
  - Action: Setup Clerk/Supabase provider, implement Middleware.

- [ ] **Task 3.4: API Route - User Profile**
  - Context: `PLAN.md#API Surface`
  - Action: Implement GET /api/me with Zod validation.
```

**Step 2: Sorting**

Ensure tasks are sorted topologically (dependencies first).

**Step 3: Commit**

```bash
git add docs/planning/TASKS.md
git commit -m "docs: create TASKS.md with atomic implementation backlog"
```
