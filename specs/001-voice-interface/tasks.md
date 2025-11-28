# Tasks: Push-to-Talk Voice Interface

**Input**: Design documents from `/specs/001-voice-interface/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - not explicitly requested in feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/push_to_talk_claude/`, `tests/` at repository root
- Paths based on plan.md structure

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure per plan.md in src/push_to_talk_claude/
- [ ] T002 Initialize Python project with pyproject.toml (Python 3.9+, uv build system)
- [ ] T003 [P] Add core dependencies to pyproject.toml: pynput, PyAudio, openai-whisper, PyYAML, rich
- [ ] T004 [P] Create .python-version file specifying Python 3.11
- [ ] T005 [P] Configure ruff and black in pyproject.toml (line-length: 100)
- [ ] T006 Create src/push_to_talk_claude/__init__.py with version info
- [ ] T007 Create empty __init__.py files in core/, hooks/, utils/, ui/ subdirectories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Implement Config dataclass and YAML loading in src/push_to_talk_claude/utils/config.py
- [ ] T009 [P] Implement InputSanitizer with shell metachar escaping in src/push_to_talk_claude/utils/sanitizer.py
- [ ] T010 [P] Implement permission checking utilities in src/push_to_talk_claude/utils/permissions.py
- [ ] T011 [P] Create SUPPORTED_HOTKEYS constant mapping in src/push_to_talk_claude/core/keyboard_monitor.py
- [ ] T012 Create default config.yaml template in config.default.yaml at repo root

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Voice Input to Claude Code (Priority: P1)

**Goal**: Enable hands-free voice input to Claude Code via push-to-talk hotkey

**Independent Test**: Press hotkey, speak "hello world", release key, verify text appears in Claude Code input area within 3 seconds

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement KeyboardMonitor class with pynput listener in src/push_to_talk_claude/core/keyboard_monitor.py
- [ ] T014 [P] [US1] Implement AudioCapture class with PyAudio in src/push_to_talk_claude/core/audio_capture.py
- [ ] T015 [P] [US1] Implement SpeechToText class with Whisper in src/push_to_talk_claude/core/speech_to_text.py
- [ ] T016 [P] [US1] Implement TmuxInjector class with send-keys in src/push_to_talk_claude/core/tmux_injector.py
- [ ] T017 [P] [US1] Implement SessionDetector for Claude pane discovery in src/push_to_talk_claude/utils/session_detector.py
- [ ] T018 [US1] Implement RecordingSession state machine in src/push_to_talk_claude/core/recording_session.py
- [ ] T019 [US1] Implement main App orchestrator connecting all components in src/push_to_talk_claude/app.py
- [ ] T020 [US1] Create CLI entry point in src/push_to_talk_claude/__main__.py
- [ ] T021 [US1] Add visual recording indicator in src/push_to_talk_claude/ui/indicators.py
- [ ] T022 [US1] Add error notifications in src/push_to_talk_claude/ui/notifications.py
- [ ] T023 [US1] Implement 5-second timeout handling in transcription flow
- [ ] T024 [US1] Implement 60-second max recording limit with auto-stop

**Checkpoint**: User Story 1 (MVP) should be fully functional - voice input to Claude Code works

---

## Phase 4: User Story 2 - Hearing Claude's Responses (Priority: P2)

**Goal**: Speak Claude's conversational responses aloud, filtering out code and command output

**Independent Test**: Ask Claude a question, verify conversational response is spoken while code blocks are silent

### Implementation for User Story 2

- [ ] T025 [P] [US2] Implement ResponseParser with classification logic in src/push_to_talk_claude/hooks/response_parser.py
- [ ] T026 [P] [US2] Implement TextToSpeech class with macOS say in src/push_to_talk_claude/core/text_to_speech.py
- [ ] T027 [US2] Implement HookHandler for Claude Code events in src/push_to_talk_claude/hooks/hook_handler.py
- [ ] T028 [US2] Create Claude Code hook script in hooks/claude-response-hook.sh
- [ ] T029 [US2] Add hook installation instructions to setup flow
- [ ] T030 [US2] Implement TTS interruption (stop current speech on new input)
- [ ] T031 [US2] Add max_length truncation for long responses (default 500 chars)

**Checkpoint**: User Stories 1 AND 2 should both work - full voice interaction loop

---

## Phase 5: User Story 3 - Customizing the Voice Experience (Priority: P3)

**Goal**: Allow configuration of hotkey, TTS voice, and speaking rate

**Independent Test**: Change hotkey from right-Ctrl to F13 in config, verify new key works

### Implementation for User Story 3

- [ ] T032 [US3] Add hotkey validation and runtime change support in src/push_to_talk_claude/core/keyboard_monitor.py
- [ ] T033 [US3] Add TTS voice selection (list_voices) in src/push_to_talk_claude/core/text_to_speech.py
- [ ] T034 [US3] Add TTS rate configuration (100-400 WPM) in src/push_to_talk_claude/core/text_to_speech.py
- [ ] T035 [US3] Add TTS enable/disable toggle in App orchestrator
- [ ] T036 [US3] Add config validation with helpful error messages in src/push_to_talk_claude/utils/config.py
- [ ] T037 [US3] Document all configuration options in config.default.yaml with comments

**Checkpoint**: All configuration options work - users can customize experience

---

## Phase 6: User Story 4 - Quick Setup Experience (Priority: P4)

**Goal**: Enable 5-minute setup from clone to first voice input

**Independent Test**: Time fresh installation on clean Mac - should complete in under 5 minutes

### Implementation for User Story 4

- [ ] T038 [P] [US4] Create install.sh master script in scripts/install.sh
- [ ] T039 [P] [US4] Create install-brew-deps.sh for Homebrew dependencies in scripts/install-brew-deps.sh
- [ ] T040 [P] [US4] Create check-permissions.sh for permission verification in scripts/check-permissions.sh
- [ ] T041 [US4] Implement --check flag for dependency/permission verification in CLI
- [ ] T042 [US4] Add startup permission checks with actionable error messages
- [ ] T043 [US4] Create README.md with 5-minute quickstart section
- [ ] T044 [US4] Add pyproject.toml entry points: claude-voice, claude-voice-setup

**Checkpoint**: New users can install and use voice input within 5 minutes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T045 [P] Add audio feedback (beep) on recording start/stop
- [ ] T046 [P] Add --debug flag for verbose logging
- [ ] T047 [P] Create docs/configuration.md with full config reference
- [ ] T048 [P] Create docs/troubleshooting.md with common issues
- [ ] T049 Add graceful shutdown handling (Ctrl+C)
- [ ] T050 Add config file auto-creation on first run (~/.claude-voice/config.yaml)
- [ ] T051 Run quickstart.md validation (verify 5-minute setup works)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 can start immediately after Foundational
  - US2 depends on US1 completion (needs voice input to test)
  - US3 can start after Foundational (independent of US1/US2)
  - US4 can start after US1 (needs working feature to document)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 for testing (need to send input to get responses)
- **User Story 3 (P3)**: Can start after Foundational - Independent (config doesn't need voice working)
- **User Story 4 (P4)**: Depends on US1 - Documentation needs working feature

### Within Each User Story

- Models/utilities before services
- Services before orchestration
- Core implementation before UI
- Commit after each task or logical group

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- T013-T017 (US1 core modules) can all run in parallel
- T025-T026 (US2 parser and TTS) can run in parallel
- T038-T040 (US4 scripts) can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all core modules in parallel:
Task T013: "Implement KeyboardMonitor class with pynput listener"
Task T014: "Implement AudioCapture class with PyAudio"
Task T015: "Implement SpeechToText class with Whisper"
Task T016: "Implement TmuxInjector class with send-keys"
Task T017: "Implement SessionDetector for Claude pane discovery"

# Then sequentially:
Task T018: "Implement RecordingSession state machine" (depends on T013-T017)
Task T019: "Implement main App orchestrator" (depends on T018)
Task T020: "Create CLI entry point" (depends on T019)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test voice input independently
5. Deploy/demo if ready - this is the MVP!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (full voice loop)
4. Add User Story 3 → Test independently → Deploy/Demo (customizable)
5. Add User Story 4 → Test independently → Deploy/Demo (easy onboarding)
6. Each story adds value without breaking previous stories

---

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| Setup | 7 | 3 | Project initialization |
| Foundational | 5 | 3 | Shared infrastructure |
| US1 (P1) | 12 | 5 | Voice Input - MVP |
| US2 (P2) | 7 | 2 | TTS Responses |
| US3 (P3) | 6 | 0 | Configuration |
| US4 (P4) | 7 | 3 | Quick Setup |
| Polish | 7 | 4 | Cross-cutting |
| **Total** | **51** | **20** | |

**MVP Scope**: Phases 1-3 (24 tasks) delivers working voice input
**Full Feature**: All phases (51 tasks) delivers complete voice interface

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included (not explicitly requested) - add if TDD approach desired
