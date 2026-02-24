---
name: skill-depth-standard
description: Use when creating or auditing skills to verify they meet Viflo's depth standard. Defines the four failure modes of shallow skills and provides a self-evaluation checklist and Gap Report template for both authors and AI-assisted audits.
---

# Skill Depth Standard

## The Four Failure Modes

Every shallow skill fails in one or more of these ways:

| Failure Mode | Symptom | Fix |
|---|---|---|
| **Abstraction Trap** | Principles without working code ("use a queue") | Add `## Implementation Patterns` with runnable examples |
| **Happy Path Bias** | No error states, race conditions, or edge inputs covered | Add `## Failure Modes & Edge Cases` section |
| **Analysis Paralysis** | Lists options without helping you choose | Add `## Decision Matrix` with explicit trade-off reasoning |
| **Technical Rot** | No version pinning; patterns may be deprecated | Add `## Version Context` with last-verified library versions |

## Self-Evaluation Checklist

Run this against any skill before marking it complete:

- [ ] `## Implementation Patterns` — contains working code, not just prose
- [ ] `## Failure Modes & Edge Cases` — covers at least 3 concrete failure scenarios
- [ ] `## Decision Matrix` — when-to-use-X-vs-Y table with explicit reasoning, not just a list
- [ ] `## Version Context` — lists last-verified versions of key libraries/frameworks
- [ ] No section is happy-path-only
- [ ] No "you can use X or Y" without a recommended default and rationale
- [ ] SKILL.md is ≤500 lines (extract to `references/` if needed)

## Gap Report Template

Use this when auditing an existing skill:

```
## Gap Report: [skill-name]

**Audited:** YYYY-MM-DD
**Overall depth score:** [1-4 / 4 failure modes addressed]

### Missing Sections
- [ ] Implementation Patterns
- [ ] Failure Modes & Edge Cases
- [ ] Decision Matrix
- [ ] Version Context

### Failure Mode Analysis
- **Abstraction Trap:** [present / absent — evidence]
- **Happy Path Bias:** [present / absent — evidence]
- **Analysis Paralysis:** [present / absent — evidence]
- **Technical Rot:** [present / absent — evidence]

### Priority
[high / medium / low] — [reason]
```

## Reference Skill

The Auth skill (`.agent/skills/auth-systems/SKILL.md`) is the canonical example of a skill built to this standard. When in doubt, use it as a structural reference.
