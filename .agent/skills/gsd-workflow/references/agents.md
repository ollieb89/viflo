# GSD Agent Definitions

Specialized agents for the GSD workflow. Kimi spawns these as subagents for specific tasks.

## gsd-project-researcher

**Purpose**: Research domain before project initialization

**When to spawn**: During `gsd init` when user wants ecosystem research

**Input**: User's project idea, tech preferences
**Output**: Research summary covering:

- Stack recommendations
- Feature comparisons
- Architecture patterns
- Common pitfalls

**Prompt**: See original at `get-shit-done/agents/gsd-project-researcher.md`

## gsd-roadmapper

**Purpose**: Create phased roadmap from requirements

**When to spawn**: After requirements extraction

**Input**: REQUIREMENTS.md
**Output**: ROADMAP.md with phases mapped to requirements

**Prompt**: See original at `get-shit-done/agents/gsd-roadmapper.md`

## gsd-phase-researcher

**Purpose**: Research implementation approach for a phase

**When to spawn**: During `gsd plan <phase>`

**Input**: Phase description, CONTEXT.md
**Output**: Research report with:

- Implementation patterns
- Library recommendations
- Code examples
- Architecture decisions

**Prompt**: See original at `get-shit-done/agents/gsd-phase-researcher.md`

## gsd-planner

**Purpose**: Create atomic task plans

**When to spawn**: After phase research

**Input**: Phase research, CONTEXT.md
**Output**: PLAN.md files (2-3 per phase) with XML task structure

**Guidelines**:

- Each plan < 150 lines
- Tasks are atomic and independently executable
- Include verification steps
- Mark manual vs auto tasks

**Prompt**: See original at `get-shit-done/agents/gsd-planner.md`

## gsd-plan-checker

**Purpose**: Verify plans achieve phase goals

**When to spawn**: After planning, before execution

**Input**: PLAN.md, phase requirements
**Output**: Validation report (pass/needs-revision)

**Prompt**: See original at `get-shit-done/agents/gsd-plan-checker.md`

## gsd-executor

**Purpose**: Execute a single plan

**When to spawn**: During `gsd execute <phase>` for each plan

**Input**: PLAN.md, fresh context
**Output**: SUMMARY.md with what was done

**Guidelines**:

- Fresh context per plan (200k tokens available)
- Execute auto tasks
- Guide user through manual tasks
- Commit after each task

**Prompt**: See original at `get-shit-done/agents/gsd-executor.md`

## gsd-verifier

**Purpose**: Verify deliverables against requirements

**When to spawn**: During `gsd verify <phase>`

**Input**: Phase requirements, codebase
**Output**: Verification report with gaps

**Prompt**: See original at `get-shit-done/agents/gsd-verifier.md`

## gsd-debugger

**Purpose**: Systematic debugging with persistent state

**When to spawn**: When verification finds issues

**Input**: Error description, codebase
**Output**: Root cause analysis and fix plan

**Prompt**: See original at `get-shit-done/agents/gsd-debugger.md`

## gsd-codebase-mapper

**Purpose**: Analyze existing codebase

**When to spawn**: `gsd init --existing` or `gsd map-codebase`

**Input**: Codebase files
**Output**: Codebase analysis covering:

- Tech stack
- Architecture
- Conventions
- Concerns

**Prompt**: See original at `get-shit-done/agents/gsd-codebase-mapper.md`
