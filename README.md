# Viflo: The Universal Agentic Development Environment

> **Maximize velocity, minimize cost, and eliminate technical debt through hybrid AI strategies.**

Viflo is a comprehensive development methodology and toolchain designed to standardize and accelerate agentic software development. By combining detailed planning protocols with a hybrid model strategy (proprietary reasoning + open-source execution), Viflo ensures that AI-generated code is robust, maintainable, and cost-effective.

## 🚀 Key Features

- **Hybrid Model Strategy**: Intelligent routing of tasks to the most effective model—using high-reasoning models (gemini-2.0-pro-exp, o3-mini) for planning and open-source models (DeepSeek V3, Qwen 2.5) for execution.
- **Structured Planning Protocol**: A mandatory "Planning-First" approach where no code is written without a granular, pre-approved `PLAN.md`.
- **Agentic Workflow**: Implementation is broken down into atomic, independently testable units executed by specialized CLI agents.
- **5-Phase Lifecycle**: A complete framework covering everything from initial Model Strategy to Continuous Improvement and Iteration.

## 🛠️ Getting Started

Follow these steps to set up the Viflo environment on your local machine.

### Prerequisites

- **Git**
- **Python 3.10+** (for verification scripts)
- **Node.js & npm** (for Claude Code)
- **Ollama** (optional, but recommended for local model execution)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-org/viflo.git
    cd viflo
    ```

2.  **Configure Environment**
    Copy the template and add your API keys.
    ```bash
    cp .env.template .env
    # Edit .env and add:
    # GEMINI_API_KEY=...
    # ANTHROPIC_API_KEY=...
    ```

3.  **Install Toolchain**
    Installs core dependencies like `aider-chat` and `claude-code`.
    ```bash
    ./scripts/install_toolchain.sh
    ```

4.  **Setup Local LLMs**
    Installs Ollama and pulls the required local models (`deepseek-r1`, `qwen2.5-coder`).
    ```bash
    ./scripts/setup_local_llms.sh
    ```

5.  **Verify Setup**
    Ensure all environment variables and tools are correctly configured.
    ```bash
    python3 scripts/verify_env.py
    ```

## 📖 Usage

### Planning Phase
Start by defining your project's roadmap using the Viflo planning templates.
- Review **[Phase 1: Model Strategy](./docs/plans/phase_01.md)** to select your model portfolio.
- Use **[Phase 2: Planning Protocol](./docs/plans/phase_02.md)** to generate your `PLAN.md`.

### Execution Phase
Execute your plans using the agentic workflow described in **[Phase 3: Implementation](./docs/plans/phase_03.md)**.
- Break down tasks into small batches.
- Use the installed CLI tools to dispatch agents for implementation.

### Verification & Iteration
Ensure quality and continuous improvement.
- Follow **[Phase 4: Testing & CI](./docs/plans/phase_04.md)** for validation.
- Use **[Phase 5: Iteration](./docs/plans/phase_05.md)** for retrospective and refinement.

## 📂 Project Structure

- `docs/` - Comprehensive documentation of the Viflo phases and protocols.
    - `overview.md` - The Master Plan and project pillars.
    - `plans/` - Detailed operational plans for each phase.
- `scripts/` - Automation scripts for environment setup and verification.
- `.agent/` - Configuration and prompt templates for AI agents.

## 🤝 Contributing

We welcome contributions! Please see our [Master Plan](./docs/overview.md) to understand the core philosophy before submitting pull requests. Ensure all changes follow the "Planning-First" methodology.

## 📄 License

(Proprietary / Internal Use Only - Placeholder)
