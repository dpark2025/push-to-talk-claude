# Contract: Summarizer API

**Version**: 1.0.0
**Date**: 2025-11-28

## Overview

This contract defines the Python summarizer module interface for extracting key sentences from long Claude responses.

---

## Module Interface

### Module Path

```python
from push_to_talk_claude.hooks.summarizer import Summarizer, summarize_response
```

### CLI Interface

The summarizer must be callable from bash scripts:

```bash
python3 -m push_to_talk_claude.hooks.summarizer "response text here"
```

**Output**: Summary text to stdout (no formatting, plain text)

---

## Class: Summarizer

### Constructor

```python
class Summarizer:
    def __init__(
        self,
        max_sentences: int = 4,
        max_words: int = 100,
        action_verbs: Optional[Set[str]] = None,
        outcome_indicators: Optional[Set[str]] = None
    ) -> None:
        """
        Initialize summarizer with strategy parameters.

        Args:
            max_sentences: Maximum sentences in summary (2-10)
            max_words: Maximum words in summary (50-200)
            action_verbs: Words indicating actions taken (defaults provided)
            outcome_indicators: Words indicating results (defaults provided)

        Raises:
            ValueError: If max_sentences or max_words out of range
        """
```

**Default Action Verbs**:
```python
{
    "implemented", "created", "added", "fixed", "updated",
    "removed", "deleted", "refactored", "optimized", "wrote",
    "built", "deployed", "tested", "validated", "enhanced"
}
```

**Default Outcome Indicators**:
```python
{
    "complete", "ready", "success", "successful", "working",
    "failed", "error", "issue", "problem", "done",
    "finished", "passes", "works", "running"
}
```

### Methods

#### `summarize(text: str) -> str`

```python
def summarize(self, text: str) -> str:
    """
    Summarize response text to key sentences.

    Args:
        text: Full Claude response text

    Returns:
        Summary text (2-4 sentences, max 100 words)
        Empty string if no meaningful content found

    Algorithm:
        1. Split into sentences
        2. Classify each sentence (action/outcome/context)
        3. Select key sentences:
           - First action sentence (if any)
           - Last outcome sentence (if any)
           - Fill with context sentences
           - Respect max_sentences and max_words
        4. Join and return
    """
```

**Example**:
```python
summarizer = Summarizer()
response = """
I'll implement user authentication for your application.

First, I created the User model with email and password fields:

```python
class User(db.Model):
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))
```

Then I added password hashing using bcrypt and created login/logout routes.
The authentication system is now complete and all tests pass.
"""

summary = summarizer.summarize(response)
# Output: "Implemented user authentication for your application. Created the User model with email and password fields. Added password hashing using bcrypt and created login/logout routes. The authentication system is now complete and all tests pass."
# (4 sentences, ~35 words)
```

#### `classify_sentence(sentence: str) -> SentenceType`

```python
from enum import Enum

class SentenceType(Enum):
    ACTION = "action"       # Contains action verb
    OUTCOME = "outcome"     # Contains outcome indicator
    CONTEXT = "context"     # Everything else

def classify_sentence(self, sentence: str) -> SentenceType:
    """
    Classify sentence by type.

    Args:
        sentence: Single sentence to classify

    Returns:
        SentenceType indicating sentence role
    """
```

**Classification Logic**:
1. Check if sentence contains any action verb → ACTION
2. Check if sentence contains any outcome indicator → OUTCOME
3. Otherwise → CONTEXT

**Example**:
```python
summarizer = Summarizer()

summarizer.classify_sentence("I implemented the feature.")  # ACTION
summarizer.classify_sentence("All tests pass.")             # OUTCOME
summarizer.classify_sentence("Here's how it works.")        # CONTEXT
```

---

## Function: summarize_response

Convenience function for one-shot summarization:

```python
def summarize_response(
    text: str,
    max_sentences: int = 4,
    max_words: int = 100
) -> str:
    """
    Summarize response text using default strategy.

    Args:
        text: Full Claude response text
        max_sentences: Maximum sentences in summary
        max_words: Maximum words in summary

    Returns:
        Summary text or empty string
    """
    summarizer = Summarizer(max_sentences=max_sentences, max_words=max_words)
    return summarizer.summarize(text)
```

---

## CLI Interface Contract

### Command

```bash
python3 -m push_to_talk_claude.hooks.summarizer [OPTIONS] <text>
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `text` | string | Yes | Response text to summarize (positional or stdin) |

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--max-sentences` | 4 | Maximum sentences (2-10) |
| `--max-words` | 100 | Maximum words (50-200) |
| `--stdin` | False | Read from stdin instead of argument |

### Output

**Format**: Plain text summary to stdout

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid arguments or error |

### Examples

**Argument input**:
```bash
python3 -m push_to_talk_claude.hooks.summarizer "I implemented the feature. It works great. All tests pass."
# Output: "Implemented the feature. It works great. All tests pass."
```

**Stdin input**:
```bash
echo "Long response text..." | python3 -m push_to_talk_claude.hooks.summarizer --stdin
```

**Custom limits**:
```bash
python3 -m push_to_talk_claude.hooks.summarizer --max-sentences 2 --max-words 50 "text here"
```

---

## Text Processing Contract

### Sentence Splitting

**Method**: Regex-based splitting on sentence boundaries

**Pattern**: `[.!?]\\s+(?=[A-Z])`

**Edge Cases**:
| Input | Handling |
|-------|----------|
| Abbreviations (e.g., "Dr.") | May split incorrectly (acceptable for v1) |
| Code inline | Strip code before splitting |
| Multiple punctuation ("...") | Treat as single boundary |

**Example**:
```python
text = "I did this. Then that. Finally, success!"
sentences = split_sentences(text)
# ["I did this", "Then that", "Finally, success"]
```

### Code Block Removal

Before processing, remove fenced code blocks:

**Pattern**: ` ```[\\s\\S]*?``` `

**Example**:
```python
text = """
I created a function:

```python
def hello():
    pass
```

It works great.
"""

cleaned = remove_code_blocks(text)
# "I created a function:\n\nIt works great."
```

### Word Counting

**Method**: `len(text.split())`

**Notes**:
- Simple whitespace-based splitting
- Accurate enough for summary length checks
- Contractions count as one word ("don't" = 1 word)

---

## Selection Algorithm Contract

### Step 1: Classify All Sentences

```python
sentences = split_sentences(clean_text(text))
classified = [
    (sentence, classify_sentence(sentence))
    for sentence in sentences
]
```

### Step 2: Group by Type

```python
actions = [s for s, t in classified if t == SentenceType.ACTION]
outcomes = [s for s, t in classified if t == SentenceType.OUTCOME]
context = [s for s, t in classified if t == SentenceType.CONTEXT]
```

### Step 3: Select Key Sentences

**Priority Order**:
1. First action sentence (if available)
2. Last outcome sentence (if available)
3. First context sentence (if needed to fill)
4. Last context sentence (if needed to fill)

**Constraints**:
- Total sentences ≤ max_sentences
- Total words ≤ max_words

**Example Selection**:
```python
# Input: 10 sentences total
# - 3 action sentences
# - 2 outcome sentences
# - 5 context sentences

# max_sentences = 4
selected = [
    actions[0],      # First action
    outcomes[-1],    # Last outcome
    context[0],      # First context
    context[-1]      # Last context
]

# If total words > max_words:
#   Drop context[-1], then context[0], keep action/outcome
```

### Step 4: Join and Return

```python
summary = ' '.join(selected)
return summary
```

---

## Edge Cases

| Case | Input | Expected Output | Rationale |
|------|-------|-----------------|-----------|
| Empty text | `""` | `""` | Nothing to summarize |
| Only code | ` ```code``` ` | `""` | No natural language content |
| Single sentence | `"One sentence."` | `"One sentence."` | Already minimal |
| All context | No actions/outcomes | First + last sentences | Best available |
| Very short | Already < max_words | Original text | Don't expand |
| No sentence boundaries | Run-on text | Split on any punctuation | Graceful fallback |

---

## Performance Contract

### Latency Targets

| Input Size | Target | Notes |
|------------|--------|-------|
| < 100 words | < 10ms | Typical short response |
| 100-500 words | < 50ms | Typical long response |
| 500-1000 words | < 100ms | Very long response |

### Memory

- No caching (stateless per-call)
- Linear memory usage O(n) where n = text length
- No persistent data structures

### Scalability

Not a concern for this use case:
- Single response at a time
- Typical input: 100-500 words
- No concurrent requests

---

## Testing Contract

### Unit Tests

**Module**: `tests/hooks/test_summarizer.py`

**Required Test Cases**:

1. **Test sentence classification**:
   ```python
   def test_classify_action_sentence():
       s = Summarizer()
       assert s.classify_sentence("I implemented the feature") == SentenceType.ACTION

   def test_classify_outcome_sentence():
       s = Summarizer()
       assert s.classify_sentence("All tests pass") == SentenceType.OUTCOME
   ```

2. **Test summarization**:
   ```python
   def test_summarize_short_response():
       s = Summarizer()
       text = "This is short."
       assert s.summarize(text) == text

   def test_summarize_long_response():
       s = Summarizer()
       text = "I implemented feature X. " * 20  # 100 words
       summary = s.summarize(text)
       assert len(summary.split()) <= 100
       assert summary.count('.') <= 4
   ```

3. **Test edge cases**:
   ```python
   def test_empty_input():
       s = Summarizer()
       assert s.summarize("") == ""

   def test_code_only():
       s = Summarizer()
       assert s.summarize("```python\ncode\n```") == ""
   ```

### Integration Tests

**Module**: `tests/integration/test_hook_integration.py`

**Test CLI invocation**:
```python
def test_cli_summarizer():
    result = subprocess.run(
        ["python3", "-m", "push_to_talk_claude.hooks.summarizer", "text here"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert len(result.stdout.strip()) > 0
```

---

## Error Handling Contract

### Validation Errors

```python
# Invalid max_sentences
summarizer = Summarizer(max_sentences=1)  # Raises ValueError

# Invalid max_words
summarizer = Summarizer(max_words=10)  # Raises ValueError
```

### Runtime Errors

| Error | Cause | Handling |
|-------|-------|----------|
| Empty text | `text == ""` | Return empty string (not error) |
| Invalid UTF-8 | Encoding issue | Attempt decode, return empty on failure |
| Regex failure | Pathological input | Fallback to simple split on space |

**Principle**: Never crash, always return a string (may be empty)

---

## Versioning

### API Stability

**Stable APIs** (won't change):
- `Summarizer.__init__` signature
- `Summarizer.summarize()` signature
- `summarize_response()` signature
- CLI argument names

**Internal APIs** (may change):
- Sentence splitting implementation
- Classification heuristics
- Selection algorithm details

### Backwards Compatibility

v1.x releases will maintain:
- CLI interface compatibility
- Python function signatures
- Output format (plain text)

Breaking changes will increment major version (v2.0.0).
