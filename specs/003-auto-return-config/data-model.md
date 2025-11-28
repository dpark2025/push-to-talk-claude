# Data Model: Auto-Return Configuration

**Feature**: 003-auto-return-config
**Date**: 2025-11-28

## Entity Changes

### InjectionConfig (Modified)

**Location**: `src/push_to_talk_claude/utils/config.py`

```python
@dataclass
class InjectionConfig:
    mode: str = "focused"  # "focused" or "tmux"
    auto_return: bool = False  # NEW: Send Enter after injection
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| mode | str | "focused" | Injection mode (existing) |
| auto_return | bool | False | Send Enter keystroke after text injection |

**Validation**: None required (boolean type is self-validating via YAML parser)

### RecordingSessionManager (Modified)

**Location**: `src/push_to_talk_claude/core/recording_session.py`

```python
class RecordingSessionManager:
    # NEW: Mutable property for runtime toggle
    auto_return: bool = False
```

| Property | Type | Description |
|----------|------|-------------|
| auto_return | bool | Current auto-return state (can be toggled at runtime) |

### AppInfo (Modified)

**Location**: `src/push_to_talk_claude/ui/models.py`

```python
@dataclass
class AppInfo:
    hotkey: str
    whisper_model: str
    injection_mode: str
    target_info: str
    auto_return: bool           # NEW: For UI display
    transcript_logging: str     # NEW: Path or "DISABLED"
```

| Field | Type | Description |
|-------|------|-------------|
| auto_return | bool | Current auto-return setting for display |
| transcript_logging | str | Transcript save path or "DISABLED" |

**Logic for transcript_logging**:
```python
if config.logging.save_transcripts:
    transcript_logging = config.logging.transcripts_dir  # e.g., ".tts-transcriptions"
else:
    transcript_logging = "DISABLED"
```

### PushToTalkTUI (Modified)

**Location**: `src/push_to_talk_claude/ui/tui_app.py`

```python
class PushToTalkTUI(App):
    BINDINGS = [
        # ... existing bindings ...
        Binding("a", "toggle_auto_return", "Auto-Return"),  # NEW
    ]
```

| Binding | Key | Action | Footer Label |
|---------|-----|--------|--------------|
| toggle_auto_return | a | Toggle auto-return on/off | "Auto-Return" |

## YAML Configuration Schema

**Location**: `~/.claude-voice/config.yaml`

```yaml
injection:
  mode: "focused"      # existing
  auto_return: false   # NEW (optional, defaults to false)
```

## State Transitions

### Auto-Return Toggle State

```
         ┌─────────────────────────────────────┐
         │                                     │
         ▼                                     │
    ┌─────────┐    press 'a'    ┌──────────┐   │
    │   OFF   │ ──────────────► │    ON    │ ──┘
    └─────────┘                 └──────────┘
         ▲                           │
         │         press 'a'         │
         └───────────────────────────┘
```

### Injection Flow with Auto-Return

```
INJECTING → inject_text() → [auto_return?] → send_enter() → COMPLETE
                                  │
                                  └── if false, skip send_enter()
```

## Relationships

```
Config.injection.auto_return (initial value)
    │
    ▼
App._initialize_components()
    │
    ├── → RecordingSessionManager.auto_return (mutable)
    │       └── → Injector.send_enter() [conditional]
    │
    └── → AppInfo.from_config()
            └── → InfoPanel display

User presses 'a'
    │
    ▼
TUI.action_toggle_auto_return()
    │
    ├── → App.toggle_auto_return()
    │       └── → RecordingSessionManager.auto_return = !current
    │
    ├── → InfoPanel.update_auto_return(new_value)
    │
    └── → TUI.notify("Auto-Return: ON/OFF")
```

## Thread Safety

- `auto_return` is a simple boolean
- Python bool assignment is atomic at the bytecode level
- Read happens after injection completes (no race with toggle)
- No explicit locking required
