#!/bin/bash
# Check macOS permissions for Push-to-Talk Claude

echo "Checking macOS permissions..."
echo ""

# Check Microphone permission
echo "🎤 Microphone Permission:"
# Try to access microphone briefly
if system_profiler SPAudioDataType 2>/dev/null | grep -q "Input"; then
    echo "   ✓ Audio input devices available"
    echo "   ℹ️  Microphone permission will be requested on first use"
else
    echo "   ⚠️  No audio input devices found"
fi
echo ""

# Check Accessibility permission
echo "⌨️  Accessibility Permission:"
echo "   ℹ️  Required for keyboard monitoring"
echo "   To grant: System Settings → Privacy & Security → Accessibility"
echo "   Add your terminal app (Terminal.app, iTerm, etc.)"
echo ""

# Check if running in tmux
echo "📺 tmux Status:"
if [ -n "$TMUX" ]; then
    echo "   ✓ Currently inside tmux session"
else
    echo "   ℹ️  Not in tmux (that's OK for installation)"
fi
echo ""

# Check for Claude Code
echo "🤖 Claude Code:"
if command -v claude &>/dev/null; then
    echo "   ✓ Claude Code CLI found"
else
    echo "   ⚠️  Claude Code CLI not found in PATH"
    echo "   Install: npm install -g @anthropic/claude-cli"
fi
echo ""

echo "Permission check complete."
echo "Some permissions will be requested when you first run claude-voice."
