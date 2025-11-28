# Widget Interface Contracts

**Branch**: `002-textual-tui` | **Date**: 2025-11-28

## Overview

This document defines the interface contracts between TUI components. All widgets follow Textual's compose pattern and use reactive attributes for state management.

---

## 1. StatusPill Widget

**Location**: `src/push_to_talk_claude/ui/widgets/status_pill.py`

### Interface

```python
class StatusPill(Static):
    """Individual status indicator that lights up when active."""

    # Reactive attributes
    active: reactive[bool]  # Whether this pill is currently active

    def __init__(
        self,
        label: str,
        emoji: str,
        color: str,
        status: RecordingStatus,
        **kwargs
    ) -> None:
        """
        Initialize status pill.

        Args:
            label: Display text (e.g., "Recording")
            emoji: Emoji indicator (e.g., "🔴")
            color: CSS color variable when active (e.g., "$error")
            status: The RecordingStatus this pill represents
        """
        ...

    def activate(self) -> None:
        """Set pill to active (illuminated) state."""
        ...

    def deactivate(self) -> None:
        """Set pill to inactive (dimmed) state."""
        ...
```

### CSS Classes

- `.active` - Applied when pill is in active state
- Default state is inactive (dimmed)

### Events Emitted

None - StatusPill is display-only

---

## 2. StatusPanel Widget

**Location**: `src/push_to_talk_claude/ui/widgets/status_panel.py`

### Interface

```python
class StatusPanel(Container):
    """Right panel containing vertically stacked status pills."""

    # Reactive attributes
    current_status: reactive[RecordingStatus]  # Current active status

    def __init__(self, **kwargs) -> None:
        """Initialize status panel with all status pills."""
        ...

    def set_status(self, status: RecordingStatus) -> None:
        """
        Update the active status pill.

        Args:
            status: The new active status
        """
        ...

    def compose(self) -> ComposeResult:
        """Yield StatusPill widgets for each status type."""
        ...
```

### Child Widgets

- 6 `StatusPill` instances (one per status type)
- Arranged vertically with spacing

### Events Emitted

None - StatusPanel is display-only

---

## 3. InfoPanel Widget

**Location**: `src/push_to_talk_claude/ui/widgets/info_panel.py`

### Interface

```python
class InfoPanel(Container):
    """Left panel displaying app configuration and instructions."""

    def __init__(self, app_info: AppInfo, **kwargs) -> None:
        """
        Initialize info panel.

        Args:
            app_info: Application configuration to display
        """
        ...

    def compose(self) -> ComposeResult:
        """Yield widgets for app info display."""
        ...

    def update_info(self, app_info: AppInfo) -> None:
        """Update displayed app information."""
        ...
```

### Display Content

- Application title/banner
- Hotkey configuration
- Whisper model
- Injection mode and target
- Usage instructions

---

## 4. RecordingTimer Widget

**Location**: `src/push_to_talk_claude/ui/widgets/recording_timer.py`

### Interface

```python
class RecordingTimer(Static):
    """Live timer showing recording duration."""

    # Reactive attributes
    elapsed: reactive[float]  # Elapsed seconds
    is_warning: reactive[bool]  # True when approaching max duration

    def __init__(
        self,
        warning_threshold: float = 50.0,
        max_duration: float = 60.0,
        **kwargs
    ) -> None:
        """
        Initialize recording timer.

        Args:
            warning_threshold: Seconds at which to show warning
            max_duration: Maximum recording duration
        """
        ...

    def start(self) -> None:
        """Start the timer from zero."""
        ...

    def stop(self) -> float:
        """
        Stop the timer and return elapsed time.

        Returns:
            Final elapsed time in seconds
        """
        ...

    def reset(self) -> None:
        """Reset timer to zero without starting."""
        ...
```

### CSS Classes

- `.warning` - Applied when elapsed >= warning_threshold
- `.active` - Applied when timer is running

### Update Frequency

10Hz (every 100ms) when running

---

## 5. LogModal Screen

**Location**: `src/push_to_talk_claude/ui/widgets/log_modal.py`

### Interface

```python
class LogModal(ModalScreen):
    """Modal screen displaying console logs."""

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("l", "dismiss", "Close"),
    ]

    def __init__(self, log_buffer: LogBuffer, **kwargs) -> None:
        """
        Initialize log modal.

        Args:
            log_buffer: Buffer containing log entries to display
        """
        ...

    def compose(self) -> ComposeResult:
        """Yield RichLog widget with log contents."""
        ...

    def action_dismiss(self) -> None:
        """Close the modal and return to main screen."""
        ...
```

### Key Bindings

- `Escape` - Close modal
- `L` - Close modal (same key that opens it)
- `Up/Down/PageUp/PageDown` - Scroll (handled by RichLog)

---

## 6. PushToTalkTUI App

**Location**: `src/push_to_talk_claude/ui/tui_app.py`

### Interface

```python
class PushToTalkTUI(App):
    """Main Textual application for push-to-talk interface."""

    CSS_PATH = "styles.css"

    BINDINGS = [
        ("l", "toggle_logs", "Logs"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        config: Config,
        session_manager: RecordingSessionManager,
        **kwargs
    ) -> None:
        """
        Initialize TUI application.

        Args:
            config: Application configuration
            session_manager: Recording session manager instance
        """
        ...

    def compose(self) -> ComposeResult:
        """Compose the main layout with info and status panels."""
        ...

    def action_toggle_logs(self) -> None:
        """Toggle the log modal visibility."""
        ...

    # Callbacks for RecordingSessionManager
    def handle_state_change(self, status: RecordingStatus) -> None:
        """Handle recording state change from background thread."""
        ...

    def handle_transcription(self, text: str) -> None:
        """Handle completed transcription from background thread."""
        ...

    def handle_error(self, error: str) -> None:
        """Handle error from background thread."""
        ...

    def handle_skipped(self, reason: str) -> None:
        """Handle skipped recording from background thread."""
        ...
```

### Layout Structure

```
┌─────────────────────────────────────────────────────┐
│                    Horizontal                        │
│  ┌─────────────────────┐ ┌───────────────────────┐  │
│  │     InfoPanel       │ │    StatusPanel        │  │
│  │     (width: 2fr)    │ │    (width: 1fr)       │  │
│  │                     │ │                       │  │
│  │  - Title            │ │  ┌─────────────────┐  │  │
│  │  - Hotkey: ctrl_r   │ │  │   Recording     │  │  │
│  │  - Model: tiny      │ │  └─────────────────┘  │  │
│  │  - Mode: focused    │ │  ┌─────────────────┐  │  │
│  │  - Target: Active   │ │  │  Transcribing   │  │  │
│  │                     │ │  └─────────────────┘  │  │
│  │  Instructions:      │ │  ┌─────────────────┐  │  │
│  │  - Hold hotkey...   │ │  │   Injecting     │  │  │
│  │  - Press L for logs │ │  └─────────────────┘  │  │
│  │  - Press Q to quit  │ │  ┌─────────────────┐  │  │
│  │                     │ │  │   Complete      │  │  │
│  │                     │ │  └─────────────────┘  │  │
│  │                     │ │  ┌─────────────────┐  │  │
│  │                     │ │  │    Error        │  │  │
│  │                     │ │  └─────────────────┘  │  │
│  │                     │ │  ┌─────────────────┐  │  │
│  │                     │ │  │   Skipped       │  │  │
│  └─────────────────────┘ │  └─────────────────┘  │  │
│                          └───────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Thread Safety Contract

All callbacks from `RecordingSessionManager` execute on background threads. The TUI must use `call_from_thread()` to safely update UI:

```python
def handle_state_change(self, status: RecordingStatus) -> None:
    """Called from background thread - route to main thread."""
    self.call_from_thread(self._update_status, status)

def _update_status(self, status: RecordingStatus) -> None:
    """Called on main thread - safe to update widgets."""
    self.query_one(StatusPanel).set_status(status)
```

---

## CSS Styling Contract

**File**: `src/push_to_talk_claude/ui/styles.css`

Required CSS variables and classes:

```css
/* Layout */
#info-panel { width: 2fr; }
#status-panel { width: 1fr; }

/* Status Pills */
StatusPill { /* inactive state */ }
StatusPill.active { /* illuminated state */ }

/* Timer */
RecordingTimer.warning { /* warning color */ }

/* Log Modal */
LogModal { background: $surface 80%; }
#log-container { /* modal container */ }
#log-view { /* RichLog widget */ }
```
