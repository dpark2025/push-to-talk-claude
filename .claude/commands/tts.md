---
description: Control TTS response hook (on/off/toggle/status)
---

## TTS Hook Control

Control the Text-to-Speech response hook for Claude Code.

**Flag file**: `~/.claude-voice/tts-hook-enabled`

### Usage

The user requested: `$ARGUMENTS`

Based on the argument, run ONE of these commands:

| Argument | Command |
|----------|---------|
| `on` | `mkdir -p ~/.claude-voice && touch ~/.claude-voice/tts-hook-enabled && echo "TTS hook enabled"` |
| `off` | `rm -f ~/.claude-voice/tts-hook-enabled && echo "TTS hook disabled"` |
| `toggle` | `if [ -f ~/.claude-voice/tts-hook-enabled ]; then rm ~/.claude-voice/tts-hook-enabled && echo "TTS hook disabled"; else mkdir -p ~/.claude-voice && touch ~/.claude-voice/tts-hook-enabled && echo "TTS hook enabled"; fi` |
| `status` or empty | `if [ -f ~/.claude-voice/tts-hook-enabled ]; then echo "TTS hook: enabled"; else echo "TTS hook: disabled"; fi` |

Run the appropriate command and report the result.
