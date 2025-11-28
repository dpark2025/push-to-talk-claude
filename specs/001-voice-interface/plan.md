# Implementation Plan: Push-to-Talk Voice Interface

**Branch**: `001-voice-interface` | **Date**: 2025-11-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-voice-interface/spec.md`

## Summary

Build a push-to-talk voice interface for Claude Code on macOS that enables hands-free voice input via configurable hotkey, local Whisper transcription, tmux-based text injection, and selective TTS for Claude's conversational responses. Privacy-first architecture with all speech processing running locally by default.

## Technical Context

**Language/Version**: Python 3.9+ (targeting 3.11 for performance)
**Primary Dependencies**: pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say)
**Storage**: YAML config files (~/.claude-voice/config.yaml), temporary WAV files (deleted after transcription)
**Testing**: pytest with pytest-asyncio, >80% coverage target
**Target Platform**: macOS 11.0+ (Big Sur and later), Apple Silicon and Intel
**Project Type**: Single CLI application
**Performance Goals**: <3s voice-to-text (p95), <100ms hotkey detection, <500ms response detection
**Constraints**: <500MB memory (with Whisper tiny model loaded), 100% local processing by default
**Scale/Scope**: Single-user CLI tool, ~2000 LOC estimated

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Privacy is Non-Negotiable | ✅ PASS | Whisper runs locally, macOS `say` for TTS, no external APIs |
| II. Speed Matters | ✅ PASS | Whisper tiny/base model, <3s target, pre-loaded models |
| III. Smart Filtering | ✅ PASS | Response parser filters code blocks, command output, >500 char |
| IV. Reliability Over Features | ✅ PASS | 80%+ test coverage, fail-fast permission handling |
| V. Terminal Agnostic | ✅ PASS | tmux send-keys for injection, works across all terminals |
| VI. Smart Defaults | ✅ PASS | Works with single command, YAML config for customization |
| VII. Secure by Default | ✅ PASS | Input sanitization, shell metachar escaping, 500 char limit |
| VIII. Ship Small | ✅ PASS | Phased delivery: PTT → TTS → Polish → Advanced |

**Gate Status**: PASSED - No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-voice-interface/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal interfaces)
│   └── interfaces.md    # Python interface contracts
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── push_to_talk_claude/
    ├── __init__.py
    ├── __main__.py           # Entry point (uv run claude-voice)
    ├── app.py                # Main application orchestrator
    │
    ├── core/                 # Core functionality modules
    │   ├── __init__.py
    │   ├── keyboard_monitor.py   # PTT hotkey detection (pynput)
    │   ├── audio_capture.py      # Microphone recording (PyAudio)
    │   ├── speech_to_text.py     # Whisper transcription
    │   ├── text_to_speech.py     # macOS say command wrapper
    │   └── tmux_injector.py      # tmux send-keys injection
    │
    ├── hooks/                # Claude Code integration
    │   ├── __init__.py
    │   ├── hook_handler.py       # Process Claude Code hooks
    │   └── response_parser.py    # Filter conversational vs code
    │
    ├── utils/                # Shared utilities
    │   ├── __init__.py
    │   ├── config.py             # YAML config loading/validation
    │   ├── sanitizer.py          # Input sanitization
    │   ├── session_detector.py   # Tmux session discovery
    │   └── permissions.py        # macOS permission checking
    │
    └── ui/                   # User feedback
        ├── __init__.py
        ├── indicators.py         # Recording status display
        └── notifications.py      # Error notifications

tests/
├── __init__.py
├── conftest.py               # pytest fixtures
├── unit/                     # Unit tests
│   ├── test_keyboard_monitor.py
│   ├── test_audio_capture.py
│   ├── test_speech_to_text.py
│   ├── test_tmux_injector.py
│   ├── test_response_parser.py
│   ├── test_sanitizer.py
│   └── test_config.py
├── integration/              # Integration tests
│   ├── test_voice_to_text_flow.py
│   └── test_hook_to_tts_flow.py
└── contract/                 # Contract tests
    └── test_interfaces.py

scripts/
├── install.sh                # One-command install
├── install-brew-deps.sh      # Homebrew dependencies
└── check-permissions.sh      # Permission verification

hooks/
└── claude-response-hook.sh   # Claude Code hook script
```

**Structure Decision**: Single project structure selected. This is a CLI tool without web/mobile components. The modular structure under `src/push_to_talk_claude/` enables independent testing of each component while maintaining a clean namespace.

## Complexity Tracking

> No constitution violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |
