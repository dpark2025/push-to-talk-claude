# Research: Push-to-Talk Voice Interface

**Phase**: 0 - Research
**Date**: 2025-11-27
**Status**: Complete

## Technology Decisions

### 1. Keyboard Monitoring (pynput)

**Decision**: Use `pynput.keyboard.Listener` with threading.Event for state management

**Rationale**:
- pynput provides cross-platform keyboard monitoring with native macOS support
- Listener runs on background thread automatically
- threading.Event provides thread-safe hotkey state without locks

**Alternatives Considered**:
- PyObjC direct: More complex, unnecessary for simple hotkey detection
- keyboard library: Requires root on macOS

**Key Implementation Notes**:
- Listener callbacks must be non-blocking (<1ms)
- Use `threading.Event()` for cross-thread state sharing
- Accessibility permissions required - check at startup
- Silent failure if permissions denied - must verify listener works

**Code Pattern**:
```python
hotkey_pressed = threading.Event()

def on_press(key):
    if key == configured_hotkey:
        hotkey_pressed.set()

def on_release(key):
    if key == configured_hotkey:
        hotkey_pressed.clear()
```

---

### 2. Audio Capture (PyAudio)

**Decision**: Record at 16kHz mono using PyAudio with CoreAudio backend

**Rationale**:
- 16kHz is Whisper's optimal input sample rate
- CoreAudio backend is native to macOS
- PyAudio is well-maintained and widely used

**Alternatives Considered**:
- sounddevice: Lower latency but less stable on macOS
- pygame: Higher latency (>300ms)
- Record at 44.1kHz and downsample: More reliable but adds complexity

**Key Implementation Notes**:
- Frame size: 1024 samples (~64ms latency at 16kHz)
- Use `exception_on_overflow=False` to prevent crashes
- Microphone permission required via System Settings
- Buffer audio in memory during recording, process on release

**Performance Targets**:
- Capture latency: <100ms
- Buffer size: 1024 frames
- Format: float32 mono

---

### 3. Speech-to-Text (openai-whisper)

**Decision**: Use Whisper "tiny" model with MPS acceleration on Apple Silicon

**Rationale**:
- tiny model: 39M params, ~100-200ms transcription for 5-10s audio
- MPS provides 2-3x speedup over CPU on Apple Silicon
- Pre-loading model eliminates 2-3s startup delay

**Alternatives Considered**:
- base model: Better accuracy but 300-500ms latency
- whisper.cpp: 3x faster with CoreML but complex integration
- Cloud API: Violates privacy-first principle

**Key Implementation Notes**:
- Pre-load model at application startup (module-level singleton)
- Specify `language="en"` to skip language detection
- Models cached in `~/.cache/whisper/` after first download
- Check `torch.backends.mps.is_available()` for GPU acceleration

**Performance Targets**:
- Model load: <50ms (cached), 2-3s (first run)
- Transcription: <200ms for 5-10 word utterance
- Accuracy: >95% WER for clear speech

---

### 4. Text Injection (tmux)

**Decision**: Use `tmux send-keys` with array-form subprocess (no shell)

**Rationale**:
- Works across all terminal emulators
- Array form avoids shell escaping issues
- send-keys handles text injection reliably

**Alternatives Considered**:
- Accessibility API typing simulation: Complex, permission-heavy
- Clipboard paste: Unreliable, overwrites user clipboard
- Direct terminal control sequences: Non-portable

**Key Implementation Notes**:
- Use `subprocess.run([...], check=True)` - no shell=True
- Target format: `session:window.pane`
- Auto-detect Claude session by checking `pane_current_command`
- Must escape or sanitize shell metacharacters before injection

**Code Pattern**:
```python
subprocess.run([
    "tmux", "send-keys",
    "-t", f"{session}:{window}.{pane}",
    sanitized_text
], check=True)
```

---

### 5. Text-to-Speech (macOS say)

**Decision**: Use macOS `say` command with async subprocess execution

**Rationale**:
- Pre-installed on all macOS systems
- No additional dependencies
- Supports multiple voices and speech rate control

**Alternatives Considered**:
- Kokoro TTS: Higher quality but adds 100MB+ dependency
- Piper TTS: Good quality but complex setup
- NSSpeechSynthesizer via PyObjC: More control but complex

**Key Implementation Notes**:
- Use `subprocess.Popen()` for non-blocking execution
- Track current process to enable interruption
- Kill previous speech when new speech requested
- Default voice: system default (configurable)

**Code Pattern**:
```python
current_speech = None

def speak(text):
    global current_speech
    if current_speech:
        current_speech.terminate()
    current_speech = subprocess.Popen(["say", text])
```

---

### 6. Configuration (PyYAML)

**Decision**: YAML config file at `~/.claude-voice/config.yaml`

**Rationale**:
- Human-readable and editable
- Standard format with good Python support
- Supports complex nested configuration

**Key Implementation Notes**:
- Load config at startup with validation
- Provide sensible defaults for all settings
- Support environment variable overrides
- Validate config with helpful error messages

---

## Performance Budget

| Component | Target | Notes |
|-----------|--------|-------|
| Hotkey detection | <100ms | pynput listener overhead |
| Audio capture stop | <50ms | Buffer flush |
| Whisper transcription | <2.5s | tiny model, MPS acceleration |
| Text injection | <350ms | tmux send-keys |
| **Total voice-to-text** | **<3s (p95)** | Constitution requirement |
| Response detection | <500ms | Hook or file watching |
| TTS startup | <200ms | say command latency |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Accessibility permission denied | Check at startup, display clear instructions |
| Microphone permission denied | Check at startup, guide to System Settings |
| Whisper model download fails | Retry with exponential backoff, fallback instructions |
| tmux session not found | Auto-detect, clear error with session creation command |
| Audio underruns | Use 1024 frame buffer, exception_on_overflow=False |

---

## Dependencies Verification

| Dependency | License | macOS 11.0+ | Actively Maintained |
|------------|---------|-------------|---------------------|
| pynput | LGPL-3.0 | ✅ | ✅ |
| PyAudio | MIT | ✅ | ✅ |
| openai-whisper | MIT | ✅ | ✅ |
| PyYAML | MIT | ✅ | ✅ |
| rich | MIT | ✅ | ✅ |

All dependencies meet Constitution requirements (permissive licenses, macOS support, actively maintained).
