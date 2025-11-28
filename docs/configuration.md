# Configuration Reference

Complete reference for all configuration options in `~/.claude-voice/config.yaml`.

## Configuration File Location

The configuration file is located at `~/.claude-voice/config.yaml`. If it doesn't exist, default values are used.

To create with defaults:
```bash
cp config.default.yaml ~/.claude-voice/config.yaml
```

## All Options

### push_to_talk

Settings for the push-to-talk hotkey behavior.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `hotkey` | string | `"ctrl_r"` | Key to hold for recording |
| `visual_feedback` | bool | `true` | Show recording indicator |
| `audio_feedback` | bool | `true` | Play beep on start/stop |
| `silence_timeout` | float | `2.0` | Auto-stop after N seconds of silence (0 to disable) |

**Supported Hotkeys:**
- Modifier keys: `ctrl_r`, `ctrl_l`, `alt_r`, `alt_l`, `cmd_r`, `cmd_l`, `shift_r`, `shift_l`
- Function keys: `f1` through `f20`

**Tip:** F13-F20 are ideal because they don't conflict with other shortcuts.

### whisper

Speech-to-text settings using OpenAI Whisper.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"tiny"` | Model size |
| `device` | string | `"auto"` | Compute device |
| `language` | string/null | `"en"` | Language code or null for auto |

**Models:**
- `tiny`: 39MB, fastest, good accuracy
- `base`: 74MB, fast, better accuracy
- `small`: 244MB, medium speed, great accuracy
- `medium`: 769MB, slower, excellent accuracy
- `large`: 1.5GB, slowest, best accuracy

**Devices:**
- `auto`: Automatically select best available
- `cpu`: Force CPU (works everywhere)
- `mps`: Apple Silicon GPU (faster on M1/M2/M3)
- `cuda`: NVIDIA GPU (if available)

### tmux

Settings for tmux integration.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `session_name` | string/null | `null` | Explicit session name |
| `window_index` | int/null | `null` | Specific window |
| `pane_index` | int/null | `null` | Specific pane |
| `auto_detect` | bool | `true` | Auto-find Claude Code |

If `auto_detect` is true, the system searches for a pane running Claude Code.

### tts

Text-to-speech settings.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable TTS |
| `voice` | string/null | `null` | macOS voice name |
| `rate` | int | `200` | Speaking rate (100-400 WPM) |
| `max_length` | int | `500` | Max chars to speak |

**List available voices:**
```bash
say -v ?
```

**Popular voices:** Samantha, Alex, Victoria, Daniel

### security

Security settings.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_input_length` | int | `500` | Max transcription length (100-5000) |

### logging

Logging settings.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | `"INFO"` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `save_transcripts` | bool | `false` | Save transcriptions to log |

## Example Configurations

### Minimal (defaults)
```yaml
# Empty file uses all defaults
```

### Power User
```yaml
push_to_talk:
  hotkey: "f13"
  audio_feedback: false

whisper:
  model: "base"
  device: "mps"

tts:
  voice: "Samantha"
  rate: 220
```

### Voice Input Only (no TTS)
```yaml
tts:
  enabled: false
```

### Maximum Accuracy
```yaml
whisper:
  model: "medium"
  language: null  # Auto-detect
```
