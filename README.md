# Push-to-Talk Voice Interface for Claude Code

🎙️ Hands-free voice input and intelligent TTS output for Claude Code on macOS.

## Features

- **Push-to-Talk Input**: Hold a hotkey to speak, release to send to Claude
- **Local Speech Recognition**: Whisper runs entirely on your machine - no data leaves your computer
- **Smart TTS Output**: Claude's conversational responses are spoken aloud; code and command output stay silent
- **Customizable**: Configure hotkey, voice, speaking rate, and more

## Quick Start (5 minutes)

### Prerequisites

- macOS 11.0+ (Big Sur or later)
- Homebrew installed
- Claude Code CLI installed
- Working microphone

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/push-to-talk-claude.git
cd push-to-talk-claude

# Run the installer
./scripts/install.sh
```

Or install manually:

```bash
# Install system dependencies
brew install python@3.11 tmux portaudio ffmpeg

# Install Python package
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### Grant Permissions

When prompted, grant these permissions in **System Settings → Privacy & Security**:

1. **Microphone**: Allow your terminal app to access the microphone
2. **Accessibility**: Add your terminal app to allowed apps (for keyboard monitoring)

### Usage

```bash
# Terminal 1: Start Claude Code in tmux
tmux new-session -s claude 'claude'

# Terminal 2: Start the voice interface
uv run claude-voice

# Now:
# 1. Press and hold Right Ctrl (or your configured hotkey)
# 2. Speak your question or command
# 3. Release the key
# 4. Watch your words appear in Claude Code!
```

## Configuration

Create `~/.claude-voice/config.yaml` to customize:

```yaml
push_to_talk:
  hotkey: "f13"        # Use F13 for dedicated voice key
  visual_feedback: true
  audio_feedback: true

whisper:
  model: "base"        # Options: tiny, base, small, medium, large
  device: "auto"       # Uses Apple Silicon GPU when available

tts:
  enabled: true
  voice: "Samantha"    # Any macOS voice (run 'say -v ?' to list)
  rate: 180            # Words per minute (100-400)
  max_length: 500      # Truncate long responses
```

### Available Hotkeys

- Modifier keys: `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, `cmd_r`, `cmd_l`
- Function keys: `f1`-`f20` (F13-F20 recommended for dedicated use)

### Whisper Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39MB | Fastest | Good |
| base | 74MB | Fast | Better |
| small | 244MB | Medium | Great |
| medium | 769MB | Slow | Excellent |
| large | 1.5GB | Slowest | Best |

## CLI Reference

```bash
# Start voice interface
uv run claude-voice

# Check prerequisites
uv run claude-voice --check

# Use custom config
uv run claude-voice --config /path/to/config.yaml

# Enable debug logging
uv run claude-voice --debug

# Show version
uv run claude-voice --version
```

## Troubleshooting

### "Keyboard monitoring not working"

Grant Accessibility permission:
1. Open **System Settings → Privacy & Security → Accessibility**
2. Click the lock to make changes
3. Add your terminal application
4. Restart the voice interface

### "No audio captured"

Grant Microphone permission:
1. Open **System Settings → Privacy & Security → Microphone**
2. Enable access for your terminal application
3. Restart the voice interface

### "Claude Code session not found"

Ensure Claude is running in tmux:
```bash
tmux list-sessions  # Check existing sessions
tmux new-session -s claude 'claude'  # Create new session
```

### "Transcription is slow"

Try a smaller model or enable GPU:
```yaml
whisper:
  model: "tiny"       # Fastest model
  device: "mps"       # Use Apple Silicon GPU
```

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Hotkey Press  │────▶│  Audio Capture  │────▶│    Whisper      │
└─────────────────┘     └─────────────────┘     │  (Local STT)    │
                                                 └────────┬────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   macOS say     │◀────│ Response Parser │◀────│  tmux send-keys │
│   (TTS)         │     │ (Filter code)   │     │  (Text inject)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Privacy

- **100% Local Processing**: Speech recognition runs on your machine
- **No Cloud APIs**: No audio data is sent anywhere
- **Ephemeral Audio**: Recordings are deleted after transcription
- **No Telemetry**: We don't collect any usage data

## License

MIT

## Contributing

Contributions welcome! Please read our contributing guidelines first.

---

**Need help?** [Open an issue](https://github.com/yourusername/push-to-talk-claude/issues)
