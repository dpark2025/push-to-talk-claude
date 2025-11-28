from typing import Optional, Callable
from pathlib import Path
import json
import logging

from .response_parser import ResponseParser, ResponseType
from ..core.text_to_speech import TextToSpeech

logger = logging.getLogger(__name__)

class HookHandler:
    """Handle Claude Code hook events for TTS."""

    def __init__(
        self,
        tts: TextToSpeech,
        parser: ResponseParser,
        enabled: bool = True,
        on_speak: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Initialize hook handler.

        Args:
            tts: TextToSpeech instance
            parser: ResponseParser instance
            enabled: Whether TTS is enabled
            on_speak: Callback when text is spoken
        """
        self._tts = tts
        self._parser = parser
        self._enabled = enabled
        self._on_speak = on_speak

    def handle_hook_event(self, event_data: dict) -> None:
        """
        Handle incoming hook event from Claude Code.

        Args:
            event_data: JSON payload from hook
        """
        try:
            response_text = event_data.get("response", "")
            if response_text:
                self.handle_response(response_text)
        except Exception as e:
            logger.error(f"Error handling hook event: {e}")

    def handle_response(self, response_text: str) -> None:
        """
        Process a Claude response for TTS.

        Args:
            response_text: Raw response text from Claude
        """
        if not self._enabled:
            return

        # Stop current speech if any
        self.stop_speaking()

        # Parse response to extract speakable text
        response_type = self._parser.classify_response(response_text)
        speakable_text = self._parser.extract_speakable(response_text, response_type)

        if speakable_text:
            logger.debug(f"Speaking: {speakable_text[:100]}...")
            self._tts.speak(speakable_text)

            if self._on_speak:
                self._on_speak(speakable_text)

    def stop_speaking(self) -> None:
        """Stop any current speech."""
        self._tts.stop()

    @property
    def is_enabled(self) -> bool:
        """Whether TTS is enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable TTS."""
        self._enabled = True

    def disable(self) -> None:
        """Disable TTS."""
        self._enabled = False
        self.stop_speaking()
