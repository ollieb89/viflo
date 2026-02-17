# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pumpl AI Local is the ML infrastructure for the Pumpl fitness platform. It handles:
- LoRA fine-tuning of LLMs for workout generation (currently Qwen3-4B, previously Llama 3.1 8B / Mistral 7B)
- Inference serving with BitsAndBytes quantization
- Training data generation via Claude distillation
- End-to-end ML pipeline orchestration with DVC

**Key Architecture**: All code lives in `src/`, models in `models/`, and training data in `data/`.

## Repository Structure

```
ml-local/
├── src/                      # All Python code
│   ├── config/               # Path & MLflow configuration
│   ├── core/                 # Logging, GPU, errors, I/O
│   ├── data/                 # Data processing & generation
│   ├── training/             # LoRA fine-tuning with Unsloth
│   ├── inference/            # BitsAndBytes and vLLM servers
│   ├── evaluation/           # Model evaluation & metrics
│   ├── merging/              # Model merging
│   ├── quantization/         # AWQ quantization
│   ├── pipeline/             # End-to-end orchestration
│   ├── deployment/           # Model registry (MLflow)
│   ├── schemas/              # Pydantic models
│   ├── context/              # Runtime state management
│   └── utils/                # Utilities
│
├── data/                     # Training data only
│   ├── raw/                  # Source datasets (DVC)
│   ├── processed/            # Transformed data (DVC)
│   ├── validated/            # Quality-checked data
│   └── workouts/             # Final training JSONL (DVC)
│
├── models/                   # Model weights only
│   ├── base/                 # Base models (DVC)
│   └── adapters/             # LoRA adapters (DVC)
│
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── docs/                     # All documentation
├── outputs/                  # Training outputs (gitignored)
│
└── [Root config files]
    ├── pixi.toml             # Environment & task definitions
    ├── pytest.ini            # Test configuration
    ├── dvc.yaml              # ML pipeline stages
    └── params.yaml           # Pipeline hyperparameters
```

## Development Commands

**Always use `pixi run` prefix** - never bare `python` or `pytest`.

```bash
# Environment setup (from ml-local/)
pixi install && pixi shell

# Inference server
pixi run serve              # Port 8000, 4-bit quantization
pixi run serve-dev          # With hot reload
pixi run serve-vllm         # High-throughput vLLM server

# Training
pixi run train              # Default training
pixi run train-full         # Full workout config

# Testing and quality
pixi run test               # pytest tests/
pixi run lint               # ruff check
pixi run format             # ruff format

# Run specific test file
pixi run pytest tests/test_foo.py

# Run tests by marker
pixi run pytest -m unit
pixi run pytest -m "not gpu"

# DVC pipeline
dvc repro                   # Run full pipeline
dvc dag                     # View pipeline DAG
dvc params diff             # Compare parameter changes
pixi run dvc-pull           # Pull data from remote
pixi run dvc-push           # Push data to remote
```

## Pixi Environments

Uses pixi with feature-based environments defined in `pixi.toml`:

- **gpu** - Training and inference (CUDA 12.8+, PyTorch, includes api feature)
- **data** - Data processing (DVC, MLflow, Polars, Databricks SDK)
- **test** - Testing (pytest, ruff, mypy, pre-commit)
- **api** - Inference server (FastAPI, uvicorn)

There is no default "all features" environment. Use the appropriate environment:
```bash
pixi run -e data dvc-pull    # Data environment only
pixi run -e gpu serve        # GPU environment (includes api)
pixi run -e test pytest      # Test environment only
```

## Path Configuration System

All paths use `src/config/paths.py` with smart resolution:

1. Environment variable (if set)
2. Project-local default (`./data/`, `./models/`)

Key functions:
- `get_model_path()` - Base model (`models/base/llama-3.1-8b-instruct`)
- `get_lora_final_path()` - Production LoRA adapter (`models/adapters/...`)
- `get_training_data_path()` - Training JSONL files (`data/workouts/`)
- `get_data_raw_path()` / `get_data_processed_path()` - Data pipeline

Key env vars in `.env`:
- `PUMPL_BASE_MODEL` - Active base model path (e.g., `./models/base/qwen3-4b-instruct`)
- `PUMPL_PROMPT_STYLE` - Prompt formatting (`auto` | `chat_template` | `mistral_inst`)
- `PUMPL_SYSTEM_PROMPT` - System prompt for inference

## Key Patterns

### Unsloth Training

Training uses Unsloth for 2x speedup. Import order matters:
```python
import unsloth  # MUST be first
from unsloth import FastLanguageModel
```

### Pydantic Schemas

All schemas are centralized in `src/schemas/`:
```python
from src.schemas.workout import Exercise, WorkoutDay, WorkoutPlanResponse
from src.schemas.training import TrainingExample, TrainingConfig
from src.schemas.inference import InferenceRequest, InferenceResponse
```

### Inference Request

```python
# POST to /generate
{
    "prompt": "Create a 30-minute HIIT workout",
    "max_tokens": 2048,
    "temperature": 0.7
}
```

## DVC Pipeline Architecture

The ML pipeline is defined in `dvc.yaml` with 11 stages:

1. **process_raw_data** - Convert CSV/Arrow to JSONL
2. **generate_data** - Generate synthetic training data
3. **validate_data** - Quality checks (JSON validity, schema compliance)
4. **merge_datasets** - Combine validated datasets
5. **split_dataset** - Train/val/test split (80/10/10)
6. **train_lora** - LoRA fine-tuning with Unsloth
7. **evaluate_model** - Quality metrics and benchmarks
8. **check_quality_gates** - Production readiness checks
9. **merge_lora** - Merge adapter with base model
10. **quantize_awq** - AWQ 4-bit quantization
11. **register_model** - MLflow model registry

Pipeline parameters are in `params.yaml` and tracked by DVC.

## VRAM Requirements

| Server Type | VRAM | Use Case |
|-------------|------|----------|
| BNB 4-bit | 10-12GB | Production (RTX 3080+) |
| BNB 8-bit | 14-16GB | Better quality |
| AWQ | 5-6GB | Memory-constrained |
| vLLM | 16GB+ | High-throughput |

## External Dependencies

- **CUDA 12.8+** with RTX 5070 Ti support (Blackwell sm_120)
- **PyTorch nightly** (2.8.0+) from `cu128` index for sm_120 support
- **Unsloth** from conda-forge for Qwen3 and newer models

## Testing

Pytest configuration in `pytest.ini`. Test directories:
- `tests/` - Standard tests (auto-discovered)
- `tests/gpu/` - GPU-required tests (excluded by default via `norecursedirs`)
- `tests/manual/` - Manual verification tests (excluded by default)
- `tests/needs-update/` - Tests needing updates (excluded by default)

Markers: `unit`, `integration`, `slow`, `gpu`

Python path includes both `.` and `src` (set in `pytest.ini`).

## Pre-commit Hooks

```bash
./scripts/setup-pre-commit.sh
# Runs: ruff, mypy, detect-secrets, YAML/TOML validation
```

## Submodule Workflow

This is a git submodule of the `pumplai` monorepo. Commit changes in two steps:

```bash
# 1. Commit in ml-local
cd ml-local
git add . && git commit -m "feat: improvement"
git push origin main

# 2. Update parent reference
cd ..
git add ml-local
git commit -m "chore: update ml-local"
```
