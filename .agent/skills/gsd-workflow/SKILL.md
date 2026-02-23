---
name: gsd-workflow
description: Guide for using the Get Shit Done (GSD) spec-driven development methodology with Kimi CLI. Use when the user wants to implement structured, phase-based development with proper planning, execution, and verification. Triggers on phrases like "get shit done", "gsd", "spec-driven development", "plan phase", "execute phase", "new project with gsd", or when the user needs systematic project planning with PROJECT.md, REQUIREMENTS.md, ROADMAP.md, and PLAN.md artifacts.
---

# GSD Workflow

Guide for implementing the Get Shit Done (GSD) methodology — a spec-driven development system that solves context rot through structured planning, execution, and verification.

## Core Philosophy

GSD gives Kimi the context it needs to do reliable work:

1. **Planning-First**: No code without a pre-approved PLAN.md
2. **Context Engineering**: Structured artifacts (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, PLAN.md) keep quality high
3. **Fresh Context Per Task**: Each plan executes in isolation, preventing context degradation
4. **Atomic Commits**: Every task gets its own commit for clean history

## Workflow Overview

```
new-project → discuss-phase → plan-phase → execute-phase → verify-work → (repeat)
```

## Commands

### Initialization

| Command | Purpose |
|---------|---------|
| `python3 scripts/init_gsd.py [--dir DIR]` | Initialize new project with PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md |
| `python3 scripts/init_gsd.py --existing` | Initialize GSD in existing codebase (runs codebase mapping first) |

### Phase Workflow

These are conceptual commands. Kimi implements them by:

| Command | What Kimi Does |
|---------|----------------|
| `gsd discuss <phase>` | Kimi asks questions, captures decisions in `{phase}-CONTEXT.md` |
| `gsd plan <phase>` | Kimi researches, creates `{phase}-{N}-PLAN.md` files with XML structure |
| `gsd execute <phase>` | Kimi executes plans in waves, commits per task |
| `gsd verify <phase>` | Kimi runs checks, creates `{phase}-UAT.md` with verification results |

### Utility

| Command | Purpose |
|---------|---------|
| `python3 scripts/status.py [--dir DIR]` | Show current progress and next steps |
| `python3 scripts/quick_task.py "task"` | Ad-hoc task with GSD guarantees (no full planning) |

## Artifacts

| File | Purpose | Location |
|------|---------|----------|
| `PROJECT.md` | Project vision, goals, constraints | `.planning/` |
| `REQUIREMENTS.md` | Scoped v1/v2/out-of-scope requirements | `.planning/` |
| `ROADMAP.md` | Phases mapped to requirements | `.planning/` |
| `STATE.md` | Decisions, blockers, session memory | `.planning/` |
| `{phase}-CONTEXT.md` | Implementation decisions per phase | `.planning/` |
| `{phase}-{N}-PLAN.md` | Atomic task plans with XML structure | `.planning/` |
| `{phase}-{N}-SUMMARY.md` | Execution results per plan | `.planning/` |

## Plan XML Structure

Every plan uses structured XML optimized for AI execution:

```xml
<plan phase="1" plan="1">
  <overview>
    <phase_name>User Authentication</phase_name>
    <goal>Implement login/signup with email and OAuth</goal>
  </overview>
  
  <dependencies>
    <complete>Phase 0: Database Setup</complete>
  </dependencies>
  
  <tasks>
    <task type="auto" priority="1">
      <name>Create user model with Prisma</name>
      <files>prisma/schema.prisma</files>
      <action>
        Add User model with email, password_hash, oauth_provider, 
        oauth_id fields. Include timestamps.
      </action>
      <verify>npx prisma validate passes</verify>
      <done>User model exists with all required fields</done>
    </task>
    
    <task type="manual" priority="1">
      <name>Run database migration</name>
      <action>Run prisma migrate dev to apply schema changes</action>
      <verify>Migration file created successfully</verify>
    </task>
  </tasks>
</plan>
```

## Task Types

- **`type="auto"`**: Kimi executes automatically
- **`type="manual"`**: User executes (database migrations, external setup)

## Phase Execution: Waves

Plans execute in parallel "waves" based on dependencies:

```
Wave 1: Independent tasks (parallel)
Wave 2: Tasks depending on Wave 1 (parallel)
Wave 3: Tasks depending on Wave 2
```

This maximizes parallelization while respecting dependencies.

## Size Limits

Keep artifacts under these limits to maintain AI quality:

| Artifact | Max Size |
|----------|----------|
| PROJECT.md | 500 lines |
| REQUIREMENTS.md | 300 lines |
| ROADMAP.md | 200 lines |
| PLAN.md | 150 lines |
| Individual task | 50 lines |

## Quick Reference

### Initialize New Project

```bash
# Interactive initialization
python3 .agent/skills/gsd-workflow/scripts/init_gsd.py

# For specific directory
python3 .agent/skills/gsd-workflow/scripts/init_gsd.py --dir ./my-project
```

### Full Phase Cycle

Tell Kimi:

```
"GSD discuss phase 1"     → Kimi asks questions, creates 1-CONTEXT.md
"GSD plan phase 1"        → Kimi researches, creates plans
"GSD execute phase 1"     → Kimi executes all plans for phase 1
"GSD verify phase 1"      → Kimi runs verification
```

### Quick Task (No Full Planning)

```bash
# Create quick task plan
python3 .agent/skills/gsd-workflow/scripts/quick_task.py "Add dark mode toggle"

# Or tell Kimi: "GSD quick: Add dark mode toggle"
```

## Advanced Features

### Codebase Mapping (Brownfield Projects)

For existing codebases, map before initializing:

```bash
gsd map-codebase
```

Creates `.planning/codebase/` with:
- Stack analysis
- Architecture overview
- Code conventions
- Concerns and constraints

### Phase Management

```bash
gsd add-phase                    # Append phase to roadmap
gsd insert-phase 2               # Insert phase between 1 and 2
gsd remove-phase 3               # Remove phase 3
```

### Milestone Management

```bash
gsd complete-milestone           # Archive milestone, tag release
gsd new-milestone                # Start next version
```

## Best Practices

1. **Always discuss before planning**: Capture your vision in CONTEXT.md
2. **Keep plans atomic**: Each PLAN.md should fit in a fresh context window
3. **Verify manually**: Automated checks + manual UAT for quality
4. **Commit per task**: Atomic commits enable easy bisect and revert
5. **Use quick mode sparingly**: For truly small tasks only

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Plans too large | Split into smaller phases |
| Context degradation | Start fresh session, use `gsd status` |
| Dependencies unclear | Use `gsd discuss` to clarify |
| Verification fails | Run `gsd plan <phase> --fix` to regenerate |

## Advanced Tools

### Project Generation

Generate PROJECT.md interactively or from quick specs:

```bash
# Interactive mode - asks questions about your project
python3 scripts/project_generator.py

# Quick mode
python3 scripts/project_generator.py --quick "My App" "A todo app" --stack nextjs,fastapi,postgres
```

### Research Aggregation

Collect and synthesize research notes before planning:

```bash
# List all research files
python3 scripts/research_aggregator.py --list

# Aggregate research for phase 1
python3 scripts/research_aggregator.py --phase 1

# Generate concise input for planning
python3 scripts/research_aggregator.py --phase 1 --planning-input

# Save full report
python3 scripts/research_aggregator.py --phase 1 --output research-summary.md
```

### Wave Planning

Before executing a phase, analyze dependencies to optimize parallelization:

```bash
python3 scripts/wave_planner.py 1
```

Output shows:
- Which plans can run in parallel
- Estimated time per wave
- Sequential vs parallel efficiency
- Circular dependency warnings

### Dependency Visualization

Visualize plan dependencies in multiple formats:

```bash
# ASCII tree view
python3 scripts/dependency_visualizer.py 1

# Mermaid diagram (for markdown)
python3 scripts/dependency_visualizer.py 1 --format mermaid

# Graphviz DOT format
python3 scripts/dependency_visualizer.py 1 --format dot

# Markdown table
python3 scripts/dependency_visualizer.py 1 --format table

# Analysis report with bottlenecks
python3 scripts/dependency_visualizer.py 1 --analyze
```

### Plan Management

Merge or split plans as needed:

```bash
# Merge multiple plans into one
python3 scripts/plan_merger.py merge 1-1-PLAN.md 1-2-PLAN.md --name "Auth System"

# Split a large plan into smaller ones
python3 scripts/plan_merger.py split 1-1-PLAN.md --after 5,10

# Consolidate all quick tasks
python3 scripts/plan_merger.py consolidate-quick
```

### Progress Reporting

Generate detailed progress reports:

```bash
# Markdown report (default)
python3 scripts/progress_reporter.py

# JSON format for automation
python3 scripts/progress_reporter.py --format json

# Plain text for terminal
python3 scripts/progress_reporter.py --format text

# Save to file
python3 scripts/progress_reporter.py --output weekly-update.md
```

### Phase Lifecycle Management

Track and manage phase state transitions:

```bash
# Check current status
python3 scripts/phase_transition.py status

# Check completion status of all phases
python3 scripts/phase_transition.py check

# Mark phase as started (updates ROADMAP.md and STATE.md)
python3 scripts/phase_transition.py start 2

# Mark phase as complete (validates all plans have summaries)
python3 scripts/phase_transition.py complete 1

# Manually set status
python3 scripts/phase_transition.py set-status 2 executing
```

### Plan Validation

Validate plan structure before execution:

```bash
# Validate specific plan
python3 scripts/validate_plan.py 1-1-PLAN.md

# Validate all plans
python3 scripts/validate_plan.py --all
```

Checks for:
- Valid XML structure
- Required elements (overview, tasks, etc.)
- Task completeness (name, action, verify)
- Size limits (plan < 150 lines, task < 50 lines)
- Best practices (verification steps, done criteria)

### GSD-Style Commits

Create conventional commits with GSD metadata:

```bash
# Interactive mode (recommended)
python3 scripts/commit_helper.py

# Quick mode
python3 scripts/commit_helper.py -m "add user authentication" -t feat -s auth

# With phase info
python3 scripts/commit_helper.py -m "implement login" -t feat -p 1 --task 1
```

Commit format: `type(scope): description`

Types: feat, fix, docs, style, refactor, test, chore, plan, research

## Helper Scripts

The skill includes Python scripts to streamline GSD workflow:

### Core Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `init_gsd.py` | `python3 scripts/init_gsd.py [--dir DIR]` | Initialize `.planning/` directory with all artifacts |
| `status.py` | `python3 scripts/status.py [--dir DIR]` | Show project status, phases progress, and next steps |
| `quick_task.py` | `python3 scripts/quick_task.py "task description"` | Create quick task plan without full GSD ceremony |

### Validation & Planning

| Script | Command | Purpose |
|--------|---------|---------|
| `validate_plan.py` | `python3 scripts/validate_plan.py [PLAN] [--all]` | Validate plan XML structure |
| `wave_planner.py` | `python3 scripts/wave_planner.py <phase>` | Analyze dependencies, create wave schedule |
| `dependency_visualizer.py` | `python3 scripts/dependency_visualizer.py <phase>` | Visualize plan dependencies (ASCII/Mermaid/DOT) |
| `plan_merger.py` | `python3 scripts/plan_merger.py <action>` | Merge or split plans |

### Project Management

| Script | Command | Purpose |
|--------|---------|---------|
| `phase_transition.py` | `python3 scripts/phase_transition.py <action>` | Manage phase lifecycle |
| `commit_helper.py` | `python3 scripts/commit_helper.py [options]` | Create GSD-style commits |
| `project_generator.py` | `python3 scripts/project_generator.py` | Interactive PROJECT.md generator |
| `research_aggregator.py` | `python3 scripts/research_aggregator.py [--phase N]` | Aggregate research notes |
| `progress_reporter.py` | `python3 scripts/progress_reporter.py [--format]` | Generate progress reports |

### Script Usage Examples

```bash
# Initialize GSD in current directory
python3 .agent/skills/gsd-workflow/scripts/init_gsd.py

# Check project status
python3 .agent/skills/gsd-workflow/scripts/status.py

# Create quick task
python3 .agent/skills/gsd-workflow/scripts/quick_task.py "Fix login redirect bug"

# Generate PROJECT.md interactively
python3 .agent/skills/gsd-workflow/scripts/project_generator.py

# Quick generate with name and stack
python3 .agent/skills/gsd-workflow/scripts/project_generator.py --quick "My App" "A todo app" --stack nextjs,fastapi,postgres

# Validate all plans
python3 .agent/skills/gsd-workflow/scripts/validate_plan.py --all

# Analyze phase 1 for wave execution
python3 .agent/skills/gsd-workflow/scripts/wave_planner.py 1

# Visualize dependencies
python3 .agent/skills/gsd-workflow/scripts/dependency_visualizer.py 1 --format ascii
python3 .agent/skills/gsd-workflow/scripts/dependency_visualizer.py 1 --format mermaid

# Merge plans
python3 .agent/skills/gsd-workflow/scripts/plan_merger.py merge 1-1-PLAN.md 1-2-PLAN.md --name "Auth System"

# Split a large plan
python3 .agent/skills/gsd-workflow/scripts/plan_merger.py split 1-1-PLAN.md --after 5,10

# Aggregate research
python3 .agent/skills/gsd-workflow/scripts/research_aggregator.py --phase 1
python3 .agent/skills/gsd-workflow/scripts/research_aggregator.py --phase 1 --planning-input

# Generate progress report
python3 .agent/skills/gsd-workflow/scripts/progress_reporter.py
python3 .agent/skills/gsd-workflow/scripts/progress_reporter.py --format json
python3 .agent/skills/gsd-workflow/scripts/progress_reporter.py --output weekly-update.md

# Manage phase lifecycle
python3 .agent/skills/gsd-workflow/scripts/phase_transition.py status
python3 .agent/skills/gsd-workflow/scripts/phase_transition.py start 2
python3 .agent/skills/gsd-workflow/scripts/phase_transition.py complete 1

# Create GSD-style commit
python3 .agent/skills/gsd-workflow/scripts/commit_helper.py
```

## Templates

### Core Artifacts

| Template | Purpose | Location |
|----------|---------|----------|
| `PROJECT.md` | Project vision, goals, constraints | `assets/templates/PROJECT.md` |
| `REQUIREMENTS.md` | v1/v2 requirements, scope | `assets/templates/REQUIREMENTS.md` |
| `ROADMAP.md` | Phases mapped to requirements | `assets/templates/ROADMAP.md` |
| `STATE.md` | Decisions, blockers, memory | `assets/templates/STATE.md` |
| `PLAN.md` | XML plan structure | `assets/templates/PLAN.md` |
| `VERIFICATION.md` | Verification checklist | `assets/templates/VERIFICATION.md` |

### Context Templates by Feature Type

Use these during `discuss-phase` to capture implementation decisions:

| Template | Use For | Location |
|----------|---------|----------|
| `CONTEXT-ui.md` | Frontend/UI features | `assets/templates/CONTEXT-ui.md` |
| `CONTEXT-api.md` | API/backend features | `assets/templates/CONTEXT-api.md` |
| `CONTEXT-database.md` | Database schema work | `assets/templates/CONTEXT-database.md` |

## Examples

Complete phase examples with plans:

| Example | Description | Location |
|---------|-------------|----------|
| `auth-phase-example.md` | Authentication with JWT, database models, login/register UI | `assets/examples/auth-phase-example.md` |
| `crud-api-example.md` | Full CRUD API with permissions, pagination, soft delete | `assets/examples/crud-api-example.md` |

## Additional References

- **Agent Prompts**: See [references/agents.md](references/agents.md) for specialized agent definitions
- **Quick Reference**: See [references/quick-reference.md](references/quick-reference.md) for one-liners, size limits, config options
- **Full Documentation**: See original GSD repo at https://github.com/glittercowboy/get-shit-done
