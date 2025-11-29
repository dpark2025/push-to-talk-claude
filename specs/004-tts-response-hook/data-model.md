# Data Model: TTS Response Hook

**Feature**: 004-tts-response-hook
**Date**: 2025-11-28

## Entity Definitions

### 1. HookEvent

Represents a Claude Code Stop hook invocation.

**Fields**:
- `transcript_path: str` - Absolute path to JSONL transcript file provided by Claude Code
- `timestamp: datetime` - When hook was triggered

**Validation Rules**:
- `transcript_path` must be absolute path
- `transcript_path` file must exist and be readable
- `timestamp` auto-populated at creation

**State Transitions**: N/A (ephemeral, not persisted)

**Source**: Provided by Claude Code hook system as command-line argument

---

### 2. TranscriptMessage

Represents a single message in the Claude Code conversation transcript.

**Fields**:
- `role: str` - Message role ("user" or "assistant")
- `content: str` - Message text content
- `sequence: int` - Position in conversation (0-indexed)

**Validation Rules**:
- `role` must be "user" or "assistant"
- `content` may be empty string (valid for some Claude responses)
- `sequence` must be non-negative

**Relationships**:
- Part of ordered collection in Transcript

**Source**: Parsed from JSONL file, one JSON object per line

**Example**:
```json
{"role": "user", "content": "Implement user authentication"}
{"role": "assistant", "content": "I'll implement user authentication..."}
```

---

### 3. Transcript

Collection of messages representing full conversation history.

**Fields**:
- `messages: List[TranscriptMessage]` - Ordered list of conversation messages
- `last_assistant_message: Optional[TranscriptMessage]` - Most recent assistant response

**Validation Rules**:
- `messages` list may be empty (edge case: malformed transcript)
- `last_assistant_message` extracted from last message where `role == "assistant"`

**Methods**:
- `get_last_response() -> Optional[str]`: Returns content of last assistant message
- `parse_from_file(path: str) -> Transcript`: Static factory method

---

### 4. ResponseSummary

Result of summarizing a Claude response.

**Fields**:
- `original_text: str` - Full original response
- `summary_text: str` - Summarized version (if applicable)
- `word_count: int` - Word count of original
- `is_short: bool` - Whether response is under threshold (50 words)
- `speakable_text: str` - Final text to speak (original if short, summary if long)

**Validation Rules**:
- `summary_text` may be empty if `is_short == True`
- `speakable_text` never empty (if empty, response shouldn't trigger TTS)
- `word_count` computed as `len(original_text.split())`

**State Transitions**:
```
Original Response
  → word_count < 50 → is_short=True, speakable_text=original_text
  → word_count >= 50 → is_short=False, speakable_text=summary_text
```

---

### 5. HookConfiguration

Runtime configuration state for hook behavior (flag file representation).

**Fields**:
- `enabled: bool` - Whether hook should process responses
- `flag_file_path: Path` - Path to flag file (`~/.claude-voice/tts-hook-enabled`)

**Validation Rules**:
- `flag_file_path` must be in `~/.claude-voice/` directory
- `enabled` state determined by file existence (not file contents)

**Methods**:
- `is_enabled() -> bool`: Check if flag file exists
- `enable() -> None`: Create flag file (touch)
- `disable() -> None`: Delete flag file
- `toggle() -> bool`: Flip state, return new state

**State Transitions**:
```
Disabled (file absent)
  → toggle() → Enabled (file exists)

Enabled (file exists)
  → toggle() → Disabled (file deleted)
```

**File Format**: Empty file (presence is the signal, content ignored)

---

### 6. SummarizationStrategy

Defines how to extract key sentences from response.

**Fields**:
- `max_sentences: int` - Maximum sentences in summary (default: 4)
- `max_words: int` - Maximum words in summary (default: 100)
- `action_verbs: Set[str]` - Verbs indicating actions taken
- `outcome_indicators: Set[str]` - Words indicating results

**Validation Rules**:
- `max_sentences` between 2 and 10
- `max_words` between 50 and 200
- `action_verbs` and `outcome_indicators` non-empty

**Default Values**:
```python
action_verbs = {
    "implemented", "created", "added", "fixed", "updated",
    "removed", "deleted", "refactored", "optimized", "wrote"
}

outcome_indicators = {
    "complete", "ready", "success", "successful", "working",
    "failed", "error", "issue", "problem", "done"
}
```

**Methods**:
- `classify_sentence(sentence: str) -> SentenceType`: Determine sentence role
- `select_sentences(sentences: List[str]) -> List[str]`: Choose key sentences

---

### 7. TTSRequest

Request to speak text via macOS say command.

**Fields**:
- `text: str` - Text to speak
- `voice: Optional[str]` - Voice name (None = system default)
- `rate: int` - Speaking rate in WPM (100-400)
- `async_mode: bool` - Whether to wait for completion

**Validation Rules**:
- `text` must be non-empty
- `rate` between 100 and 400
- `voice` must be in available voices list if provided

**Source**: Constructed from ResponseSummary.speakable_text + TTSConfig

---

## Data Flow

### Hook Execution Flow

```
1. Claude Code triggers Stop hook
   → HookEvent created with transcript_path

2. Read transcript file
   → Parse JSONL into Transcript
   → Extract last_assistant_message

3. Check HookConfiguration
   → If disabled, exit early

4. Extract response content
   → Create ResponseSummary
   → Determine if short or long

5. Generate speakable text
   → If short: use original
   → If long: apply SummarizationStrategy

6. Create TTSRequest
   → Invoke say command
   → Log completion
```

### Toggle Flow

```
1. User presses toggle key in TUI
   → HookConfiguration.toggle() called

2. Check current state
   → HookConfiguration.is_enabled()

3. Flip state
   → If enabled: delete flag file
   → If disabled: create flag file

4. Update UI
   → Show notification
   → Update status indicator
```

## File Formats

### Flag File

**Path**: `~/.claude-voice/tts-hook-enabled`

**Format**: Empty file (0 bytes)

**Semantics**: File existence = enabled, file absence = disabled

**Example**:
```bash
# Enable
touch ~/.claude-voice/tts-hook-enabled

# Disable
rm ~/.claude-voice/tts-hook-enabled

# Check
[ -f ~/.claude-voice/tts-hook-enabled ] && echo "enabled"
```

---

### Transcript JSONL

**Path**: Provided by Claude Code (varies per session)

**Format**: JSONL (JSON Lines) - one JSON object per line

**Schema**:
```typescript
interface Message {
  role: "user" | "assistant";
  content: string;
}
```

**Example**:
```json
{"role":"user","content":"Create a new function"}
{"role":"assistant","content":"I'll create a new function for you.\n\n```python\ndef example():\n    pass\n```\n\nFunction created successfully."}
```

**Edge Cases**:
- Empty file: No messages to process
- Malformed JSON: Skip line, log error
- Missing fields: Treat as invalid message
- Only user messages: No assistant response to speak

---

### Hook Log (Debug Mode)

**Path**: `~/.claude-voice/hook.log`

**Format**: Plain text, one entry per line

**Schema**: `[timestamp] LEVEL: message`

**Example**:
```
[2025-11-28 14:32:15] INFO: Hook triggered for transcript /tmp/claude-abc123.jsonl
[2025-11-28 14:32:15] DEBUG: Extracted response: "I'll implement..."
[2025-11-28 14:32:15] INFO: Speaking summary (112 words → 4 sentences)
[2025-11-28 14:32:17] INFO: TTS completed successfully
```

**Rotation**: Manual cleanup (not auto-rotated in v1)

---

## Configuration Integration

### Existing TTSConfig (no changes needed)

```python
@dataclass
class TTSConfig:
    enabled: bool = True           # Global TTS enable (separate from hook toggle)
    voice: Optional[str] = None    # Used by hook when invoking say
    rate: int = 200                # Used by hook when invoking say
    max_length: int = 500          # Used by response parser
```

**Note**: `TTSConfig.enabled` controls TTS globally. Hook toggle is separate, runtime-only state.

---

## Validation Rules Summary

| Entity | Rule | Enforcement |
|--------|------|-------------|
| HookEvent | transcript_path must exist | Hook script checks with `[ -f "$path" ]` |
| TranscriptMessage | role must be "user" or "assistant" | jq filter `select(.role == "user" or .role == "assistant")` |
| Transcript | last_assistant_message may be None | Python: `messages[-1] if messages and messages[-1].role == "assistant" else None` |
| ResponseSummary | speakable_text never empty | Return None from summarizer if no content, skip TTS |
| HookConfiguration | flag_file_path in ~/.claude-voice/ | Hardcoded constant in both Python and bash |
| SummarizationStrategy | max_sentences 2-10 | Constructor validation with ValueError |
| TTSRequest | text non-empty | Checked before creating TTSRequest |

---

## Error Cases

| Scenario | Detection | Handling |
|----------|-----------|----------|
| Transcript file missing | `[ ! -f "$path" ]` | Exit 0, log error |
| Transcript malformed JSON | jq parse error | Skip line, continue |
| No assistant messages | `last_assistant_message == None` | Exit 0, no TTS |
| Empty response content | `content == ""` | Exit 0, no TTS |
| say command fails | Exit code != 0 | Log error, exit 0 |
| Flag file permission denied | `touch` fails | Log error, show notification |
| Summarizer timeout | Process timeout | Fallback to truncation |

All errors result in exit 0 to avoid disrupting Claude Code.
