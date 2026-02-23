---
name: Skill Suggestion
about: Propose a new skill package for the .agent/skills/ directory
title: "[Skill] "
labels: ["skill", "needs-triage"]
assignees: ""
---

## Skill Name

Proposed directory name (kebab-case, e.g., `rust-patterns`, `graphql-api`):

## Description

A 1-2 sentence description of what this skill teaches an AI agent.

## Problem This Skill Solves

What does an AI agent currently get wrong or struggle with in this domain that this skill would fix?

## Target Technology / Domain

What technology, framework, pattern, or domain does this skill cover?

## Proposed Contents

What would this skill include? Check all that apply:

- [ ] `SKILL.md` — Main knowledge document with rules and patterns
- [ ] `rules/` — Subdirectory with focused rule files
- [ ] `scripts/` — Helper scripts (generators, validators, etc.)
- [ ] `templates/` — Project or file templates
- [ ] `examples/` — Example code or configurations

## SKILL.md Frontmatter Draft

```yaml
---
name: your-skill-name
description: |
  What this skill is about and when to load it.
  Include trigger phrases the AI should recognize.
---
```

## Example Use Case

Describe a concrete scenario where loading this skill would produce noticeably better AI output. What would the agent do differently with this skill vs without it?

## Do You Want to Build It?

- [ ] Yes, I'll submit a PR with the full skill
- [ ] I can contribute a draft, but would need review
- [ ] I'm suggesting it for someone else to build

## References / Prior Art

Any existing resources, guides, or codebases that the skill could draw from?
