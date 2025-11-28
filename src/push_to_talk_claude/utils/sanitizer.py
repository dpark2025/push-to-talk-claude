"""Input sanitization for tmux injection safety."""

import re


class InputSanitizer:
    """Sanitize user input before injection."""

    # Characters that must be escaped for shell/tmux
    SHELL_METACHARACTERS: str = "$`\\\"'|&;><(){}[]!*?~#"

    def __init__(self, max_length: int = 500, escape_shell: bool = True) -> None:
        """Initialize sanitizer with max length.

        Args:
            max_length: Maximum allowed length of sanitized text.
            escape_shell: Whether to escape shell metacharacters (True for tmux, False for focused mode).
        """
        self.max_length = max_length
        self.escape_shell = escape_shell
        self._ansi_pattern = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')

    def sanitize(self, text: str) -> str:
        """
        Clean and validate input text.

        Steps:
        1. Remove ANSI escape sequences
        2. Replace newlines with spaces
        3. Escape shell metacharacters
        4. Truncate to max_length
        5. Strip leading/trailing whitespace

        Args:
            text: Input text to sanitize.

        Returns:
            Sanitized text safe for tmux injection.
        """
        if text is None or not text.strip():
            return ""

        # Step 1: Remove ANSI escape sequences
        result = self._ansi_pattern.sub('', text)

        # Step 2: Replace newlines with spaces
        result = result.replace('\n', ' ').replace('\r', ' ')

        # Step 3: Escape shell metacharacters (only for tmux mode)
        if self.escape_shell:
            for char in self.SHELL_METACHARACTERS:
                result = result.replace(char, f'\\{char}')

        # Step 4: Truncate to max_length
        result = result[:self.max_length]

        # Step 5: Strip leading/trailing whitespace
        result = result.strip()

        return result

    def is_safe(self, text: str) -> bool:
        """Check if text is safe without modifying.

        Args:
            text: Input text to check.

        Returns:
            True if text equals its sanitized version, False otherwise.
        """
        return text == self.sanitize(text)
