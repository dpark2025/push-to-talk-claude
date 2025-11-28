"""Focused window injector - types text into whatever window has focus."""

from pynput.keyboard import Controller
import time


class FocusedInjector:
    """Inject text by typing into the currently focused window."""

    def __init__(self, typing_delay: float = 0.0) -> None:
        """
        Initialize focused injector.

        Args:
            typing_delay: Delay between keystrokes in seconds (0 for fastest)
        """
        self._keyboard = Controller()
        self._typing_delay = typing_delay

    def inject_text(self, text: str) -> bool:
        """
        Type text into the currently focused window.

        Args:
            text: Text to type (should already be sanitized)

        Returns:
            True if injection succeeded

        Raises:
            ValueError: If text is empty
        """
        if not text:
            raise ValueError("Text cannot be empty")

        try:
            if self._typing_delay > 0:
                for char in text:
                    self._keyboard.type(char)
                    time.sleep(self._typing_delay)
            else:
                self._keyboard.type(text)
            return True
        except Exception:
            return False

    @staticmethod
    def is_available() -> bool:
        """Check if focused injection is available (always true on macOS)."""
        return True
