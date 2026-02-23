---
trigger: glob
globs: "**/*"
description: Spec Driven Workflow applies when touching any file.
---

# Spec Driven Workflow v1

Bridge the gap between requirements and implementation.

## Core Artifacts

Maintain these artifacts at all times:

| Artifact          | Purpose                                                                  |
| ----------------- | ------------------------------------------------------------------------ |
| `requirements.md` | User stories and acceptance criteria in structured EARS notation         |
| `design.md`       | Technical architecture, sequence diagrams, implementation considerations |
| `tasks.md`        | Detailed, trackable implementation plan                                  |

## Table of Contents

- [Universal Documentation Framework](#universal-documentation-framework)
- [Execution Workflow](#execution-workflow-6-phase-loop)
  - [Phase 1: ANALYZE](#phase-1-analyze)
  - [Phase 2: DESIGN](#phase-2-design)
  - [Phase 3: IMPLEMENT](#phase-3-implement)
  - [Phase 4: VALIDATE](#phase-4-validate)
  - [Phase 5: REFLECT](#phase-5-reflect)
  - [Phase 6: HANDOFF](#phase-6-handoff)
- [Troubleshooting & Retry Protocol](#troubleshooting--retry-protocol)
- [Technical Debt Management](#technical-debt-management)
- [Quality Assurance](#quality-assurance)
- [EARS Notation Reference](#ears-notation-reference)

## Universal Documentation Framework

> Use the detailed templates as the **primary source of truth** for all documentation.

### Detailed Documentation Templates

#### Action Documentation Template

```markdown
### [TYPE] - [ACTION] - [TIMESTAMP]

**Objective:** [Goal being accomplished]

**Context:** [Current state, requirements, and reference to prior steps]

**Decision:** [Approach chosen and rationale, referencing the Decision Record if applicable]

**Execution:** [Steps taken with parameters and commands used. For code, include file paths.]

**Output:** [Complete and unabridged results, logs, command outputs, and metrics]

**Validation:** [Success verification method and results. If failed, include a remediation plan.]

**Next:** [Automatic continuation plan to the next specific action]
```

#### Decision Record Template

```markdown
### Decision - [TIMESTAMP]

**Decision:** [What was decided]

**Context:** [Situation requiring decision and data driving it]

**Options:** [Alternatives evaluated with brief pros and cons]

**Rationale:** [Why the selected option is superior, with trade-offs explicitly stated]

**Impact:** [Anticipated consequences for implementation, maintainability, and performance]

**Review:** [Conditions or schedule for reassessing this decision]
```

### Summary Formats

#### Streamlined Action Log

```
[TYPE][TIMESTAMP] Goal: [X] → Action: [Y] → Result: [Z] → Next: [W]
```

#### Compressed Decision Record

```
Decision: [X] | Rationale: [Y] | Impact: [Z] | Review: [Date]
```

## Execution Workflow (6-Phase Loop)

> **Never skip any step.** Use consistent terminology. Reduce ambiguity.

### Phase 1: ANALYZE

**Objective**

- Understand the problem
- Analyze the existing system
- Produce a clear, testable set of requirements
- Think about possible solutions and their implications

**Checklist**

- [ ] **Read code, docs, tests, and logs**
  - Document inventory and analysis
- [ ] **Define requirements in EARS Notation**
  - Format: `WHEN [condition] THE SYSTEM SHALL [behavior]`
- [ ] **Identify dependencies, constraints, and risks**
- [ ] **Map data flows and interactions**
- [ ] **Catalog edge cases and failures**
- [ ] **Generate Confidence Score (0–100%)**
  - Document rationale

**Critical Constraint**

Do not proceed until all requirements are clear and documented.

### Phase 2: DESIGN

**Objective**

- Create a comprehensive technical design and detailed implementation plan

**Checklist**

- [ ] **Define adaptive execution strategy based on Confidence Score**
  - **High Confidence (>85%):** Full plan, skip PoC, comprehensive docs
  - **Medium Confidence (66–85%):** Build PoC/MVP first, then expand
  - **Low Confidence (<66%):** Research first, then re-analyze

- [ ] **Document technical design in `design.md`**
  - **Architecture:** High-level overview of components and interactions
  - **Data Flow:** Diagrams and descriptions
  - **Interfaces:** API contracts, schemas, public-facing function signatures
  - **Data Models:** Data structures and database schemas

- [ ] **Document error handling**
  - Create an error matrix with procedures and expected responses

- [ ] **Define unit testing strategy**

- [ ] **Create implementation plan in `tasks.md`**
  - For each task: description, expected outcome, and dependencies

**Critical Constraint**

Do not proceed to implementation until design and plan are complete and validated.

### Phase 3: IMPLEMENT

**Objective**

- Write production-quality code according to the design and plan

**Checklist**

- [ ] **Code in small, testable increments**
  - Document each increment with code changes, results, and test links

- [ ] **Implement from dependencies upward**
  - Document resolution order, justification, and verification

- [ ] **Follow conventions**
  - Document adherence and any deviations with a Decision Record

- [ ] **Add meaningful comments**
  - Focus on intent ("why"), not mechanics ("what")

- [ ] **Create files as planned**
  - Document file creation log

- [ ] **Update task status in real time**

**Critical Constraint**

Do not merge or deploy code until all implementation steps are documented and tested.

### Phase 4: VALIDATE

**Objective**

- Verify that implementation meets all requirements and quality standards

**Checklist**

- [ ] **Execute automated tests**
  - Document outputs, logs, and coverage reports
  - For failures, document root cause analysis and remediation

- [ ] **Perform manual verification if necessary**
  - Document procedures, checklists, and results

- [ ] **Test edge cases and errors**
  - Document results and evidence of correct error handling

- [ ] **Verify performance**
  - Document metrics and profile critical sections

- [ ] **Log execution traces**
  - Document path analysis and runtime behavior

**Critical Constraint**

Do not proceed until all validation steps are complete and all issues are resolved.

### Phase 5: REFLECT

**Objective**

- Improve codebase, update documentation, and analyze performance

**Checklist**

- [ ] **Refactor for maintainability**
  - Document decisions, before/after comparisons, and impact

- [ ] **Update all project documentation**
  - Ensure all READMEs, diagrams, and comments are current

- [ ] **Identify potential improvements**
  - Document backlog with prioritization

- [ ] **Validate success criteria**
  - Document final verification matrix

- [ ] **Perform meta-analysis**
  - Reflect on efficiency, tool usage, and protocol adherence

- [ ] **Auto-create technical debt issues**
  - Document inventory and remediation plans

**Critical Constraint**

Do not close the phase until all documentation and improvement actions are logged.

### Phase 6: HANDOFF

**Objective**

- Package work for review and deployment, and transition to next task

**Checklist**

- [ ] **Generate executive summary**
  - Use Compressed Decision Record format

- [ ] **Prepare pull request (if applicable)**
  1. Executive summary
  2. Changelog from Streamlined Action Log
  3. Links to validation artifacts and Decision Records
  4. Links to final `requirements.md`, `design.md`, and `tasks.md`

- [ ] **Finalize workspace**
  - Archive intermediate files, logs, and temporary artifacts to `.agent_work/`

- [ ] **Continue to next task**
  - Document transition or completion

**Critical Constraint**

Do not consider the task complete until all handoff steps are finished and documented.

## Troubleshooting & Retry Protocol

If you encounter errors, ambiguities, or blockers:

**Checklist**

1. **Re-analyze**
   - Revisit the ANALYZE phase
   - Confirm all requirements and constraints are clear and complete

2. **Re-design**
   - Revisit the DESIGN phase
   - Update technical design, plans, or dependencies as needed

3. **Re-plan**
   - Adjust the implementation plan in `tasks.md` to address new findings

4. **Retry execution**
   - Re-execute failed steps with corrected parameters or logic

5. **Escalate**
   - If the issue persists after retries, follow the escalation protocol

**Critical Constraint**

Never proceed with unresolved errors or ambiguities. Always document troubleshooting steps and outcomes.

## Technical Debt Management (Automated)

### Identification & Documentation

- **Code Quality:** Continuously assess code quality during implementation using static analysis
- **Shortcuts:** Explicitly record all speed-over-quality decisions with their consequences in a Decision Record
- **Workspace:** Monitor for organizational drift and naming inconsistencies
- **Documentation:** Track incomplete, outdated, or missing documentation

### Auto-Issue Creation Template

```markdown
**Title:** [Technical Debt] - [Brief Description]

**Priority:** [High/Medium/Low based on business impact and remediation cost]

**Location:** [File paths and line numbers]

**Reason:** [Why the debt was incurred, linking to a Decision Record if available]

**Impact:** [Current and future consequences (e.g., slows development, increases bug risk)]

**Remediation:** [Specific, actionable resolution steps]

**Effort:** [Estimate for resolution (e.g., T-shirt size: S, M, L)]
```

### Remediation (Auto-Prioritized)

- Risk-based prioritization with dependency analysis
- Effort estimation to aid in future planning
- Propose migration strategies for large refactoring efforts

### Quality Assurance

**Monitoring:** Static/Dynamic Analysis, Documentation checks

**Metrics:** Code coverage, complexity, maintainability, technical debt ratio, documentation coverage

## EARS Notation Reference

**EARS (Easy Approach to Requirements Syntax)** — Standard format for requirements:

| Pattern               | Format                                                              |
| --------------------- | ------------------------------------------------------------------- |
| **Ubiquitous**        | `THE SYSTEM SHALL [expected behavior]`                              |
| **Event-driven**      | `WHEN [trigger event] THE SYSTEM SHALL [expected behavior]`         |
| **State-driven**      | `WHILE [in specific state] THE SYSTEM SHALL [expected behavior]`    |
| **Unwanted behavior** | `IF [unwanted condition] THEN THE SYSTEM SHALL [required response]` |
| **Optional**          | `WHERE [feature is included] THE SYSTEM SHALL [expected behavior]`  |
| **Complex**           | Combinat                                                            |
