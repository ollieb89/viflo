# Creating Skills for Viflo

Skills are reusable knowledge packages that AI agents load as context when working on specific tasks. A skill tells the agent _how to do something well_ — encoding best practices, patterns, and conventions that would otherwise have to be communicated through lengthy prompts.

This guide explains how to create a skill that the community can use and benefit from.

---

## What Is a Skill?

A skill lives in `.agent/skills/<skill-name>/` and contains:

- A `SKILL.md` — the primary knowledge document the AI reads
- Optionally: `rules/`, `scripts/`, `references/`, `templates/`, `examples/`

When an AI agent is working on a relevant task, it loads the `SKILL.md` (and any referenced files) into its context. The skill's job is to give the agent accurate, actionable guidance so it produces better output than it would from training data alone.

---

## Directory Structure

```
.agent/skills/
└── your-skill-name/
    ├── SKILL.md              # Required: main knowledge document
    ├── rules/                # Optional: focused rule files
    │   ├── naming.md
    │   ├── patterns.md
    │   └── testing.md
    ├── scripts/              # Optional: helper scripts
    │   ├── generate.sh
    │   └── validate.py
    ├── references/           # Optional: reference documents
    │   └── api-reference.md
    ├── templates/            # Optional: starter templates
    │   └── component.tsx
    └── examples/             # Optional: worked examples
        └── example-usage.md
```

The `SKILL.md` is the only required file. Keep it focused — a skill that does one thing well is more useful than one that covers everything superficially.

---

## SKILL.md Format

Every `SKILL.md` starts with YAML frontmatter followed by the knowledge content.

### Frontmatter

```yaml
---
name: your-skill-name
description: |
  A clear description of what this skill teaches.
  Include trigger phrases — the situations where an AI should load this skill.
  Example: "Use when creating FastAPI endpoints, designing database schemas,
  or implementing authentication. Triggers on phrases like 'FastAPI endpoint',
  'SQLAlchemy model', 'Pydantic schema'."
triggers:
  - Creating FastAPI endpoints # Optional: explicit trigger list
  - Designing database models
  - Implementing authentication
version: "1.0" # Optional but recommended
tags: [backend, python, fastapi] # Optional: for discoverability
---
```

**Required fields:**

- `name` — Must match the directory name exactly (kebab-case)
- `description` — One or two paragraphs. The first sentence should clearly state what the skill covers. Include trigger conditions so agents know when to load it.

**Optional but recommended:**

- `triggers` — Explicit list of situations that warrant loading this skill
- `version` — Semantic version for tracking changes
- `tags` — Keywords for discoverability

### Content Structure

After the frontmatter, write the skill content in Markdown. Structure it for AI consumption:

```markdown
# Skill Name

## Overview

Brief summary of what this skill covers and why it matters.

## When to Use This Skill

- Specific situation 1
- Specific situation 2

## Core Principles

High-level rules that govern all decisions in this domain.

## Patterns

### Pattern Name

Explanation with code example.

## Common Mistakes

Things agents (and humans) frequently get wrong — and how to avoid them.

## Quick Reference

Tables, checklists, or command references for fast lookup.
```

---

## Writing Good Skill Content

### Be Specific and Actionable

Vague advice is useless. Compare:

**Too vague:**

> Write clean code with good error handling.

**Actionable:**

> Every FastAPI endpoint must:
>
> 1. Validate input with a Pydantic model (never raw `dict`)
> 2. Return typed response models (never `dict` or `Any`)
> 3. Raise `HTTPException` with meaningful status codes, not return error strings
> 4. Include a docstring that becomes the OpenAPI description

### Include Code Examples

AI agents learn from examples. For every rule, show the correct pattern:

````markdown
## Repository Pattern

Always use the repository pattern. Never query the database directly in endpoint handlers.

**Correct:**

```python
# endpoints/users.py
@router.get("/users/{user_id}")
async def get_user(user_id: int, repo: UserRepo = Depends(get_user_repo)):
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)
```
````

**Incorrect:**

```python
# Direct DB access in endpoint — avoid this
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)  # Wrong: bypass repository
    return user
```

````

### Document "Why", Not Just "What"

An agent that understands the reasoning makes better decisions in edge cases:

```markdown
## Use `model_validate()` instead of `Model(**data)`

Pydantic v2's `model_validate()` is required for ORM mode (converting SQLAlchemy objects
to Pydantic schemas). It also provides better error messages and is the v2 idiomatic approach.
`Model(**data)` works for dicts but silently fails with ORM objects.
````

### Avoid Hallucination Traps

Skills should correct common AI hallucinations for the domain:

```markdown
## Common AI Mistakes to Avoid

- **Wrong:** `session.query(User).filter(...)` — this is SQLAlchemy 1.x syntax
- **Right:** `select(User).where(...)` — use SQLAlchemy 2.0 core style
- **Wrong:** `@validator` decorator — this is Pydantic v1
- **Right:** `@field_validator` decorator — Pydantic v2
```

---

## Subdirectory Files

### rules/

For complex skills, split detailed rules into focused files rather than one monolithic `SKILL.md`. Reference them from the main skill:

```markdown
## Detailed Rules

- [Naming conventions](rules/naming.md)
- [Error handling patterns](rules/error-handling.md)
- [Testing requirements](rules/testing.md)
```

Keep each rules file focused on a single concern. 100-300 lines is a good target — long enough to be comprehensive, short enough to be loaded without dominating context.

### scripts/

Include scripts that help developers or agents execute the skill's patterns:

- **Generators**: Scaffold boilerplate that follows the skill's conventions
- **Validators**: Check that existing code follows the rules
- **Setup scripts**: Install dependencies or configure tooling

Scripts should be self-contained and include usage comments at the top.

### references/

For external knowledge that an agent might need: API reference tables, comparison charts, decision guides. These are loaded on demand, not by default.

### templates/

Starter files for new projects or components. A template should be immediately usable with minimal modification — not a generic scaffold that still needs significant filling in.

---

## Testing Your Skill

Before submitting, verify your skill actually improves AI output:

1. **Start a fresh agent session** — no prior context about the domain.
2. **Give the agent a task** that the skill is designed to help with.
3. **Load the skill** and ask the agent the same task.
4. **Compare the output**: Is it noticeably better, more accurate, or more idiomatic?

A skill that doesn't produce measurably better output doesn't belong in the collection.

**Specific checks:**

- [ ] `SKILL.md` frontmatter is valid YAML (no syntax errors)
- [ ] `name` field matches directory name exactly
- [ ] `description` field clearly explains when to use the skill
- [ ] All files referenced in `SKILL.md` exist
- [ ] All scripts are executable and include usage documentation
- [ ] Code examples are syntactically correct and follow the skill's own rules
- [ ] Tested with an actual AI agent session

---

## Naming Conventions

Skill directories use **kebab-case** and follow this pattern:

| Pattern                   | Examples                                            |
| ------------------------- | --------------------------------------------------- |
| `{technology}-patterns`   | `react-patterns`, `rust-patterns`                   |
| `{technology}-guidelines` | `frontend-dev-guidelines`, `backend-dev-guidelines` |
| `{domain}-design`         | `database-design`, `api-design-principles`          |
| `{technology}-{type}`     | `fastapi-templates`, `postgresql`                   |

Avoid generic names like `best-practices` or `guidelines` — be specific about what domain the skill covers.

---

## Submitting a Skill

1. Create your skill in a feature branch: `git checkout -b feat/add-your-skill-name`
2. Write the skill following this guide
3. Test with an actual AI agent
4. Open a pull request using the [Skill Suggestion issue template](../.github/ISSUE_TEMPLATE/skill_suggestion.md) first (optional but recommended for larger skills)
5. Reference the issue in your PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the full contribution workflow.

---

## Examples

The following existing skills are good references for style and structure:

| Skill                     | What to Study                                     |
| ------------------------- | ------------------------------------------------- |
| `backend-dev-guidelines`  | Comprehensive tech stack skill with code examples |
| `frontend-dev-guidelines` | Trigger phrase examples, "when to use" clarity    |
| `gsd-workflow`            | Procedural skill covering a methodology           |
| `database-design`         | Reference tables and decision guides              |
| `ci-cd-pipelines`         | Multi-platform skill with workflow examples       |

---

## Questions?

Open a [GitHub Discussion](https://github.com/your-org/viflo/discussions) or use the **Skill Suggestion** issue template to get feedback before investing significant time.
