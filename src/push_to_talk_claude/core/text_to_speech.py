import shutil
import subprocess
import threading


class TextToSpeech:
    """Convert text to speech using macOS say command."""

    def __init__(self, voice: str | None = None, rate: int = 200) -> None:
        """
        Initialize TTS engine.

        Args:
            voice: Voice name or None for system default
            rate: Speaking rate in words per minute (100-400)

        Raises:
            ValueError: If rate is out of range
            RuntimeError: If say command not available
        """
        if not self.is_available():
            raise RuntimeError("say command not available")

        if not 100 <= rate <= 400:
            raise ValueError(f"Rate must be between 100 and 400, got {rate}")

        self._voice = voice
        self._rate = rate
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()

    def speak(self, text: str, async_mode: bool = True) -> None:
        """
        Convert text to speech.

        Args:
            text: Text to speak
            async_mode: If True, return immediately (default)
        """
        # Stop any current speech
        self.stop()

        # Build command
        cmd = ["say", "-r", str(self._rate)]

        if self._voice:
            cmd.extend(["-v", self._voice])

        # Escape text for shell
        escaped_text = text.replace('"', '\\"')
        cmd.append(escaped_text)

        with self._lock:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
                start_new_session=True,
            )

        if not async_mode:
            self._process.wait()

    def stop(self) -> None:
        """Stop current speech immediately."""
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.terminate()
                self._process.wait()
                self._process = None

    @property
    def is_speaking(self) -> bool:
        """Whether currently speaking."""
        with self._lock:
            if self._process:
                return self._process.poll() is None
            return False

    @property
    def voice(self) -> str | None:
        """Current voice name."""
        return self._voice

    @property
    def rate(self) -> int:
        """Current speaking rate."""
        return self._rate

    @staticmethod
    def list_voices() -> list[str]:
        """List available macOS voices."""
        try:
            result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True)

            voices = []
            for line in result.stdout.strip().split("\n"):
                # Format: "Voice_Name language_code # description"
                parts = line.split()
                if parts:
                    voices.append(parts[0])

            return voices
        except subprocess.CalledProcessError:
            return []

    @staticmethod
    def is_available() -> bool:
        """Check if say command is available."""
        return shutil.which("say") is not None
