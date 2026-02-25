#!/bin/bash
# Developer setup script for viflo
# Usage: ./scripts/setup-dev.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Setting up viflo development environment..."
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d ".agent" ]; then
    echo -e "${RED}❌ Error: Please run this script from the viflo repository root${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

echo "📋 Checking prerequisites..."

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "   Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | sed 's/v//')
REQUIRED_NODE=$(cat .nvmrc | tr -d 'v')

if ! version_ge "$NODE_VERSION" "$REQUIRED_NODE"; then
    echo -e "${RED}❌ Node.js version $NODE_VERSION is too old (required: $REQUIRED_NODE+)${NC}"
    echo "   Please upgrade Node.js"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"

# Check pnpm
if ! command_exists pnpm; then
    echo -e "${RED}❌ pnpm is not installed${NC}"
    echo "   Please install pnpm: npm install -g pnpm"
    exit 1
fi

PNPM_VERSION=$(pnpm --version)
if ! version_ge "$PNPM_VERSION" "10.0.0"; then
    echo -e "${YELLOW}⚠ pnpm version $PNPM_VERSION (recommended: 10.0.0+)${NC}"
else
    echo -e "${GREEN}✓${NC} pnpm $PNPM_VERSION"
fi

# Check Python (for pre-commit)
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "   Please install Python 3 from https://python.org/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2)"

# Check pre-commit
if ! command_exists pre-commit; then
    echo -e "${YELLOW}⚠ pre-commit is not installed${NC}"
    echo "   Installing pre-commit..."
    pip3 install pre-commit || pip install pre-commit
    if ! command_exists pre-commit; then
        echo -e "${RED}❌ Failed to install pre-commit${NC}"
        exit 1
    fi
fi

PRE_COMMIT_VERSION=$(pre-commit --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} pre-commit $PRE_COMMIT_VERSION"

echo ""
echo "📦 Installing dependencies..."

# Install dependencies
if [ -d "node_modules" ]; then
    echo "   node_modules exists, running pnpm install..."
else
    echo "   Fresh install..."
fi

pnpm install

echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""
echo "🔧 Setting up pre-commit hooks..."

# Auto-attempt deterministic security hook setup. Fail open with loud remediation.
if bash scripts/setup-security-hooks.sh; then
    echo -e "${GREEN}✓${NC} Pre-commit hooks installed"
else
    echo ""
    echo -e "${YELLOW}================================================================${NC}"
    echo -e "${YELLOW}WARNING: security hooks setup failed${NC}"
    echo "Commits and pull requests can fail CI until hooks are installed."
    echo "Run: bash scripts/setup-security-hooks.sh"
    echo "Docs: CONTRIBUTING.md#pre-commit-hooks-secret-scanning"
    echo -e "${YELLOW}================================================================${NC}"
fi

echo ""
echo "🧪 Verifying setup..."

# Verify node_modules exists in workspace packages
if [ ! -d "apps/web/node_modules" ]; then
    echo -e "${RED}❌ apps/web/node_modules not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Workspace packages have dependencies"
if [ -f ".git/hooks/pre-commit" ]; then
    echo -e "${GREEN}✓${NC} Pre-commit hooks are active"
else
    echo -e "${YELLOW}⚠ Pre-commit hooks are not active (run: bash scripts/setup-security-hooks.sh)${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  - Run tests:          pnpm test"
echo "  - Run lint:           pnpm run lint"
echo "  - Run type-check:     pnpm run type-check"
echo "  - Make a commit:      git commit (pre-commit hooks will run)"
echo ""
echo "For more information, see CONTRIBUTING.md"
