# Contributing to Viflo

Thank you for your interest in contributing to Viflo! We welcome contributions from the community and are excited to work with developers, documentation writers, and agentic workflow enthusiasts.

This guide explains how to contribute effectively and get your changes merged quickly.

---

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this standard. Please report unacceptable behavior to the maintainers.

---

## Ways to Contribute

- **Bug reports**: Found something that's broken? Let us know.
- **Feature requests**: Have an idea that would make Viflo better?
- **Skill contributions**: Create a new `.agent/skills/` package for the community.
- **Documentation improvements**: Fix typos, improve clarity, add examples.
- **Pull requests**: Implement a fix or feature you'd like to see.

---

## Reporting Bugs

Before filing a bug report, please check the [existing issues](https://github.com/your-org/viflo/issues) to avoid duplicates.

When you do open a bug report, use the **Bug Report** issue template and include:

1. A clear, descriptive title
2. Steps to reproduce the problem
3. What you expected to happen
4. What actually happened
5. Your environment (OS, Node.js version, Python version, tool versions)
6. Any relevant logs or screenshots

The more detail you provide, the faster we can diagnose and fix the issue.

---

## Suggesting Features

We use GitHub Issues to track feature requests. Use the **Feature Request** issue template.

Good feature requests explain:

- The problem you're trying to solve (not just the solution)
- How the feature fits the Viflo philosophy (Planning-First, hybrid model strategy)
- Any alternatives you've considered
- Whether you'd be willing to implement it yourself

---

## Contributing a New Skill

Skills are the heart of Viflo — reusable knowledge packages that AI agents load as context. If you've developed patterns or guidelines that work well, consider packaging them as a skill.

See [docs/CREATING_SKILLS.md](./docs/CREATING_SKILLS.md) for the complete skill creation guide.

Use the **Skill Suggestion** issue template to propose a skill before building it, so we can align on scope.

---

## Submitting Pull Requests

### Step 1: Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/viflo.git
cd viflo
git remote add upstream https://github.com/your-org/viflo.git
```

### Step 2: Create a Branch

Use a descriptive branch name:

```bash
# For features:
git checkout -b feat/add-rust-skill

# For bug fixes:
git checkout -b fix/skill-frontmatter-validation

# For documentation:
git checkout -b docs/improve-getting-started
```

### Step 3: Set Up the Development Environment

We provide an automated setup script that handles all dependencies and pre-commit hook installation:

```bash
# Run the setup script
./scripts/setup-dev.sh
```

This script will:

- Check for required tools (Node.js 20+, pnpm, Python 3, pre-commit)
- Install all dependencies with `pnpm install`
- Set up pre-commit hooks for secret scanning
- Verify the setup is working correctly

#### Manual Setup (if you prefer)

If you prefer to set up manually:

```bash
# Install Node.js dependencies
pnpm install

# Install pre-commit hooks
pip3 install pre-commit
pre-commit install

# Verify your environment
python3 scripts/verify_env.py
```

#### Pre-commit Hooks (Secret Scanning)

This repository uses [pre-commit](https://pre-commit.com/) to run secret scanning before every commit. The hooks run `gitleaks` and `detect-secrets` to prevent accidental credential exposure.

If you used `./scripts/setup-dev.sh`, hooks are already installed. To run them manually against all files:

```bash
pre-commit run --all-files
```

If a commit is blocked, the hook will print the detected secret's file and line. Remove the secret, use an environment variable instead, and re-commit.

### Step 4: Make Your Changes

Follow these conventions:

- **Planning-First**: For significant changes, open an issue first to discuss the approach.
- **Atomic commits**: Each commit should represent one logical change.
- **Commit message format**: `type(scope): concise description`
  - Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
  - Examples: `feat(skills): add rust-patterns skill`, `fix(scripts): handle missing env vars`
- **No breaking changes** without a major version bump and prior discussion.

### Step 5: Test Your Changes

```bash
# Run the environment verification
python3 scripts/verify_env.py

# If you added or modified a skill, verify the SKILL.md frontmatter is valid YAML
# and that all referenced files exist
```

For documentation changes, read the rendered output carefully for clarity and accuracy.

#### CI Policy and MCP Probe Mode

Our standard CI pipeline runs deterministically to ensure reliable and fast feedback on pull requests. Tests that interact with external MCP servers (which might introduce flakiness) are disabled by default.

However, we provide an optional **MCP probe mode** for testing agentic workflows that hit actual endpoints. You can trigger these extended tests by running the benchmark commands locally with the following environment variables:

```bash
MCP_PROBE_CMD=true ALLOW_FLAKY_PROBES=1 pnpm run bench:sc-reflect
```

These tests also run automatically in our nightly benchmark workflows to monitor the health of the agent integrations over time without blocking everyday development.

### Step 6: Push and Open a PR

```bash
git push origin your-branch-name
```

Then open a pull request on GitHub using the **Pull Request Template**. Fill in all sections — an incomplete PR description slows down review.

---

## Development Setup Details

### Requirements

| Tool    | Version    | Purpose                       |
| ------- | ---------- | ----------------------------- |
| Node.js | 20+        | Toolchain (Claude Code, etc.) |
| pnpm    | 10.0.0+    | Package management            |
| Python  | 3.10+      | Verification scripts          |
| Git     | Any recent | Version control               |
| Ollama  | Optional   | Local model execution         |

### Environment Variables

Copy `.env.template` to `.env` and configure:

```bash
cp .env.template .env
```

Required keys (depending on which tools you use):

- `ANTHROPIC_API_KEY` — For Claude Code
- `GEMINI_API_KEY` — For Gemini models

### Project Structure

| Path                | What's There                                |
| ------------------- | ------------------------------------------- |
| `.agent/skills/`    | Skill packages (the main contribution area) |
| `.agent/rules/`     | Coding rules by technology                  |
| `.agent/workflows/` | Workflow definitions                        |
| `docs/`             | Viflo methodology documentation             |
| `scripts/`          | Setup and verification scripts              |
| `packages/`         | Shared TypeScript packages                  |

---

## Skill Contributions

Skills are the primary way the community extends Viflo. A high-quality skill:

- Covers a specific technology, pattern, or domain
- Has a well-structured `SKILL.md` with accurate frontmatter
- Includes practical rules in `rules/` subdirectories
- Optionally includes scripts, templates, or examples
- Is tested by actually using it with an AI agent

See [docs/CREATING_SKILLS.md](./docs/CREATING_SKILLS.md) for full details.

---

## Review Process

1. A maintainer will review your PR, usually within a few days.
2. We may request changes — this is normal and not a rejection.
3. Once approved, a maintainer will merge your PR.
4. Your contribution will appear in the next release.

We review for: correctness, clarity, consistency with Viflo philosophy, and impact.

---

## Questions?

If you're unsure about something, open a [Discussion](https://github.com/your-org/viflo/discussions) or ask in an issue. We'd rather answer a question than have you spend time going in the wrong direction.

Thank you for helping make Viflo better for everyone.
