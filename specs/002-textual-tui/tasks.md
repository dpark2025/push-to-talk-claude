# Tasks: Textual TUI for Push-to-Talk Interface

**Branch**: `002-textual-tui` | **Generated**: 2025-11-28
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## Phase 0: Setup

### Task 0.1: Add Textual Dependency
**File**: `pyproject.toml`
**Depends on**: None
**Parallel**: Yes

Add Textual framework to project dependencies.

```bash
uv add textual
```

**Checkpoint**: `uv run python -c "import textual; print(textual.__version__)"` succeeds

---

### Task 0.2: Create Widget Directory Structure
**Files**: `src/push_to_talk_claude/ui/widgets/__init__.py`
**Depends on**: None
**Parallel**: Yes

Create the widgets subdirectory for Textual custom widgets.

```bash
mkdir -p src/push_to_talk_claude/ui/widgets
touch src/push_to_talk_claude/ui/widgets/__init__.py
```

**Checkpoint**: Directory exists and `__init__.py` is importable

---

### Task 0.3: Create CSS Styles File
**File**: `src/push_to_talk_claude/ui/styles.tcss`
**Depends on**: None
**Parallel**: Yes

Create empty CSS file for Textual styling.

**Checkpoint**: File exists at correct path

---

## Phase 1: Shared Infrastructure

### Task 1.1: Create Data Models
**File**: `src/push_to_talk_claude/ui/models.py`
**Depends on**: Task 0.2
**Parallel**: No

Create data models from data-model.md:
- `StatusPillConfig` dataclass
- `LogEntry` dataclass
- `LogBuffer` class with circular buffer
- `AppInfo` dataclass with `from_config()` factory
- `TimerState` dataclass with `is_warning` and `formatted` properties
- `STATUS_PILLS` default configuration list

**TDD**:
```python
# tests/unit/ui/test_models.py
def test_log_buffer_max_size():
    buffer = LogBuffer(max_size=3)
    buffer.append("INFO", "msg1")
    buffer.append("INFO", "msg2")
    buffer.append("INFO", "msg3")
    buffer.append("INFO", "msg4")
    assert len(buffer) == 3
    assert list(buffer)[0].message == "msg2"

def test_timer_state_warning():
    state = TimerState(elapsed=51.0, warning_threshold=50.0)
    assert state.is_warning is True

def test_timer_state_formatted():
    state = TimerState(elapsed=65.5)
    assert state.formatted == "01:05.50"

def test_app_info_from_config():
    # Test with mock Config object
    ...
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_models.py -v` passes

---

## Phase 2: User Story 1 - Real-Time Status (P1)

### Task 2.1: Implement StatusPill Widget
**File**: `src/push_to_talk_claude/ui/widgets/status_pill.py`
**Depends on**: Task 1.1
**Parallel**: No

Create StatusPill widget per contracts/widget-interfaces.md:
- Extend `Static` widget
- Reactive `active` attribute
- `activate()` and `deactivate()` methods
- `watch_active()` to toggle CSS class
- Display emoji + label text

**TDD**:
```python
# tests/unit/ui/test_status_pill.py
from textual.app import App, ComposeResult

async def test_status_pill_activate():
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield StatusPill("Recording", "🔴", "$error", RecordingStatus.RECORDING)

    async with TestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)
        assert pill.active is False
        pill.activate()
        assert pill.active is True
        assert "active" in pill.classes
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_status_pill.py -v` passes

---

### Task 2.2: Implement StatusPanel Widget
**File**: `src/push_to_talk_claude/ui/widgets/status_panel.py`
**Depends on**: Task 2.1
**Parallel**: No

Create StatusPanel container per contracts/widget-interfaces.md:
- Extend `Container`
- Compose 6 StatusPill children (one per status type)
- `set_status()` method to activate correct pill and deactivate others
- Reactive `current_status` attribute

**TDD**:
```python
# tests/unit/ui/test_status_panel.py
async def test_status_panel_set_status():
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield StatusPanel()

    async with TestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)
        panel.set_status(RecordingStatus.RECORDING)
        pills = pilot.app.query(StatusPill)
        active_pills = [p for p in pills if p.active]
        assert len(active_pills) == 1
        assert active_pills[0].status == RecordingStatus.RECORDING
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_status_panel.py -v` passes

---

### Task 2.3: Add StatusPill CSS Styles
**File**: `src/push_to_talk_claude/ui/styles.tcss`
**Depends on**: Task 2.1
**Parallel**: No

Add CSS for StatusPill widget:
- Default inactive state (dimmed background, muted text)
- `.active` class (bright background, normal text)
- Pill shape with height, padding, text-align
- Color variables for each status type

**Checkpoint**: Visual inspection - pills appear correctly styled

---

## Phase 3: User Story 2 - Live Timer (P2)

### Task 3.1: Implement RecordingTimer Widget
**File**: `src/push_to_talk_claude/ui/widgets/recording_timer.py`
**Depends on**: Task 1.1
**Parallel**: No

Create RecordingTimer widget per contracts/widget-interfaces.md:
- Extend `Static`
- Reactive `elapsed` and `is_warning` attributes
- `start()`, `stop()`, `reset()` methods
- `set_interval(1/10, callback)` for 10Hz updates
- `watch_elapsed()` to update display and warning state

**TDD**:
```python
# tests/unit/ui/test_recording_timer.py
async def test_recording_timer_start_stop():
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield RecordingTimer()

    async with TestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.2)  # Wait 200ms
        elapsed = timer.stop()
        assert elapsed >= 0.15  # Allow some tolerance
        assert elapsed <= 0.3

async def test_recording_timer_warning_state():
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield RecordingTimer(warning_threshold=0.1)

    async with TestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.15)
        assert timer.is_warning is True
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_recording_timer.py -v` passes

---

### Task 3.2: Add RecordingTimer CSS Styles
**File**: `src/push_to_talk_claude/ui/styles.tcss`
**Depends on**: Task 3.1
**Parallel**: No

Add CSS for RecordingTimer widget:
- Default state styling
- `.warning` class with warning color
- `.active` class when running

**Checkpoint**: Visual inspection - timer shows warning color near threshold

---

## Phase 4: User Story 3 - Log History (P2)

### Task 4.1: Implement LogModal Screen
**File**: `src/push_to_talk_claude/ui/widgets/log_modal.py`
**Depends on**: Task 1.1
**Parallel**: No

Create LogModal per contracts/widget-interfaces.md:
- Extend `ModalScreen`
- Key bindings: Escape and L to dismiss
- Compose `RichLog` widget
- Populate from `LogBuffer` on mount
- Container with proper sizing

**TDD**:
```python
# tests/unit/ui/test_log_modal.py
async def test_log_modal_display():
    buffer = LogBuffer()
    buffer.append("INFO", "Test message 1")
    buffer.append("ERROR", "Test message 2")

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield Static("Main")

        def action_show_logs(self):
            self.push_screen(LogModal(buffer))

    async with TestApp().run_test() as pilot:
        await pilot.press("l")  # Assuming L triggers action
        # Verify modal is showing
        assert pilot.app.screen.__class__.__name__ == "LogModal"

async def test_log_modal_dismiss():
    buffer = LogBuffer()

    async with TestApp().run_test() as pilot:
        pilot.app.push_screen(LogModal(buffer))
        await pilot.press("escape")
        assert pilot.app.screen.__class__.__name__ != "LogModal"
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_log_modal.py -v` passes

---

### Task 4.2: Add LogModal CSS Styles
**File**: `src/push_to_talk_claude/ui/styles.tcss`
**Depends on**: Task 4.1
**Parallel**: No

Add CSS for LogModal:
- Semi-transparent background overlay
- Centered container with border
- RichLog widget sizing
- Scroll styling

**Checkpoint**: Visual inspection - modal appears centered with proper overlay

---

## Phase 5: User Story 4 - Emoji/Unicode Alignment (P3)

### Task 5.1: Verify Emoji Alignment in StatusPill
**File**: `tests/unit/ui/test_emoji_alignment.py`
**Depends on**: Task 2.1
**Parallel**: No

Create tests verifying emoji character width is handled correctly:
- Test each status emoji (🔴, ⏳, 💉, ✅, ❌, ⏭️)
- Verify panel borders align correctly
- Test compound emojis specifically

**TDD**:
```python
# tests/unit/ui/test_emoji_alignment.py
async def test_emoji_character_width():
    """Verify emojis don't cause alignment issues."""
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield StatusPanel()

    async with TestApp().run_test() as pilot:
        # Take screenshot and verify alignment
        # Or check rendered output
        pills = pilot.app.query(StatusPill)
        for pill in pills:
            # Verify no extra spacing in rendered content
            assert pill.renderable is not None
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_emoji_alignment.py -v` passes

---

### Task 5.2: Test Graceful Degradation (FR-013)
**File**: `tests/unit/ui/test_degradation.py`
**Depends on**: Task 2.1, Task 1.1
**Parallel**: No

Test terminal capability detection and fallback behavior:
- Test with limited color support
- Test ASCII fallback for emojis when unicode unsupported
- Verify app doesn't crash on basic terminals

**TDD**:
```python
# tests/unit/ui/test_degradation.py
async def test_ascii_fallback_indicators():
    """Verify ASCII fallbacks work when emojis unavailable."""
    # Test that StatusPill can render with ASCII indicators
    ...

async def test_limited_color_support():
    """Verify app works with 16-color terminals."""
    ...
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_degradation.py -v` passes

---

## Phase 6: Integration

### Task 6.1: Implement InfoPanel Widget
**File**: `src/push_to_talk_claude/ui/widgets/info_panel.py`
**Depends on**: Task 1.1
**Parallel**: No

Create InfoPanel per contracts/widget-interfaces.md:
- Extend `Container`
- Display AppInfo data (title, hotkey, model, mode, target)
- Include RecordingTimer widget
- Usage instructions text
- `update_info()` method

**TDD**:
```python
# tests/unit/ui/test_info_panel.py
async def test_info_panel_display():
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="tiny",
        injection_mode="focused",
        target_info="Active window"
    )

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield InfoPanel(app_info)

    async with TestApp().run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        content = str(panel.render())
        assert "ctrl_r" in content
        assert "tiny" in content
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_info_panel.py -v` passes

---

### Task 6.2: Implement PushToTalkTUI App
**File**: `src/push_to_talk_claude/ui/tui_app.py`
**Depends on**: Task 2.2, Task 3.1, Task 4.1, Task 6.1
**Parallel**: No

Create main TUI application per contracts/widget-interfaces.md:
- Extend `App`
- Set `CSS_PATH = "styles.tcss"`
- Key bindings: L for logs, Q for quit
- Compose Horizontal layout with InfoPanel (2fr) and StatusPanel (1fr)
- Thread-safe callbacks using `call_from_thread()`:
  - `handle_state_change(status)`
  - `handle_transcription(text)`
  - `handle_error(error)`
  - `handle_skipped(reason)`
- Wire callbacks to `RecordingSessionManager`

**TDD**:
```python
# tests/unit/ui/test_tui_app.py
async def test_tui_layout():
    config = Mock()
    session_manager = Mock()

    async with PushToTalkTUI(config, session_manager).run_test() as pilot:
        info_panel = pilot.app.query_one("#info-panel")
        status_panel = pilot.app.query_one("#status-panel")
        assert info_panel is not None
        assert status_panel is not None

async def test_tui_toggle_logs():
    async with PushToTalkTUI(config, session_manager).run_test() as pilot:
        await pilot.press("l")
        assert isinstance(pilot.app.screen, LogModal)
        await pilot.press("l")
        assert not isinstance(pilot.app.screen, LogModal)
```

**Checkpoint**: `uv run pytest tests/unit/ui/test_tui_app.py -v` passes

---

### Task 6.3: Add Layout CSS Styles
**File**: `src/push_to_talk_claude/ui/styles.tcss`
**Depends on**: Task 6.2
**Parallel**: No

Add CSS for main layout:
- `#info-panel { width: 2fr; }`
- `#status-panel { width: 1fr; }`
- Horizontal container styling
- Border and padding for panels

**Checkpoint**: Visual inspection - two-panel layout with 2:1 ratio

---

### Task 6.4: Update Widget Exports
**File**: `src/push_to_talk_claude/ui/widgets/__init__.py`
**Depends on**: Task 2.1, Task 2.2, Task 3.1, Task 4.1, Task 6.1
**Parallel**: No

Export all widgets from the package:
```python
from .status_pill import StatusPill
from .status_panel import StatusPanel
from .recording_timer import RecordingTimer
from .log_modal import LogModal
from .info_panel import InfoPanel
```

**Checkpoint**: `from push_to_talk_claude.ui.widgets import StatusPill` works

---

## Phase 7: App Integration

### Task 7.1: Integrate TUI into app.py
**File**: `src/push_to_talk_claude/app.py`
**Depends on**: Task 6.2
**Parallel**: No

Modify main App class to use Textual TUI:
- Import `PushToTalkTUI`
- Replace Rich panel printing with TUI
- Wire existing callbacks to TUI handlers
- Ensure `call_from_thread()` is used for background thread callbacks
- Keep all existing core functionality unchanged

**Checkpoints**:
- `uv run claude-voice --help` works
- Hotkey (ctrl_r) still triggers recording start/stop (FR-009 verification)
- Status transitions display correctly in TUI

---

### Task 7.2: Integration Test - Full Flow
**File**: `tests/integration/test_tui_integration.py`
**Depends on**: Task 7.1
**Parallel**: No

Create integration test with mock session manager:
- Verify status transitions work
- Verify timer updates during recording
- Verify log modal opens/closes
- Verify app exits cleanly

**TDD**:
```python
# tests/integration/test_tui_integration.py
async def test_full_recording_flow():
    """Test complete recording cycle through TUI."""
    mock_session = Mock()
    config = create_test_config()

    async with PushToTalkTUI(config, mock_session).run_test() as pilot:
        # Simulate state change
        pilot.app.handle_state_change(RecordingStatus.RECORDING)
        await pilot.pause(0.1)

        status_panel = pilot.app.query_one(StatusPanel)
        assert status_panel.current_status == RecordingStatus.RECORDING

        # Simulate transcription complete
        pilot.app.handle_transcription("Hello world")
        pilot.app.handle_state_change(RecordingStatus.COMPLETE)
        await pilot.pause(0.1)

        assert status_panel.current_status == RecordingStatus.COMPLETE
```

**Checkpoint**: `uv run pytest tests/integration/test_tui_integration.py -v` passes

---

## Phase 8: Polish & Cleanup

### Task 8.1: Handle Terminal Resize
**File**: `src/push_to_talk_claude/ui/tui_app.py`
**Depends on**: Task 6.2
**Parallel**: No

Ensure graceful terminal resize handling:
- Test resize during recording
- Test resize with modal open
- Verify no display corruption

**Checkpoint**: Manual test - resize terminal, verify no corruption

---

### Task 8.2: Remove Legacy Rich UI Code
**Files**: `src/push_to_talk_claude/ui/indicators.py`, `src/push_to_talk_claude/ui/notifications.py`
**Depends on**: Task 7.2
**Parallel**: No

Remove or deprecate Rich-based UI code that is no longer needed:
- Keep any shared utilities
- Remove panel printing functions
- Update imports in app.py

**Checkpoint**: No unused imports, app still works

---

### Task 8.3: Update Documentation
**Files**: `README.md`, `specs/002-textual-tui/quickstart.md`
**Depends on**: Task 7.2
**Parallel**: No

Update documentation to reflect new TUI:
- Update README with new screenshots
- Update quickstart with final commands
- Document new key bindings (L for logs, Q for quit)

**Checkpoint**: Documentation is accurate and up to date

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 0 | 0.1-0.3 | Setup (3 tasks, parallel) |
| 1 | 1.1 | Shared Infrastructure (1 task) |
| 2 | 2.1-2.3 | User Story 1 - Status (3 tasks) |
| 3 | 3.1-3.2 | User Story 2 - Timer (2 tasks) |
| 4 | 4.1-4.2 | User Story 3 - Logs (2 tasks) |
| 5 | 5.1-5.2 | User Story 4 - Emoji + Degradation (2 tasks) |
| 6 | 6.1-6.4 | Integration (4 tasks) |
| 7 | 7.1-7.2 | App Integration (2 tasks) |
| 8 | 8.1-8.3 | Polish & Cleanup (3 tasks) |

**Total**: 22 tasks

## Dependency Graph

```
Phase 0 (parallel)
├── 0.1 Add Textual ─────────────────────────┐
├── 0.2 Create Widget Dir ───────┐           │
└── 0.3 Create CSS File          │           │
                                 ▼           │
Phase 1                          1.1 Models ◄┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
Phase 2          2.1 StatusPill  │         Phase 4
                    │            │         4.1 LogModal
                    ▼            │            │
                 2.2 StatusPanel │            ▼
                    │            │         4.2 LogModal CSS
                    ▼            │
                 2.3 StatusPill CSS
                                 │
Phase 3                          ▼
                          3.1 RecordingTimer
                                 │
                                 ▼
                          3.2 Timer CSS
                                 │
Phase 5                          │
                          5.1 Emoji Tests ◄──┘
                                 │
                          5.2 Degradation Tests
                                 │
Phase 6              ┌───────────┼───────────┐
                     ▼           │           │
              6.1 InfoPanel      │           │
                     │           │           │
                     └───────────┼───────────┘
                                 ▼
                          6.2 PushToTalkTUI
                                 │
                                 ▼
                          6.3 Layout CSS
                                 │
                                 ▼
                          6.4 Widget Exports
                                 │
Phase 7                          ▼
                          7.1 Integrate app.py
                                 │
                                 ▼
                          7.2 Integration Test
                                 │
Phase 8              ┌───────────┼───────────┐
                     ▼           ▼           ▼
              8.1 Resize   8.2 Cleanup   8.3 Docs
```
