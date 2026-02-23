---
name: generate-readme
description: Generates a comprehensive, GitHub-optimized README.md for the current project using the github-readme-writer skill.
---

# Generate GitHub README

This workflow orchestrates the creation of a high-quality `README.md` file by leveraging the **GitHub README Writer** skill.

## 1. Activate Skill Context

- **Load Skill**: Read and adopt the persona defined in the skill file:
  - `@.agent/skills/github-readme-writer/SKILL.md`
- **Role**: You are now the "GitHub README Writer." Adhere strictly to the tone, structure, and formatting guidelines defined in that skill file.

## 2. Analysis & Planning

- **Analyze Context**: Scan the project structure at the root (`@/`) to understand the language, framework, key features, and entry points.
- **Draft Plan**: Before writing the final file, generate a **Plan Artifact** that outlines the proposed structure of the README.
  - _Required Sections_: Title, Description, Key Features, Installation/Getting Started, Usage, Support, and Maintenance.
  - _Constraint_: Ensure the plan aligns with the complexity of the analyzed code (e.g., don't add "Deployment" sections for a simple utility script).

## 3. Execution

- **Write Content**: Upon plan validation, generate the `README.md` file in the project root.
- **Formatting Rules**:
  - Use **GitHub Flavored Markdown (GFM)**.
  - Use relative links for internal file references.
  - Ensure code blocks have correct language tagging (e.g., ````python`).
  - Do not include large binary files or absolute local paths.

## 4. Verification

- **Review**: Perform a self-review of the generated `README.md`.
  - Check that all links are valid.
  - Verify that installation commands (e.g., `npm install`, `pip install`) match the detected dependency files (`package.json`, `requirements.txt`).
