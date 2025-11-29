# Quickstart: TTS Response Hook

**Feature**: 004-tts-response-hook
**Audience**: Developers implementing this feature
**Time**: 10 minutes to understand, 2-4 hours to implement

---

## What This Feature Does

Adds audio feedback for Claude Code responses using macOS `say` command:
- **Short responses** (< 50 words): Spoken verbatim
- **Long responses** (≥ 50 words): Summarized to 2-4 sentences, then spoken
- **Runtime toggle**: Press `t` in TUI to enable/disable
- **Manual setup**: User must configure Claude Code hook (documented)

---

## Implementation Overview

### Components to Build

1. **Hook Script** (`stop_hook.sh`)
   - Bash script registered with Claude Code
   - Reads transcript JSONL file
   - Determines short vs long response
   - Invokes summarizer or speaks directly

2. **Summarizer** (`summarizer.py`)
   - Python module for heuristic summarization
   - CLI interface for bash script to call
   - Pattern-based sentence selection

3. **TUI Toggle** (enhance `tui_app.py`)
   - Keybinding: `t` key
   - Creates/deletes flag file
   - Updates status indicator

4. **Documentation** (`docs/claude-code-hook-setup.md`)
   - User guide for manual hook configuration
   - Troubleshooting section

---

## File Structure

```
New files:
  src/push_to_talk_claude/hooks/summarizer.py
  src/push_to_talk_claude/hooks/stop_hook.sh
  docs/claude-code-hook-setup.md

Modified files:
  src/push_to_talk_claude/ui/tui_app.py
  (Add toggle keybinding)

New tests:
  tests/hooks/test_summarizer.py
  tests/hooks/test_stop_hook_integration.sh
```

---

## Implementation Steps

### Step 1: Summarizer (Python)

**File**: `src/push_to_talk_claude/hooks/summarizer.py`

**Core Logic**:
```python
class Summarizer:
    def __init__(self, max_sentences=4, max_words=100):
        self.max_sentences = max_sentences
        self.max_words = max_words
        self.action_verbs = {"implemented", "created", "added", ...}
        self.outcome_indicators = {"complete", "ready", "success", ...}

    def summarize(self, text: str) -> str:
        # 1. Remove code blocks
        text = self._remove_code_blocks(text)

        # 2. Split into sentences
        sentences = self._split_sentences(text)

        # 3. Classify sentences
        actions = [s for s in sentences if self._is_action(s)]
        outcomes = [s for s in sentences if self._is_outcome(s)]
        context = [s for s in sentences if not self._is_action(s) and not self._is_outcome(s)]

        # 4. Select key sentences
        selected = []
        if actions:
            selected.append(actions[0])
        if outcomes:
            selected.append(outcomes[-1])
        # Fill remaining with context (first/last)
        ...

        # 5. Respect limits
        summary = ' '.join(selected[:self.max_sentences])
        if len(summary.split()) > self.max_words:
            summary = self._truncate_to_words(summary, self.max_words)

        return summary
```

**CLI Interface**:
```python
# __main__.py
if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(Summarizer().summarize(text))
```

**Test**:
```bash
python3 -m push_to_talk_claude.hooks.summarizer "I implemented feature X. It works great. All tests pass."
# Output: "Implemented feature X. It works great. All tests pass."
```

---

### Step 2: Hook Script (Bash)

**File**: `src/push_to_talk_claude/hooks/stop_hook.sh`

**Template**:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Configuration
FLAG_FILE="$HOME/.claude-voice/tts-hook-enabled"
CONFIG_FILE="$HOME/.claude-voice/config.yaml"
LOG_FILE="$HOME/.claude-voice/hook.log"
DEBUG="${DEBUG:-0}"

# Logging
log() {
    if [ "$DEBUG" = "1" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    fi
}

log_error() {
    log "ERROR: $1"
}

# Check if enabled
if [ ! -f "$FLAG_FILE" ]; then
    log "Hook disabled (flag file not found)"
    exit 0
fi

# Check dependencies
if ! command -v jq &> /dev/null; then
    log_error "jq not installed. Install with: brew install jq"
    exit 0
fi

# Get transcript path
TRANSCRIPT_FILE="${1:-}"
if [ -z "$TRANSCRIPT_FILE" ] || [ ! -f "$TRANSCRIPT_FILE" ]; then
    log_error "Transcript file not found: $TRANSCRIPT_FILE"
    exit 0
fi

log "Processing transcript: $TRANSCRIPT_FILE"

# Extract last assistant message
RESPONSE=$(jq -r 'select(.role == "assistant") | .content' "$TRANSCRIPT_FILE" | tail -1)

if [ -z "$RESPONSE" ]; then
    log "No assistant message found"
    exit 0
fi

# Remove code blocks (simple sed approach)
CLEAN_RESPONSE=$(echo "$RESPONSE" | sed '/```/,/```/d')

# Count words
WORD_COUNT=$(echo "$CLEAN_RESPONSE" | wc -w | tr -d ' ')
log "Word count: $WORD_COUNT"

# Read TTS config (voice and rate)
VOICE=$(grep -E '^\s*voice:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *//;s/"//g' || echo "")
RATE=$(grep -E '^\s*rate:' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *//' || echo "200")

# Prepare say command
SAY_CMD="say -r $RATE"
if [ -n "$VOICE" ]; then
    SAY_CMD="$SAY_CMD -v $VOICE"
fi

# Speak or summarize
if [ "$WORD_COUNT" -le 50 ]; then
    log "Speaking short response ($WORD_COUNT words)"
    $SAY_CMD "$CLEAN_RESPONSE" &
else
    log "Summarizing long response ($WORD_COUNT words)"
    SUMMARY=$(python3 -m push_to_talk_claude.hooks.summarizer "$CLEAN_RESPONSE")
    log "Summary: $SUMMARY"
    $SAY_CMD "$SUMMARY" &
fi

log "TTS initiated"
exit 0
```

**Install**:
```bash
# Make executable
chmod +x src/push_to_talk_claude/hooks/stop_hook.sh

# Create symlink to standard location
mkdir -p ~/.claude-voice/hooks
ln -sf "$(pwd)/src/push_to_talk_claude/hooks/stop_hook.sh" ~/.claude-voice/hooks/stop_hook.sh
```

**Test**:
```bash
# Create test transcript
echo '{"role":"user","content":"Hello"}' > /tmp/test.jsonl
echo '{"role":"assistant","content":"Hi there!"}' >> /tmp/test.jsonl

# Enable hook
touch ~/.claude-voice/tts-hook-enabled

# Run hook
DEBUG=1 ~/.claude-voice/hooks/stop_hook.sh /tmp/test.jsonl

# Should hear "Hi there!" and see log output
```

---

### Step 3: TUI Toggle

**File**: `src/push_to_talk_claude/ui/tui_app.py`

**Add Binding**:
```python
from textual.binding import Binding

class ClaudeVoiceTUI(App):
    BINDINGS = [
        # ... existing bindings ...
        Binding("t", "toggle_tts_hook", "Toggle TTS Hook", show=True),
    ]
```

**Add Action**:
```python
def action_toggle_tts_hook(self) -> None:
    """Toggle TTS hook enabled/disabled."""
    from pathlib import Path

    flag_file = Path.home() / ".claude-voice" / "tts-hook-enabled"

    try:
        if flag_file.exists():
            flag_file.unlink()
            self._tts_hook_enabled = False
            self.notify("TTS Hook Disabled", severity="info")
        else:
            flag_file.parent.mkdir(parents=True, exist_ok=True)
            flag_file.touch()
            self._tts_hook_enabled = True
            self.notify("TTS Hook Enabled", severity="success")

        # Update status indicator (if you have one)
        # self._update_tts_hook_status()

    except Exception as e:
        self.notify(f"Toggle failed: {e}", severity="error")
```

**Initialize State**:
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    from pathlib import Path
    flag_file = Path.home() / ".claude-voice" / "tts-hook-enabled"
    self._tts_hook_enabled = flag_file.exists()
```

**Test**:
```bash
# Run TUI
uv run claude-voice

# Press 't' key
# Should see notification "TTS Hook Enabled" or "TTS Hook Disabled"
# Check flag file exists/deleted
```

---

### Step 4: User Documentation

**File**: `docs/claude-code-hook-setup.md`

**Contents**:
```markdown
# Claude Code Hook Setup

## Overview

This guide explains how to manually configure Claude Code to trigger TTS
audio feedback for responses.

**⚠️ Important**: This is a brittle integration that may break with Claude Code
updates. You may need to reconfigure after updating Claude Code.

## Prerequisites

- Claude Code installed
- push-to-talk-claude installed
- jq installed: `brew install jq`

## Step 1: Locate Claude Code Settings

Find your Claude Code settings file:

\`\`\`bash
~/.claude/settings.json
\`\`\`

## Step 2: Add Stop Hook

Edit `~/.claude/settings.json` and add the hook:

\`\`\`json
{
  "hooks": {
    "stop": "~/.claude-voice/hooks/stop_hook.sh"
  }
}
\`\`\`

If `hooks` section already exists, just add the `stop` entry.

## Step 3: Verify Hook Installation

Check that the hook script exists and is executable:

\`\`\`bash
ls -l ~/.claude-voice/hooks/stop_hook.sh
# Should show -rwxr-xr-x (executable)
\`\`\`

## Step 4: Enable TTS Hook

In the push-to-talk TUI, press `t` to enable the hook.

## Step 5: Test

1. Ask Claude a question in Claude Code
2. You should hear the response spoken aloud
3. Check debug log if issues: `~/.claude-voice/hook.log`

## Troubleshooting

### No audio feedback

- Check flag file exists: `ls ~/.claude-voice/tts-hook-enabled`
- Enable debug logging: `export DEBUG=1` in terminal before starting Claude Code
- Check hook log: `tail -f ~/.claude-voice/hook.log`

### "jq not found" error

Install jq: `brew install jq`

### Hook not triggering

- Verify hook in settings: `cat ~/.claude/settings.json`
- Ensure hook path is absolute or uses `~`
- Check hook is executable: `chmod +x ~/.claude-voice/hooks/stop_hook.sh`

## Disabling

Press `t` in TUI to disable, or delete flag file:

\`\`\`bash
rm ~/.claude-voice/tts-hook-enabled
\`\`\`

## Uninstalling

Remove hook from `~/.claude/settings.json`:

\`\`\`json
{
  "hooks": {
    "stop": null
  }
}
\`\`\`

Or remove entire `hooks` section.
```

---

## Testing Strategy

### Unit Tests

```python
# tests/hooks/test_summarizer.py
def test_summarize_short():
    s = Summarizer()
    text = "Short response."
    assert s.summarize(text) == text

def test_summarize_long():
    s = Summarizer()
    text = "I implemented feature. " * 30  # 90 words
    summary = s.summarize(text)
    assert len(summary.split()) <= 100
    assert summary.count('.') <= 4
```

### Integration Tests

```bash
# tests/hooks/test_stop_hook_integration.sh
#!/bin/bash

# Test 1: Short response
echo '{"role":"assistant","content":"Yes."}' > /tmp/test1.jsonl
touch ~/.claude-voice/tts-hook-enabled
./src/push_to_talk_claude/hooks/stop_hook.sh /tmp/test1.jsonl
# Manual check: Hear "Yes."

# Test 2: Long response
echo '{"role":"assistant","content":"'$(python3 -c 'print("I implemented this. " * 20)')'"}' > /tmp/test2.jsonl
./src/push_to_talk_claude/hooks/stop_hook.sh /tmp/test2.jsonl
# Manual check: Hear summary (4 sentences)

# Test 3: Disabled hook
rm ~/.claude-voice/tts-hook-enabled
./src/push_to_talk_claude/hooks/stop_hook.sh /tmp/test1.jsonl
# Manual check: No audio
```

---

## Common Issues & Solutions

### Issue: "jq: command not found"

**Solution**: Install jq: `brew install jq`

### Issue: Hook not executable

**Solution**: `chmod +x src/push_to_talk_claude/hooks/stop_hook.sh`

### Issue: Summary too verbose

**Solution**: Adjust `max_sentences` in summarizer (default: 4)

### Issue: Toggle not working

**Solution**: Check permissions on `~/.claude-voice/` directory

---

## Performance Checklist

- [ ] Short response TTS starts < 2s after Claude finishes
- [ ] Long response TTS starts < 5s after Claude finishes
- [ ] Toggle responds < 500ms to keypress
- [ ] Hook script exits 0 even on errors
- [ ] No Claude Code disruption from hook failures

---

## Deployment Checklist

- [ ] Hook script tested with real Claude Code session
- [ ] Summarizer produces coherent summaries for typical responses
- [ ] Toggle creates/deletes flag file correctly
- [ ] Documentation covers all manual setup steps
- [ ] Error messages are helpful for troubleshooting
- [ ] Debug logging works when enabled

---

## Next Steps After Implementation

1. Test with various Claude Code responses (short, long, code-heavy)
2. Gather user feedback on summary quality
3. Adjust action verbs / outcome indicators if needed
4. Consider adding custom voice selection in future version
