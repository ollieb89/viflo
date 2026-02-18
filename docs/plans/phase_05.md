# 5. Iteration & Continuous Improvement

## Overview

This phase closes the **feedback loop** that connects real-world development outcomes back to the decisions made in Phases 1–4. Without structured iteration, model choices go stale, prompting templates drift, costs creep upward, and process inefficiencies compound. Phase 5 ensures the workflow evolves as fast as the LLM landscape it depends on.

**Inputs:** Metrics collected during Phase 4 (agent performance, cost, latency, coverage, flaky test rate), sprint artifacts from Phase 3, and the original `PLAN.md` from Phase 2.

**Outputs:** Updated model selections (Phase 1), refined planning templates (Phase 2), improved implementation practices (Phase 3), and tighter quality gates (Phase 4).

**Model Selection:** Phase 5 itself is a **human-driven** process. LLMs assist with analysis (summarizing metrics, suggesting optimizations) but decisions about model swaps, process changes, and budget allocation are made by humans.

---

## 5.1 Post-Sprint Retrospective Protocol

### Purpose

At the end of every sprint or iteration, conduct a structured review of the AI-assisted development workflow. This is not a standard agile retro — it specifically evaluates the performance of the agentic pipeline.

### Sprint Review Inputs

Collect the following data before the retrospective:

| Data Source                | Metric                          | Where to Find It                              |
|----------------------------|---------------------------------|-----------------------------------------------|
| Phase 4 § 4.6              | First-pass acceptance rate     | Agent session logs / manual tracking          |
| Phase 4 § 4.6              | Refinement rounds per task     | Agent session logs                             |
| Phase 4 § 4.6              | Token usage per task           | API provider dashboard / billing              |
| Phase 4 § 4.6              | Cost per feature               | Aggregated token cost                          |
| Phase 4 § 4.4              | CI pipeline duration           | GitHub Actions run history                     |
| Phase 4 § 4.7              | Flaky test count               | CI logs / quarantine list                      |
| Phase 3 § 3.8              | Tasks completed vs planned     | Task board (GitHub Issues / Linear)           |
| Phase 3 § 3.8              | Blocked time                   | Task board                                     |

### Sprint Review Agenda

Run through these items in order. Timebox the entire retrospective to **45 minutes**.

1. **Metrics Review** (10 min) — Walk through the data table above. Highlight anything outside target thresholds.
2. **Model Performance Assessment** (10 min) — Which models performed well? Which underperformed? Were any tasks routed to the wrong tier?
3. **Process Friction** (10 min) — Where did the workflow slow down? Planning gaps? Prompting issues? Review bottlenecks?
4. **Cost Check** (5 min) — Are we within budget? Any unexpected spikes?
5. **Action Items** (10 min) — Define concrete changes for the next sprint. Each action item must have an owner and a deadline.

### Sprint Review Output Template

```markdown
## Sprint [N] Retrospective — [Date]

### Metrics Summary
| Metric                     | Target   | Actual   | Status |
|----------------------------|----------|----------|--------|
| First-pass acceptance      | > 70%    |          | ✅/⚠️/❌ |
| Avg refinement rounds      | < 2.5    |          | ✅/⚠️/❌ |
| Monthly API cost           | < $X     |          | ✅/⚠️/❌ |
| CI pipeline duration       | < 10 min |          | ✅/⚠️/❌ |
| Flaky test count           | < 2%     |          | ✅/⚠️/❌ |
| Tasks completed/planned    | > 80%    |          | ✅/⚠️/❌ |

### What Worked
- [List specific successes]

### What Didn't Work
- [List specific issues]

### Action Items
| # | Action                         | Owner  | Due Date   |
|---|--------------------------------|--------|------------|
| 1 |                                |        |            |
| 2 |                                |        |            |
```

---

## 5.2 Model Performance Evaluation

### Purpose

Evaluate each LLM's real-world performance against the tasks it was assigned. This is not about benchmarks — it's about **how well the model performed on your specific codebase, tech stack, and task types**.

### Model Scorecard

Maintain a scorecard per model. Update it every sprint.

```markdown
## Model Scorecard: [Model Name]

**Tier:** [High Performance / Code Execution Mid / Code Execution Cheap / Open-Source]
**Usage:** [Task types this model was assigned]

| Dimension              | Score (1-5) | Notes                                      |
|------------------------|-------------|--------------------------------------------|
| Code correctness       |             | Does it produce code that compiles/runs?   |
| Convention adherence   |             | Does it follow project patterns?           |
| Test quality           |             | Are generated tests meaningful?            |
| Context utilization    |             | Does it use provided context effectively?  |
| Error handling         |             | Does it handle edge cases unprompted?      |
| Response time          |             | Is it fast enough for the workflow?        |
| Cost efficiency        |             | Cost vs quality tradeoff                   |

**Overall Assessment:** [Keep / Monitor / Replace]
**Recommended Action:** [None / Adjust routing / Downgrade tier / Replace with X]
```

### Performance Comparison Matrix

Compare models side-by-side for each task type:

| Task Type               | Current Model         | Acceptance Rate | Avg Cost | Latency | Verdict     |
|--------------------------|-----------------------|-----------------|----------|---------|-------------|
| Single-file generation   | Gemini 3 Flash        |                 |          |         | Keep/Change |
| Multi-file refactoring   | Claude Sonnet 4.5     |                 |          |         | Keep/Change |
| Complex debugging        | Claude Opus 4.5       |                 |          |         | Keep/Change |
| Test generation          | GPT-5 Mini            |                 |          |         | Keep/Change |
| Infrastructure / IaC     | Google Q CLI          |                 |          |         | Keep/Change |
| Privacy-sensitive tasks  | Qwen / DeepSeek       |                 |          |         | Keep/Change |

### When to Change Models

Apply the following decision tree:

```
Is the model's first-pass acceptance < 60% for its assigned task type?
  ├── Yes → Switch to a higher-tier model for that task type
  └── No
       └── Is the model's cost > 2× the next-cheapest viable model?
            ├── Yes → A/B test the cheaper model for 1 sprint
            └── No
                 └── Is the model's latency > 2× the target?
                      ├── Yes → Switch to a faster model
                      └── No → Keep current model
```

---

## 5.3 Cost Optimization Loop

### Purpose

Keep the total cost of AI-assisted development within budget while maintaining quality. Cost optimization is a **continuous process**, not a one-time exercise.

### Budget Allocation Framework

Allocate the monthly AI budget across model tiers:

| Tier                   | Budget Share | Rationale                                         |
|------------------------|-------------|---------------------------------------------------|
| High Performance       | 15–25%      | Reserved for planning, complex debugging, pivots  |
| Code Execution Mid     | 30–40%      | Bulk of multi-file tasks, integration tests       |
| Code Execution Cheap   | 30–40%      | Unit tests, boilerplate, single-file generation   |
| Open-Source / Local     | 5–15%       | Privacy tasks, experimentation, offline work      |

### Cost Reduction Strategies

| Strategy                                 | Expected Savings | Trade-off                                          |
|------------------------------------------|------------------|----------------------------------------------------|
| Downgrade task routing by one tier        | 20–40%          | May increase refinement rounds                     |
| Use open-source for test generation       | 30–50%          | Lower quality; requires more human review          |
| Reduce context window utilization         | 10–20%          | Less reference material; may reduce accuracy       |
| Cache common prompting patterns           | 5–15%           | Prompt drift if templates aren't updated           |
| Batch similar tasks for one agent session | 10–25%          | Longer sessions; risk of context pollution         |
| Shift E2E tests to PR-only (not every push) | 15–30% CI mins | Slightly slower feedback for E2E regressions     |

### Monthly Cost Review

At the end of each month:

1. **Pull API spend** from provider dashboards (OpenAI, Anthropic, Google, etc.)
2. **Break down by model** — which models consumed the most tokens?
3. **Break down by task type** — which tasks consumed the most tokens?
4. **Compare to budget** — are we within the allocation framework above?
5. **Identify top cost drivers** — top 5 most expensive tasks/features
6. **Adjust routing** — move high-cost, low-complexity tasks to cheaper models

### Anti-Patterns in Cost Management

| Anti-Pattern                              | Why It Fails                                         | Correct Approach                                    |
|-------------------------------------------|------------------------------------------------------|-----------------------------------------------------|
| Using High Performance for all tasks      | 5–10× cost with minimal quality gain for simple tasks | Route by complexity, not convenience                |
| Optimizing cost without tracking quality  | Savings are illusory if refinement rounds double      | Track cost and acceptance rate together             |
| Ignoring CI costs                         | Pipeline minutes add up; E2E tests are expensive     | Monitor CI spend alongside API spend               |
| No budget ceiling                         | Spend spirals during deadline pressure               | Set and enforce monthly caps                        |
| Refusing to use open-source models        | Misses 30–50% savings on low-stakes tasks            | Evaluate open-source for non-critical work          |

---

## 5.4 Workflow & Process Refinement

### Purpose

Improve Phases 2–4 based on real-world feedback. The workflow itself is a product that needs iteration.

### Planning Process Improvements (Phase 2 Feedback)

Review the quality of `PLAN.md` documents retrospectively:

| Question                                                 | If No → Action                                              |
|----------------------------------------------------------|-------------------------------------------------------------|
| Did the plan have enough detail for agents to execute?   | Add more granular specifications to the template             |
| Were there missing sections that caused blockers?        | Add sections to the Phase 2 template                         |
| Did the tech stack assumptions hold up?                  | Update the default stack context in Phase 2 § 2.1            |
| Were API routes complete and accurate?                   | Improve the route definition checklist                       |
| Did the database schema need mid-sprint changes?         | Require more thorough schema review before lock              |

### Implementation Process Improvements (Phase 3 Feedback)

| Question                                                 | If No → Action                                              |
|----------------------------------------------------------|-------------------------------------------------------------|
| Were tasks sized correctly (2–15 min)?                   | Adjust sizing guidelines in Phase 3 § 3.1                    |
| Did the agent routing match task complexity?             | Update the decision matrix in Phase 3 § 3.2                  |
| Were prompting templates effective?                      | Refine templates in Phase 3 § 3.4                            |
| Did context management work (right files in prompt)?     | Update context loading strategy in Phase 3 § 3.5             |
| Was the review checklist thorough enough?                | Add/remove items from the checklist in Phase 3 § 3.6         |

### Testing Process Improvements (Phase 4 Feedback)

| Question                                                 | If No → Action                                              |
|----------------------------------------------------------|-------------------------------------------------------------|
| Were AI-generated tests meaningful?                      | Improve test generation prompts in Phase 4 § 4.2             |
| Did coverage targets match real-world needs?             | Adjust per-layer targets in Phase 4 § 4.1                    |
| Was the CI pipeline fast enough?                         | Optimize stages, add caching in Phase 4 § 4.4                |
| Were there too many flaky tests?                         | Tighten test quality criteria in Phase 4 § 4.2               |
| Did the cost monitoring catch issues early enough?       | Adjust thresholds in Phase 4 § 4.6                           |

### Template Evolution

All templates (planning, prompting, testing, review) should be treated as **living documents**:

1. **Track template versions** — use git history or explicit version numbers
2. **Log template changes** — note what changed and why (tied to a retro action item)
3. **A/B test template changes** — try the new template for one sprint before adopting
4. **Share improvements across projects** — template improvements in one project should propagate to others

---

## 5.5 Model Reassessment & Migration

### Purpose

The LLM landscape evolves rapidly. New models, providers, and pricing tiers emerge monthly. This section defines a structured process for evaluating new models and safely migrating when a better option is available.

### Quarterly Benchmarking Process

Every quarter, run a standardized evaluation:

**Step 1: Identify candidates**
- Monitor model releases from major providers (OpenAI, Anthropic, Google, Meta, Mistral, DeepSeek)
- Check community benchmarks (LiveCodeBench, HumanEval, Terminal-Bench, SWE-Bench)
- Evaluate pricing changes from existing providers

**Step 2: Run internal test suite**

Maintain a set of **10–20 representative tasks** drawn from your actual codebase:

| Task Category       | Example Task                                         | Evaluation Criteria                       |
|----------------------|------------------------------------------------------|-------------------------------------------|
| Simple CRUD          | Generate a `GET /api/items/:id` endpoint             | Correctness, convention adherence         |
| Complex logic        | Implement pagination with cursor-based navigation    | Edge case handling, type safety           |
| Test generation      | Write tests for an auth middleware                    | Test quality, meaningful assertions       |
| Debugging            | Fix a type error in a multi-file refactoring          | Root cause identification, fix quality    |
| Planning             | Generate a schema design for a new feature            | Completeness, adherence to template       |

**Step 3: Score candidates**

Use the Model Scorecard (§ 5.2) for each candidate. Compare against the current model for the same task type.

**Step 4: Decision**

| Outcome                                   | Action                                                  |
|-------------------------------------------|---------------------------------------------------------|
| New model scores higher on all dimensions | Migrate immediately                                      |
| New model scores higher on some dimensions| A/B test for 1 sprint, then decide                       |
| New model scores similarly but is cheaper | Migrate after verifying quality parity                   |
| New model scores lower                    | Do not migrate; re-evaluate next quarter                 |

### Model Migration Protocol

When migrating from one model to another:

1. **Parallel run** — Use both models for the same task type for 1 sprint
2. **Compare outputs** — Track acceptance rate, refinement rounds, and cost for both
3. **Gradual rollout** — Start with low-risk tasks (test generation, docs), then expand
4. **Rollback plan** — Keep the previous model configuration for 2 sprints after full migration
5. **Update Phase 1** — Reflect the new model in the model portfolio document
6. **Update routing rules** — Adjust Phase 3 § 3.2 decision matrix if task routing changes
7. **Communicate** — Notify the team and update onboarding documentation

### Provider Diversification

Avoid over-reliance on a single provider:

- Maintain at least **2 providers** in the active model portfolio
- For critical tasks (planning, complex debugging), have a **fallback model** from a different provider
- Monitor provider SLA, rate limits, and deprecation notices
- Consider open-source models as the **offline fallback** for provider outages

---

## 5.6 Knowledge Management & Institutional Memory

### Purpose

Capture learnings from AI-assisted development so they compound over time. Without deliberate knowledge management, each sprint starts from scratch and repeats past mistakes.

### Sprint Knowledge Artifacts

After each sprint, update the following:

| Artifact                   | Contents                                                 | Location                          |
|----------------------------|----------------------------------------------------------|-----------------------------------|
| Prompt Library             | Effective prompting patterns per task type                | `docs/prompts/` or memory system  |
| Anti-Pattern Log           | Failed approaches and why they failed                     | Sprint retro notes                |
| Model Performance History  | Scorecard data over time                                  | `docs/metrics/` or memory system  |
| Template Changelog         | Changes to planning, prompting, and testing templates     | Git history + changelog           |
| Cost History               | Monthly cost data with breakdowns                         | Spreadsheet or dashboard          |

### Prompt Library Maintenance

The **prompt library** is the most high-leverage knowledge artifact. Effective prompts save hours of refinement.

**Structure:**

```
docs/prompts/
  frontend/
    component-generation.md       # Template for generating UI components
    page-scaffolding.md           # Template for generating pages with data fetching
  backend/
    endpoint-generation.md        # Template for generating API endpoints
    migration-generation.md       # Template for generating DB migrations
  testing/
    unit-test-generation.md       # Template for generating unit tests
    e2e-test-generation.md        # Template for generating E2E tests
  infrastructure/
    ci-pipeline.md                # Template for generating CI configs
    docker-config.md              # Template for generating Docker configs
```

**Maintenance rules:**
- Update templates when refinement rounds for a task type average > 2.5
- Add examples from successful first-pass generations
- Remove prompting patterns that consistently produce low-quality output
- Version templates with dates and link to the retro action item that triggered the change

### Pattern Library

Maintain a living document of **successful patterns** and **observed anti-patterns**:

| Pattern Type  | Example                                          | Outcome                                      |
|---------------|--------------------------------------------------|-----------------------------------------------|
| ✅ Success    | Providing 2 example files as style reference     | 90% first-pass adherence to project conventions |
| ✅ Success    | Using repo map instead of full file contents     | 40% token reduction with no quality loss       |
| ❌ Anti-pattern | Generating 5+ files in a single agent session   | Context pollution; files 4–5 had 50% defect rate |
| ❌ Anti-pattern | Skipping the review checklist under time pressure | 3× more bugs found in next sprint             |

---

## 5.7 Scaling the Workflow

### Purpose

Expand the AI-assisted development workflow to new projects, new team members, and new domains.

### New Project Onboarding

When starting a new project with this workflow:

1. **Copy the Phase 1 model portfolio** — Use the current best model for each tier as the starting point
2. **Adapt the Phase 2 planning template** — Update the tech stack context for the new project
3. **Reuse prompting templates** from the prompt library — Adapt to the new stack
4. **Copy CI/CD pipeline** (Phase 4) — Adjust paths, test commands, and deployment targets
5. **Set initial targets** — Use the defaults from Phase 4 § 4.1 (coverage) and § 4.6 (performance)
6. **Run Phase 5 retrospective after Sprint 1** — Calibrate all thresholds to the new project

### New Team Member Onboarding

When a new developer joins:

1. **Read Phases 1–5** — Understand the full workflow end-to-end
2. **Review the prompt library** — Learn effective prompting patterns
3. **Shadow a sprint retrospective** — Understand the feedback loop
4. **Execute 3–5 tasks with review** — Pair with an experienced team member for the first few tasks
5. **Contribute to the pattern library** — Add new learnings from their onboarding experience

### Multi-Project Governance

When running this workflow across multiple projects:

- **Shared model portfolio** — Maintain a single Phase 1 document across projects
- **Project-specific templates** — Each project has its own Phase 2 context and prompting templates
- **Shared CI/CD patterns** — Use a common pipeline template with project-specific overrides
- **Cross-project retros** — Quarterly, compare metrics across projects to identify workflow-wide improvements
- **Centralized prompt library** — Share effective prompts across projects; tag by tech stack

---

## 5.8 Done Criteria

Phase 5 is not a phase that "completes" — it is a **continuous process**. However, the following criteria define when the iteration system is operational.

### System Operational Criteria

- [ ] **Retrospective cadence** is established (end of every sprint)
- [ ] **Sprint review template** is in use and producing action items
- [ ] **Model scorecards** are being maintained for all active models
- [ ] **Cost tracking** is in place with monthly reviews
- [ ] **Prompt library** exists with at least one template per task type
- [ ] **Quarterly benchmarking** process is scheduled and documented
- [ ] **Model migration protocol** is documented and has been tested at least once

### Per-Sprint Criteria

After every sprint, verify:

- [ ] Retrospective was conducted and documented
- [ ] All action items from the previous sprint's retro are addressed or deferred with justification
- [ ] Metrics are within target thresholds, or action items exist for out-of-target metrics
- [ ] No model is being used with < 60% first-pass acceptance without a mitigation plan
- [ ] Monthly cost is within budget allocation

### Per-Quarter Criteria

Every quarter, verify:

- [ ] Model reassessment was conducted (§ 5.5)
- [ ] Internal test suite was run against at least one new model candidate
- [ ] Phase 1 model portfolio is up to date with current recommendations
- [ ] Templates (planning, prompting, testing) have been reviewed and updated if needed
- [ ] Cost trends are stable or improving
- [ ] Prompt library has been maintained and grown

### Continuous Criteria

Always true at any point:

- [ ] The workflow is documented well enough for a new team member to be productive within 1 week
- [ ] Model choices are treated as **dynamic variables**, not permanent decisions
- [ ] Process improvements are driven by **data from metrics**, not opinions
- [ ] The feedback loop from Phase 5 actively influences Phases 1–4
