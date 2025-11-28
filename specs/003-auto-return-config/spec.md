# Feature Specification: Auto-Return Configuration

**Feature Branch**: `003-auto-return-config`
**Created**: 2025-11-28
**Status**: Draft
**Input**: User description: "Configuration that allows the user to have the text transcribed and also include an auto return at the end so that it automatically hits enter after the text is put into the window."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Submit Voice Commands (Priority: P1)

A user wants to use voice commands to interact with Claude Code hands-free. When they speak a command and release the push-to-talk key, the transcribed text should be automatically submitted (enter key pressed) without requiring manual intervention.

**Why this priority**: This is the core feature request - enabling hands-free operation by automatically submitting after transcription. Without this, users must still press Enter manually, defeating the hands-free workflow.

**Independent Test**: Can be fully tested by speaking a command with auto-return enabled and verifying the text is transcribed AND submitted without touching the keyboard.

**Acceptance Scenarios**:

1. **Given** auto_return is enabled in config, **When** user speaks "hello world" and releases push-to-talk key, **Then** "hello world" is typed into the active window AND Enter key is automatically pressed
2. **Given** auto_return is enabled in config, **When** user speaks a command to Claude Code, **Then** the command is transcribed and submitted automatically to Claude Code
3. **Given** auto_return is disabled in config (default), **When** user speaks "hello world", **Then** only "hello world" is typed (no automatic Enter) preserving current behavior

---

### User Story 2 - Configure Auto-Return via Config File (Priority: P2)

A user wants to enable or disable auto-return behavior through the configuration file (~/.claude-voice/config.yaml) rather than through a runtime toggle.

**Why this priority**: Persistent configuration is essential for users who always want auto-return behavior. Without persistent config, users would need to enable it each session.

**Independent Test**: Can be tested by modifying config.yaml and restarting the application to verify the new setting takes effect.

**Acceptance Scenarios**:

1. **Given** config.yaml has `injection.auto_return: true`, **When** application starts, **Then** auto-return behavior is enabled
2. **Given** config.yaml has `injection.auto_return: false`, **When** application starts, **Then** auto-return behavior is disabled
3. **Given** config.yaml has no auto_return setting, **When** application starts, **Then** auto-return defaults to false (preserving backward compatibility)

---

### User Story 3 - Runtime Toggle via Keyboard (Priority: P1)

A user wants to toggle auto-return on or off at runtime using a keyboard shortcut, without editing config files or restarting the application.

**Why this priority**: Runtime control is essential for hands-free workflow. Users need to quickly enable/disable auto-return based on context (e.g., disable when dictating partial text, enable for commands).

**Independent Test**: Can be tested by pressing the toggle key and observing both the UI indicator change and the behavior change on next transcription.

**Acceptance Scenarios**:

1. **Given** auto_return is OFF, **When** user presses the toggle key (a), **Then** auto-return switches to ON and the UI indicator updates immediately
2. **Given** auto_return is ON, **When** user presses the toggle key (a), **Then** auto-return switches to OFF and the UI indicator updates immediately
3. **Given** user toggles auto-return at runtime, **When** user speaks next command, **Then** the new setting is applied to that transcription
4. **Given** user toggles auto-return at runtime, **When** application restarts, **Then** auto-return reverts to the config file setting (runtime toggle is session-only)

---

### User Story 4 - Visual Status Indicator (Priority: P2)

A user wants to see at a glance whether auto-return is currently enabled or disabled in the main TUI window, so they know what behavior to expect when they speak.

**Why this priority**: Visual feedback prevents user confusion and mistakes. Users need to know if their voice input will be auto-submitted before they speak.

**Independent Test**: Can be tested by launching the application and verifying the auto-return status is visible in the main window.

**Acceptance Scenarios**:

1. **Given** auto_return is enabled, **When** user views the main window, **Then** an indicator shows auto-return is ON
2. **Given** auto_return is disabled, **When** user views the main window, **Then** an indicator shows auto-return is OFF
3. **Given** the application is running, **When** user looks at the main window, **Then** the auto-return status is clearly visible without scrolling or navigation
4. **Given** user toggles auto-return via keyboard, **When** toggle completes, **Then** the indicator updates immediately to reflect new state

---

### User Story 5 - Startup Configuration Box (Priority: P2)

A user wants to clearly distinguish between settings that are fixed at startup (from config file) versus settings that can be toggled at runtime. The startup configuration should be visually grouped in a labeled box.

**Why this priority**: Clear visual organization prevents confusion about which settings can be changed without restarting. Users need to understand the difference between static config and runtime-adjustable options.

**Independent Test**: Can be tested by launching the application and verifying startup settings are grouped in a labeled box separate from runtime-toggleable options.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** user views the main window, **Then** startup configuration items (Hotkey, Model, Mode, Target, Transcript Logging) are displayed within a visually distinct box
2. **Given** the application is running, **When** user views the main window, **Then** the box has a clear label such as "Startup Configuration" indicating these are startup-time settings
3. **Given** the application is running, **When** user views the main window, **Then** runtime-toggleable options (Auto-Return) are displayed outside the startup configuration box

---

### User Story 6 - Transcript Logging Status Display (Priority: P3)

A user wants to see whether transcript logging is enabled and where transcripts are being saved, so they know if their voice inputs are being recorded to disk.

**Why this priority**: Privacy awareness - users should know at a glance if their transcriptions are being saved and where.

**Independent Test**: Can be tested by launching the application with logging enabled/disabled and verifying the display shows the correct status.

**Acceptance Scenarios**:

1. **Given** transcript logging is enabled in config, **When** user views the main window, **Then** the display shows "Transcript Logging: /path/to/transcripts"
2. **Given** transcript logging is disabled in config, **When** user views the main window, **Then** the display shows "Transcript Logging: DISABLED"
3. **Given** the application is running, **When** user looks at the startup configuration box, **Then** the transcript logging status is clearly visible

---

### Edge Cases

- What happens when auto_return is enabled but the target window doesn't accept Enter key input (e.g., single-line field that submits on Enter)?
  - **Behavior**: Enter key is still sent; the application behavior depends on the target window
- What happens when transcription results in empty text?
  - **Behavior**: No Enter key is sent when transcription is empty (prevents submitting blank input)
- What happens when injection mode is "tmux"?
  - **Behavior**: Auto-return applies to tmux injection as well, sending Enter after the transcribed text

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support an `auto_return` configuration option within the injection settings
- **FR-002**: System MUST send an Enter keystroke immediately after injecting transcribed text when auto_return is enabled
- **FR-003**: System MUST NOT send an Enter keystroke after transcription when auto_return is disabled
- **FR-004**: System MUST default auto_return to `false` to maintain backward compatibility with existing installations
- **FR-005**: System MUST NOT send Enter when transcription result is empty (regardless of auto_return setting)
- **FR-006**: System MUST support auto_return behavior for both injection modes: "focused" and "tmux"
- **FR-007**: System MUST validate auto_return as a boolean value in configuration validation
- **FR-008**: System MUST display the current auto-return status (ON/OFF) in the main TUI window
- **FR-009**: System MUST show the auto-return indicator in a location visible without scrolling or additional navigation
- **FR-010**: System MUST provide a keyboard shortcut (key: `a`) to toggle auto-return on/off at runtime
- **FR-011**: System MUST update the UI indicator immediately when auto-return is toggled
- **FR-012**: System MUST apply the toggled setting to the next transcription without requiring restart
- **FR-013**: System MUST show the toggle shortcut in the TUI footer (e.g., "a Auto-Return")
- **FR-014**: Runtime toggle MUST NOT persist to config file (session-only change)
- **FR-015**: System MUST display startup configuration items in a visually distinct bordered box
- **FR-016**: System MUST label the startup configuration box with text such as "Startup Configuration"
- **FR-017**: System MUST display runtime-toggleable options (Auto-Return) outside the startup configuration box
- **FR-018**: System MUST display transcript logging status within the startup configuration box
- **FR-019**: System MUST show the transcript directory path when logging is enabled (e.g., "Transcript Logging: /path/to/dir")
- **FR-020**: System MUST show "DISABLED" when transcript logging is disabled (e.g., "Transcript Logging: DISABLED")

### Key Entities

- **InjectionConfig**: Extended to include `auto_return` boolean property alongside existing `mode` property
- **Config YAML structure**: New optional field `injection.auto_return` (boolean, default: false)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a voice-to-submit workflow without touching the keyboard (zero additional keystrokes after voice input)
- **SC-002**: Existing users who upgrade experience no change in behavior (backward compatibility maintained via false default)
- **SC-003**: Configuration change takes effect on next application start (no restart-free requirement)
- **SC-004**: Auto-return works correctly in both focused window mode and tmux mode
- **SC-005**: Users can determine auto-return status within 1 second of viewing the main window (clear visual indicator)
- **SC-006**: Users can toggle auto-return with a single keypress (no modifier keys required)
- **SC-007**: Toggle response time is under 100ms (immediate visual feedback)
- **SC-008**: Users can distinguish startup config from runtime options within 2 seconds of viewing the window (clear visual separation)
- **SC-009**: Users can determine transcript logging status within 1 second of viewing the startup config box

## Assumptions

- Users understand that enabling auto_return means their transcriptions will be immediately submitted
- The Enter keystroke timing occurs immediately after text injection with no configurable delay
- Auto-return applies to all transcriptions when enabled (no per-transcription control)
