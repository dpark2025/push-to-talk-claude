# Implementation Plan: Textual TUI for Push-to-Talk Interface

**Branch**: `002-textual-tui` | **Date**: 2025-11-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-textual-tui/spec.md`

## Summary

Replace the current Rich-based panel printing UI with a Textual TUI framework. The new interface features a two-panel layout: a main info panel (~2/3 width) showing app configuration on the left, and a status panel (~1/3 width) on the right with vertically stacked pill-shaped status indicators that illuminate when active. A log modal accessible via "L" key shows the last 100 console log lines.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.11 for performance)
**Primary Dependencies**: Textual (TUI framework), pynput (keyboard), PyAudio (audio), openai-whisper (STT)
**Storage**: In-memory log buffer (100 lines max), existing config.yaml for settings
**Testing**: pytest with pytest-asyncio for async TUI testing
**Target Platform**: macOS 11.0+ (primary), Linux/Windows (secondary via Textual compatibility)
**Project Type**: Single project (existing structure)
**Performance Goals**: Status updates <50ms, timer updates 10Hz, startup overhead <500ms
**Constraints**: Must preserve existing hotkey functionality, must work with existing core components
**Scale/Scope**: Single-user CLI application, ~20 source files affected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy Non-Negotiable | ✅ PASS | No external services added. Textual runs locally. |
| II. Speed Matters | ✅ PASS | Target <50ms status updates, 10Hz timer - within requirements |
| III. Smart Filtering | ✅ PASS | UI changes only, filtering logic unchanged |
| IV. Reliability Over Features | ✅ PASS | Core PTT loop preserved, TUI is presentation layer only |
| V. Terminal Agnostic, macOS Native | ✅ PASS | Textual supports multiple terminals (iTerm2, Terminal.app, Kitty, Alacritty) |
| VI. Smart Defaults, Deep Customization | ✅ PASS | Works with existing config.yaml, "L" key for logs is sensible default |
| VII. Secure by Default | ✅ PASS | No new input vectors, existing sanitization preserved |
| VIII. Ship Small, Ship Often | ✅ PASS | UI layer can be shipped incrementally |

**Gate Result**: PASS - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/002-textual-tui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal component contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/push_to_talk_claude/
├── __init__.py
├── __main__.py
├── app.py                    # Main orchestrator (MODIFY: integrate TUI)
├── core/
│   ├── audio_capture.py
│   ├── focused_injector.py
│   ├── keyboard_monitor.py
│   ├── recording_session.py
│   ├── speech_to_text.py
│   ├── text_to_speech.py
│   └── tmux_injector.py
├── hooks/
│   ├── hook_handler.py
│   └── response_parser.py
├── ui/                       # Primary modification area
│   ├── __init__.py
│   ├── audio_feedback.py
│   ├── indicators.py         # REPLACE: with Textual widgets
│   ├── notifications.py      # REPLACE: with Textual integration
│   ├── tui_app.py            # NEW: Main Textual application
│   ├── widgets/              # NEW: Custom Textual widgets
│   │   ├── __init__.py
│   │   ├── info_panel.py     # NEW: Left panel with app info
│   │   ├── status_panel.py   # NEW: Right panel with status pills
│   │   ├── status_pill.py    # NEW: Individual status indicator
│   │   └── log_modal.py      # NEW: Log viewer modal
│   └── styles.tcss           # NEW: Textual CSS styling
└── utils/
    ├── config.py
    ├── permissions.py
    ├── sanitizer.py
    └── session_detector.py

tests/
├── unit/
│   └── ui/
│       ├── test_tui_app.py       # NEW
│       ├── test_status_panel.py  # NEW
│       └── test_log_modal.py     # NEW
└── integration/
    └── test_tui_integration.py   # NEW
```

**Structure Decision**: Extend existing single-project structure. Add `ui/widgets/` subdirectory for Textual custom widgets. Add `ui/styles.css` for Textual CSS styling.

## Complexity Tracking

> No constitution violations to justify.

N/A - All gates passed without violations.
