"""Unit tests for the summarizer module."""

import pytest

from push_to_talk_claude.hooks.summarizer import SentenceType, Summarizer, summarize_response


class TestSentenceClassification:
    """Test sentence classification logic."""

    def test_classify_action_sentence(self):
        """Test that action verbs are correctly identified."""
        s = Summarizer()
        assert s.classify_sentence("I implemented the feature") == SentenceType.ACTION

    def test_classify_outcome_sentence(self):
        """Test that outcome indicators are correctly identified."""
        s = Summarizer()
        assert s.classify_sentence("All tests pass") == SentenceType.OUTCOME

    def test_classify_context_sentence(self):
        """Test that context sentences are correctly identified."""
        s = Summarizer()
        assert s.classify_sentence("Here's how it works") == SentenceType.CONTEXT

    def test_action_verb_variations(self):
        """Test various action verbs."""
        s = Summarizer()
        action_sentences = [
            "I created a new module",
            "Updated the configuration",
            "Fixed the bug in the parser",
            "Added error handling",
            "Removed deprecated code",
        ]
        for sentence in action_sentences:
            assert s.classify_sentence(sentence) == SentenceType.ACTION

    def test_outcome_indicator_variations(self):
        """Test various outcome indicators."""
        s = Summarizer()
        outcome_sentences = [
            "The feature is complete",
            "All tests are passing",
            "The build was successful",
            "Everything is working now",
            "The task is done",
        ]
        for sentence in outcome_sentences:
            assert s.classify_sentence(sentence) == SentenceType.OUTCOME


class TestSummarization:
    """Test summarization logic."""

    def test_summarize_short_response(self):
        """Test that short responses are returned as-is."""
        s = Summarizer()
        text = "This is short."
        assert s.summarize(text) == text

    def test_summarize_empty_input(self):
        """Test that empty input returns empty string."""
        s = Summarizer()
        assert s.summarize("") == ""
        assert s.summarize("   ") == ""

    def test_summarize_code_only(self):
        """Test that code-only input returns empty string."""
        s = Summarizer()
        text = "```python\ndef hello():\n    pass\n```"
        assert s.summarize(text) == ""

    def test_summarize_long_response(self):
        """Test that long responses are summarized."""
        s = Summarizer()
        text = "I implemented feature X. " * 20  # 100 words
        summary = s.summarize(text)
        assert len(summary.split()) <= 100
        assert summary.count(".") <= 4

    def test_summarize_with_code_blocks(self):
        """Test that code blocks are removed before summarization."""
        s = Summarizer()
        text = """
I created a function:

```python
def hello():
    pass
```

It works great.
"""
        summary = s.summarize(text)
        assert "```" not in summary
        assert "python" not in summary
        assert "created" in summary.lower() or "works" in summary.lower()

    def test_summarize_respects_max_sentences(self):
        """Test that summary respects max_sentences limit."""
        s = Summarizer(max_sentences=2, max_words=100)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        summary = s.summarize(text)
        # Should have at most 2 sentences
        assert summary.count(".") <= 2

    def test_summarize_respects_max_words(self):
        """Test that summary respects max_words limit."""
        s = Summarizer(max_sentences=10, max_words=50)
        text = " ".join(["word"] * 100) + "."
        summary = s.summarize(text)
        assert len(summary.split()) <= 50

    def test_summarize_prioritizes_action_and_outcome(self):
        """Test that action and outcome sentences are prioritized."""
        s = Summarizer(max_sentences=2, max_words=100)
        text = "Some context. I implemented the feature. More context. All tests pass."
        summary = s.summarize(text)
        # Should contain the action and outcome sentences
        assert "implemented" in summary.lower()
        assert "pass" in summary.lower()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_max_sentences_low(self):
        """Test that invalid max_sentences raises ValueError."""
        with pytest.raises(ValueError):
            Summarizer(max_sentences=1)

    def test_invalid_max_sentences_high(self):
        """Test that invalid max_sentences raises ValueError."""
        with pytest.raises(ValueError):
            Summarizer(max_sentences=11)

    def test_invalid_max_words_low(self):
        """Test that invalid max_words raises ValueError."""
        with pytest.raises(ValueError):
            Summarizer(max_words=10)

    def test_invalid_max_words_high(self):
        """Test that invalid max_words raises ValueError."""
        with pytest.raises(ValueError):
            Summarizer(max_words=300)

    def test_single_sentence(self):
        """Test single sentence input."""
        s = Summarizer()
        text = "One sentence."
        assert s.summarize(text) == text

    def test_no_sentence_boundaries(self):
        """Test text without clear sentence boundaries."""
        s = Summarizer()
        text = "run-on text without proper punctuation"
        # Should still return something
        summary = s.summarize(text)
        assert isinstance(summary, str)

    def test_mixed_content(self):
        """Test text with mixed action, outcome, and context."""
        s = Summarizer()
        text = """
Here's some context about the problem.
I implemented a solution using Python.
The code handles edge cases properly.
All tests pass successfully.
You can now use the feature.
"""
        summary = s.summarize(text)
        assert len(summary) > 0
        assert len(summary.split()) <= 100


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_summarize_response_default_params(self):
        """Test summarize_response with default parameters."""
        text = "I fixed the bug. Everything works now."
        summary = summarize_response(text)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summarize_response_custom_params(self):
        """Test summarize_response with custom parameters."""
        text = "First. Second. Third. Fourth. Fifth."
        summary = summarize_response(text, max_sentences=2, max_words=50)
        assert summary.count(".") <= 2


class TestCodeBlockRemoval:
    """Test code block removal utility."""

    def test_remove_single_code_block(self):
        """Test removal of single code block."""
        s = Summarizer()
        text = "Before\n```code\nblock\n```\nAfter"
        cleaned = s._remove_code_blocks(text)
        assert "```" not in cleaned
        assert "Before" in cleaned
        assert "After" in cleaned

    def test_remove_multiple_code_blocks(self):
        """Test removal of multiple code blocks."""
        s = Summarizer()
        text = "Text\n```block1```\nMore\n```block2```\nEnd"
        cleaned = s._remove_code_blocks(text)
        assert "```" not in cleaned
        assert "Text" in cleaned
        assert "More" in cleaned
        assert "End" in cleaned

    def test_remove_code_block_with_language(self):
        """Test removal of code block with language specifier."""
        s = Summarizer()
        text = "Text\n```python\ndef foo():\n    pass\n```\nAfter"
        cleaned = s._remove_code_blocks(text)
        assert "```" not in cleaned
        assert "python" not in cleaned
        assert "def foo" not in cleaned


class TestSentenceSplitting:
    """Test sentence splitting logic."""

    def test_split_simple_sentences(self):
        """Test splitting simple sentences."""
        s = Summarizer()
        text = "First sentence. Second sentence. Third sentence."
        sentences = s._split_sentences(text)
        assert len(sentences) == 3

    def test_split_with_exclamation(self):
        """Test splitting with exclamation marks."""
        s = Summarizer()
        text = "First! Second! Third!"
        sentences = s._split_sentences(text)
        assert len(sentences) >= 1

    def test_split_with_question(self):
        """Test splitting with question marks."""
        s = Summarizer()
        text = "First? Second? Third?"
        sentences = s._split_sentences(text)
        assert len(sentences) >= 1

    def test_split_mixed_punctuation(self):
        """Test splitting with mixed punctuation."""
        s = Summarizer()
        text = "First. Second! Third? Fourth."
        sentences = s._split_sentences(text)
        assert len(sentences) >= 1
