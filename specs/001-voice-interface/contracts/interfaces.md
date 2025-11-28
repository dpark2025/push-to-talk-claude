# Interface Contracts: Push-to-Talk Voice Interface

**Phase**: 1 - Design
**Date**: 2025-11-27

## Core Module Interfaces

### 1. KeyboardMonitor

**Location**: `src/push_to_talk_claude/core/keyboard_monitor.py`

```python
from typing import Callable, Optional
from enum import Enum

class HotkeyState(Enum):
    IDLE = "idle"
    PRESSED = "pressed"

class KeyboardMonitor:
    """Monitor keyboard for push-to-talk hotkey events."""

    def __init__(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ) -> None:
        """
        Initialize keyboard monitor.

        Args:
            hotkey: Key name from SUPPORTED_HOTKEYS (e.g., "ctrl_r", "f13")
            on_press: Callback when hotkey is pressed
            on_release: Callback when hotkey is released

        Raises:
            ValueError: If hotkey is not supported
            PermissionError: If accessibility permission not granted
        """
        ...

    def start(self) -> None:
        """Start listening for keyboard events. Non-blocking."""
        ...

    def stop(self) -> None:
        """Stop listening and cleanup resources."""
        ...

    @property
    def state(self) -> HotkeyState:
        """Current hotkey state."""
        ...

    @property
    def is_listening(self) -> bool:
        """Whether monitor is actively listening."""
        ...

    @staticmethod
    def check_permissions() -> bool:
        """Check if accessibility permissions are granted."""
        ...

# Supported hotkeys constant
SUPPORTED_HOTKEYS: dict[str, object]  # Maps key names to pynput Key objects
```

**Contract Tests**:
- `test_valid_hotkey_initialization`: Accepts all SUPPORTED_HOTKEYS
- `test_invalid_hotkey_raises`: Raises ValueError for unknown keys
- `test_callbacks_fire_on_press_release`: Callbacks invoked correctly
- `test_state_transitions`: IDLE → PRESSED → IDLE on press/release
- `test_permission_check`: Returns bool without side effects

---

### 2. AudioCapture

**Location**: `src/push_to_talk_claude/core/audio_capture.py`

```python
from typing import Optional, List
from dataclasses import dataclass
import numpy as np

@dataclass
class AudioDevice:
    index: int
    name: str
    sample_rate: int
    channels: int

class AudioCapture:
    """Capture audio from microphone during push-to-talk sessions."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        frame_size: int = 1024,
        device_index: Optional[int] = None
    ) -> None:
        """
        Initialize audio capture.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for Whisper)
            channels: Number of channels (default: 1 for mono)
            frame_size: Frames per buffer (default: 1024)
            device_index: Specific device or None for default

        Raises:
            PermissionError: If microphone permission not granted
            RuntimeError: If audio device initialization fails
        """
        ...

    def start_recording(self) -> None:
        """Begin capturing audio frames to internal buffer."""
        ...

    def stop_recording(self) -> np.ndarray:
        """
        Stop capture and return recorded audio.

        Returns:
            numpy array of float32 audio samples
        """
        ...

    def cancel_recording(self) -> None:
        """Stop capture and discard audio buffer."""
        ...

    @property
    def is_recording(self) -> bool:
        """Whether currently recording."""
        ...

    @property
    def duration_seconds(self) -> float:
        """Duration of current/last recording in seconds."""
        ...

    @staticmethod
    def list_devices() -> List[AudioDevice]:
        """List available audio input devices."""
        ...

    @staticmethod
    def check_permissions() -> bool:
        """Check if microphone permission is granted."""
        ...
```

**Contract Tests**:
- `test_recording_produces_audio`: Returns non-empty numpy array
- `test_audio_format`: Output is float32 mono at 16kHz
- `test_cancel_discards_buffer`: No audio returned after cancel
- `test_duration_tracking`: Duration matches actual recording time
- `test_permission_check`: Returns bool without recording

---

### 3. SpeechToText

**Location**: `src/push_to_talk_claude/core/speech_to_text.py`

```python
from typing import Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_ms: int

class SpeechToText:
    """Transcribe audio using local Whisper model."""

    def __init__(
        self,
        model_name: str = "tiny",
        device: str = "auto",
        language: Optional[str] = "en"
    ) -> None:
        """
        Initialize Whisper model.

        Args:
            model_name: Model size (tiny, base, small, medium, large)
            device: Compute device (auto, cpu, mps, cuda)
            language: Language code or None for auto-detect

        Raises:
            ValueError: If model_name is invalid
            RuntimeError: If model loading fails
        """
        ...

    def transcribe(
        self,
        audio: np.ndarray,
        timeout_seconds: float = 5.0
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio: Float32 numpy array at 16kHz
            timeout_seconds: Maximum transcription time

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            TimeoutError: If transcription exceeds timeout
            RuntimeError: If transcription fails
        """
        ...

    @property
    def model_name(self) -> str:
        """Currently loaded model name."""
        ...

    @property
    def is_loaded(self) -> bool:
        """Whether model is loaded and ready."""
        ...

    @staticmethod
    def available_models() -> List[str]:
        """List available Whisper model names."""
        ...
```

**Contract Tests**:
- `test_transcription_returns_text`: Non-empty text for valid audio
- `test_timeout_raises`: TimeoutError when exceeding limit
- `test_empty_audio_returns_empty`: Empty string for silence
- `test_model_loading`: Model loaded after initialization
- `test_available_models`: Returns list of valid model names

---

### 4. TmuxInjector

**Location**: `src/push_to_talk_claude/core/tmux_injector.py`

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class TmuxTarget:
    session_name: str
    window_index: int
    pane_index: int
    is_claude_code: bool

class TmuxInjector:
    """Inject text into tmux sessions."""

    def __init__(
        self,
        session_name: Optional[str] = None,
        auto_detect: bool = True
    ) -> None:
        """
        Initialize tmux injector.

        Args:
            session_name: Explicit session or None for auto-detect
            auto_detect: Whether to auto-find Claude Code session

        Raises:
            RuntimeError: If tmux is not installed
        """
        ...

    def inject_text(self, text: str) -> bool:
        """
        Send text to tmux target.

        Args:
            text: Text to inject (will be sanitized)

        Returns:
            True if injection succeeded

        Raises:
            RuntimeError: If no valid target found
            ValueError: If text is empty after sanitization
        """
        ...

    def find_claude_session(self) -> Optional[TmuxTarget]:
        """
        Find tmux session running Claude Code.

        Returns:
            TmuxTarget if found, None otherwise
        """
        ...

    def validate_target(self) -> bool:
        """Check if current target is valid and accessible."""
        ...

    @property
    def target(self) -> Optional[TmuxTarget]:
        """Current injection target."""
        ...

    @staticmethod
    def is_tmux_available() -> bool:
        """Check if tmux is installed and accessible."""
        ...
```

**Contract Tests**:
- `test_injection_succeeds`: Text appears in target pane
- `test_sanitization_applied`: Dangerous chars escaped
- `test_empty_text_rejected`: ValueError for empty input
- `test_session_detection`: Finds Claude Code session
- `test_tmux_availability`: Returns bool without side effects

---

### 5. TextToSpeech

**Location**: `src/push_to_talk_claude/core/text_to_speech.py`

```python
from typing import Optional, List

class TextToSpeech:
    """Convert text to speech using macOS say command."""

    def __init__(
        self,
        voice: Optional[str] = None,
        rate: int = 200
    ) -> None:
        """
        Initialize TTS engine.

        Args:
            voice: Voice name or None for system default
            rate: Speaking rate in words per minute (100-400)

        Raises:
            ValueError: If rate is out of range
        """
        ...

    def speak(self, text: str, async_mode: bool = True) -> None:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            async_mode: If True, return immediately (default)
        """
        ...

    def stop(self) -> None:
        """Stop current speech immediately."""
        ...

    @property
    def is_speaking(self) -> bool:
        """Whether currently speaking."""
        ...

    @staticmethod
    def list_voices() -> List[str]:
        """List available macOS voices."""
        ...
```

**Contract Tests**:
- `test_speak_async_returns_immediately`: Non-blocking execution
- `test_stop_interrupts_speech`: Speech stops when called
- `test_is_speaking_state`: Correct state during/after speech
- `test_list_voices`: Returns non-empty list on macOS

---

### 6. ResponseParser

**Location**: `src/push_to_talk_claude/hooks/response_parser.py`

```python
from typing import Optional
from enum import Enum

class ResponseType(Enum):
    CONVERSATIONAL = "conversational"
    CODE_BLOCK = "code_block"
    COMMAND_OUTPUT = "command_output"
    MIXED = "mixed"
    TOO_LONG = "too_long"

class ResponseParser:
    """Parse Claude responses to extract speakable content."""

    def __init__(self, max_length: int = 500) -> None:
        """
        Initialize parser.

        Args:
            max_length: Maximum text length to speak
        """
        ...

    def classify(self, text: str) -> ResponseType:
        """
        Classify response type.

        Args:
            text: Raw response text

        Returns:
            ResponseType classification
        """
        ...

    def extract_speakable(self, text: str) -> Optional[str]:
        """
        Extract text suitable for TTS.

        Args:
            text: Raw response text

        Returns:
            Filtered text or None if nothing to speak
        """
        ...

    def should_speak(self, text: str) -> bool:
        """
        Determine if response should trigger TTS.

        Args:
            text: Raw response text

        Returns:
            True if response should be spoken
        """
        ...
```

**Contract Tests**:
- `test_code_block_classified`: Fenced code → CODE_BLOCK
- `test_conversational_classified`: Natural text → CONVERSATIONAL
- `test_command_output_classified`: Tool output → COMMAND_OUTPUT
- `test_extract_removes_code`: Code blocks stripped from output
- `test_max_length_enforced`: Long text classified as TOO_LONG

---

### 7. InputSanitizer

**Location**: `src/push_to_talk_claude/utils/sanitizer.py`

```python
class InputSanitizer:
    """Sanitize user input before tmux injection."""

    def __init__(self, max_length: int = 500) -> None:
        """
        Initialize sanitizer.

        Args:
            max_length: Maximum allowed input length
        """
        ...

    def sanitize(self, text: str) -> str:
        """
        Clean and validate input text.

        Args:
            text: Raw transcription text

        Returns:
            Sanitized text safe for tmux injection
        """
        ...

    def is_safe(self, text: str) -> bool:
        """
        Check if text is safe without modifying.

        Args:
            text: Text to check

        Returns:
            True if text passes all safety checks
        """
        ...

# Characters that must be escaped
SHELL_METACHARACTERS: str = "$`\\\"'|&;><(){}[]!*?~#"
```

**Contract Tests**:
- `test_metachar_escaped`: All SHELL_METACHARACTERS escaped
- `test_length_enforced`: Text truncated at max_length
- `test_newlines_replaced`: Newlines become spaces
- `test_ansi_removed`: ANSI escape sequences stripped
- `test_empty_after_sanitization`: Empty input returns empty

---

## Configuration Interface

### Config

**Location**: `src/push_to_talk_claude/utils/config.py`

```python
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class PushToTalkConfig:
    hotkey: str = "ctrl_r"
    visual_feedback: bool = True
    audio_feedback: bool = True
    silence_timeout: float = 2.0

@dataclass
class WhisperConfig:
    model: str = "tiny"
    device: str = "auto"
    language: Optional[str] = "en"

@dataclass
class TmuxConfig:
    session_name: Optional[str] = None
    window_index: Optional[int] = None
    pane_index: Optional[int] = None
    auto_detect: bool = True

@dataclass
class TTSConfig:
    enabled: bool = True
    voice: Optional[str] = None
    rate: int = 200
    max_length: int = 500

@dataclass
class SecurityConfig:
    max_input_length: int = 500

@dataclass
class Config:
    push_to_talk: PushToTalkConfig
    whisper: WhisperConfig
    tmux: TmuxConfig
    tts: TTSConfig
    security: SecurityConfig

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load config from file or use defaults."""
        ...

    @classmethod
    def default(cls) -> "Config":
        """Create config with default values."""
        ...

    def save(self, path: Path) -> None:
        """Save config to YAML file."""
        ...

    def validate(self) -> List[str]:
        """
        Validate config values.

        Returns:
            List of validation error messages (empty if valid)
        """
        ...
```

**Contract Tests**:
- `test_default_config_valid`: Default config passes validation
- `test_load_missing_file_uses_defaults`: Graceful fallback
- `test_invalid_hotkey_fails_validation`: Validation catches errors
- `test_save_and_load_roundtrip`: Config survives save/load cycle
