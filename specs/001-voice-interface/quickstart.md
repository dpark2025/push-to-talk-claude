# Quickstart: Push-to-Talk Voice Interface for Claude Code

**Goal**: Get voice control working in under 5 minutes.

## Prerequisites

- macOS 11.0+ (Big Sur or later)
- Homebrew installed
- Claude Code CLI installed
- Working microphone

## Installation (2 minutes)

### 1. Install system dependencies

```bash
brew install python@3.11 tmux portaudio ffmpeg
```

### 2. Clone and install

```bash
git clone https://github.com/dpark2025/push-to-talk-claude.git
cd push-to-talk-claude

# Install with uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 3. Grant permissions

When prompted, grant these permissions in **System Settings → Privacy & Security**:

- **Microphone**: Allow Terminal (or your terminal app) to access the microphone
- **Accessibility**: Add Terminal (or your terminal app) to allowed apps

## Usage (1 minute)

### 1. Start Claude Code in tmux

```bash
tmux new-session -s claude 'claude'
```

### 2. Start voice interface (in another terminal)

```bash
uv run claude-voice
```

### 3. Talk to Claude

1. **Press and hold** Right Ctrl (or your configured hotkey)
2. **Speak** your question or command
3. **Release** the key
4. Watch your words appear in Claude Code!

## Quick Configuration

Create `~/.claude-voice/config.yaml`:

```yaml
# Change hotkey to F13 (great for avoiding conflicts)
push_to_talk:
  hotkey: "f13"

# Use larger Whisper model for better accuracy
whisper:
  model: "base"

# Adjust TTS settings
tts:
  enabled: true
  rate: 180  # Slightly slower speech
```

## Verify Setup

```bash
# Check all components
uv run claude-voice --check

# Expected output:
# ✅ Microphone permission: granted
# ✅ Accessibility permission: granted
# ✅ tmux: installed (3.4)
# ✅ Whisper model: tiny (loaded)
# ✅ Claude Code session: found (claude:0.0)
```

## Troubleshooting

### "Keyboard monitoring not working"

Grant Accessibility permission:
1. Open **System Settings → Privacy & Security → Accessibility**
2. Click the lock to make changes
3. Add your terminal application (Terminal.app, iTerm, etc.)
4. Restart the voice interface

### "No audio captured"

Grant Microphone permission:
1. Open **System Settings → Privacy & Security → Microphone**
2. Enable access for your terminal application
3. Restart the voice interface

### "Claude Code session not found"

Ensure Claude is running in tmux:
```bash
# List tmux sessions
tmux list-sessions

# If no 'claude' session, create one:
tmux new-session -s claude 'claude'
```

### "Transcription is slow"

Try the tiny model or enable GPU acceleration:
```yaml
whisper:
  model: "tiny"      # Fastest model
  device: "mps"      # Use Apple Silicon GPU
```

## What's Next?

- **Customize hotkey**: Change to F13-F20 for dedicated voice key
- **Adjust TTS**: Disable, change voice, or adjust speaking rate
- **Enable logging**: Debug issues with `logging.level: DEBUG`

Full configuration reference: [configuration.md](../docs/configuration.md)

---

**Need help?** Open an issue: https://github.com/dpark2025/push-to-talk-claude/issues
