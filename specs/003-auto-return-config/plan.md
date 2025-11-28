# Implementation Plan: Auto-Return Configuration

**Branch**: `003-auto-return-config` | **Date**: 2025-11-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-auto-return-config/spec.md`

## Summary

Add an `auto_return` configuration option to the injection settings that automatically sends an Enter keystroke after transcribed text is injected. Includes a visual status indicator in the TUI info panel and a runtime toggle via keyboard shortcut (`a` key).

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.11)
**Primary Dependencies**: pynput (keyboard), Textual (TUI), PyYAML (config)
**Storage**: YAML config file (~/.claude-voice/config.yaml)
**Testing**: pytest, pytest-asyncio
**Target Platform**: macOS 11.0+
**Project Type**: Single Python package
**Performance Goals**: Enter keystroke sent within 50ms of text injection; toggle response <100ms
**Constraints**: Must work with both focused injection (pynput) and tmux injection modes
**Scale/Scope**: Config option + runtime toggle + UI indicator + behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy is Non-Negotiable | PASS | No external services touched; purely local keystroke |
| II. Speed Matters | PASS | Single keystroke adds <10ms latency; toggle is instant |
| III. Smart Filtering | N/A | Does not affect TTS filtering |
| IV. Reliability Over Features | PASS | Core loop unchanged; auto-return is additive |
| V. Terminal Agnostic | PASS | Works with both focused and tmux modes |
| VI. Smart Defaults | PASS | Defaults to false (backward compatible) |
| VII. Secure by Default | PASS | No new input vectors; Enter is just a keystroke |
| VIII. Ship Small | PASS | Minimal scope: config + toggle + indicator + behavior |

**Gate Result**: PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-auto-return-config/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A - no new APIs)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/push_to_talk_claude/
├── utils/
│   └── config.py           # Modify: Add auto_return to InjectionConfig
├── core/
│   ├── focused_injector.py # Modify: Add send_enter() method
│   ├── tmux_injector.py    # Modify: Add send_enter() method
│   └── recording_session.py # Modify: Call send_enter() after inject_text()
├── app.py                  # Modify: Wire auto_return, expose toggle method
└── ui/
    ├── models.py           # Modify: Add auto_return to AppInfo
    ├── tui_app.py          # Modify: Add toggle binding and action
    └── widgets/
        └── info_panel.py   # Modify: Display auto-return status, add update method

config.default.yaml         # Modify: Add auto_return documentation

tests/
├── unit/
│   └── test_config.py      # Add: Test auto_return validation
└── integration/
    └── test_auto_return.py # Add: Test end-to-end auto-return + toggle
```

**Structure Decision**: Existing single project structure; no new directories needed.

## Complexity Tracking

> No Constitution Check violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Implementation Approach

### Layer 1: Configuration

1. **InjectionConfig dataclass** (config.py:35-36)
   - Add `auto_return: bool = False` field
   - No validation needed (boolean type is self-validating)

2. **config.default.yaml** (injection section)
   - Add `auto_return: false` with documentation comment

### Layer 2: Injector Changes

3. **FocusedInjector** (focused_injector.py)
   - Add `send_enter()` method using `pynput.keyboard.Key.enter`

4. **TmuxInjector** (tmux_injector.py)
   - Add `send_enter()` method using `tmux send-keys Enter`

### Layer 3: Session Manager

5. **RecordingSessionManager** (recording_session.py)
   - Add `auto_return: bool` property (mutable, not constructor arg)
   - After `inject_text()` succeeds, call `send_enter()` if enabled AND text is non-empty

### Layer 4: App Wiring + Toggle

6. **App** (app.py)
   - Initialize session_manager.auto_return from config
   - Add `toggle_auto_return()` method that flips the boolean
   - Expose current state for TUI to read

### Layer 5: UI Display + Toggle Action

7. **AppInfo** (models.py)
   - Add `auto_return: bool` field
   - Add `transcript_logging: str` field (path or "DISABLED")
   - Update `from_config()` to extract both values

8. **InfoPanel** (info_panel.py)
   - Reorganize into two sections:
     a. **Startup Configuration Box** (bordered, labeled):
        - Hotkey, Model, Mode, Target (existing)
        - Transcript Logging: /path or DISABLED (new)
     b. **Runtime Options** (outside box):
        - Auto-Return: ON/OFF (toggleable)
   - Add `update_auto_return(enabled: bool)` method for dynamic updates

9. **PushToTalkTUI** (tui_app.py)
   - Add binding: `Binding("a", "toggle_auto_return", "Auto-Return")`
   - Add `action_toggle_auto_return()` method:
     - Call app.toggle_auto_return()
     - Update InfoPanel display
     - Show notification confirming new state

### Layer 6: UI Styles

10. **styles.tcss** (ui/styles.tcss)
    - Add styling for startup configuration box border
    - Add styling for box label/title

## Key Integration Points

| Component | Receives From | Passes To |
|-----------|---------------|-----------|
| Config.injection.auto_return | YAML file | App (initial value) |
| App.toggle_auto_return() | TUI action | RecordingSessionManager.auto_return |
| RecordingSessionManager.auto_return | App | Injector.send_enter() (conditional) |
| TUI action_toggle_auto_return | User keypress | App + InfoPanel update |

## Runtime State Flow

```
User presses 'a'
    → TUI.action_toggle_auto_return()
        → App.toggle_auto_return() → flips session_manager.auto_return
        → InfoPanel.update_auto_return(new_value)
        → TUI.notify("Auto-Return: ON/OFF")
```

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Enter sent before text fully typed | Send enter only after inject_text() returns True |
| Empty transcription triggers Enter | Check for non-empty text before sending Enter |
| pynput Enter key not working | Use `Key.enter` constant, not string |
| tmux Enter not working | Use literal `Enter` argument to send-keys |
| Toggle during recording | Check is safe - auto_return read after injection |
| Thread safety on toggle | auto_return is simple bool, atomic read is sufficient |

## Testing Strategy

1. **Unit Tests**
   - Config loads auto_return correctly (true, false, missing/default)
   - FocusedInjector.send_enter() calls pynput correctly
   - TmuxInjector.send_enter() runs correct subprocess command
   - Toggle flips boolean state correctly

2. **Integration Tests**
   - With auto_return=true: verify Enter sent after injection
   - With auto_return=false: verify no Enter sent
   - With empty transcription: verify no Enter sent (regardless of setting)
   - Toggle mid-session: verify next transcription uses new setting

3. **Manual Testing**
   - Launch TUI, verify "Auto-Return: OFF" displayed
   - Press `a`, verify indicator changes to "ON" and notification appears
   - Press `a` again, verify indicator changes to "OFF"
   - Enable via toggle, speak command, verify Enter sent
   - Disable via toggle, speak command, verify no Enter sent
   - Restart app, verify reverts to config file setting
   - Test in both focused and tmux modes
   - Verify startup config is in bordered box with "Startup Configuration" label
   - Verify Auto-Return is outside the startup config box
   - With logging enabled: verify path displayed in startup config box
   - With logging disabled: verify "DISABLED" displayed in startup config box
