# Data Model: Push-to-Talk Voice Interface

**Phase**: 1 - Design
**Date**: 2025-11-27

## Entity Definitions

### 1. Configuration

User preferences and application settings.

```
Configuration
├── push_to_talk
│   ├── hotkey: str              # Key name (e.g., "ctrl_r", "f13")
│   ├── visual_feedback: bool    # Show recording indicator
│   ├── audio_feedback: bool     # Play beep on start/stop
│   └── silence_timeout: float   # Auto-stop after N seconds (0 = disabled)
│
├── whisper
│   ├── model: str               # Model name: "tiny", "base", "small"
│   ├── device: str              # "cpu", "mps", "cuda"
│   └── language: str | null     # Language code or null for auto-detect
│
├── tmux
│   ├── session_name: str | null # Explicit session or null for auto-detect
│   ├── window_index: int | null # Specific window or null for current
│   ├── pane_index: int | null   # Specific pane or null for current
│   └── auto_detect: bool        # Auto-find Claude Code session
│
├── tts
│   ├── enabled: bool            # Enable text-to-speech
│   ├── voice: str               # macOS voice name (e.g., "Samantha")
│   ├── rate: int                # Words per minute (150-300)
│   └── max_length: int          # Max chars to speak (truncate beyond)
│
├── security
│   └── max_input_length: int    # Max transcription length (default: 500)
│
└── logging
    ├── level: str               # DEBUG, INFO, WARNING, ERROR
    └── save_transcripts: bool   # Save transcriptions to log
```

**Storage**: `~/.claude-voice/config.yaml`

**Validation Rules**:
- hotkey must be in SUPPORTED_HOTKEYS list
- whisper.model must be one of: tiny, base, small, medium, large
- tts.rate must be between 100 and 400
- security.max_input_length must be between 100 and 5000

---

### 2. RecordingSession

A single push-to-talk interaction from hotkey press to transcription completion.

```
RecordingSession
├── id: UUID                     # Unique session identifier
├── started_at: datetime         # When hotkey was pressed
├── ended_at: datetime | null    # When hotkey was released
├── duration_ms: int             # Recording duration in milliseconds
├── audio_frames: List[bytes]    # Raw audio buffer (in memory)
├── transcription: str | null    # Whisper output text
├── status: RecordingStatus      # State machine state
└── error: str | null            # Error message if failed
```

**States** (RecordingStatus):
```
IDLE → RECORDING → TRANSCRIBING → INJECTING → COMPLETE
                 ↘ TIMEOUT      ↘ ERROR
                 ↘ CANCELLED
```

**Lifecycle**:
1. IDLE: Waiting for hotkey press
2. RECORDING: Hotkey held, capturing audio
3. TRANSCRIBING: Hotkey released, Whisper processing
4. INJECTING: Sending text to tmux
5. COMPLETE: Successfully injected
6. TIMEOUT: Transcription exceeded 5s limit
7. CANCELLED: User cancelled or error occurred
8. ERROR: Failure at any stage

**Storage**: In-memory only (ephemeral per Constitution)

---

### 3. ClaudeResponse

Output from Claude Code that may trigger TTS.

```
ClaudeResponse
├── session_id: str              # Claude Code session identifier
├── timestamp: datetime          # When response was detected
├── raw_text: str                # Full response text
├── response_type: ResponseType  # Classification result
├── speakable_text: str | null   # Filtered text for TTS (if any)
└── was_spoken: bool             # Whether TTS was triggered
```

**Response Types** (ResponseType):
```
CONVERSATIONAL    # Natural language response → speak
CODE_BLOCK        # Fenced code block → silent
COMMAND_OUTPUT    # Tool/command result → silent
MIXED             # Contains both → extract and speak conversational parts
TOO_LONG          # Exceeds max_length → truncate or skip
```

**Classification Rules**:
1. Lines starting with ``` → CODE_BLOCK
2. Lines starting with `$`, `>`, `#` → COMMAND_OUTPUT
3. Patterns: "File created:", "Running:", "Error:" → COMMAND_OUTPUT
4. Text starting with "I'll", "I can", "Let me", "Here's" → CONVERSATIONAL
5. Length > config.tts.max_length → TOO_LONG

**Storage**: In-memory only

---

### 4. TmuxTarget

Reference to a tmux session/window/pane for text injection.

```
TmuxTarget
├── session_name: str            # tmux session name
├── window_index: int            # Window number (0-based)
├── pane_index: int              # Pane number (0-based)
├── is_claude_code: bool         # Whether Claude Code is running
└── last_verified: datetime      # When target was last validated
```

**Discovery Logic**:
1. List all tmux sessions: `tmux list-sessions`
2. For each session, list panes: `tmux list-panes -t <session>`
3. Check each pane's command: `tmux display-message -p -t <pane> '#{pane_current_command}'`
4. If command contains "claude" → mark as Claude Code pane

**Storage**: In-memory, refreshed on startup and periodically

---

### 5. PermissionStatus

macOS permission states for required capabilities.

```
PermissionStatus
├── microphone: PermissionState  # Audio recording permission
├── accessibility: PermissionState # Keyboard monitoring permission
└── checked_at: datetime         # When permissions were last verified
```

**Permission States** (PermissionState):
```
GRANTED           # Permission available
DENIED            # Explicitly denied by user
NOT_DETERMINED    # Not yet requested
RESTRICTED        # System policy prevents access
UNKNOWN           # Could not determine status
```

**Storage**: Checked at runtime, not persisted

---

## Relationships

```
┌─────────────────┐
│  Configuration  │
└────────┬────────┘
         │ loads
         ▼
┌─────────────────┐     triggers    ┌─────────────────┐
│ KeyboardMonitor │ ───────────────▶│ RecordingSession│
└─────────────────┘                 └────────┬────────┘
                                             │ produces
                                             ▼
                                    ┌─────────────────┐
                                    │   TmuxTarget    │
                                    └────────┬────────┘
                                             │ receives
                                             ▼
                                    ┌─────────────────┐
                                    │ ClaudeResponse  │
                                    └────────┬────────┘
                                             │ triggers
                                             ▼
                                    ┌─────────────────┐
                                    │  TextToSpeech   │
                                    └─────────────────┘
```

---

## State Transitions

### Recording Session State Machine

```
                    ┌──────────────────────────────────────┐
                    │                                      │
                    ▼                                      │
┌──────┐  press  ┌───────────┐  release  ┌──────────────┐ │
│ IDLE │ ──────▶ │ RECORDING │ ────────▶ │ TRANSCRIBING │ │
└──────┘         └───────────┘           └──────┬───────┘ │
   ▲                │                           │         │
   │                │ >60s                      │ success │
   │                ▼                           ▼         │
   │         ┌───────────┐              ┌───────────┐     │
   │         │  TIMEOUT  │              │ INJECTING │     │
   │         └───────────┘              └─────┬─────┘     │
   │                │                         │           │
   │                │                         │ success   │
   │                ▼                         ▼           │
   │         ┌───────────┐              ┌──────────┐      │
   └─────────│   ERROR   │              │ COMPLETE │──────┘
             └───────────┘              └──────────┘
                    ▲
                    │ any failure
                    │
              ┌─────┴─────┐
              │ (any state)│
              └───────────┘
```

---

## Data Flow

### Voice Input Flow
```
User Press Hotkey
       │
       ▼
┌──────────────┐    audio frames    ┌──────────────┐
│ AudioCapture │ ──────────────────▶│RecordingSession│
└──────────────┘                    └───────┬──────┘
                                            │
User Release Hotkey                         │
       │                                    ▼
       ▼                           ┌──────────────┐
┌──────────────┐    transcription  │ SpeechToText │
│RecordingSession│◀────────────────│   (Whisper)  │
└───────┬──────┘                   └──────────────┘
        │
        │ sanitized text
        ▼
┌──────────────┐    send-keys      ┌──────────────┐
│ TmuxInjector │ ─────────────────▶│  Claude Code │
└──────────────┘                   └──────────────┘
```

### Response Output Flow
```
┌──────────────┐    hook event     ┌──────────────┐
│  Claude Code │ ─────────────────▶│  HookHandler │
└──────────────┘                   └───────┬──────┘
                                           │
                                           ▼
                                  ┌──────────────┐
                                  │ResponseParser│
                                  └───────┬──────┘
                                          │
                           ┌──────────────┴──────────────┐
                           │                             │
                    conversational                    code/output
                           │                             │
                           ▼                             ▼
                  ┌──────────────┐              ┌──────────────┐
                  │ TextToSpeech │              │   (silent)   │
                  └──────────────┘              └──────────────┘
```
