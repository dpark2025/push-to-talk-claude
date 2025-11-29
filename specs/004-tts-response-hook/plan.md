# Implementation Plan: TTS Response Hook

**Branch**: `004-tts-response-hook` | **Date**: 2025-11-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-tts-response-hook/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a Claude Code Stop hook that provides audio feedback for Claude's responses by speaking them aloud using macOS `say` command. Short responses (under 50 words) are spoken verbatim, while longer responses are summarized to 2-4 sentences before speaking. The hook is enabled/disabled via a runtime toggle accessible from the TUI. This is a brittle integration requiring manual user configuration in Claude Code settings.

## Technical Context

**Language/Version**: Python 3.11 (existing project standard)
**Primary Dependencies**:
- Existing: Textual (TUI), macOS `say` command (TTS), PyYAML (config)
- New: jq (JSONL parsing in hook script), bash (hook script interpreter)

**Storage**:
- Flag file: `~/.claude-voice/tts-hook-enabled` (presence indicates enabled)
- Transcript file: Provided by Claude Code hook as JSONL file path
- Config: Existing `~/.claude-voice/config.yaml` for TTS settings

**Testing**: pytest (existing), manual testing with Claude Code required

**Target Platform**: macOS 11.0+ (existing project constraint)

**Project Type**: Single Python project with bash hook script

**Performance Goals**:
- Short response TTS: < 2 seconds from Claude finish to audio start
- Long response TTS: < 5 seconds from Claude finish to audio start
- Toggle operation: < 500ms with visual confirmation

**Constraints**:
- Hook processing must not block Claude Code
- Must handle malformed/missing transcript files gracefully
- Summarization must be heuristic-based (no LLM calls) to avoid latency
- Hook script must be standalone executable (bash + jq + Python)

**Scale/Scope**:
- Single hook script (~100-150 lines bash)
- Enhanced response parser (~50 lines Python for summarization)
- TUI toggle keybinding (minimal addition)
- Documentation (~200 lines markdown)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Privacy (Principle I) ✅ PASS
- **Gate**: No audio data sent to external servers
- **Status**: Uses local macOS `say` command only. No external API calls.
- **Evidence**: Spec FR-004, FR-005 specify macOS `say` command. Out of scope excludes LLM-based summarization.

### Speed (Principle II) ✅ PASS
- **Gate**: Hook processing < 1s
- **Status**: Target < 2s for short responses, < 5s for long responses (includes summarization)
- **Evidence**: Performance targets in spec SC-001, SC-002. Heuristic summarization avoids LLM latency.

### Reliability (Principle IV) ✅ PASS
- **Gate**: Core PTT loop unaffected, graceful degradation
- **Status**: Hook is decoupled, errors logged but don't crash main app. Flag file enables/disables.
- **Evidence**: Spec FR-010 (graceful error handling), FR-006 (toggle flag), edge cases documented.

### Smart Defaults (Principle VI) ⚠️ REVIEW
- **Gate**: Works with defaults, customizable
- **Status**: Requires manual Claude Code hook configuration (brittle integration)
- **Evidence**: Spec FR-008, FR-009 acknowledge this limitation. User Story 4 (P2) covers documentation.
- **Justification**: Claude Code doesn't support automatic hook registration. This is unavoidable external dependency.

### Security (Principle VII) ✅ PASS
- **Gate**: Input sanitization, no eval
- **Status**: Hook reads JSONL transcript safely, extracts text without code execution
- **Evidence**: Spec FR-011 (strip code blocks), existing ResponseParser sanitizes text.

### Ship Small (Principle VIII) ✅ PASS
- **Gate**: Incremental delivery
- **Status**: Single focused feature building on existing TTS and response parsing infrastructure
- **Evidence**: Reuses existing TextToSpeech and ResponseParser. Minimal new code (hook script + toggle).

**Overall Assessment**: ✅ PASSES with justified exception for manual configuration requirement

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/push_to_talk_claude/
├── hooks/
│   ├── __init__.py
│   ├── hook_handler.py         # Existing - orchestrates TTS from hook events
│   ├── response_parser.py      # Existing - extract speakable text
│   ├── summarizer.py           # NEW - heuristic summarization for long responses
│   └── stop_hook.sh            # NEW - bash script registered with Claude Code
├── core/
│   └── text_to_speech.py       # Existing - macOS say wrapper
├── ui/
│   └── tui_app.py              # Existing - add toggle keybinding
└── utils/
    └── config.py               # Existing - TTS config already present

tests/
├── hooks/
│   ├── test_summarizer.py      # NEW - test summarization logic
│   └── test_stop_hook.sh       # NEW - integration test for hook script
└── integration/
    └── test_hook_integration.py # NEW - end-to-end hook → TTS flow

docs/
└── claude-code-hook-setup.md   # NEW - user documentation for manual setup
```

**Structure Decision**: Single Python project with existing structure. New components:
1. **stop_hook.sh**: Standalone bash script that reads transcript JSONL, checks flag file, extracts response, calls Python summarizer if needed, invokes `say` command
2. **summarizer.py**: Python module for heuristic summarization (extractable for use by hook script via CLI)
3. **TUI toggle**: Keybinding in existing tui_app.py to create/remove flag file
4. **Documentation**: Markdown guide for manual Claude Code hook configuration

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Manual Claude Code hook configuration | Claude Code requires explicit hook registration in settings file | Automatic registration not supported by Claude Code API. User must edit `~/.claude/settings.json` manually per Claude Code documentation. |
| Bash hook script reads config.yaml directly | Hook runs outside Python runtime (Claude Code invokes bash scripts, not Python modules) | Cannot import Python config modules in bash context. Hook must parse YAML with yq/grep or hardcode paths. Chose direct YAML parsing for flexibility. |
