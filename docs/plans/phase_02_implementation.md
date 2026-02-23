# Implementation Plan: Phase 2 - Architectural Design & Adaptable Flow

## Goal
Fully implement the "Detailed Planning and Architectural Design" phase (Phase 2) for the current project, while establishing an **adaptable and configurable flow** (as a reusable Skill) that can be applied to any future project.

## Current Status
- **Phase 2 Document**: `docs/implementation/phase_02.md` exists.
- **Implementation Status**: **NOT STARTED**.
  - `docs/planning/` directory does not exist.
  - `docs/planning/PLAN.md` does not exist.
  - `docs/planning/TASKS.md` does not exist.

## Strategy: "Skill-First" Architecture
Instead of manually creating single-use documents, we will build an **`architectural-design` Skill**. This skill will encapuslate the Phase 2 methodology, providing templates and logic to bootstrap architectural planning for *any* project.

## Proposed Changes

### 1. Create `architectural-design` Skill
**Location**: `.agent/skills/architectural-design/`

- **`SKILL.md`**: Defines the "Planning-First" methodology.
- **`templates/PLAN.md`**: Jinja2-style template for the Architectural Blueprint.
  - Sections: Goal, Tech Stack, System Constraints (Infra, Budget, Security).
- **`templates/TASKS.md`**: Template for the Task Backlog.
- **`scripts/init_architecture.py`**: A Python script to:
  1.  Ask/Infer Project Name and Goal.
  2.  Select Tech Stack (from presets or custom).
  3.  Generate `docs/planning/PLAN.md` from template.
  4.  Generate `docs/planning/TASKS.md` from template.

### 2. Implement Phase 2 for *This* Project
Use the newly created skill to generate the artifacts for the "Universal Agentic Development Environment" project.

1.  **Run Skill**: `python .agent/skills/architectural-design/scripts/init_architecture.py`
2.  **Configure**:
    -   **Goal**: "Create a Universal Agentic Development Environment..."
    -   **Tech Stack**: Next.js 16, Python/FastAPI (as per Phase 2 doc), PGVector.
3.  **Verify**: Ensure `docs/planning/PLAN.md` matches the specific requirements in `phase_02.md` (lines 17-67 + rest).

## Implementation Steps

### Step 1: Scaffold Skill
- Create directory structure for `.agent/skills/architectural-design`.
- Write `SKILL.md` with strict "Planning-First" rules.

### Step 2: Create Templates
- **`PLAN.md`**:
    ```markdown
    # Architectural Blueprint: {{ project_name }}

    ## Goal
    {{ goal }}

    ## Tech Stack
    {{ tech_stack_list }}

    ## System Constraints
    {{ constraints }}
    ```
- **`TASKS.md`**: Standard ACID-T task tracking template.

### Step 3: Develop Automation Script
- Write `init_architecture.py` to handle user input and template rendering.
- Ensure it respects existing files (safe overwrite or skip).

### Step 4: Execute & Verify
- Run the script for the current repository.
- Commit the generated `docs/planning/*` files.
- Verify against `docs/implementation/phase_02.md` checklist.

## Verification Plan of the Plan
- **Automated**: Run `ls -R docs/planning` to confirm file creation.
- **Manual**: Review `PLAN.md` content to ensure it matches the specific constraints of Phase 2 (e.g., "Latnecy < 200ms", "Gemini Flash").

## User Review Required
- **Adaptability**: Does the "Skill" approach satisfy the requirement for an "adaptable and configurable flow"?
- **Tech Stack**: Confirming the tech stack from Phase 2 is still accurate (Next.js 16, Supabase, etc.).
