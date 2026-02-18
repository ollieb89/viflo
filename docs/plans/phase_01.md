# 1. Discover and Choose the Right LLMs

## Proprietary Models (High Performance)

### Gemini 3 Pro
- **Strengths:** Leading coding and reasoning benchmarks (2026). ~2M token context window. Excellent inside Google ecosystem.
- **Setup:**
  1. Get API Key from [Google AI Studio](https://aistudio.google.com/).
  2. Install SDK: `pip install -q -U google-genai`
  3. Env Var: `export GEMINI_API_KEY="your_key"`

### GPT-5 (5.1 Pro / Auto)
- **Strengths:** Excellent general-purpose reasoning. Strong multi-step code workflows. Widely supported via CLI integrations.
- **Setup:**
  1. Get API Key from [OpenAI Platform](https://platform.openai.com/).
  2. Install SDK: `pip install openai`
  3. Env Var: `export OPENAI_API_KEY="your_key"`

### Claude 4.6 Sonnet / Opus 4.5
- **Strengths:** Deep architectural reasoning. Excellent for structured plans and debugging.
- **Setup:**
  1. Get API Key from [Anthropic Console](https://console.anthropic.com/).
  2. Install SDK: `pip install anthropic`
  3. Env Var: `export ANTHROPIC_API_KEY="your_key"`

### Grok 4.1
- **Strengths:** Extremely long context. Useful for very large repositories and complex reasoning.
- **Setup:**
  1. Get API Key from [xAI Console](https://console.x.ai/).
  2. Env Var: `export XAI_API_KEY="your_key"`

### DeepSeek R1
- **Strengths:** Top-tier reasoning capabilities at a budget-friendly price point.
- **Setup:**
  - **Cloud:** Get API Key from DeepSeek Platform.
  - **Local:** See Open-Source section below.

## Proprietary Models (Code Execution)

### GPT-5 Mini / GPT-4.5
- **Best For:** Fast, correct script generation; tests + examples from specs.
- **Strengths:** Ultra-low latency, low cost. Daily Python/FastAPI/ML pipelines.

### Claude 3.7 Sonnet / 4.6 Haiku
- **Best For:** CLI scripts, repo edits.
- **Strengths:** Reliable for env/debug loops. Fast, moderate cost.

### Gemini 3 Flash
- **Best For:** Quick fixes, short tasks; huge context for multi-file plans.
- **Strengths:** Very fast, cheap. JS/TS (Vue/Nuxt) or data scripts.

------------------------------------------------------------------------

## Open-Source Models (Cost-Optimized)

### DeepSeek R1 / V3
- **Strengths:** Competitive coding performance. Cost-efficient or free (local).
- **Setup (Local):**
  1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
  2. Run: `ollama run deepseek-r1`

### Qwen 2.5-Coder
- **Strengths:** Excellent local deployment support. Privacy-first option.
- **Setup (Local):** `ollama run qwen2.5-coder`

------------------------------------------------------------------------

## Development Tools (CLIs & IDEs)

### Agentic CLIs
- **Aider**
  - **Best For:** Multi-file editing, git-aware refactoring.
  - **Setup:** `pip install aider-chat`
  - **Run:** `aider` (Ensure relevant API key is set, e.g., `ANTHROPIC_API_KEY`)

- **Claude Code**
  - **Best For:** Autonomous coding tasks, deep integration with Claude capabilities.
  - **Setup:** `npm install -g @anthropic-ai/claude-code`
  - **Init:** `claude-code init`

### AI Native IDEs
- **Windsurf** (by Codeium)
  - **Best For:** Deeply integrated AI editor workflow (Cascade).
  - **Setup:** Download from [windsurf.ai](https://windsurf.ai/).

- **Cursor**
  - **Best For:** VS Code fork with powerful AI chat and composer features.
  - **Setup:** Download from [cursor.com](https://cursor.com/).
