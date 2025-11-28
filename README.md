# Push-to-Talk Voice Interface for Claude Code

Hands-free voice input for Claude Code on macOS.

## Features

- **Push-to-Talk Input**: Hold a hotkey to speak, release to send to Claude Code
- **Local Speech Recognition**: Whisper runs entirely on your machine - no data leaves your computer
- **Fast Transcription**: MPS-accelerated on Apple Silicon (~0.05s per transcription after warmup)
- **Customizable**: Configure hotkey, Whisper model, and tmux target

## Quick Start

### Prerequisites

- macOS 11.0+ (Big Sur or later) with Apple Silicon recommended
- Python 3.11+
- Homebrew installed
- Claude Code CLI installed and working
- Working microphone

### Installation

```bash
# Fork this repository on GitHub first, then clone your fork
git clone https://github.com/YOUR_USERNAME/push-to-talk-claude.git
cd push-to-talk-claude

# Install system dependencies
brew install portaudio ffmpeg tmux

# Install Python dependencies with uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### Grant Permissions

When prompted, grant these permissions in **System Settings > Privacy & Security**:

1. **Microphone**: Allow your terminal app to access the microphone
2. **Accessibility**: Add your terminal app (for keyboard monitoring)

### Usage

You need **two separate terminals**:

```bash
# Terminal 1: Start Claude Code in tmux
tmux new-session -s claude 'claude'
```

```bash
# Terminal 2 (separate window, NOT in tmux): Start voice interface
uv run claude-voice
```

Then:
1. **Press and hold** the Right Control key (or your configured hotkey)
2. **Speak** your question or command
3. **Release** the key
4. Watch your words appear in Claude Code!

## Configuration

Copy the default config to customize:

```bash
cp config.default.yaml ~/.claude-voice/config.yaml
```

Edit `~/.claude-voice/config.yaml`:

```yaml
push_to_talk:
  hotkey: "ctrl_r"       # Right Control key (hold to talk)
  visual_feedback: true
  audio_feedback: true

whisper:
  model: "tiny"          # Options: tiny, base, small, medium, large
  device: "mps"          # Use Apple Silicon GPU (or "cpu" for Intel)
  language: "en"

tmux:
  session_name: null     # Auto-detect Claude session, or set explicitly
  auto_detect: true
```

### Available Hotkeys

- Modifier keys: `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, `cmd_r`, `cmd_l`, `shift_r`, `shift_l`
- Function keys: `f1`-`f20` (F13-F20 recommended for dedicated use)

**Note**: `ctrl_r` means the **physical Right Control key**, not Ctrl+R combination.

### Whisper Models

| Model  | Size   | Speed   | Accuracy  |
|--------|--------|---------|-----------|
| tiny   | 39MB   | Fastest | Good      |
| base   | 74MB   | Fast    | Better    |
| small  | 244MB  | Medium  | Great     |
| medium | 769MB  | Slow    | Excellent |
| large  | 1.5GB  | Slowest | Best      |

For most use cases, `tiny` with MPS acceleration provides excellent speed and accuracy.

## CLI Reference

```bash
# Start voice interface
uv run claude-voice

# Check prerequisites and permissions
uv run claude-voice --check

# Use custom config file
uv run claude-voice --config /path/to/config.yaml

# Enable debug logging
uv run claude-voice --debug

# Show version
uv run claude-voice --version
```

## Troubleshooting

### "Keyboard monitoring not working"

Grant Accessibility permission:
1. Open **System Settings > Privacy & Security > Accessibility**
2. Click the lock to make changes
3. Add your terminal application (Terminal, iTerm2, etc.)
4. Restart the voice interface

### "No audio captured"

Grant Microphone permission:
1. Open **System Settings > Privacy & Security > Microphone**
2. Enable access for your terminal application
3. Restart the voice interface

### "Claude Code session not found"

Ensure Claude is running in tmux:
```bash
tmux list-sessions          # Check existing sessions
tmux new-session -s claude 'claude'  # Create new session
```

### "Transcription is slow"

1. Ensure you're using MPS (Apple Silicon GPU):
   ```yaml
   whisper:
     device: "mps"
   ```
2. Use the `tiny` model for fastest transcription
3. First transcription is slower (model warmup), subsequent ones are fast

### "Target session/pane is no longer valid"

The voice interface may have detected the wrong tmux session. Set explicit target in config:
```yaml
tmux:
  session_name: "your-session-name"
  window_index: 1
  pane_index: 1
  auto_detect: false
```

Run `tmux list-panes -a` to see all available targets.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Hotkey Press   │────▶│  Audio Capture  │────▶│    Whisper      │
│  (pynput)       │     │  (PyAudio)      │     │  (Local STT)    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │  tmux send-keys │
                                                │  (Text inject)  │
                                                └─────────────────┘
```

## Privacy

- **100% Local Processing**: Speech recognition runs entirely on your machine
- **No Cloud APIs**: No audio data is sent anywhere
- **Ephemeral Audio**: Recordings are processed in memory, not saved to disk
- **No Telemetry**: No usage data is collected

## Development

```bash
# Clone and setup
git clone https://github.com/dpark2025/push-to-talk-claude.git
cd push-to-talk-claude
uv sync

# Run tests
uv run pytest

# Run with debug logging
uv run claude-voice --debug
```

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Need help?** [Open an issue](https://github.com/dpark2025/push-to-talk-claude/issues)
