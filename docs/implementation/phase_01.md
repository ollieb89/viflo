# Phase 1 Implementation Plan: Universal Agentic Development Environment

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Establish the foundational "Polyglot AI Environment" enabling seamless routing between Premium (Cloud), Cheap (Cloud), and Local LLMs, along with the necessary Agentic CLI toolchain and IDE configuration.

**Architecture:**
- **Configuration:** Centralized `.env` management for API keys.
- **Local Infra:** Scripted setup of Ollama/vLLM for cost-effective local inference.
- **Toolchain:** Automated installation and configuration of Aider and Claude Code with specific model routing (Architect vs. Execution).
- **IDE:** Project-specific `.cursorrules` and settings to optimize AI context.

**Tech Stack:** Bash, Python, Node.js, Ollama, Aider, Claude Code, Cursor/Windsurf.

---

### Task 1: High-Performance Model Procurement & Configuration [Completed]

**Files:**
- Create: `.env.template`
- Modify: `.gitignore`
- Create: `scripts/verify_env.py`

**Step 1: Create .env.template**

Create a template file with standard nomenclature for required keys.

```bash
cat <<EOF > .env.template
# Premium Models
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
XAI_API_KEY=

# Optional: Secrets Manager
DOPPLER_TOKEN=
EOF
```

**Step 2: Update .gitignore**

Ensure sensitive files are ignored.

```bash
echo ".env" >> .gitignore
```

**Step 3: Create Verification Script**

Create a script to verify SDKs are installed and keys are present (basic check).

```python
# scripts/verify_env.py
import os
import sys

required_keys = ["GEMINI_API_KEY", "ANTHROPIC_API_KEY"]
missing = [key for key in required_keys if not os.getenv(key)]

if missing:
    print(f"Missing keys: {', '.join(missing)}")
    sys.exit(1)
print("Environment keys present.")
```

**Step 4: Commit**

```bash
git add .env.template .gitignore scripts/verify_env.py
git commit -m "chore: setup environment configuration templates"
```

---

### Task 2: Local Cost-Optimization Infrastructure Setup [Completed]

**Files:**
- Create: `scripts/setup_local_llms.sh`

**Step 1: Create Setup Script**

Script to install Ollama and pull specific models (DeepSeek, Qwen).

```bash
# scripts/setup_local_llms.sh
#!/bin/bash
set -e

# Detect OS and Install Ollama (Simplified)
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

# Start Ollama server in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 5
fi

# Pull Models
echo "Pulling DeepSeek V3 (Reasoning fallback)..."
ollama pull deepseek-r1

echo "Pulling Qwen 2.5 Coder (Coding)..."
ollama pull qwen2.5-coder
```

**Step 2: Make Executable**

```bash
chmod +x scripts/setup_local_llms.sh
```

**Step 3: Commit**

```bash
git add scripts/setup_local_llms.sh
git commit -m "infra: add local llm setup script"
```

---

### Task 3: Agentic CLI Toolchain Installation & Configuration [Completed]

**Files:**
- Create: `scripts/install_toolchain.sh`
- Create: `.aider.conf.yml`

**Step 1: Create Installation Script**

Installs Aider and Claude Code.

```bash
# scripts/install_toolchain.sh
#!/bin/bash
pip install -U aider-chat
npm install -g @anthropic-ai/claude-code
```

**Step 2: Configure Aider**

Create Aider config to route Architect tasks to Opus/Sonnet and Edit tasks to Flash.

```yaml
# .aider.conf.yml
model: gemini/gemini-1.5-flash
architect: true
architect-model: anthropic/claude-3-5-sonnet-20241022
editor-model: gemini/gemini-1.5-flash
weak-model: gemini/gemini-1.5-flash
cache-prompts: true
```

**Step 3: Commit**

```bash
chmod +x scripts/install_toolchain.sh
git add scripts/install_toolchain.sh .aider.conf.yml
git commit -m "chore: configure aider and toolchain scripts"
```

---

### Task 4: IDE Integration & Extension Setup [Completed]

**Files:**
- Create: `.cursorrules`
- Create: `.vscode/settings.json`

**Step 1: Create .cursorrules**

Define project-specific AI rules.

```markdown
# .cursorrules
You are an expert software engineer working on the Universal Agentic Workflow project.

# Project Context
- Stack: Next.js, Python, TypeScript.
- Rules:
  - ALWAYS use the implementation plans in docs/plans/.
  - DO NOT invent new patterns; follow docs/implementation/universal_agentic_development.md.
  - Test Driven Development (TDD) is mandatory.
```

**Step 2: Configure Editor Settings**

Exclude heavy folders to save context.

```json
// .vscode/settings.json
{
    "cursor.ai.index.exclude": {
        "**/node_modules": true,
        "**/dist": true,
        ".git": true,
        "**/.next": true
    },
    "files.exclude": {
        "**/.git": true,
        "**/.DS_Store": true
    }
}
```

**Step 3: Commit**

```bash
git add .cursorrules .vscode/settings.json
git commit -m "config: setup IDE rules and context optimization"
```
