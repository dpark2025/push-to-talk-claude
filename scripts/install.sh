#!/bin/bash
# Push-to-Talk Claude Voice Interface - Installation Script
# Usage: ./scripts/install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎙️  Push-to-Talk Claude Voice Interface Installer"
echo "=================================================="
echo ""

# Check macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This tool only supports macOS"
    exit 1
fi

# Step 1: Install Homebrew dependencies
echo "📦 Step 1: Installing system dependencies..."
"$SCRIPT_DIR/install-brew-deps.sh"
echo ""

# Step 2: Install Python package
echo "🐍 Step 2: Installing Python package..."
if command -v uv &> /dev/null; then
    cd "$PROJECT_DIR"
    uv sync
else
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env" 2>/dev/null || true
    cd "$PROJECT_DIR"
    uv sync
fi
echo ""

# Step 3: Check permissions
echo "🔐 Step 3: Checking permissions..."
"$SCRIPT_DIR/check-permissions.sh"
echo ""

# Step 4: Create default config
echo "⚙️  Step 4: Setting up configuration..."
CONFIG_DIR="$HOME/.claude-voice"
if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    cp "$PROJECT_DIR/config.default.yaml" "$CONFIG_DIR/config.yaml"
    echo "Created default config at $CONFIG_DIR/config.yaml"
else
    echo "Config directory exists: $CONFIG_DIR"
fi
echo ""

# Done
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start Claude Code in tmux: tmux new-session -s claude 'claude'"
echo "2. In another terminal: uv run claude-voice"
echo "3. Press and hold Right Ctrl to speak"
echo ""
