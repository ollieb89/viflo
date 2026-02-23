---
name: architectural-design
description: Standardized workflow for creating Detailed Implementation Plans and Architectural Blueprints (PLAN.md) and Task Backlogs (TASKS.md).
triggers:
  - Creating PLAN.md for a new project
  - Generating implementation blueprints
  - Creating task backlogs (TASKS.md)
  - Planning-first development setup
---

# Architectural Design Skill

This skill enforces a "Planning-First" development methodology by providing templates and automation for creating rigorous architectural documentation.

## Core Philosophy
1.  **Plan Before Code**: No implementation begins without a `PLAN.md`.
2.  **Granularity**: Tasks must be atomic (ACID-T).
3.  **Constraints**: Technical and budget constraints are defined upfront.

## Usage

Run the initialization script to bootstrap the planning documents for a new project or phase:

```bash
python .agent/skills/architectural-design/scripts/init_architecture.py
```

## Outputs

The skill generates:
-   `docs/planning/PLAN.md`: The Architectural Blueprint (Goal, Tech Stack, Constraints, Schema, API).
-   `docs/planning/TASKS.md`: The Implementation Backlog (Context, Action, Verification).

## Template Structure

### PLAN.md
-   **Goal**: Clear objective.
-   **Tech Stack**: Frontend, Backend, Database, Auth, etc.
-   **System Constraints**: Infrastructure, Budget, Security.
-   **Database Schema**: ERD and DDL.
-   **API Surface**: Routes, Inputs (Zod), Outputs.
-   **Security**: Middleware, RLS.

### TASKS.md
-   **Context**: Reference to specific `PLAN.md` section.
-   **Action**: Atomic implementation step.
-   **Verification**: How to confirm success.
