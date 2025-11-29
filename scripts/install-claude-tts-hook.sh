#!/bin/bash
#
# install-claude-tts-hook.sh
#
# Sets up the TTS Response Hook for Claude Code integration.
# This hook speaks Claude's responses aloud using macOS 'say' command.
#
# WARNING: This is a brittle integration that may break with Claude Code updates.
#
# Usage: ./scripts/install-claude-tts-hook.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "  Claude Code TTS Hook Installer"
echo "======================================"
echo ""

# Find script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOK_SCRIPT="$PROJECT_ROOT/src/push_to_talk_claude/hooks/stop_hook.sh"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

# Check prerequisites
echo "Checking prerequisites..."

# Check macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}Error: This script only works on macOS${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} macOS detected"

# Check jq
if ! command -v jq &> /dev/null; then
    echo -e "  ${YELLOW}!${NC} jq not found"
    echo ""
    echo "Please install jq first:"
    echo "  brew install jq"
    echo ""
    exit 1
fi
echo -e "  ${GREEN}✓${NC} jq installed ($(jq --version))"

# Check hook script exists
if [[ ! -f "$HOOK_SCRIPT" ]]; then
    echo -e "${RED}Error: Hook script not found at $HOOK_SCRIPT${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Hook script found"

# Check Claude Code settings directory
if [[ ! -d "$HOME/.claude" ]]; then
    echo -e "  ${YELLOW}!${NC} ~/.claude directory not found"
    echo "Please run Claude Code at least once before installing this hook."
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Claude Code directory exists"

echo ""
echo "Setting up hook..."

# Make hook script executable
chmod +x "$HOOK_SCRIPT"
echo -e "  ${GREEN}✓${NC} Made hook script executable"

# Create or update settings.json
if [[ -f "$CLAUDE_SETTINGS" ]]; then
    # Check if hooks.Stop already exists
    if jq -e '.hooks.Stop' "$CLAUDE_SETTINGS" &> /dev/null; then
        echo -e "  ${YELLOW}!${NC} Stop hook already configured in settings.json"
        echo ""
        echo "Existing Stop hook found. To avoid conflicts, please manually update:"
        echo "  $CLAUDE_SETTINGS"
        echo ""
        echo "Add this command to your existing Stop hooks:"
        echo "  $HOOK_SCRIPT"
        exit 0
    fi

    # Add hooks to existing settings
    TEMP_FILE=$(mktemp)
    jq --arg cmd "$HOOK_SCRIPT" '.hooks = (.hooks // {}) | .hooks.Stop = [{"matcher": "*", "hooks": [{"type": "command", "command": $cmd}]}]' "$CLAUDE_SETTINGS" > "$TEMP_FILE"
    mv "$TEMP_FILE" "$CLAUDE_SETTINGS"
    echo -e "  ${GREEN}✓${NC} Added Stop hook to existing settings.json"
else
    # Create new settings.json
    cat > "$CLAUDE_SETTINGS" << EOF
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "$HOOK_SCRIPT"
          }
        ]
      }
    ]
  }
}
EOF
    echo -e "  ${GREEN}✓${NC} Created settings.json with Stop hook"
fi

# Create flag file directory
mkdir -p "$HOME/.claude-voice"
echo -e "  ${GREEN}✓${NC} Ensured ~/.claude-voice directory exists"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "======================================"
echo "  Next Steps"
echo "======================================"
echo ""
echo "1. Start the TUI:"
echo "   uv run claude-voice"
echo ""
echo "2. Press 's' to enable Speak Responses"
echo ""
echo "3. Ask Claude something - you'll hear the response!"
echo ""
echo -e "${YELLOW}Note: This is a brittle integration that may break"
echo -e "with Claude Code updates. See docs/claude-code-hook-setup.md${NC}"
echo ""
