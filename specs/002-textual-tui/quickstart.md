# Quickstart: Textual TUI Implementation

**Branch**: `002-textual-tui` | **Date**: 2025-11-28

## Prerequisites

1. Existing push-to-talk-claude codebase checked out
2. Python 3.9+ installed
3. uv package manager

## Setup

### 1. Add Textual Dependency

```bash
# Add textual to pyproject.toml dependencies
uv add textual
```

### 2. Create Widget Directory Structure

```bash
mkdir -p src/push_to_talk_claude/ui/widgets
touch src/push_to_talk_claude/ui/widgets/__init__.py
```

### 3. Create CSS File

```bash
touch src/push_to_talk_claude/ui/styles.css
```

## Implementation Order

### Phase 1: Core Widgets (can be tested standalone)

1. **StatusPill** (`ui/widgets/status_pill.py`)
   - Simple Static widget with active/inactive states
   - Test: `python -m pytest tests/unit/ui/test_status_pill.py`

2. **StatusPanel** (`ui/widgets/status_panel.py`)
   - Container with 6 StatusPill children
   - Test: Verify set_status() activates correct pill

3. **InfoPanel** (`ui/widgets/info_panel.py`)
   - Static display of app configuration
   - Test: Verify renders AppInfo correctly

### Phase 2: Dynamic Widgets

4. **RecordingTimer** (`ui/widgets/recording_timer.py`)
   - Reactive timer with 10Hz updates
   - Test: Start/stop/reset, verify warning state

5. **LogModal** (`ui/widgets/log_modal.py`)
   - ModalScreen with RichLog
   - Test: Open/close, verify log display

### Phase 3: Integration

6. **PushToTalkTUI** (`ui/tui_app.py`)
   - Main App composing all widgets
   - Wire callbacks to RecordingSessionManager
   - Test: Full integration test

7. **Update app.py**
   - Replace Rich-based UI with TUI
   - Keep existing core logic unchanged

## Minimal Working Example

```python
# Test the TUI layout without recording functionality
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

class TestTUI(App):
    CSS = """
    #info-panel { width: 2fr; border: solid green; }
    #status-panel { width: 1fr; border: solid blue; }
    .pill { height: 3; margin: 1; text-align: center; }
    .pill.active { background: $primary; }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="info-panel"):
                yield Static("Claude Voice\n\nHotkey: ctrl_r\nModel: tiny")
            with Vertical(id="status-panel"):
                yield Static("🔴 Recording", classes="pill active")
                yield Static("⏳ Transcribing", classes="pill")
                yield Static("✅ Complete", classes="pill")

if __name__ == "__main__":
    TestTUI().run()
```

Run with:
```bash
uv run python -c "$(cat above_code)"
```

## Testing Strategy

### Unit Tests

```bash
# Test individual widgets
uv run pytest tests/unit/ui/ -v
```

### Integration Tests

```bash
# Test full TUI with mock session manager
uv run pytest tests/integration/test_tui_integration.py -v
```

### Manual Testing

```bash
# Run the actual application
uv run claude-voice

# Verify:
# 1. Two-panel layout appears correctly (Catppuccin Mocha theme)
# 2. Press hotkey - Recording pill lights up
# 3. Release hotkey - Transcribing pill lights up
# 4. Completion - Complete pill lights up briefly
# 5. Press L - Log modal opens
# 6. Press Escape or L - Log modal closes
# 7. Press Ctrl+\ - Options/command palette opens
# 8. Press Q - App exits cleanly
# 9. Instruction text shows correct target (focused window or tmux session)
```

## Common Issues

### Textual not finding CSS

Ensure `CSS_PATH = "styles.css"` points to correct location relative to the module.

### pynput conflicts with Textual

Both use separate event loops. Ensure pynput callbacks use `call_from_thread()`:

```python
def _handle_state_change(self, status: RecordingStatus) -> None:
    self.call_from_thread(self._update_status, status)
```

### Timer not updating

Check that `set_interval()` timer is resumed after creation:

```python
def start(self) -> None:
    self.start_time = monotonic()
    self.timer.resume()  # Don't forget this!
```

## Verification Checklist

- [x] `uv run claude-voice --help` works
- [x] TUI displays two-panel layout with Catppuccin Mocha theme
- [x] Status pills illuminate on state changes
- [x] Timer counts up during recording
- [x] Timer shows warning color near 60s
- [x] Log modal opens/closes with L key
- [x] Options/command palette opens with Ctrl+\
- [x] App exits cleanly with Q or Ctrl+C
- [x] Emoji indicators align correctly (no border offset)
- [x] Terminal resize doesn't corrupt display
- [x] Instruction text shows mode-specific target (focused window or tmux session)

## Implementation Complete

All 22 tasks have been implemented and tested. The Textual TUI is now the default UI mode.

### Key Files Created

- `src/push_to_talk_claude/ui/widgets/` - Widget package
  - `status_pill.py` - Individual status indicator
  - `status_panel.py` - Container for status pills
  - `recording_timer.py` - Live recording timer
  - `log_modal.py` - Log history modal
  - `info_panel.py` - App configuration panel
- `src/push_to_talk_claude/ui/tui_app.py` - Main TUI application
- `src/push_to_talk_claude/ui/styles.tcss` - Textual CSS styles
- `src/push_to_talk_claude/ui/models.py` - Data models

### Test Coverage

- 84 tests total (75 unit + 9 integration)
- All tests passing
