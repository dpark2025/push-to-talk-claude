<!--
SYNC IMPACT REPORT
==================
Version Change: N/A → 1.0.0 (initial ratification)
Modified Principles: N/A (new constitution)
Added Sections:
  - 8 Core Principles (Privacy, Speed, Smart Filtering, Reliability, Terminal Agnostic,
    Smart Defaults, Security, Ship Small)
  - Technical Standards
  - Decision Framework
  - Success Metrics
  - Governance
Removed Sections: N/A
Templates Requiring Updates:
  - .specify/templates/plan-template.md: ✅ No updates needed (Constitution Check is generic)
  - .specify/templates/spec-template.md: ✅ No updates needed (requirements section is generic)
  - .specify/templates/tasks-template.md: ✅ No updates needed (phase structure is compatible)
Follow-up TODOs: None
-->

# Claude Voice macOS Constitution

**Mission**: Enable seamless, privacy-first voice interaction with Claude Code on macOS through
push-to-talk input and intelligent text-to-speech output.

## Core Principles

### I. Privacy is Non-Negotiable

All speech processing defaults to local execution. Audio data MUST NOT be sent to external servers
without explicit user consent. Audio is ephemeral—delete after processing unless user opts to save.

**Key Rules:**
- Whisper MUST run locally by default
- System TTS MUST be used by default (already installed on macOS)
- No telemetry without opt-in
- Documentation MUST clearly state what touches external services

### II. Speed Matters

Voice interaction MUST feel instantaneous. Any lag breaks conversational flow.

**Performance Targets:**
- Hotkey to recording: < 100ms
- Voice to text in Claude: < 3s (p95)
- Hook processing: < 1s

**Implementation Requirements:**
- Use smallest viable Whisper model (tiny/base)
- Leverage Apple Silicon GPU when available
- Pre-load models on startup
- Profile everything in the hot path

### III. Smart Filtering

Speak Claude's thoughts, not its tools. Users want conversation, not code dumps.

**What to Speak:**
- Conversational responses
- High-level explanations
- Confirmations and questions

**What to Silence:**
- Code blocks (```...```)
- Command output
- Tool invocation results
- Anything over 500 chars by default

### IV. Reliability Over Features

Core push-to-talk → transcribe → inject MUST never fail. Everything else is secondary.

**Standards:**
- 80%+ test coverage minimum
- Clear error messages with actionable steps
- Graceful degradation when optional features fail
- Test every error path

### V. Terminal Agnostic, macOS Native

Works everywhere via tmux. Leverages macOS capabilities when available.

**Implementation Requirements:**
- tmux for text injection (works in all terminals)
- macOS Accessibility API for keyboard
- CoreAudio for audio capture
- MUST test on iTerm2, Terminal.app, Kitty, Alacritty

### VI. Smart Defaults, Deep Customization

Works immediately for beginners. Customizable for power users.

**Philosophy:**
- Single command to start with defaults
- YAML config for all settings
- Environment variables for quick overrides
- Validate config with helpful errors

### VII. Secure by Default

Treat all input as potentially malicious.

**Security Requirements:**
- Sanitize transcribed text before tmux injection
- Escape shell metacharacters
- Limit input length (default: 500 chars)
- Validate file paths
- NEVER eval() or exec() user input

### VIII. Ship Small, Ship Often

Incremental delivery beats big bang releases.

**Development Phases:**
1. Core PTT + text injection
2. Response handling + TTS
3. Polish & UX
4. Advanced features

**Shipping Criteria:**
- Feature is documented
- Tests pass
- Manual checklist complete
- No critical bugs

## Technical Standards

**Code Quality:**
- Python 3.9+
- Black formatter (line length 100)
- Type hints on public APIs
- 80%+ test coverage

**Dependencies:**
- Minimize count
- Actively maintained only
- Permissive licenses (MIT/Apache/BSD)
- MUST work on macOS 11.0+

**Documentation:**
- Every feature documented before merge
- README: 5-minute quick start
- Code comments for complex logic
- Docstrings for public APIs

## Decision Framework

### When Adding Features

**Ask:**
1. Does this align with our mission?
2. Does it violate any first principles?
3. Is this the simplest solution?
4. Is it documented and tested?

**Green Light:** Improves core loop, reduces latency, enhances privacy, increases reliability

**Red Flag:** Adds latency, requires external services, poor docs, not tested

### When Choosing Technology

**Criteria:**
- Works on macOS 11.0+?
- Actively maintained?
- Acceptable performance?
- Standard solution?
- License compatible?

## Success Metrics

- **Setup**: < 5 min from clone to first voice input
- **Latency**: < 3s voice-to-text (p95)
- **Error Rate**: < 1% of inputs fail
- **Test Coverage**: > 80% overall, 100% core loop
- **Accuracy**: > 95% WER (clear audio)

## Governance

This constitution supersedes all other practices for the Claude Voice macOS project.

### Amendment Process

1. Open GitHub issue with "Constitution:" prefix
2. Explain what and why
3. Community discussion (7+ days)
4. PR if consensus reached

### When to Amend

- New use cases emerge
- Technology landscape changes
- Better approaches discovered
- Principles conflict in practice

### Versioning Policy

- MAJOR: Backward incompatible governance/principle removals or redefinitions
- MINOR: New principle/section added or materially expanded guidance
- PATCH: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review

All PRs and code reviews MUST verify compliance with this constitution. Deviations require
explicit justification documented in the Complexity Tracking section of the implementation plan.

### Guiding Questions

When in doubt, ask:

1. Does this help users?
2. Does this respect privacy?
3. Does this make the core more reliable?

If yes to all three, we're on the right track.

**Version**: 1.0.0 | **Ratified**: 2025-01-28 | **Last Amended**: 2025-11-27
