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
