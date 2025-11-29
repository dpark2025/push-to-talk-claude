# Push-to-Talk Voice Interface for Claude Code

Hands-free voice input for Claude Code on macOS.

## Features

- **Push-to-Talk Input**: Hold a hotkey to speak, release to type text into any application
- **Local Speech Recognition**: Whisper runs entirely on your machine - no data leaves your computer
- **Fast Transcription**: MPS-accelerated on Apple Silicon (~0.05s per transcription after warmup)
- **Flexible Injection**: Type into focused window (default) or send to specific tmux pane
- **Beautiful TUI**: Textual-based terminal UI with live recording timer, status indicators, and log viewer
- **TTS Response Hook**: Optional Claude Code integration to hear Claude's responses aloud ([setup guide](docs/claude-code-hook-setup.md))
- **Customizable**: Configure hotkey, Whisper model, and injection target

## Quick Start

**TL;DR** for experienced users:

```bash
brew install portaudio ffmpeg
git clone https://github.com/YOUR_USERNAME/push-to-talk-claude.git && cd push-to-talk-claude
uv sync
uv run claude-voice
# Hold Right-Ctrl to talk, release to send. Text types into focused window!
```

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
brew install portaudio ffmpeg
# Optional: brew install tmux  (only needed for tmux injection mode)

# Install Python dependencies with uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### Grant Permissions

The voice interface needs macOS permissions. Grant these in **System Settings > Privacy & Security**:

1. **Microphone**: Allow your terminal app (the one running `claude-voice`) to access the microphone
2. **Accessibility**: Add your terminal app (for global keyboard monitoring)

> **Tip**: Run `uv run claude-voice --check` to verify permissions are configured correctly.

### Usage

#### Simple Setup (Focused Mode - Default)

Just start the voice interface:

```bash
uv run claude-voice
```

Then:
1. **Click into any application** where you want text to appear (Claude Code, VS Code, browser, etc.)
2. **Press and hold** the Right Control key
3. **Speak** your question or command
4. **Release** the key
5. Your words are typed into the focused window!

> **Key insight**: The hotkey is detected system-wide. Text goes wherever your cursor is.

> **First run note**: The first transcription takes longer (~5-10s) as Whisper downloads the `small` model (~244MB) and initializes. Subsequent transcriptions are fast on Apple Silicon.

#### Advanced Setup (tmux Mode)

If you prefer to always send text to a specific tmux pane (regardless of focus), use tmux mode:

1. Start Claude Code in tmux:
   ```bash
   tmux new-session -s claude 'claude'
   ```

2. Configure tmux mode in `~/.claude-voice/config.yaml`:
   ```yaml
   injection:
     mode: "tmux"
   tmux:
     session_name: "claude"
     auto_detect: true
   ```

3. Start the voice interface in a separate terminal:
   ```bash
   uv run claude-voice
   ```

4. Hold the hotkey to speak - text injects into the tmux pane regardless of focus.

5. **(Optional)** Position windows side-by-side if you want to monitor recording status:
   ```
   ┌─────────────────────────────┬─────────────────────────────┐
   │   Claude Code (tmux)        │   Voice Interface           │
   │   Keep your focus here      │   Shows recording status    │
   └─────────────────────────────┴─────────────────────────────┘
   ```

### TUI Interface

The voice interface displays a modern terminal UI with:

- **Info Panel** (left): Shows hotkey, model, mode, and target configuration
- **Status Panel** (right): Visual indicators for Recording, Transcribing, Injecting, Complete, and Error states
- **Recording Timer**: Live duration counter during recording with warning at 50 seconds
- **Footer**: Keyboard shortcuts

**Keyboard Shortcuts**:
| Key | Action |
|-----|--------|
| `L` | Toggle log viewer (shows recent activity) |
| `S` | Toggle TTS hook (speaks Claude responses aloud) |
| `Q` | Quit the application |
| `Ctrl+\` | Open options/command palette |

The TUI uses the Catppuccin Mocha theme for a comfortable dark mode experience.

### TTS Response Hook (Experimental)

The TUI includes an experimental feature that speaks Claude's responses aloud using macOS TTS. When enabled:
- Claude's responses are automatically spoken after each reply
- Long responses are intelligently summarized
- Code blocks are filtered out (not spoken)
- Toggle on/off with the `S` key

**⚠️ Requires manual setup** - see [Claude Code Hook Setup Guide](docs/claude-code-hook-setup.md) for detailed instructions.

**Note:** This is a brittle integration that depends on Claude Code's internal hook system and may break with future updates.

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
  model: "small"         # Options: tiny, base, small, medium, large
  device: "mps"          # Use Apple Silicon GPU (or "cpu" for Intel)
  language: "en"

injection:
  mode: "focused"        # "focused" = type into active window (default)
                         # "tmux" = send to specific tmux pane

# Only used when injection.mode is "tmux"
tmux:
  session_name: null     # Auto-detect Claude session, or set explicitly
  window_index: null     # Specific window (0-indexed)
  pane_index: null       # Specific pane (0-indexed)
  auto_detect: true
```

### Injection Modes

**Focused Mode** (default): Types into whatever window has keyboard focus. Works with any application - Claude Code, VS Code, browsers, Slack, etc.

**tmux Mode**: Sends text to a specific tmux pane. Useful when you want to inject into a background tmux session regardless of focus.

```yaml
# Example: Always send to a specific tmux pane
injection:
  mode: "tmux"
tmux:
  session_name: "claude"
  window_index: 0
  pane_index: 0
  auto_detect: false
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

The default `small` model provides great accuracy. Use `tiny` for faster transcription if accuracy is less important.

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
2. Use a smaller model (`tiny` or `base`) for faster transcription
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
