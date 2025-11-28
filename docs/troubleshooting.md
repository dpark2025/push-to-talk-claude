# Troubleshooting Guide

Common issues and solutions for Push-to-Talk Claude.

## Permission Issues

### Microphone Permission Denied

**Symptoms:**
- "Microphone permission not granted" error
- No audio captured when speaking

**Solution:**
1. Open **System Settings** → **Privacy & Security** → **Microphone**
2. Find your terminal app (Terminal, iTerm2, etc.)
3. Toggle the switch to enable
4. Restart the voice interface

**Note:** If your terminal isn't listed, run `uv run claude-voice` once to trigger the permission request.

### Accessibility Permission Denied

**Symptoms:**
- "Accessibility permission not granted" error
- Hotkey not detected

**Solution:**
1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the lock icon and authenticate
3. Click the + button
4. Add your terminal app from Applications/Utilities
5. Restart the voice interface

### Permission Checks Pass But Still Not Working

Try these steps:
1. Quit your terminal completely (Cmd+Q)
2. Remove and re-add the permissions
3. Restart your terminal
4. Run `uv run claude-voice --check` to verify

## Audio Issues

### No Audio Captured

**Check microphone selection:**
```bash
# List audio devices
system_profiler SPAudioDataType
```

**Check input volume:**
1. Open **System Settings** → **Sound** → **Input**
2. Ensure correct microphone is selected
3. Check input level while speaking

### Poor Transcription Quality

**Solutions:**
1. Use a larger Whisper model:
   ```yaml
   whisper:
     model: "base"  # or "small"
   ```

2. Reduce background noise

3. Speak clearly and at normal pace

4. Check microphone position

### Transcription Too Slow

**Solutions:**
1. Use a smaller model:
   ```yaml
   whisper:
     model: "tiny"
   ```

2. Enable GPU acceleration:
   ```yaml
   whisper:
     device: "mps"  # Apple Silicon
   ```

## tmux Issues

### "Claude Code session not found"

**Check tmux is running:**
```bash
tmux list-sessions
```

**Start Claude in tmux:**
```bash
tmux new-session -s claude 'claude'
```

**Check the voice interface can find it:**
```bash
uv run claude-voice --check
```

### Text Not Appearing in Claude

**Check target session:**
The auto-detect looks for panes with "claude" in the command name.

**Manual target specification:**
```yaml
tmux:
  session_name: "claude"
  window_index: 0
  pane_index: 0
  auto_detect: false
```

## TTS Issues

### No Speech Output

**Check TTS is enabled:**
```yaml
tts:
  enabled: true
```

**Check voice is valid:**
```bash
# List available voices
say -v ?

# Test a voice
say -v Samantha "Hello world"
```

### TTS Speaking Code

This shouldn't happen if the response parser is working. Check:
1. Parser is filtering code blocks (```...```)
2. Parser is filtering command output

Enable debug logging:
```bash
uv run claude-voice --debug
```

## Installation Issues

### PyAudio Build Fails

**Error:** `portaudio.h not found`

**Solution:**
```bash
brew install portaudio
uv sync
```

### Whisper Model Download Fails

**Manual download:**
Models are cached in `~/.cache/whisper/`. Try:
```bash
# Clear cache and retry
rm -rf ~/.cache/whisper
uv run claude-voice
```

### "command not found: uv"

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc  # or ~/.bashrc
```

## Debug Mode

Enable verbose logging:
```bash
uv run claude-voice --debug
```

Or in config:
```yaml
logging:
  level: "DEBUG"
```

## Getting Help

If you're still stuck:
1. Check existing issues: https://github.com/yourusername/push-to-talk-claude/issues
2. Open a new issue with:
   - Your macOS version
   - Output of `uv run claude-voice --check`
   - Debug log output
   - Steps to reproduce
