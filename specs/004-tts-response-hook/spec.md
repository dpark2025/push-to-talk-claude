# Feature Specification: TTS Response Hook

**Feature Branch**: `004-tts-response-hook`
**Created**: 2025-11-28
**Status**: Draft
**Input**: User description: "Claude Code Stop hook for TTS responses - speaks short responses directly using macOS say command, summarizes longer responses before speaking, includes runtime toggle to enable/disable"

## Overview

This feature provides audio feedback for Claude Code responses by implementing a Stop hook that speaks Claude's responses aloud. Short, conversational responses (yes/no, confirmations, brief answers) are spoken directly, while longer responses are first summarized to a few sentences describing what was done and the outcome before being spoken.

**Important**: This feature requires manual Claude Code configuration by the end user and represents a brittle integration that may break with Claude Code updates.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hear Short Responses (Priority: P1)

As a user working hands-free with push-to-talk, I want Claude's short responses (confirmations, yes/no answers, brief status updates) to be spoken aloud immediately so I can continue working without looking at my screen.

**Why this priority**: This is the core value proposition - enabling true hands-free interaction for quick exchanges with Claude.

**Independent Test**: Can be fully tested by asking Claude a yes/no question and hearing the response spoken aloud.

**Acceptance Scenarios**:

1. **Given** TTS hook is enabled, **When** Claude responds with a short message (under 50 words), **Then** the response is spoken aloud using the system voice within 2 seconds
2. **Given** TTS hook is enabled, **When** Claude responds "Yes, I'll do that.", **Then** user hears "Yes, I'll do that." spoken aloud
3. **Given** TTS hook is enabled, **When** Claude responds with a single sentence confirmation, **Then** the entire sentence is spoken verbatim

---

### User Story 2 - Hear Summarized Long Responses (Priority: P1)

As a user working hands-free, I want Claude's long responses (code implementations, detailed explanations, multi-step completions) to be summarized and spoken so I know what was accomplished without reading the full output.

**Why this priority**: Equally critical to P1-1 - long responses are common and need audio feedback to be useful.

**Independent Test**: Can be fully tested by asking Claude to implement a feature and hearing a summary of what was done.

**Acceptance Scenarios**:

1. **Given** TTS hook is enabled, **When** Claude responds with a long message (50+ words), **Then** a summary (2-4 sentences) describing the work done and outcome is spoken
2. **Given** TTS hook is enabled, **When** Claude completes a multi-file code change, **Then** user hears a summary like "Implemented the authentication feature across 3 files. All tests pass. Ready for review."
3. **Given** TTS hook is enabled, **When** Claude provides a detailed explanation, **Then** user hears the key conclusion/answer, not the full explanation

---

### User Story 3 - Toggle TTS Hook at Runtime (Priority: P2)

As a user, I want to enable or disable the TTS response hook without restarting Claude Code so I can control when responses are spoken based on my environment (office vs home, meeting vs focused work).

**Why this priority**: Essential for practical use - users need control without disrupting their workflow.

**Independent Test**: Can be fully tested by toggling the setting and verifying subsequent responses are/aren't spoken.

**Acceptance Scenarios**:

1. **Given** TTS hook is currently enabled, **When** user presses the toggle key in TUI, **Then** TTS hook is disabled and a confirmation is shown
2. **Given** TTS hook is currently disabled, **When** user presses the toggle key in TUI, **Then** TTS hook is enabled and a confirmation is shown
3. **Given** TTS hook was toggled off, **When** Claude responds, **Then** no audio is played

---

### User Story 4 - Setup Documentation (Priority: P2)

As a new user, I want clear documentation explaining how to manually configure the Claude Code Stop hook so I can set up the TTS feature correctly.

**Why this priority**: Without clear documentation, users cannot use this feature at all.

**Independent Test**: Can be tested by having a new user follow the documentation and successfully configure the hook.

**Acceptance Scenarios**:

1. **Given** a user has push-to-talk-claude installed, **When** they read the setup documentation, **Then** they understand all manual steps required to configure the Claude Code hook
2. **Given** documentation exists, **When** user follows the steps, **Then** the hook is properly registered in Claude Code settings
3. **Given** documentation exists, **When** Claude Code updates, **Then** documentation clearly indicates this is a brittle integration that may require reconfiguration

---

### Edge Cases

- What happens when the transcript file is empty or missing?
  - Hook exits silently without error
- What happens when Claude's response contains code blocks or special formatting?
  - Summary strips code blocks and speaks only natural language portions
- What happens when the macOS `say` command is unavailable?
  - Hook logs an error and exits gracefully
- What happens when multiple Claude responses occur rapidly?
  - Each response is queued and spoken in order
- What happens when the user toggles TTS off mid-speech?
  - Current speech completes, subsequent responses not spoken

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a hook script that integrates with Claude Code's Stop hook event
- **FR-002**: System MUST read Claude's response from the transcript file provided by the hook, processing ONLY the last assistant message (not the full conversation history)
- **FR-003**: System MUST distinguish between short responses (under 50 words) and long responses (50+ words)
- **FR-004**: System MUST speak short responses verbatim using the macOS `say` command
- **FR-005**: System MUST summarize long responses to 2-4 sentences before speaking
- **FR-006**: System MUST check for an enable/disable flag file before processing responses
- **FR-007**: System MUST provide a TUI keybinding to toggle the enable/disable flag
- **FR-008**: System MUST include user documentation explaining manual Claude Code hook configuration
- **FR-009**: Documentation MUST clearly state this is a brittle integration that may break with Claude Code updates
- **FR-010**: System MUST handle missing or malformed transcript files gracefully
- **FR-011**: System MUST strip code blocks and formatting from responses before summarizing/speaking

### Summarization Requirements

- **FR-012**: Summaries MUST focus on what action was taken and the outcome
- **FR-013**: Summaries MUST be conversational and suitable for spoken delivery
- **FR-014**: Summaries MUST NOT exceed 4 sentences or 100 words

### Key Entities

- **Hook Script**: The executable script registered with Claude Code's Stop hook that processes responses
- **Flag File**: A file (`~/.claude-voice/tts-hook-enabled`) whose presence indicates the hook is active
- **Transcript**: The JSONL file provided by Claude Code containing the conversation history
- **Response**: Claude's assistant message extracted from the transcript for processing

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Short responses (under 50 words) are spoken within 2 seconds of Claude finishing
- **SC-002**: Long responses are summarized and spoken within 5 seconds of Claude finishing
- **SC-003**: Toggle operation completes within 500ms and provides visual confirmation
- **SC-004**: 100% of hook errors are handled gracefully without disrupting Claude Code
- **SC-005**: Documentation enables a new user to configure the hook within 5 minutes
- **SC-006**: Summaries accurately reflect the work done in 90%+ of cases

## Assumptions

- Users are on macOS with the `say` command available
- Users have Claude Code installed and understand basic hook configuration
- The Claude Code transcript format remains stable (JSONL with role/content fields)
- Users accept that this integration may require reconfiguration after Claude Code updates
- Short response threshold of 50 words is appropriate (can be adjusted based on feedback)
- Summaries will be generated using simple heuristics (first sentence + outcome detection) rather than LLM-based summarization to avoid latency and API dependencies

## Out of Scope

- Windows or Linux support (macOS `say` command only)
- Custom voice selection (uses system default)
- LLM-based summarization (would add latency and require API keys)
- Automatic hook registration (requires manual Claude Code configuration)
- Speaking responses from subagents (only main agent Stop hook)

## Dependencies

- Claude Code with hooks support
- macOS with `say` command
- Existing push-to-talk-claude TUI for toggle integration
- jq for JSON parsing (standard on most systems, can be installed via Homebrew)
