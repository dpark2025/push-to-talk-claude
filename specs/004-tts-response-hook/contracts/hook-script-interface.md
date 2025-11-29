# Contract: Hook Script Interface

**Version**: 1.0.0
**Date**: 2025-11-28

## Overview

This contract defines the interface between Claude Code and the TTS response hook script (`stop_hook.sh`).

## Hook Registration

### Claude Code Configuration

The hook must be registered in Claude Code's settings file:

**File**: `~/.claude/settings.json`

**Registration**:
```json
{
  "hooks": {
    "stop": "~/.claude-voice/hooks/stop_hook.sh"
  }
}
```

**Notes**:
- Path must be absolute or use `~` for home directory
- Script must be executable (`chmod +x`)
- Claude Code expands `~` to user's home directory

---

## Hook Invocation

### Command Line Interface

```bash
stop_hook.sh <transcript_file_path>
```

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `$1` | string | Absolute path to transcript JSONL file | `/tmp/claude-session-abc123.jsonl` |

### Environment

Claude Code provides no special environment variables. Hook inherits user's shell environment.

### Exit Codes

| Code | Meaning | Claude Code Behavior |
|------|---------|---------------------|
| `0` | Success (or graceful failure) | Continue normally |
| `non-zero` | Error | May log warning, continue normally |

**Contract**: Hook must ALWAYS exit 0 to avoid disrupting Claude Code.

---

## Input Format: Transcript JSONL

### File Format

**Format**: JSONL (JSON Lines)
- One JSON object per line
- No comma separators between lines
- Each line is valid JSON

**Encoding**: UTF-8

**Location**: Temporary file in `/tmp/` (varies per session)

**Lifetime**: File exists for duration of Claude Code session, may be cleaned up after

### Message Schema

```typescript
interface TranscriptMessage {
  role: "user" | "assistant";
  content: string;
}
```

### Example File

```json
{"role":"user","content":"Create a hello world function"}
{"role":"assistant","content":"I'll create a hello world function.\n\n```python\ndef hello():\n    print('Hello, World!')\n```\n\nFunction created."}
{"role":"user","content":"Thanks"}
{"role":"assistant","content":"You're welcome!"}
```

### Parsing Contract

**Hook Responsibilities**:
1. Read file from path in `$1`
2. Parse each line as JSON
3. Filter for `role == "assistant"`
4. Extract last assistant message's `content` field

**Example Parsing (jq)**:
```bash
TRANSCRIPT_FILE="$1"
LAST_RESPONSE=$(jq -r 'select(.role == "assistant") | .content' "$TRANSCRIPT_FILE" | tail -1)
```

### Edge Cases

| Case | File Content | Expected Behavior |
|------|--------------|-------------------|
| Empty file | `` | Exit 0, no TTS |
| No assistant messages | Only `{"role":"user",...}` | Exit 0, no TTS |
| Malformed JSON | `{invalid json}` | Skip line, continue |
| Missing `role` field | `{"content":"..."}` | Treat as invalid, skip |
| Empty `content` | `{"role":"assistant","content":""}` | Exit 0, no TTS |

---

## Output: TTS Invocation

### macOS `say` Command

The hook invokes the macOS `say` command to speak the response.

**Command Structure**:
```bash
say -r <rate> [-v <voice>] "<text>"
```

**Parameters**:
| Flag | Value | Source |
|------|-------|--------|
| `-r` | 100-400 (WPM) | From `~/.claude-voice/config.yaml` or default 200 |
| `-v` | Voice name | From `~/.claude-voice/config.yaml` or omit for default |
| text | Speakable text | From response (original or summary) |

**Example**:
```bash
say -r 200 "Implemented authentication feature. All tests pass. Ready for review."
```

### Text Preparation

Before invoking `say`, the hook must:

1. **Strip code blocks**: Remove fenced code blocks (``````...```````)
2. **Strip command output**: Remove lines starting with `$`, `>`, `#`, etc.
3. **Escape quotes**: Escape double quotes for shell safety
4. **Summarize if long**: If > 50 words, call summarizer

**Code Block Removal (bash)**:
```bash
# Using sed to remove code blocks
echo "$TEXT" | sed '/```/,/```/d'
```

**Word Count Check**:
```bash
WORD_COUNT=$(echo "$TEXT" | wc -w | tr -d ' ')
if [ "$WORD_COUNT" -gt 50 ]; then
    # Summarize
    SUMMARY=$(python3 -m push_to_talk_claude.hooks.summarizer "$TEXT")
    say -r 200 "$SUMMARY"
else
    # Speak directly
    say -r 200 "$TEXT"
fi
```

---

## Hook Toggle: Flag File

### Flag File Path

**Location**: `~/.claude-voice/tts-hook-enabled`

**Format**: Empty file (0 bytes)

**Semantics**:
- File exists → Hook enabled, process responses
- File absent → Hook disabled, exit immediately

### Check Logic

```bash
FLAG_FILE="$HOME/.claude-voice/tts-hook-enabled"

if [ ! -f "$FLAG_FILE" ]; then
    exit 0  # Disabled, exit silently
fi

# Continue with hook logic...
```

### Toggle Operations

**Enable** (from TUI):
```bash
touch ~/.claude-voice/tts-hook-enabled
```

**Disable** (from TUI):
```bash
rm -f ~/.claude-voice/tts-hook-enabled
```

**Check** (from anywhere):
```bash
[ -f ~/.claude-voice/tts-hook-enabled ] && echo "enabled" || echo "disabled"
```

---

## Error Handling Contract

### Principle: Fail Silent

The hook must NEVER disrupt Claude Code operation.

### Error Categories

| Error Type | Detection | Handling |
|------------|-----------|----------|
| Missing transcript file | `[ ! -f "$1" ]` | Log if debug, exit 0 |
| jq not installed | `command -v jq` | Log error, exit 0 |
| Malformed JSON | jq parse error | Skip line, continue |
| say command fails | Exit code check | Log error, exit 0 |
| Summarizer timeout | `timeout` command | Fallback to truncation, exit 0 |

### Logging (Debug Mode)

**Enable**: Set `DEBUG=1` environment variable

**Log File**: `~/.claude-voice/hook.log`

**Format**:
```
[2025-11-28 14:32:15] INFO: Hook triggered
[2025-11-28 14:32:15] ERROR: jq not found
```

**Example**:
```bash
log_error() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> ~/.claude-voice/hook.log
    fi
}

if ! command -v jq &> /dev/null; then
    log_error "jq not installed, please run: brew install jq"
    exit 0
fi
```

---

## Dependencies Contract

### Required Executables

| Dependency | Version | Check Command | Install Command |
|------------|---------|---------------|-----------------|
| bash | 3.2+ | `bash --version` | Built-in on macOS |
| jq | 1.6+ | `jq --version` | `brew install jq` |
| say | Any | `command -v say` | Built-in on macOS |
| python3 | 3.9+ | `python3 --version` | Project requirement |

### Dependency Checks

The hook should check for required dependencies at startup:

```bash
#!/usr/bin/env bash

# Check jq
if ! command -v jq &> /dev/null; then
    log_error "jq not installed. Install with: brew install jq"
    exit 0
fi

# Check say
if ! command -v say &> /dev/null; then
    log_error "say command not found (macOS only)"
    exit 0
fi

# Check python3
if ! command -v python3 &> /dev/null; then
    log_error "python3 not found"
    exit 0
fi
```

---

## Performance Contract

### Latency Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| File existence check | < 1ms | `time [ -f "$FLAG_FILE" ]` |
| JSONL parsing | < 100ms | `time jq ... "$FILE"` |
| Summarization | < 500ms | `time python3 -m summarizer` |
| say invocation | < 200ms | Time to process start (async) |
| **Total (short response)** | **< 2s** | File check → audio start |
| **Total (long response)** | **< 5s** | File check → audio start |

### Async Execution

The `say` command runs asynchronously (fire-and-forget). Hook exits immediately after invoking `say`, does not wait for TTS completion.

```bash
# Async invocation
say -r 200 "$TEXT" &

# Exit immediately
exit 0
```

---

## Security Contract

### Input Sanitization

The hook must sanitize all inputs to prevent command injection:

1. **Quote all variables**: Always use `"$VAR"` not `$VAR`
2. **Validate file paths**: Ensure transcript path is absolute
3. **Escape text for say**: Use proper quoting

**Example**:
```bash
# BAD - command injection risk
say -r 200 $TEXT

# GOOD - safe quoting
say -r 200 "$TEXT"
```

### File Access

- **Read-only**: Hook only reads transcript file, never writes
- **Validate paths**: Reject relative paths or suspicious patterns
- **No temp files**: Stream processing, no intermediate files

---

## Versioning

### Contract Version

This contract is version `1.0.0`.

### Breaking Changes

Changes that would break this contract:
- Changing transcript file format (JSONL → JSON)
- Changing message schema (adding required fields)
- Changing hook invocation signature (different arguments)

### Non-Breaking Changes

Changes that preserve compatibility:
- Adding optional fields to message schema
- Adding new hook types (different events)
- Enhancing error messages

---

## Testing Contract

### Minimal Test Case

```bash
# Create test transcript
echo '{"role":"user","content":"Hello"}' > /tmp/test.jsonl
echo '{"role":"assistant","content":"Hi there!"}' >> /tmp/test.jsonl

# Enable hook
touch ~/.claude-voice/tts-hook-enabled

# Invoke hook
~/.claude-voice/hooks/stop_hook.sh /tmp/test.jsonl

# Expected: Hear "Hi there!" spoken aloud
# Expected: Exit code 0
```

### Edge Case Tests

1. **Disabled hook**:
   ```bash
   rm ~/.claude-voice/tts-hook-enabled
   ./stop_hook.sh /tmp/test.jsonl
   # Expected: No TTS, exit 0
   ```

2. **Missing file**:
   ```bash
   ./stop_hook.sh /nonexistent/file.jsonl
   # Expected: No TTS, exit 0
   ```

3. **Empty file**:
   ```bash
   touch /tmp/empty.jsonl
   ./stop_hook.sh /tmp/empty.jsonl
   # Expected: No TTS, exit 0
   ```

4. **Long response**:
   ```bash
   echo '{"role":"assistant","content":"'$(python3 -c 'print("word " * 100)')'"}' > /tmp/long.jsonl
   ./stop_hook.sh /tmp/long.jsonl
   # Expected: Hear summary (< 4 sentences)
   ```
