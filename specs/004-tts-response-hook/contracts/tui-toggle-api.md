# Contract: TUI Toggle API

**Version**: 1.0.0
**Date**: 2025-11-28

## Overview

This contract defines the TUI keybinding interface for toggling the TTS response hook at runtime.

---

## Keybinding Registration

### Key Assignment

**Key**: `t` (lowercase)

**Context**: Available from main TUI screen

**Conflict Check**: Ensure no existing binding for `t` key

### Textual Binding

```python
from textual.app import App
from textual.binding import Binding

class ClaudeVoiceTUI(App):
    BINDINGS = [
        # ... existing bindings ...
        Binding("t", "toggle_tts_hook", "Toggle TTS Hook", show=True),
    ]
```

---

## Action Handler

### Method Signature

```python
def action_toggle_tts_hook(self) -> None:
    """
    Toggle TTS hook enabled/disabled state.

    Side Effects:
        - Creates or deletes flag file
        - Updates status indicator in TUI
        - Shows notification toast
        - Logs state change
    """
```

### Implementation Flow

```python
def action_toggle_tts_hook(self) -> None:
    flag_file = Path.home() / ".claude-voice" / "tts-hook-enabled"

    try:
        if flag_file.exists():
            # Disable: remove flag file
            flag_file.unlink()
            self._tts_hook_enabled = False
            self._show_notification("TTS Hook Disabled", severity="info")
            self.log.info("TTS hook disabled")
        else:
            # Enable: create flag file
            flag_file.parent.mkdir(parents=True, exist_ok=True)
            flag_file.touch()
            self._tts_hook_enabled = True
            self._show_notification("TTS Hook Enabled", severity="success")
            self.log.info("TTS hook enabled")

        # Update status indicator
        self._update_tts_hook_status()

    except Exception as e:
        self._show_notification(f"Toggle failed: {e}", severity="error")
        self.log.error(f"Failed to toggle TTS hook: {e}")
```

---

## State Management

### State Variable

```python
class ClaudeVoiceTUI(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tts_hook_enabled: bool = self._check_tts_hook_enabled()
```

### State Check

```python
def _check_tts_hook_enabled(self) -> bool:
    """Check current TTS hook state from flag file."""
    flag_file = Path.home() / ".claude-voice" / "tts-hook-enabled"
    return flag_file.exists()
```

### State Persistence

State is persisted via flag file:
- **Enable**: Create file
- **Disable**: Delete file
- **Check**: Test file existence

No in-memory state beyond `_tts_hook_enabled` for UI updates.

---

## UI Updates

### Status Indicator

**Location**: Status panel (top-right or header)

**Widget Type**: StatusPill or similar

**Visual States**:

| State | Display | Color | Icon |
|-------|---------|-------|------|
| Enabled | "TTS Hook ON" | Green | ✓ or 🔊 |
| Disabled | "TTS Hook OFF" | Gray | ✗ or 🔇 |

**Example**:
```python
def _update_tts_hook_status(self) -> None:
    """Update TTS hook status indicator in UI."""
    status_widget = self.query_one("#tts-hook-status", StatusPill)

    if self._tts_hook_enabled:
        status_widget.update(
            text="TTS Hook ON",
            variant="success"  # Green
        )
    else:
        status_widget.update(
            text="TTS Hook OFF",
            variant="default"  # Gray
        )
```

### Notification Toast

**Type**: Temporary toast/notification

**Duration**: 2 seconds

**Examples**:
- "TTS Hook Enabled" (green, success)
- "TTS Hook Disabled" (blue, info)
- "Toggle failed: Permission denied" (red, error)

**Implementation**:
```python
def _show_notification(self, message: str, severity: str = "info") -> None:
    """Show toast notification."""
    self.notify(
        message,
        severity=severity,
        timeout=2.0
    )
```

---

## Error Handling

### Permission Errors

**Cause**: Cannot create/delete flag file (permissions)

**Handling**:
```python
try:
    flag_file.touch()
except PermissionError:
    self._show_notification(
        "Permission denied. Check ~/.claude-voice permissions",
        severity="error"
    )
    return
```

### Directory Missing

**Cause**: `~/.claude-voice/` directory doesn't exist

**Handling**:
```python
flag_file.parent.mkdir(parents=True, exist_ok=True)  # Create if needed
```

### Concurrent Modifications

**Scenario**: External process modifies flag file while TUI running

**Handling**:
- TUI state may become stale
- Next toggle operation will correct state
- Not critical (hook script always checks file)

**Future Enhancement**: Watch flag file for external changes

---

## Logging

### Log Format

```python
self.log.info("TTS hook enabled")
self.log.info("TTS hook disabled")
self.log.error(f"Failed to toggle TTS hook: {error_message}")
```

### Log Destination

- In-app log buffer (displayed in log modal)
- Optional file logging if configured

---

## Testing Contract

### Manual Testing

**Test Case 1: Enable hook**
1. Start TUI with hook disabled
2. Press `t` key
3. **Expected**:
   - Notification: "TTS Hook Enabled"
   - Status indicator: "TTS Hook ON" (green)
   - Flag file created: `~/.claude-voice/tts-hook-enabled`

**Test Case 2: Disable hook**
1. Start TUI with hook enabled
2. Press `t` key
3. **Expected**:
   - Notification: "TTS Hook Disabled"
   - Status indicator: "TTS Hook OFF" (gray)
   - Flag file deleted

**Test Case 3: Rapid toggle**
1. Press `t` multiple times quickly
2. **Expected**:
   - State toggles correctly each time
   - No race conditions or errors

**Test Case 4: Permission error**
1. Make `~/.claude-voice/` read-only: `chmod 444 ~/.claude-voice`
2. Press `t` key
3. **Expected**:
   - Error notification shown
   - State unchanged
   - No crash

### Automated Testing

```python
# tests/ui/test_tts_toggle.py

import pytest
from pathlib import Path
from push_to_talk_claude.ui.tui_app import ClaudeVoiceTUI

def test_toggle_enables_hook(tmp_path, monkeypatch):
    """Test that toggling creates flag file."""
    flag_file = tmp_path / "tts-hook-enabled"
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    app = ClaudeVoiceTUI()
    assert not flag_file.exists()

    app.action_toggle_tts_hook()

    assert flag_file.exists()
    assert app._tts_hook_enabled is True

def test_toggle_disables_hook(tmp_path, monkeypatch):
    """Test that toggling removes flag file."""
    flag_file = tmp_path / "tts-hook-enabled"
    flag_file.touch()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    app = ClaudeVoiceTUI()
    assert flag_file.exists()

    app.action_toggle_tts_hook()

    assert not flag_file.exists()
    assert app._tts_hook_enabled is False

def test_toggle_handles_permission_error(tmp_path, monkeypatch):
    """Test graceful handling of permission errors."""
    flag_file = tmp_path / "tts-hook-enabled"
    flag_file.parent.chmod(0o444)  # Read-only
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    app = ClaudeVoiceTUI()

    # Should not raise exception
    app.action_toggle_tts_hook()

    # State should be unchanged
    assert not flag_file.exists()
```

---

## Integration with Hook Script

### Independence

The TUI toggle and hook script are independent:
- TUI modifies flag file
- Hook script reads flag file
- No direct communication between them

### Synchronization

**Mechanism**: File system as single source of truth

**Flow**:
1. User presses `t` in TUI
2. TUI creates/deletes flag file
3. Next hook invocation checks flag file
4. Hook proceeds or exits based on file existence

**Timing**: Changes take effect on next Claude Code response (not retroactive)

---

## User Documentation

### Help Text

**In-app help**: List `t` key in keybindings help modal

**Description**: "Toggle TTS Hook - Enable/disable audio feedback for Claude responses"

### README Section

```markdown
## TTS Hook Toggle

Press `t` in the TUI to toggle the TTS response hook on or off.

- **Enabled**: Claude's responses will be spoken aloud via macOS `say` command
- **Disabled**: Responses are displayed but not spoken

The toggle state persists across sessions. You can also manually toggle by
creating or removing the file `~/.claude-voice/tts-hook-enabled`.
```

---

## Accessibility

### Keyboard Access

- Pure keyboard operation (no mouse required)
- Single key press (`t`)
- Visible in keybinding list

### Screen Reader

- Status changes announced via notification
- Status indicator readable by screen readers

---

## Performance

### Latency Target

**Target**: < 100ms from keypress to UI update

**Breakdown**:
- File operation: ~10ms (create/delete)
- UI update: ~50ms (widget re-render)
- Notification: ~10ms (toast display)

**Actual**: Typically 20-50ms on modern Macs

### No Blocking

Toggle operation is synchronous but fast enough not to block UI thread.

**Alternative**: Could make async if file operations are slow:
```python
async def action_toggle_tts_hook(self) -> None:
    await run_in_executor(self._toggle_flag_file)
```

---

## Future Enhancements

### Planned (not in v1)

1. **Status in header**: Show TTS hook status in main header bar
2. **File watching**: Detect external flag file changes, update UI
3. **Config integration**: Sync with `config.yaml` for persistence
4. **Per-session toggle**: Option to disable for current session only

### Not Planned

- Remote toggle (API/CLI)
- Multiple toggle profiles
- Scheduled enable/disable
