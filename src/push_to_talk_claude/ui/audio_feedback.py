"""Audio feedback for push-to-talk events."""

import subprocess
import threading


class AudioFeedback:
    """Provide audio feedback using macOS system sounds."""

    # macOS system sounds (in /System/Library/Sounds/)
    SOUND_START = "Tink"  # Light tap for recording start
    SOUND_STOP = "Pop"  # Pop for recording stop
    SOUND_ERROR = "Basso"  # Bass tone for errors
    SOUND_SUCCESS = "Glass"  # Glass sound for success

    def __init__(self, enabled: bool = True) -> None:
        """
        Initialize audio feedback.

        Args:
            enabled: Whether audio feedback is enabled
        """
        self._enabled = enabled
        self._current_process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    @property
    def enabled(self) -> bool:
        """Whether audio feedback is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable audio feedback."""
        self._enabled = value

    def play_start(self) -> None:
        """Play sound for recording start."""
        self._play_sound(self.SOUND_START)

    def play_stop(self) -> None:
        """Play sound for recording stop."""
        self._play_sound(self.SOUND_STOP)

    def play_error(self) -> None:
        """Play sound for error."""
        self._play_sound(self.SOUND_ERROR)

    def play_success(self) -> None:
        """Play sound for success."""
        self._play_sound(self.SOUND_SUCCESS)

    def _play_sound(self, sound_name: str) -> None:
        """
        Play a macOS system sound.

        Args:
            sound_name: Name of sound in /System/Library/Sounds/
        """
        if not self._enabled:
            return

        # Use afplay for playing system sounds
        sound_path = f"/System/Library/Sounds/{sound_name}.aiff"

        with self._lock:
            # Run async so we don't block
            # Use close_fds and start_new_session to prevent FD conflicts with Textual TUI
            try:
                self._current_process = subprocess.Popen(
                    ["afplay", sound_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    start_new_session=True,
                )
            except FileNotFoundError:
                # afplay not available, silently skip
                pass

    def stop(self) -> None:
        """Stop any currently playing sound."""
        with self._lock:
            if self._current_process is not None:
                try:
                    self._current_process.terminate()
                except ProcessLookupError:
                    pass
                self._current_process = None
