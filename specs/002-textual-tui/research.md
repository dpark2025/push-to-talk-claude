# Research: Textual TUI for Push-to-Talk Interface

**Branch**: `002-textual-tui` | **Date**: 2025-11-28

## Research Topics

### 1. Textual Framework Selection

**Decision**: Use Textual (by Textualize) as the TUI framework

**Rationale**:
- Made by the same team as Rich (our current dependency) - ensures compatibility
- Handles unicode/emoji character width calculation correctly (solving our core problem)
- Supports reactive UI updates without screen reprinting
- Built-in CSS styling system for visual customization
- Active development, high-quality documentation (2483 code snippets in docs)
- MIT licensed, works on macOS 11.0+

**Alternatives Considered**:
- **Rich panels (current)**: Rejected - character width calculation issues with emojis
- **PyTermGUI**: Less documentation, smaller community
- **Bubble Tea (Go)**: Would require rewriting entire app in Go
- **Curses/ncurses**: Too low-level, poor unicode support

### 2. Layout Architecture

**Decision**: Use Horizontal container with two child containers (2/3 + 1/3 split)

**Rationale**:
- Textual's `Horizontal` container provides simple side-by-side layout
- CSS `width: 2fr` and `width: 1fr` gives 2:1 ratio (66%/33%)
- Containers automatically handle resize events
- Clean separation between info panel and status panel

**Implementation Pattern**:
```python
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult

def compose(self) -> ComposeResult:
    with Horizontal():
        yield InfoPanel(id="info-panel")      # width: 2fr
        yield StatusPanel(id="status-panel")  # width: 1fr
```

**CSS**:
```css
#info-panel { width: 2fr; }
#status-panel { width: 1fr; }
```

### 3. Real-Time Timer Updates

**Decision**: Use `set_interval()` with reactive attributes at 10Hz (100ms)

**Rationale**:
- Textual's `set_interval(1/10, callback)` provides precise timing
- Reactive attributes (`reactive`) automatically trigger UI updates
- `watch_*` methods respond to attribute changes without manual refresh
- 10Hz is smooth enough for timer display, not too CPU intensive

**Implementation Pattern**:
```python
from textual.reactive import reactive
from time import monotonic

class RecordingTimer(Static):
    start_time = reactive(0.0)
    elapsed = reactive(0.0)

    def on_mount(self) -> None:
        self.timer = self.set_interval(1/10, self.update_elapsed, pause=True)

    def update_elapsed(self) -> None:
        self.elapsed = monotonic() - self.start_time

    def watch_elapsed(self, elapsed: float) -> None:
        minutes, seconds = divmod(elapsed, 60)
        self.update(f"{int(minutes):02d}:{seconds:05.2f}")

    def start(self) -> None:
        self.start_time = monotonic()
        self.timer.resume()

    def stop(self) -> None:
        self.timer.pause()
```

### 4. Status Pill Widgets

**Decision**: Custom widget extending `Static` with CSS styling for pill shape and active/inactive states

**Rationale**:
- `Static` widget provides simple text display with full CSS support
- CSS classes can toggle between active (bright) and inactive (dim) states
- Border-radius and padding create pill/rounded rectangle appearance
- Reactive `active` attribute triggers visual state changes

**Implementation Pattern**:
```python
from textual.reactive import reactive
from textual.widgets import Static

class StatusPill(Static):
    active = reactive(False)

    def __init__(self, label: str, **kwargs):
        super().__init__(label, **kwargs)
        self.label = label

    def watch_active(self, active: bool) -> None:
        self.set_class(active, "active")
```

**CSS**:
```css
StatusPill {
    width: 100%;
    height: 3;
    padding: 0 2;
    text-align: center;
    border: round $surface-lighten-2;
    background: $surface;
    color: $text-muted;
}

StatusPill.active {
    background: $primary;
    color: $text;
    border: round $primary-lighten-2;
}
```

### 5. Modal Log Viewer

**Decision**: Use `ModalScreen` subclass with `RichLog` widget for scrollable logs

**Rationale**:
- `ModalScreen` blocks underlying UI interaction and dims background
- `RichLog` widget provides efficient scrolling log display
- Key binding "L" to push/pop modal screen
- Stores last 100 lines in circular buffer

**Implementation Pattern**:
```python
from textual.screen import ModalScreen
from textual.widgets import RichLog
from textual.containers import Container

class LogModal(ModalScreen):
    BINDINGS = [("escape", "dismiss", "Close"), ("l", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        with Container(id="log-container"):
            yield RichLog(id="log-view", max_lines=100)

    def on_mount(self) -> None:
        # Populate from app's log buffer
        log_view = self.query_one("#log-view", RichLog)
        for line in self.app.log_buffer:
            log_view.write(line)
```

### 6. Integration with Existing Core Components

**Decision**: Keep existing `RecordingSessionManager` callbacks, route them to TUI updates

**Rationale**:
- Core recording logic remains unchanged (reliability principle)
- TUI layer only handles presentation
- Existing callbacks (`on_state_change`, `on_transcription`, `on_error`, `on_skipped`) map directly to UI updates
- Thread-safe communication via Textual's `call_from_thread()` for background callbacks

**Implementation Pattern**:
```python
class PushToTalkTUI(App):
    def __init__(self, session_manager: RecordingSessionManager):
        super().__init__()
        self.session_manager = session_manager
        # Wire callbacks to UI methods
        session_manager._on_state_change = self._handle_state_change

    def _handle_state_change(self, status: RecordingStatus) -> None:
        # Called from background thread - use call_from_thread
        self.call_from_thread(self._update_status_pills, status)

    def _update_status_pills(self, status: RecordingStatus) -> None:
        # Runs on main thread, safe to update UI
        for pill in self.query(StatusPill):
            pill.active = pill.status_type == status
```

### 7. Keyboard Handling with pynput

**Decision**: Continue using pynput for global hotkey, Textual handles in-app keys

**Rationale**:
- pynput captures global hotkeys even when terminal not focused
- Textual handles in-app keys (L for logs, arrow keys for scrolling)
- Both can coexist - pynput runs in separate listener thread
- Must use `call_from_thread()` when pynput triggers TUI updates

**Key Bindings**:
- Global (pynput): Configurable hotkey (default: ctrl_r) for recording
- In-app (Textual): "L" for log modal, "Q" for quit, arrow keys for log scroll

### 8. Graceful Degradation

**Decision**: Detect terminal capabilities and adjust styling

**Rationale**:
- Textual auto-detects color support (16, 256, truecolor)
- Falls back gracefully on limited terminals
- Unicode support checked via environment/terminal detection
- Can provide ASCII fallback for status indicators if needed

**Implementation**:
```python
class StatusPill(Static):
    def __init__(self, label: str, emoji: str, ascii_fallback: str, **kwargs):
        self.emoji = emoji
        self.ascii_fallback = ascii_fallback
        display = emoji if self.app.console.is_terminal else ascii_fallback
        super().__init__(f"{display} {label}", **kwargs)
```

## Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # ... existing ...
    "textual>=0.40.0",  # TUI framework
]
```

## Performance Considerations

1. **Timer update rate**: 10Hz (100ms) balances smoothness vs CPU
2. **Log buffer size**: 100 lines prevents memory growth
3. **Reactive updates**: Only changed attributes trigger redraws
4. **Thread safety**: `call_from_thread()` for background callbacks

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Textual conflicts with pynput | Test early - both use separate event loops |
| Performance regression on startup | Profile model loading, consider lazy init |
| Terminal compatibility issues | Test on iTerm2, Terminal.app, Kitty, Alacritty |
| Unicode width still wrong | Textual uses wcwidth internally - verify with test cases |
