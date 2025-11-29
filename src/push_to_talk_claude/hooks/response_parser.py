"""Response parser for extracting speakable content from Claude responses."""

import re
from enum import Enum


class ResponseType(Enum):
    """Classification of Claude response types."""

    CONVERSATIONAL = "conversational"
    CODE_BLOCK = "code_block"
    COMMAND_OUTPUT = "command_output"
    MIXED = "mixed"
    TOO_LONG = "too_long"


class ResponseParser:
    """Parse Claude responses to extract speakable content."""

    # Patterns that indicate code/command output
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")
    COMMAND_OUTPUT_INDICATORS = [
        r"^\$\s",  # Shell prompt
        r"^>\s",  # REPL prompt
        r"^#\s",  # Comment or root prompt
        r"^File created:",
        r"^Running:",
        r"^Error:",
        r"^Warning:",
        r"^\[\d+\]",  # Line numbers
    ]

    # Patterns that indicate conversational text
    CONVERSATIONAL_STARTERS = [
        r"^I'll\s",
        r"^I can\s",
        r"^I've\s",
        r"^Let me\s",
        r"^Here's\s",
        r"^This\s",
        r"^The\s",
        r"^You\s",
        r"^Sure",
        r"^Yes",
        r"^No,?\s",
        r"^Okay",
    ]

    def __init__(self, max_length: int = 500) -> None:
        """Initialize parser with max length for TTS."""
        self.max_length = max_length
        self._command_output_regex = re.compile(
            "|".join(self.COMMAND_OUTPUT_INDICATORS), re.MULTILINE
        )
        self._conversational_regex = re.compile(
            "|".join(self.CONVERSATIONAL_STARTERS), re.IGNORECASE
        )

    def classify(self, text: str) -> ResponseType:
        """Classify response type."""
        if not text or not text.strip():
            return ResponseType.CONVERSATIONAL

        # Count code blocks
        code_blocks = self.CODE_BLOCK_PATTERN.findall(text)
        code_block_chars = sum(len(block) for block in code_blocks)
        total_chars = len(text)

        # If >50% is code blocks
        if total_chars > 0 and code_block_chars / total_chars > 0.5:
            return ResponseType.CODE_BLOCK

        # Remove code blocks to analyze remaining content
        text_without_code = self._remove_code_blocks(text)
        lines = [line for line in text_without_code.split("\n") if line.strip()]

        if not lines:
            return ResponseType.CODE_BLOCK

        # Count command output lines
        command_output_lines = sum(
            1 for line in lines if self._command_output_regex.match(line.strip())
        )

        # Count conversational lines
        conversational_lines = sum(1 for line in lines if self._is_conversational(line.strip()))

        total_lines = len(lines)
        command_ratio = command_output_lines / total_lines if total_lines > 0 else 0
        conversational_ratio = conversational_lines / total_lines if total_lines > 0 else 0

        # Determine type based on ratios
        if command_ratio > 0.6:
            return ResponseType.COMMAND_OUTPUT
        elif conversational_ratio > 0.3 and command_ratio > 0.1:
            return ResponseType.MIXED
        elif conversational_ratio > 0.3 or self._is_conversational(text_without_code):
            # Check if too long after extraction
            speakable = self.extract_speakable(text)
            if speakable and len(speakable) > self.max_length:
                return ResponseType.TOO_LONG
            return ResponseType.CONVERSATIONAL
        elif command_ratio > 0:
            return ResponseType.MIXED
        else:
            # Default to conversational if unclear
            speakable = self.extract_speakable(text)
            if speakable and len(speakable) > self.max_length:
                return ResponseType.TOO_LONG
            return ResponseType.CONVERSATIONAL

    def extract_speakable(self, text: str) -> str | None:
        """
        Extract text suitable for TTS.

        - Removes code blocks
        - Removes command output lines
        - Truncates to max_length
        - Returns None if nothing suitable found
        """
        if not text or not text.strip():
            return None

        # Remove code blocks
        text = self._remove_code_blocks(text)

        # Remove command output lines
        text = self._remove_command_output(text)

        # Clean up whitespace
        text = text.strip()

        if not text:
            return None

        # Truncate to max length
        if len(text) > self.max_length:
            # Try to truncate at sentence boundary
            truncated = text[: self.max_length]
            last_period = truncated.rfind(".")
            last_exclamation = truncated.rfind("!")
            last_question = truncated.rfind("?")
            last_sentence = max(last_period, last_exclamation, last_question)

            if last_sentence > self.max_length * 0.7:
                text = truncated[: last_sentence + 1]
            else:
                # No good sentence boundary, just truncate with ellipsis
                text = truncated.rstrip() + "..."

        return text if text else None

    def should_speak(self, text: str) -> bool:
        """Determine if response should trigger TTS."""
        response_type = self.classify(text)

        # Don't speak code blocks or command output
        if response_type in (ResponseType.CODE_BLOCK, ResponseType.COMMAND_OUTPUT):
            return False

        # For conversational or mixed, check if we can extract something
        speakable = self.extract_speakable(text)
        return speakable is not None and len(speakable.strip()) > 0

    def _remove_code_blocks(self, text: str) -> str:
        """Remove fenced code blocks from text."""
        return self.CODE_BLOCK_PATTERN.sub("", text)

    def _remove_command_output(self, text: str) -> str:
        """Remove lines that look like command output."""
        lines = text.split("\n")
        filtered_lines = []

        for line in lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                continue
            # Skip lines matching command output patterns
            if self._command_output_regex.match(stripped):
                continue
            filtered_lines.append(line)

        return "\n".join(filtered_lines)

    def _is_conversational(self, text: str) -> bool:
        """Check if text appears conversational."""
        if not text or not text.strip():
            return False

        # Check if starts with conversational pattern
        first_line = text.strip().split("\n")[0]
        if self._conversational_regex.match(first_line):
            return True

        # Check for sentence-like structure (contains proper punctuation)
        has_sentence_endings = bool(re.search(r"[.!?]\s", text))
        has_common_words = bool(
            re.search(
                r"\b(the|a|an|is|are|was|were|have|has|will|would|can|could)\b", text, re.IGNORECASE
            )
        )

        return has_sentence_endings and has_common_words
