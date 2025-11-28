# Feature Specification: Textual TUI for Push-to-Talk Interface

**Feature Branch**: `002-textual-tui`
**Created**: 2025-11-28
**Status**: Draft
**Input**: User description: "Replace Rich-based panel printing with Textual TUI framework for push-to-talk voice interface. Build a proper terminal UI with persistent status bar showing recording state, live recording timer with duration display, scrolling transcript history, proper emoji/unicode character width handling, and real-time updating displays without reprinting panels."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Recording Status in Real-Time (Priority: P1)

As a user recording voice input, I want to see a persistent status indicator that updates in real-time so I can always know the current state of my recording without the screen scrolling or reprinting.

**Why this priority**: Core functionality - users need immediate visual feedback during recording to know when to speak and when recording has stopped. Without this, users cannot effectively use the push-to-talk feature.

**Independent Test**: Can be fully tested by pressing the hotkey and observing that the status bar updates instantly from "Idle" to "Recording" to "Transcribing" to "Complete" without any screen flicker or panel reprinting.

**Acceptance Scenarios**:

1. **Given** the application is running and idle, **When** I press the hotkey, **Then** the status bar immediately shows "Recording" state with a visual indicator
2. **Given** I am recording, **When** I release the hotkey, **Then** the status bar transitions to "Transcribing" state
3. **Given** transcription completes, **When** text is injected, **Then** the status bar shows "Complete" briefly before returning to "Idle"
4. **Given** any state, **When** an error occurs, **Then** the status bar shows "Error" with a brief description

---

### User Story 2 - See Live Recording Duration (Priority: P2)

As a user recording voice input, I want to see a live timer showing how long I've been recording so I can manage my message length and know I'm not approaching the timeout limit.

**Why this priority**: Important for user awareness but not blocking - users can still record without knowing exact duration. Helps prevent timeout surprises and builds user confidence.

**Independent Test**: Can be fully tested by pressing the hotkey and observing the timer counting up in real-time (updating every 100ms or faster) during recording.

**Acceptance Scenarios**:

1. **Given** I start recording, **When** the recording begins, **Then** a timer starts at 0:00 and increments in real-time
2. **Given** I am recording, **When** 5 seconds pass, **Then** the timer shows approximately "0:05"
3. **Given** I am recording, **When** I approach the max duration (60s), **Then** the timer provides visual warning (color change or animation)
4. **Given** I release the hotkey, **When** recording stops, **Then** the timer freezes at the final duration

---

### User Story 3 - View Transcript History (Priority: P2)

As a user who has made multiple voice inputs, I want to see a scrollable history of my recent transcriptions so I can review what I've said and verify the transcriptions were accurate.

**Why this priority**: Valuable for verification and debugging transcription issues. Users can see patterns in transcription errors and confirm their input was captured correctly.

**Independent Test**: Can be fully tested by making 3-4 voice recordings and observing that all transcriptions appear in a scrollable list, with the most recent at the bottom.

**Acceptance Scenarios**:

1. **Given** I complete a transcription, **When** text is successfully processed, **Then** the transcribed text appears in the history panel
2. **Given** I have multiple transcriptions, **When** viewing the history, **Then** I can scroll through past entries
3. **Given** a recording is skipped, **When** the reason is determined, **Then** a "Skipped: [reason]" entry appears in history
4. **Given** an error occurs, **When** the error is logged, **Then** an error entry appears in history with the message

---

### User Story 4 - Correct Display of Emojis and Unicode (Priority: P3)

As a user viewing the interface, I want all emojis and unicode characters to display correctly with proper alignment so the interface looks polished and professional.

**Why this priority**: Visual polish - the current Rich-based implementation has character width calculation issues with certain emojis. This is the core problem that prompted this feature.

**Independent Test**: Can be fully tested by observing that all status indicators (recording, transcribing, complete, error, skipped) display with proper alignment and no border misalignment.

**Acceptance Scenarios**:

1. **Given** any status state, **When** displayed with emoji indicators, **Then** the panel borders align correctly
2. **Given** transcribed text contains emojis, **When** displayed in history, **Then** the text aligns properly
3. **Given** any unicode characters in the interface, **When** rendered, **Then** character width is calculated correctly

---

### Edge Cases

- What happens when the terminal window is resized during recording?
- How does the system handle very long transcriptions that exceed the display width?
- What happens if the terminal doesn't support the required colors or unicode?
- How does the interface behave when transcript history exceeds available memory?
- What happens during rapid hotkey press/release cycles?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a two-panel layout: primary info panel (~2/3 width) on left showing app configuration, and status panel (~1/3 width) on right with fixed status boxes
- **FR-002**: System MUST display fixed status boxes for each state type (Recording, Transcribing, Injecting, Complete, Skipped, Error) that illuminate when active and dim when inactive
- **FR-003**: System MUST display a live recording timer that updates at least 10 times per second during recording
- **FR-004**: System MUST show the recording timer in MM:SS format with sub-second precision optional
- **FR-005**: System MUST provide a modal window (accessible via keypress) that displays the last 100 lines of console logs
- **FR-006**: System MUST correctly calculate and render unicode/emoji character widths
- **FR-007**: System MUST handle terminal resize events gracefully without crashing or corrupting display
- **FR-008**: System MUST support "L" key to open/close the log modal and arrow keys to scroll within it
- **FR-009**: System MUST preserve all existing hotkey functionality (recording start/stop)
- **FR-010**: System MUST display skip reasons when recordings are too short or have no speech
- **FR-011**: System MUST show error messages in the interface when errors occur
- **FR-012**: System MUST provide visual warning when approaching maximum recording duration
- **FR-013**: System MUST gracefully degrade on terminals with limited capability (no unicode support, limited colors)

### Key Entities

- **Status State**: Current recording state with associated visual indicator (icon, color, label)
- **Recording Timer**: Duration counter with start time, current elapsed time, and warning threshold
- **Transcript Entry**: A single history item containing timestamp, type (success/skipped/error), and content
- **Transcript History**: Collection of recent transcript entries with scroll position

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Status updates appear within 50ms of state change (perceived as instant)
- **SC-002**: Recording timer updates at least 10 times per second with no visible lag
- **SC-003**: All emoji indicators display with correct panel alignment (no border offset)
- **SC-004**: Interface remains responsive during recording and transcription operations
- **SC-005**: Log modal displays and scrolls through 100 log lines without performance degradation
- **SC-006**: Terminal resize completes without display corruption within 200ms
- **SC-007**: Application startup time does not increase by more than 500ms compared to current Rich-based implementation

## Clarifications

### Session 2025-11-28

- Q: What layout arrangement should the TUI use? → A: Two-panel layout: Primary large window (~2/3 width) on LEFT showing app info (service name, mic, configuration, instructions), smaller status panel (~1/3 width) on RIGHT with vertically stacked pill-shaped status indicators for each state type (Recording, Transcribing, Injecting, Complete, Skipped, Error) that light up when active and dim when inactive. No scrolling feed. (See mockup provided by user)
- Q: How should activity history be viewed? → A: Modal window accessible via keypress that shows last 100 lines of console logs. Not a scrolling feed in main view.
- Q: What keyboard shortcut should open the log modal? → A: "L" key (for Logs)

## Assumptions

- Terminal supports basic ANSI escape codes for colors and cursor movement
- Terminal width is at least 80 characters
- Users have standard keyboard for navigation (arrow keys, page up/down)
- Textual framework handles low-level terminal compatibility across macOS, Linux, and Windows
- Existing core functionality (audio capture, speech-to-text, injection) remains unchanged
- Configuration options remain compatible with existing config.yaml structure
