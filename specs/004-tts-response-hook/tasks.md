# Tasks: TTS Response Hook

**Input**: Design documents from `/specs/004-tts-response-hook/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL for this feature. Unit tests included for summarizer only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for hook components

- [ ] T001 Create hooks package directory at src/push_to_talk_claude/hooks/__init__.py
- [ ] T002 [P] Create tests/hooks directory for hook-specific tests
- [ ] T003 [P] Create docs directory if not exists for user documentation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement Summarizer class in src/push_to_talk_claude/hooks/summarizer.py with sentence classification logic
- [ ] T005 Implement CLI interface for summarizer in src/push_to_talk_claude/hooks/summarizer.py (__main__ block)
- [ ] T006 Create unit tests for summarizer in tests/hooks/test_summarizer.py
- [ ] T006a Implement code block stripping utility in response processing module (src/push_to_talk_claude/hooks/summarizer.py or response_parser.py)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Hear Short Responses (Priority: P1) 🎯 MVP

**Goal**: Enable audio feedback for Claude's short responses (< 50 words) spoken verbatim

**Independent Test**: Ask Claude a yes/no question and verify response is spoken aloud within 2 seconds

### Implementation for User Story 1

- [ ] T007 [US1] Create stop_hook.sh script skeleton in src/push_to_talk_claude/hooks/stop_hook.sh with shebang and basic structure
- [ ] T008 [US1] Implement flag file check logic in stop_hook.sh for ~/.claude-voice/tts-hook-enabled
- [ ] T009 [US1] Implement dependency checks (jq, say, python3) in stop_hook.sh with error logging
- [ ] T010 [US1] Implement transcript file parsing with jq in stop_hook.sh to extract last assistant message
- [ ] T010a [US1] Integrate hook script invocation with existing hook infrastructure if applicable (check if hook_handler.py should be used or if bash script is standalone)
- [ ] T011 [US1] Implement code block removal logic in stop_hook.sh using sed
- [ ] T012 [US1] Implement word count check in stop_hook.sh to determine short vs long response
- [ ] T013 [US1] Implement TTS config reading from ~/.claude-voice/config.yaml in stop_hook.sh (voice and rate)
- [ ] T014 [US1] Implement say command invocation for short responses in stop_hook.sh (async with &)
- [ ] T015 [US1] Add debug logging to stop_hook.sh with DEBUG environment variable support
- [ ] T016 [US1] Make stop_hook.sh executable with chmod +x

**Checkpoint**: At this point, User Story 1 should be fully functional - short responses are spoken aloud

---

## Phase 4: User Story 2 - Hear Summarized Long Responses (Priority: P1)

**Goal**: Enable audio feedback for Claude's long responses (≥ 50 words) with heuristic summarization to 2-4 sentences

**Independent Test**: Ask Claude to implement a feature and verify a summary of the work is spoken within 5 seconds

### Implementation for User Story 2

- [ ] T017 [US2] Integrate summarizer CLI call in stop_hook.sh for long responses (> 50 words)
- [ ] T018 [US2] Implement summary TTS invocation in stop_hook.sh with say command
- [ ] T019 [US2] Add error handling for summarizer failures in stop_hook.sh with fallback to truncation
- [ ] T020 [US2] Test end-to-end flow with sample long response transcript

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - short responses spoken verbatim, long responses summarized and spoken

---

## Phase 5: User Story 3 - Toggle TTS Hook at Runtime (Priority: P2)

**Goal**: Enable users to toggle TTS hook on/off from TUI without restarting

**Independent Test**: Toggle setting in TUI and verify subsequent responses are/aren't spoken

### Implementation for User Story 3

- [ ] T021 [US3] Add toggle keybinding to BINDINGS list in src/push_to_talk_claude/ui/tui_app.py (key: 't')
- [ ] T022 [US3] Implement action_toggle_tts_hook method in src/push_to_talk_claude/ui/tui_app.py
- [ ] T023 [US3] Implement _check_tts_hook_enabled method in src/push_to_talk_claude/ui/tui_app.py
- [ ] T024 [US3] Add _tts_hook_enabled state variable initialization in src/push_to_talk_claude/ui/tui_app.py __init__
- [ ] T025 [US3] Implement flag file create/delete logic in action_toggle_tts_hook
- [ ] T026 [US3] Add notification display for toggle operations in action_toggle_tts_hook
- [ ] T027 [US3] Add logging for toggle state changes in action_toggle_tts_hook
- [ ] T028 [US3] Test toggle functionality manually in TUI

**Checkpoint**: Toggle functionality complete - users can enable/disable hook from TUI

---

## Phase 6: User Story 4 - Setup Documentation (Priority: P2)

**Goal**: Provide clear documentation for manual Claude Code hook configuration

**Independent Test**: New user follows documentation and successfully configures hook

### Implementation for User Story 4

- [ ] T029 [US4] Create docs/claude-code-hook-setup.md with overview section
- [ ] T030 [US4] Document prerequisites in claude-code-hook-setup.md (Claude Code, jq, push-to-talk-claude)
- [ ] T031 [US4] Document Claude Code settings.json configuration steps in claude-code-hook-setup.md
- [ ] T032 [US4] Document hook installation verification steps in claude-code-hook-setup.md
- [ ] T033 [US4] Document TUI toggle usage in claude-code-hook-setup.md
- [ ] T034 [US4] Document testing steps in claude-code-hook-setup.md
- [ ] T035 [US4] Add troubleshooting section to claude-code-hook-setup.md (common errors, solutions)
- [ ] T036 [US4] Add brittle integration warning to claude-code-hook-setup.md (may break with updates)
- [ ] T036a [US4] Add brittle integration warning to TUI startup message and main README.md (this is a fragile integration)
- [ ] T037 [US4] Document debug logging enablement in claude-code-hook-setup.md (DEBUG=1)

**Checkpoint**: Documentation complete - users have clear setup guide

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, validation, and documentation

- [ ] T038 [P] Add hook installation instructions to main README.md
- [ ] T039 [P] Create integration test script in tests/hooks/test_stop_hook_integration.sh
- [ ] T040 Run all integration tests with various transcript scenarios (short, long, empty, malformed)
- [ ] T041 Validate performance targets (SC-001: <2s short, SC-002: <5s long, SC-003: <500ms toggle)
- [ ] T042 Create symlink setup for hook script at ~/.claude-voice/hooks/stop_hook.sh
- [ ] T043 Run quickstart.md validation with manual testing
- [ ] T044 [P] Update project documentation with TTS hook feature overview

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in sequence (P1 → P2)
  - US1 and US2 are both P1, but US2 depends on US1 (hook script foundation)
  - US3 and US4 are P2 and can proceed in parallel after US1+US2
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 - Extends hook script with summarization
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent TUI component
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent documentation

### Within Each User Story

**User Story 1 (Hook Script - Short Responses)**:
- T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 (sequential)

**User Story 2 (Hook Script - Long Responses)**:
- T017 → T018 → T019 → T020 (sequential, depends on US1 completion)

**User Story 3 (TUI Toggle)**:
- T021 → T022 → T023 → T024 → T025 → T026 → T027 → T028 (sequential)

**User Story 4 (Documentation)**:
- T029 → T030, T031, T032, T033, T034, T035, T036, T037 (T029 first, rest can be parallel)

### Parallel Opportunities

- Phase 1 Setup: T001, T002, T003 can run in parallel (different directories)
- Phase 2 Foundational: T004, T005, T006 are sequential (same file, dependencies)
- After US1+US2 complete: US3 and US4 can proceed in parallel (different files)
- Phase 7 Polish: T038, T039, T044 can run in parallel (different files)

---

## Parallel Example: After Foundational Phase

```bash
# After Phase 2 completes, start User Story 1:
Task T007: Create stop_hook.sh script skeleton
Task T008: Implement flag file check logic
# ... continue US1 sequentially

# After US1 and US2 complete, parallel execution possible:
Task T021: Add toggle keybinding (US3 - TUI component)
Task T029: Create documentation (US4 - Docs)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (short responses)
4. Complete Phase 4: User Story 2 (long responses with summarization)
5. **STOP and VALIDATE**: Test both short and long responses end-to-end
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Basic TTS works for short responses
3. Add User Story 2 → Test independently → TTS works for all responses (MVP!)
4. Add User Story 3 → Test independently → Runtime toggle available
5. Add User Story 4 → Test independently → Documentation complete
6. Polish phase → Production ready

### Sequential Single-Developer Strategy

Given the dependencies and single-file conflicts:

1. Complete Phases 1-2: Setup + Foundational (summarizer)
2. Complete Phases 3-4: User Stories 1+2 sequentially (both modify stop_hook.sh)
3. Complete Phases 5-6: User Stories 3+4 in either order or parallel (different files)
4. Complete Phase 7: Polish and validation

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Stop hook script (US1, US2) must be developed sequentially (same file)
- TUI toggle (US3) and documentation (US4) are independent, can be parallel
- Tests are minimal (unit tests for summarizer only, integration tests manual)
- Hook script errors must always exit 0 (never disrupt Claude Code)
- Verify performance targets at Polish phase (SC-001, SC-002, SC-003)
- Manual Claude Code configuration required (documented in US4)
