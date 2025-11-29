"""Summarizer for Claude responses using heuristic-based text extraction.

This module provides functionality to summarize long Claude responses by identifying
and extracting key action and outcome sentences.
"""

import re
import sys
from enum import Enum


class SentenceType(Enum):
    """Classification of sentence types based on content."""

    ACTION = "action"
    OUTCOME = "outcome"
    CONTEXT = "context"


class Summarizer:
    """Heuristic-based summarizer for Claude responses."""

    DEFAULT_ACTION_VERBS = {
        "implemented",
        "created",
        "added",
        "fixed",
        "updated",
        "removed",
        "deleted",
        "refactored",
        "optimized",
        "wrote",
        "built",
        "deployed",
        "tested",
        "validated",
        "enhanced",
    }

    DEFAULT_OUTCOME_INDICATORS = {
        "complete",
        "ready",
        "success",
        "successful",
        "working",
        "failed",
        "error",
        "issue",
        "problem",
        "done",
        "finished",
        "pass",
        "passes",
        "passing",
        "running",
    }

    def __init__(
        self,
        max_sentences: int = 4,
        max_words: int = 100,
        action_verbs: set[str] | None = None,
        outcome_indicators: set[str] | None = None,
    ) -> None:
        """Initialize summarizer with strategy parameters.

        Args:
            max_sentences: Maximum sentences in summary (2-10)
            max_words: Maximum words in summary (50-200)
            action_verbs: Words indicating actions taken (defaults provided)
            outcome_indicators: Words indicating results (defaults provided)

        Raises:
            ValueError: If max_sentences or max_words out of range
        """
        if max_sentences < 2 or max_sentences > 10:
            raise ValueError("max_sentences must be between 2 and 10")
        if max_words < 50 or max_words > 200:
            raise ValueError("max_words must be between 50 and 200")

        self.max_sentences = max_sentences
        self.max_words = max_words
        self.action_verbs = action_verbs or self.DEFAULT_ACTION_VERBS
        self.outcome_indicators = outcome_indicators or self.DEFAULT_OUTCOME_INDICATORS

    def summarize(self, text: str) -> str:
        """Summarize response text to key sentences.

        Args:
            text: Full Claude response text

        Returns:
            Summary text (2-4 sentences, max 100 words)
            Empty string if no meaningful content found

        Algorithm:
            1. Remove code blocks
            2. Split into sentences
            3. Classify each sentence (action/outcome/context)
            4. Select key sentences with priority order
            5. Join and return
        """
        if not text or not text.strip():
            return ""

        # Remove code blocks before processing
        cleaned_text = self._remove_code_blocks(text)
        if not cleaned_text.strip():
            return ""

        # Split into sentences
        sentences = self._split_sentences(cleaned_text)
        if not sentences:
            return ""

        # If already very short, return as-is
        word_count = len(cleaned_text.split())
        if word_count <= self.max_words and len(sentences) <= self.max_sentences:
            return cleaned_text.strip()

        # Classify all sentences
        classified = [(s, self.classify_sentence(s)) for s in sentences]

        # Group by type
        actions = [s for s, t in classified if t == SentenceType.ACTION]
        outcomes = [s for s, t in classified if t == SentenceType.OUTCOME]
        context = [s for s, t in classified if t == SentenceType.CONTEXT]

        # Select key sentences with priority order
        selected = []

        # Priority 1: First action sentence
        if actions:
            selected.append(actions[0])

        # Priority 2: Last outcome sentence
        if outcomes:
            selected.append(outcomes[-1])

        # Priority 3: Fill with context if needed
        remaining_slots = self.max_sentences - len(selected)
        if remaining_slots > 0 and context:
            if remaining_slots >= 2:
                # Add first and last context
                selected.append(context[0])
                if len(context) > 1:
                    selected.append(context[-1])
            elif remaining_slots == 1:
                # Add first context only
                selected.append(context[0])

        # Check word count and trim if needed
        summary = " ".join(selected)
        summary_words = summary.split()

        if len(summary_words) > self.max_words:
            # Trim from the end, keeping action and outcome sentences
            while len(selected) > 2 and len(" ".join(selected).split()) > self.max_words:
                selected.pop()

            # If still over limit, truncate words directly
            summary = " ".join(selected)
            summary_words = summary.split()
            if len(summary_words) > self.max_words:
                summary = " ".join(summary_words[: self.max_words])

        return summary.strip()

    def classify_sentence(self, sentence: str) -> SentenceType:
        """Classify sentence by type.

        Args:
            sentence: Single sentence to classify

        Returns:
            SentenceType indicating sentence role
        """
        sentence_lower = sentence.lower()

        # Check for action verbs with word boundaries
        for verb in self.action_verbs:
            pattern = r"\b" + re.escape(verb) + r"\b"
            if re.search(pattern, sentence_lower):
                return SentenceType.ACTION

        # Check for outcome indicators with word boundaries
        for indicator in self.outcome_indicators:
            pattern = r"\b" + re.escape(indicator) + r"\b"
            if re.search(pattern, sentence_lower):
                return SentenceType.OUTCOME

        # Default to context
        return SentenceType.CONTEXT

    def _remove_code_blocks(self, text: str) -> str:
        """Remove fenced code blocks from text.

        Args:
            text: Text potentially containing code blocks

        Returns:
            Text with code blocks removed
        """
        # Remove fenced code blocks (```...```)
        pattern = r"```[\s\S]*?```"
        return re.sub(pattern, "", text)

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Split on sentence boundaries: period, exclamation, question mark
        # followed by whitespace and capital letter
        pattern = r"[.!?]\s+(?=[A-Z])"
        sentences = re.split(pattern, text)

        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        # Handle case where last sentence doesn't end with punctuation
        if sentences and text.strip() and text.strip()[-1] not in ".!?":
            # Keep it as-is, it's already in the list
            pass

        return sentences


def summarize_response(text: str, max_sentences: int = 4, max_words: int = 100) -> str:
    """Summarize response text using default strategy.

    Args:
        text: Full Claude response text
        max_sentences: Maximum sentences in summary
        max_words: Maximum words in summary

    Returns:
        Summary text or empty string
    """
    summarizer = Summarizer(max_sentences=max_sentences, max_words=max_words)
    return summarizer.summarize(text)


def main():
    """CLI interface for summarizer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Summarize Claude response text using heuristic extraction"
    )
    parser.add_argument("text", nargs="?", help="Response text to summarize (or use --stdin)")
    parser.add_argument(
        "--max-sentences", type=int, default=4, help="Maximum sentences in summary (2-10)"
    )
    parser.add_argument(
        "--max-words", type=int, default=100, help="Maximum words in summary (50-200)"
    )
    parser.add_argument("--stdin", action="store_true", help="Read from stdin instead of argument")

    args = parser.parse_args()

    # Get input text
    if args.stdin:
        text = sys.stdin.read()
    elif args.text:
        text = args.text
    else:
        parser.error("Must provide text argument or use --stdin")

    # Summarize and output
    try:
        summary = summarize_response(text, args.max_sentences, args.max_words)
        print(summary)
        sys.exit(0)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
