# Feature Specification: Push-to-Talk Voice Interface for Claude Code

**Feature Branch**: `001-voice-interface`
**Created**: 2025-11-27
**Status**: Draft
**Input**: User description: "Build a push-to-talk voice interface for Claude Code on macOS. Core features: (1) Configurable hotkey triggers audio recording, (2) Local speech-to-text transcribes speech, (3) Transcribed text injected into Claude Code via tmux, (4) Claude Code hooks trigger response handling, (5) Response parser filters code blocks and command output, (6) macOS system TTS speaks only conversational responses. Privacy-first: all processing local by default. Target: <3s voice-to-text latency, <5 min setup time."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Voice Input to Claude Code (Priority: P1)

As a developer using Claude Code in a terminal, I want to speak my questions and commands instead of typing them, so that I can interact with Claude hands-free while looking at documentation, sketching on paper, or when typing is inconvenient.

**Why this priority**: This is the core value proposition. Without voice input working reliably, no other features matter. A developer should be able to hold a key, speak naturally, release the key, and see their words appear in Claude Code.

**Independent Test**: Can be fully tested by pressing the hotkey, speaking a simple phrase like "hello world", releasing the key, and verifying the text appears in the Claude Code input area. Delivers immediate hands-free input capability.

**Acceptance Scenarios**:

1. **Given** the voice interface is running and Claude Code is active in tmux, **When** I press and hold the hotkey and speak "create a hello world function", **Then** my spoken words appear as text in Claude Code's input within 3 seconds of releasing the key.

2. **Given** the voice interface is running, **When** I press and release the hotkey without speaking, **Then** no text is injected and no error occurs.

3. **Given** the voice interface is running, **When** I speak with background noise (fan, music at low volume), **Then** the system still transcribes my speech with reasonable accuracy (>90% word accuracy).

4. **Given** the voice interface is running, **When** I speak a phrase with punctuation context like "what is the error question mark", **Then** the transcription includes appropriate punctuation ("What is the error?").

---

### User Story 2 - Hearing Claude's Conversational Responses (Priority: P2)

As a developer, I want Claude's explanatory responses spoken aloud so that I can listen while keeping my eyes on code or documentation, but I don't want code blocks or command output read to me.

**Why this priority**: Completes the voice interaction loop. After P1 delivers input, P2 delivers output. This creates a true conversational experience. However, it depends on P1 working first.

**Independent Test**: Can be tested by asking Claude a simple question (via keyboard or voice) and verifying that Claude's conversational response is spoken aloud, while any code in the response is silently skipped.

**Acceptance Scenarios**:

1. **Given** Claude responds with "I'll help you create that function. Here's the code:", **When** the response is processed, **Then** the text "I'll help you create that function. Here's the code:" is spoken aloud.

2. **Given** Claude responds with a code block containing Python code, **When** the response is processed, **Then** the code block content is NOT spoken.

3. **Given** Claude runs a command and shows output like "File created: src/main.py", **When** the response is processed, **Then** the command output is NOT spoken.

4. **Given** Claude responds with a very long explanation (>500 characters), **When** the response is processed, **Then** only the first portion is spoken (to avoid lengthy readings), or the user is informed the response was truncated.

---

### User Story 3 - Customizing the Voice Experience (Priority: P3)

As a power user, I want to change the push-to-talk hotkey and voice settings so that the interface fits my workflow and doesn't conflict with other shortcuts I use.

**Why this priority**: Enhances usability but is not essential for core functionality. Users can work with defaults initially; customization improves long-term experience.

**Independent Test**: Can be tested by modifying a configuration setting (e.g., changing hotkey from right-Ctrl to F13) and verifying the new setting takes effect.

**Acceptance Scenarios**:

1. **Given** I want to use F13 as my hotkey instead of the default, **When** I update the configuration and restart the voice interface, **Then** F13 triggers voice recording and the previous default key no longer does.

2. **Given** I want a faster speaking rate for TTS, **When** I update the voice rate setting, **Then** Claude's responses are spoken at the new rate.

3. **Given** I want to disable TTS entirely (voice input only), **When** I set TTS to disabled in configuration, **Then** voice input still works but no responses are spoken.

---

### User Story 4 - Quick Setup Experience (Priority: P4)

As a new user, I want to install and start using voice control within 5 minutes so that I can quickly evaluate if this tool fits my workflow.

**Why this priority**: Reduces adoption friction. A complex setup process will deter users before they experience the value.

**Independent Test**: Can be tested by timing a fresh installation on a clean macOS system from clone to first successful voice input.

**Acceptance Scenarios**:

1. **Given** I have a Mac with Homebrew installed, **When** I follow the quick start instructions, **Then** I can complete setup and make my first voice input within 5 minutes.

2. **Given** I need microphone and accessibility permissions, **When** the system needs these permissions, **Then** clear instructions guide me to the correct macOS settings.

3. **Given** I'm missing a required dependency, **When** I run the setup, **Then** the system tells me exactly what's missing and how to install it.

---

### Edge Cases

- What happens when no microphone is connected or microphone permission is denied?
- How does the system handle tmux not running or Claude Code not being in the active pane?
- What happens if the user holds the hotkey for an excessively long time (>60 seconds)?
- How does the system behave when speech transcription returns empty or gibberish?
- What happens if TTS is still speaking when new input is given?
- How does the system handle special characters or non-English words in transcription?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect when the configured hotkey is pressed and released
- **FR-002**: System MUST record audio from the default microphone while the hotkey is held
- **FR-003**: System MUST transcribe recorded audio to text locally (no external API calls by default)
- **FR-004**: System MUST inject transcribed text into the active Claude Code session running in tmux
- **FR-005**: System MUST sanitize transcribed text before injection to prevent command injection
- **FR-006**: System MUST detect Claude Code responses via hooks or transcript monitoring
- **FR-007**: System MUST distinguish between conversational responses and code/command output
- **FR-008**: System MUST speak conversational responses using text-to-speech
- **FR-009**: System MUST NOT speak code blocks, command output, or tool invocation results
- **FR-010**: System MUST allow configuration of the push-to-talk hotkey
- **FR-011**: System MUST allow configuration of TTS voice and speaking rate
- **FR-012**: System MUST provide clear error messages when permissions are missing
- **FR-013**: System MUST work across common macOS terminal emulators (Terminal.app, iTerm2, Kitty)
- **FR-014**: System MUST limit transcribed text length (configurable, default 500 chars) to prevent injection of excessively long content
- **FR-015**: System MUST provide visual or audio feedback when recording starts and stops

### Key Entities

- **Recording Session**: A single push-to-talk interaction; has start time, end time, audio data, and resulting transcription
- **Configuration**: User preferences including hotkey selection, TTS settings, and model preferences
- **Claude Response**: Output from Claude Code that needs classification as conversational or non-conversational
- **Tmux Session**: The terminal multiplexer session where Claude Code is running; has session name, window, and pane identifiers

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete voice input (press hotkey, speak, release, see text) within 3 seconds for a typical utterance (5-10 words)
- **SC-002**: New users can install and make their first voice input within 5 minutes
- **SC-003**: Voice transcription achieves >95% word accuracy for clear speech in quiet environments
- **SC-004**: Less than 1% of voice inputs result in errors or failures
- **SC-005**: Users report the TTS correctly filters out code blocks in >95% of Claude responses containing code
- **SC-006**: System uses no external services for speech processing by default (100% local processing)
- **SC-007**: 90% of users successfully configure a custom hotkey on first attempt
- **SC-008**: System provides actionable error messages for 100% of permission-related failures

## Technical Decisions

The following architectural decisions resolve ambiguities and align with the project constitution.

### TD-001: Text Injection Mechanism

**Decision**: Use `tmux send-keys` command for text injection.

**Rationale**:
- Works reliably across all terminal emulators (FR-013)
- No GUI automation required (avoids Accessibility API complexity for injection)
- Text sent as complete string, not character-by-character
- Aligns with Constitution Principle V (Terminal Agnostic, macOS Native)

**Specification**:
- Primary method: `tmux send-keys -t <session>:<window>.<pane> "<sanitized_text>"`
- Text MUST be properly quoted/escaped for shell
- If tmux session not found, system SHALL display error with instructions to start Claude in tmux
- System SHALL auto-detect Claude Code pane by checking `pane_current_command`

### TD-002: Response Detection Strategy

**Decision**: Use Claude Code hooks as primary method, with transcript file watching as fallback.

**Rationale**:
- Hooks provide lowest latency and most reliable detection
- File watching enables compatibility if hooks unavailable
- Aligns with Constitution Principle II (Speed Matters)

**Specification**:
- Primary: Register hook script via Claude Code's hook system (`~/.claude/settings.json`)
- Hook receives JSON payload with session_id, event type, transcript path
- Fallback: Watch `~/.claude/` transcript files using filesystem events
- Detection latency target: < 500ms from response completion to TTS start
- System SHALL distinguish Claude responses from user input by event type or content markers

### TD-003: Text Sanitization Rules

**Decision**: Escape shell metacharacters and enforce configurable character limits per Constitution Principle VII.

**Specification**:
- Maximum input length: configurable, default 500 characters (~5 sentence paragraph)
- Character limit MUST be configurable via config file (`security.max_input_length`)
- If input exceeds limit, truncate and display warning to user
- MUST escape these shell metacharacters before injection: `$`, `` ` ``, `\`, `"`, `'`, `|`, `&`, `;`, `>`, `<`, `(`, `)`, `{`, `}`, `[`, `]`, `!`, `*`, `?`, `~`, `#`
- MUST remove ANSI escape sequences
- MUST replace newlines with spaces
- Sanitization occurs BEFORE length check
- Empty transcriptions (after sanitization) SHALL NOT be injected

### TD-004: Permission Handling Behavior

**Decision**: Fail fast with actionable guidance; do not silently degrade.

**Specification**:
- **At startup (missing permission)**: System SHALL refuse to start and display specific instructions:
  - Microphone: "Grant microphone access: System Settings → Privacy & Security → Microphone → Enable for Terminal"
  - Accessibility: "Grant accessibility access: System Settings → Privacy & Security → Accessibility → Enable for Terminal"
- **Permission revoked during operation**: System SHALL stop recording immediately, display error, and prompt user to re-grant permission
- **Microphone disconnected mid-recording**: System SHALL stop recording, discard partial audio, display "Microphone disconnected" error, and await next hotkey press
- **Tmux session not found**: System SHALL display "Claude Code not found in tmux. Start with: tmux new-session -s claude 'claude'"

### TD-005: Latency SLA and Timeout Behavior

**Decision**: 3-second p95 target with 5-second hard timeout.

**Specification**:
- **Target latency**: < 3 seconds (p95) for complete voice-to-text cycle
- **Component breakdown**:
  - Hotkey detection: < 100ms
  - Audio capture stop: < 50ms
  - Transcription: < 2.5s (for 5-10 word utterance)
  - Text injection: < 350ms
- **Hard timeout**: 5 seconds from hotkey release
- **Timeout behavior**: If transcription exceeds 5 seconds, system SHALL:
  1. Cancel the transcription
  2. Play error audio feedback (if audio feedback enabled)
  3. Display "Transcription timed out" message
  4. NOT inject any partial text
- **Long recording handling**: Recordings > 60 seconds SHALL be automatically stopped with warning

### TD-006: Edge Case Resolutions

| Edge Case | Behavior |
|-----------|----------|
| No microphone connected | Refuse to start; display device setup instructions |
| Empty transcription | Silently discard; no injection, no error |
| Gibberish transcription | Inject as-is (user can cancel in Claude Code) |
| TTS speaking when new input starts | Stop current TTS immediately, process new input |
| Special characters in speech | Allow through sanitization if safe; escape if shell-unsafe |
| Non-English words | Attempt transcription; accuracy not guaranteed |

## Assumptions

- Users have macOS 11.0 (Big Sur) or later
- Users have a working microphone (built-in or external)
- Users run Claude Code within tmux (required for text injection)
- Users are willing to grant microphone and accessibility permissions
- Default hotkey (right Ctrl) is acceptable for most users; power users will customize
- English is the primary language; other languages may work but are not guaranteed
- Users have sufficient disk space for speech recognition models (~100MB)
