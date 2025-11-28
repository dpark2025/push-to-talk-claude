# Research: Auto-Return Configuration

**Feature**: 003-auto-return-config
**Date**: 2025-11-28

## Overview

This feature has no unknowns requiring research. All technical decisions are straightforward extensions of existing patterns.

## Decisions

### D1: Enter Key Implementation (Focused Mode)

**Decision**: Use `pynput.keyboard.Key.enter` constant

**Rationale**:
- pynput is already a dependency for keyboard monitoring
- `Key.enter` is the standard cross-platform constant
- Consistent with existing `Controller.type()` usage in FocusedInjector

**Alternatives Considered**:
- PyAutoGUI: Would add a new dependency unnecessarily
- AppleScript: macOS-specific, less portable

### D2: Enter Key Implementation (tmux Mode)

**Decision**: Use `tmux send-keys Enter` command

**Rationale**:
- tmux's `send-keys` command already supports the `Enter` keyword natively
- Follows existing pattern in TmuxInjector for subprocess calls
- No additional escaping or handling needed

**Alternatives Considered**:
- Sending `\n` or `\r`: Could cause issues with different terminal emulators
- Using pynput in tmux mode: Would require focus management, breaks terminal-agnostic design

### D3: Config Location

**Decision**: Add to existing `InjectionConfig` dataclass

**Rationale**:
- Auto-return is conceptually part of "injection" behavior
- Keeps related settings together
- Follows existing config organization pattern

**Alternatives Considered**:
- New top-level config section: Over-engineering for a single boolean
- Under push_to_talk section: Semantically incorrect (PTT is about recording, not injection)

### D4: UI Indicator Placement

**Decision**: Add after "Target:" line in InfoPanel

**Rationale**:
- Groups with other injection-related info (Mode, Target)
- Visible without scrolling (within first 6 lines)
- Consistent Static widget pattern

**Alternatives Considered**:
- Status bar/footer: Would require Textual Footer modifications
- Separate widget: Over-engineering for a single line of text

## No Further Research Required

All NEEDS CLARIFICATION markers from spec were resolved during specification phase.
