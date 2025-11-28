# Data Model: Textual TUI for Push-to-Talk Interface

**Branch**: `002-textual-tui` | **Date**: 2025-11-28

## Entities

### 1. RecordingStatus (Enum) - Existing

Current recording state enumeration. **No changes required.**

```python
class RecordingStatus(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    INJECTING = "injecting"
    COMPLETE = "complete"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"
```

**Used by**: StatusPanel to determine which pill is active

### 2. StatusPillConfig (New)

Configuration for each status indicator pill in the status panel.

| Attribute | Type | Description |
|-----------|------|-------------|
| status | RecordingStatus | The status this pill represents |
| label | str | Display text (e.g., "Recording") |
| emoji | str | Emoji indicator (e.g., "🔴") |
| color | str | CSS color when active (e.g., "$error") |

```python
@dataclass
class StatusPillConfig:
    status: RecordingStatus
    label: str
    emoji: str
    color: str  # Textual CSS color variable
```

**Default configurations**:
```python
STATUS_PILLS = [
    StatusPillConfig(RecordingStatus.RECORDING, "Recording", "🔴", "$error"),
    StatusPillConfig(RecordingStatus.TRANSCRIBING, "Transcribing", "⏳", "$warning"),
    StatusPillConfig(RecordingStatus.INJECTING, "Injecting", "💉", "$primary"),
    StatusPillConfig(RecordingStatus.COMPLETE, "Complete", "✅", "$success"),
    StatusPillConfig(RecordingStatus.ERROR, "Error", "❌", "$error"),
    StatusPillConfig(RecordingStatus.IDLE, "Skipped", "⏭️", "$surface"),
]
```

### 3. LogEntry (New)

Single entry in the console log buffer.

| Attribute | Type | Description |
|-----------|------|-------------|
| timestamp | float | Unix timestamp (monotonic) |
| level | str | Log level (DEBUG, INFO, WARNING, ERROR) |
| message | str | Log message text |

```python
@dataclass
class LogEntry:
    timestamp: float
    level: str
    message: str

    def __str__(self) -> str:
        time_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        return f"[{time_str}] [{self.level}] {self.message}"
```

### 4. LogBuffer (New)

Circular buffer storing recent log entries for the log modal.

| Attribute | Type | Description |
|-----------|------|-------------|
| max_size | int | Maximum entries to retain (default: 100) |
| entries | deque[LogEntry] | Circular buffer of log entries |

```python
from collections import deque

class LogBuffer:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.entries: deque[LogEntry] = deque(maxlen=max_size)

    def append(self, level: str, message: str) -> None:
        self.entries.append(LogEntry(
            timestamp=time.time(),
            level=level,
            message=message
        ))

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)
```

### 5. AppInfo (New)

Application configuration displayed in the info panel.

| Attribute | Type | Description |
|-----------|------|-------------|
| hotkey | str | Configured push-to-talk hotkey |
| whisper_model | str | Whisper model name (tiny, base, etc.) |
| injection_mode | str | "focused" or "tmux" |
| target_info | str | tmux target or "Active window" |

```python
@dataclass
class AppInfo:
    hotkey: str
    whisper_model: str
    injection_mode: str
    target_info: str

    @classmethod
    def from_config(cls, config: Config) -> "AppInfo":
        if config.injection.mode == "focused":
            target = "Active window"
        else:
            target = f"{config.tmux.session_name}:{config.tmux.window_index}.{config.tmux.pane_index}"

        return cls(
            hotkey=config.push_to_talk.hotkey,
            whisper_model=config.whisper.model,
            injection_mode=config.injection.mode,
            target_info=target
        )
```

### 6. TimerState (New)

State for the recording duration timer.

| Attribute | Type | Description |
|-----------|------|-------------|
| start_time | float | Monotonic time when recording started |
| elapsed | float | Current elapsed seconds |
| is_running | bool | Whether timer is actively counting |
| warning_threshold | float | Seconds before max when warning shows (default: 50) |
| max_duration | float | Maximum recording duration (default: 60) |

```python
@dataclass
class TimerState:
    start_time: float = 0.0
    elapsed: float = 0.0
    is_running: bool = False
    warning_threshold: float = 50.0  # Show warning at 50s of 60s max
    max_duration: float = 60.0

    @property
    def is_warning(self) -> bool:
        return self.elapsed >= self.warning_threshold

    @property
    def formatted(self) -> str:
        minutes, seconds = divmod(self.elapsed, 60)
        return f"{int(minutes):02d}:{seconds:05.2f}"
```

## State Transitions

### Recording State Machine

```
                    ┌──────────────┐
                    │     IDLE     │◄─────────────────┐
                    └──────┬───────┘                  │
                           │ hotkey_press             │
                           ▼                          │
                    ┌──────────────┐                  │
                    │  RECORDING   │──────────────────┤ (timeout/cancel)
                    └──────┬───────┘                  │
                           │ hotkey_release           │
                           ▼                          │
                    ┌──────────────┐                  │
            ┌───────│ TRANSCRIBING │───────┐          │
            │       └──────────────┘       │          │
            │ (skip)       │               │ (error)  │
            │              │ success       │          │
            │              ▼               ▼          │
            │       ┌──────────────┐ ┌──────────┐     │
            │       │  INJECTING   │ │  ERROR   │─────┤
            │       └──────┬───────┘ └──────────┘     │
            │              │                          │
            │              │ complete                 │
            │              ▼                          │
            │       ┌──────────────┐                  │
            └──────►│  COMPLETE    │──────────────────┘
                    └──────────────┘
                           │
                           │ (auto-return after brief display)
                           ▼
                    ┌──────────────┐
                    │     IDLE     │
                    └──────────────┘
```

### UI Update Triggers

| Event | UI Update |
|-------|-----------|
| Status change | Activate corresponding pill, deactivate others |
| Recording start | Start timer, show elapsed time |
| Recording stop | Freeze timer display |
| Transcription complete | Show in log buffer |
| Skip detected | Show skip reason in log buffer |
| Error occurred | Show error in log buffer, activate error pill |
| Log modal open | Populate RichLog from buffer |

## Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                      PushToTalkTUI (App)                    │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────────┐    │
│  │     InfoPanel       │    │     StatusPanel         │    │
│  │                     │    │                         │    │
│  │  ┌───────────────┐  │    │  ┌─────────────────┐   │    │
│  │  │   AppInfo     │  │    │  │  StatusPill x6  │   │    │
│  │  │  (display)    │  │    │  │  (one per status)│   │    │
│  │  └───────────────┘  │    │  └─────────────────┘   │    │
│  │                     │    │                         │    │
│  │  ┌───────────────┐  │    │  ┌─────────────────┐   │    │
│  │  │ RecordingTimer│  │    │  │  TimerDisplay   │   │    │
│  │  │  (live)       │  │    │  │  (when active)  │   │    │
│  │  └───────────────┘  │    │  └─────────────────┘   │    │
│  └─────────────────────┘    └─────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    LogBuffer                         │   │
│  │                  (100 entries)                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │               LogModal (ModalScreen)                 │   │
│  │                  (on "L" keypress)                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │
         │ callbacks via call_from_thread()
         ▼
┌─────────────────────────────────────────────────────────────┐
│              RecordingSessionManager (existing)             │
│                                                             │
│  on_state_change(status) ──────► StatusPanel.update()      │
│  on_transcription(text) ───────► LogBuffer.append()        │
│  on_error(msg) ────────────────► LogBuffer.append()        │
│  on_skipped(reason) ───────────► LogBuffer.append()        │
└─────────────────────────────────────────────────────────────┘
```

## Validation Rules

1. **LogBuffer.max_size**: Must be > 0, default 100
2. **TimerState.warning_threshold**: Must be < max_duration
3. **StatusPillConfig.color**: Must be valid Textual CSS color variable
4. **AppInfo.hotkey**: Must be in SUPPORTED_HOTKEYS
