# Tasks: Auto-Return Configuration

**Input**: Design documents from `/specs/003-auto-return-config/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: Not explicitly requested - test tasks omitted. Manual testing steps included in Polish phase.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: No new project setup needed - existing project structure

- [ ] T001 Verify branch `003-auto-return-config` is checked out and clean

---

## Phase 2: Foundational (Configuration Layer)

**Purpose**: Add auto_return config option that ALL user stories depend on

**⚠️ CRITICAL**: User story implementation cannot begin until this phase is complete

- [ ] T002 Add `auto_return: bool = False` field to InjectionConfig dataclass in `src/push_to_talk_claude/utils/config.py`
- [ ] T003 Add `auto_return: false` with documentation comment to injection section in `config.default.yaml`

**Checkpoint**: Config infrastructure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Auto-Submit Voice Commands (Priority: P1) 🎯 MVP

**Goal**: When auto_return is enabled, automatically press Enter after transcribed text is injected

**Independent Test**: Enable auto_return in config, speak a command, verify text is typed AND Enter is pressed

### Implementation for User Story 1

- [ ] T004 [P] [US1] Add `send_enter()` method to FocusedInjector using `pynput.keyboard.Key.enter` in `src/push_to_talk_claude/core/focused_injector.py`
- [ ] T005 [P] [US1] Add `send_enter()` method to TmuxInjector using `tmux send-keys Enter` in `src/push_to_talk_claude/core/tmux_injector.py`
- [ ] T006 [US1] Add `auto_return: bool = False` property to RecordingSessionManager in `src/push_to_talk_claude/core/recording_session.py`
- [ ] T007 [US1] Modify `_transcribe_and_inject()` to call `send_enter()` after successful `inject_text()` when auto_return is True AND text is non-empty in `src/push_to_talk_claude/core/recording_session.py`
- [ ] T008 [US1] Initialize `session_manager.auto_return` from `config.injection.auto_return` in App._initialize_components() in `src/push_to_talk_claude/app.py`

**Checkpoint**: Auto-return behavior works when enabled via config file

---

## Phase 4: User Stories 3+4 - Toggle + Visual Indicator (Priority: P1/P2)

**Goal**: Display auto-return status and enable runtime toggle via 'a' key

**Independent Test**: Launch app, verify status visible; press 'a', verify indicator updates and behavior changes

**Note**: US4 (Indicator) implemented first as US3 (Toggle) depends on it for visual feedback

### Implementation for User Story 4 - Visual Indicator (FIRST - dependency)

- [ ] T009 [P] [US4] Add `auto_return: bool` field to AppInfo dataclass in `src/push_to_talk_claude/ui/models.py`
- [ ] T010 [US4] Update `AppInfo.from_config()` to extract `config.injection.auto_return` in `src/push_to_talk_claude/ui/models.py`
- [ ] T011 [US4] Add "Auto-Return: ON/OFF" Static widget to InfoPanel.compose() in `src/push_to_talk_claude/ui/widgets/info_panel.py`
- [ ] T012 [US4] Add `update_auto_return(enabled: bool)` method to InfoPanel for dynamic updates in `src/push_to_talk_claude/ui/widgets/info_panel.py`

### Implementation for User Story 3 - Runtime Toggle (SECOND - uses indicator)

- [ ] T013 [US3] Add `toggle_auto_return()` method to App class that flips `session_manager.auto_return` and returns new value in `src/push_to_talk_claude/app.py`
- [ ] T014 [US3] Store reference to App in TUI for toggle action in `src/push_to_talk_claude/ui/tui_app.py`
- [ ] T015 [US3] Add `Binding("a", "toggle_auto_return", "Auto-Return")` to BINDINGS list in PushToTalkTUI in `src/push_to_talk_claude/ui/tui_app.py`
- [ ] T016 [US3] Implement `action_toggle_auto_return()` method in PushToTalkTUI that calls app toggle, updates InfoPanel, and shows notification in `src/push_to_talk_claude/ui/tui_app.py`

**Checkpoint**: Auto-return status visible AND can toggle with 'a' key at runtime

---

## Phase 5: User Story 5 - Startup Configuration Box (Priority: P2)

**Goal**: Group startup config items in a labeled bordered box, show runtime options outside

**Independent Test**: Launch app, verify startup settings in labeled box, auto-return outside box

### Implementation for User Story 5

- [ ] T017 [US5] Reorganize InfoPanel.compose() to wrap startup config items (Hotkey, Model, Mode, Target) in a Container with border in `src/push_to_talk_claude/ui/widgets/info_panel.py`
- [ ] T018 [US5] Add "Startup Configuration" label/title to the bordered container in `src/push_to_talk_claude/ui/widgets/info_panel.py`
- [ ] T019 [US5] Move Auto-Return indicator outside the startup config box in `src/push_to_talk_claude/ui/widgets/info_panel.py`
- [ ] T020 [P] [US5] Add CSS styling for startup config box border and label in `src/push_to_talk_claude/ui/styles.tcss`

**Checkpoint**: Startup config in labeled box, runtime options outside

---

## Phase 6: User Story 6 - Transcript Logging Status Display (Priority: P3)

**Goal**: Show transcript logging path or DISABLED in startup config box

**Independent Test**: Launch with logging enabled/disabled, verify correct status displayed

### Implementation for User Story 6

- [ ] T021 [US6] Add `transcript_logging: str` field to AppInfo dataclass in `src/push_to_talk_claude/ui/models.py`
- [ ] T022 [US6] Update `AppInfo.from_config()` to set transcript_logging to path or "DISABLED" based on `config.logging.save_transcripts` in `src/push_to_talk_claude/ui/models.py`
- [ ] T023 [US6] Add "Transcript Logging: {path/DISABLED}" Static widget inside startup config box in `src/push_to_talk_claude/ui/widgets/info_panel.py`

**Checkpoint**: Transcript logging status visible in startup config box

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification and cleanup

- [ ] T024 Run `uv run claude-voice --help` to verify CLI still works
- [ ] T025 Manual test: Launch TUI, verify startup config box with label visible
- [ ] T026 Manual test: Verify "Auto-Return: OFF" displayed outside startup box
- [ ] T027 Manual test: Press 'a', verify indicator changes to "ON" and notification appears
- [ ] T028 Manual test: With auto_return ON, speak command, verify Enter is sent after text
- [ ] T029 Manual test: With auto_return OFF, speak command, verify NO Enter is sent
- [ ] T030 Manual test: Restart app, verify auto-return reverts to config file setting
- [ ] T031 Manual test: Enable logging in config, verify path displayed in startup box
- [ ] T032 Manual test: Disable logging in config, verify "DISABLED" displayed
- [ ] T033 Run quickstart.md validation - follow steps and verify all work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 - Core auto-return behavior
- **Phase 4 (US3+US4)**: Depends on Phase 2 - Toggle + Indicator (merged, US4 first then US3)
- **Phase 5 (US5)**: Depends on Phase 4 (builds on InfoPanel changes)
- **Phase 6 (US6)**: Depends on Phase 5 (adds to startup config box)
- **Phase 7 (Polish)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 2 (Foundational)
    │
    ├──► US1 (Auto-Submit) ─────────────────────────┐
    │                                               │
    └──► US4 (Indicator) ──► US3 (Toggle) ──────────┤
                                                    │
                        US5 (Box) ──► US6 (Logging) ┴──► Phase 7 (Polish)
```

### Parallel Opportunities

**After Phase 2 completes, these can run in parallel:**
- US1 tasks (T004-T008): Injector and session manager changes
- US4 tasks (T009-T012): Indicator display (then US3 T013-T016 sequentially)

**Within phases:**
- T004 and T005 can run in parallel (different injector files)
- T009 can run in parallel with T004-T005 (different files)
- T020 can run in parallel with T017-T019 (different file: styles.tcss)

---

## Parallel Example: Phase 3 + Phase 4

```bash
# After Phase 2 (Foundational) completes, launch these in parallel:

# Developer A: US1 - Auto-Submit Behavior
Task: T004 - Add send_enter() to FocusedInjector
Task: T005 - Add send_enter() to TmuxInjector
Task: T006 - Add auto_return property to RecordingSessionManager
Task: T007 - Modify _transcribe_and_inject()
Task: T008 - Wire in App._initialize_components()

# Developer B: US4 + US3 - Indicator (first) + Toggle (second)
Task: T009 - Add auto_return field to AppInfo
Task: T010 - Update from_config()
Task: T011 - Add Static widget to InfoPanel
Task: T012 - Add update_auto_return() method
# Then sequentially:
Task: T013-T016 - Toggle functionality (depends on T012)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T003)
3. Complete Phase 3: User Story 1 (T004-T008)
4. **STOP and VALIDATE**: Test auto-return with config file
5. Can ship MVP with just config-based auto-return!

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 → Auto-return via config works
2. **+Toggle**: Add US4 + US3 (Phase 4) → Can toggle at runtime with feedback
3. **+UI Polish**: Add US5 + US6 → Nice visual organization
4. **Complete**: Polish phase → Fully tested and validated

### Single Developer Order

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → (MVP CHECKPOINT) → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024-T033

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- No test tasks generated (tests not explicitly requested)
- Manual testing checklist in Phase 8 covers all acceptance scenarios
- Each user story checkpoint allows validation before proceeding
- MVP achievable after just Phase 3 (13 tasks total including setup)
