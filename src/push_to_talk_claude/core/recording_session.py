"""Recording session state machine for push-to-talk interactions."""

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import numpy as np


class RecordingStatus(Enum):
    """Status of a recording session."""

    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    INJECTING = "injecting"
    COMPLETE = "complete"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class RecordingSession:
    """A single push-to-talk interaction."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime | None = None
    ended_at: datetime | None = None
    duration_ms: int = 0
    transcription: str | None = None
    status: RecordingStatus = RecordingStatus.IDLE
    error: str | None = None


class RecordingSessionManager:
    """Manages the lifecycle of recording sessions."""

    MAX_RECORDING_DURATION = 60.0  # seconds
    TRANSCRIPTION_TIMEOUT = 30.0  # seconds (needs time for model init on first run)
    MIN_RECORDING_DURATION = 0.3  # seconds - skip if shorter (accidental press)
    MIN_AUDIO_RMS = 0.01  # minimum RMS threshold - skip if quieter (no speech)

    def __init__(
        self,
        audio_capture,
        speech_to_text,
        tmux_injector,
        sanitizer,
        on_state_change: Callable[[RecordingStatus], None] | None = None,
        on_transcription: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
        on_skipped: Callable[[str], None] | None = None,
    ) -> None:
        """Initialize session manager with required components."""
        self._audio_capture = audio_capture
        self._speech_to_text = speech_to_text
        self._tmux_injector = tmux_injector
        self._sanitizer = sanitizer
        self._on_state_change = on_state_change
        self._on_transcription = on_transcription
        self._on_error = on_error
        self._on_skipped = on_skipped

        self._session: RecordingSession | None = None
        self._lock = threading.Lock()
        self._max_duration_timer: threading.Timer | None = None
        self._auto_return: bool = False

    @property
    def current_session(self) -> RecordingSession | None:
        """Get current session if any."""
        with self._lock:
            return self._session

    @property
    def status(self) -> RecordingStatus:
        """Get current status."""
        with self._lock:
            if self._session is None:
                return RecordingStatus.IDLE
            return self._session.status

    @property
    def auto_return(self) -> bool:
        """Get auto_return setting."""
        return self._auto_return

    @auto_return.setter
    def auto_return(self, value: bool) -> None:
        """Set auto_return setting."""
        self._auto_return = value

    def start_recording(self) -> None:
        """Start a new recording session. Called when hotkey pressed."""
        with self._lock:
            if self._session is not None and self._session.status == RecordingStatus.RECORDING:
                return

            self._session = RecordingSession(
                started_at=datetime.now(), status=RecordingStatus.RECORDING
            )

        self._audio_capture.start_recording()

        self._max_duration_timer = threading.Timer(
            self.MAX_RECORDING_DURATION, self._check_max_duration
        )
        self._max_duration_timer.start()

        self._notify_state_change(RecordingStatus.RECORDING)

    def stop_recording(self) -> None:
        """Stop recording and begin transcription. Called when hotkey released."""
        if self._max_duration_timer is not None:
            self._max_duration_timer.cancel()
            self._max_duration_timer = None

        audio = self._audio_capture.stop_recording()

        with self._lock:
            if self._session is None:
                return

            self._session.ended_at = datetime.now()
            if self._session.started_at:
                duration = (self._session.ended_at - self._session.started_at).total_seconds()
                self._session.duration_ms = int(duration * 1000)
            self._session.status = RecordingStatus.TRANSCRIBING

        self._notify_state_change(RecordingStatus.TRANSCRIBING)

        thread = threading.Thread(target=self._transcribe_and_inject, args=(audio,), daemon=True)
        thread.start()

    def cancel(self) -> None:
        """Cancel current session."""
        if self._max_duration_timer is not None:
            self._max_duration_timer.cancel()
            self._max_duration_timer = None

        self._audio_capture.cancel_recording()

        with self._lock:
            if self._session is None:
                return
            self._session.status = RecordingStatus.CANCELLED
            self._session.ended_at = datetime.now()

        self._notify_state_change(RecordingStatus.CANCELLED)

    def _transcribe_and_inject(self, audio) -> None:
        """Background task: transcribe audio and inject text."""
        try:
            # Check if audio is too short (accidental press)
            if len(audio) == 0:
                with self._lock:
                    if self._session:
                        self._session.status = RecordingStatus.COMPLETE
                self._notify_skipped("No audio captured")
                return

            duration = len(audio) / 16000  # Assuming 16kHz sample rate
            if duration < self.MIN_RECORDING_DURATION:
                with self._lock:
                    if self._session:
                        self._session.status = RecordingStatus.COMPLETE
                self._notify_skipped("Too short (accidental press?)")
                return

            # Check if audio is too quiet (no speech detected)
            rms = np.sqrt(np.mean(audio**2))
            if rms < self.MIN_AUDIO_RMS:
                with self._lock:
                    if self._session:
                        self._session.status = RecordingStatus.COMPLETE
                self._notify_skipped("No speech detected")
                return

            transcription_result = [None]
            transcription_error = [None]

            def transcribe():
                try:
                    result = self._speech_to_text.transcribe(audio)
                    text = result.text if hasattr(result, "text") else str(result)
                    transcription_result[0] = text
                except Exception as e:
                    transcription_error[0] = e

            transcribe_thread = threading.Thread(target=transcribe, daemon=True)
            transcribe_thread.start()
            transcribe_thread.join(timeout=self.TRANSCRIPTION_TIMEOUT)

            if transcribe_thread.is_alive():
                with self._lock:
                    if self._session:
                        self._session.status = RecordingStatus.TIMEOUT
                        self._session.error = "Transcription timeout"
                self._notify_state_change(RecordingStatus.TIMEOUT)
                if self._on_error:
                    self._on_error("Transcription timeout")
                return

            if transcription_error[0]:
                raise transcription_error[0]

            transcription = transcription_result[0]

            with self._lock:
                if self._session:
                    self._session.transcription = transcription

            if self._on_transcription:
                self._on_transcription(transcription)

            if not transcription or not transcription.strip():
                with self._lock:
                    if self._session:
                        self._session.status = RecordingStatus.COMPLETE
                self._notify_state_change(RecordingStatus.COMPLETE)
                return

            sanitized = self._sanitizer.sanitize(transcription)

            with self._lock:
                if self._session:
                    self._session.status = RecordingStatus.INJECTING
            self._notify_state_change(RecordingStatus.INJECTING)

            self._tmux_injector.inject_text(sanitized)

            # Send Enter keystroke if auto_return enabled and text was injected
            if self._auto_return and sanitized:
                time.sleep(0.1)  # Brief delay to ensure text is fully processed
                self._tmux_injector.send_enter()

            with self._lock:
                if self._session:
                    self._session.status = RecordingStatus.COMPLETE
            self._notify_state_change(RecordingStatus.COMPLETE)

        except Exception as e:
            error_msg = str(e)
            with self._lock:
                if self._session:
                    self._session.status = RecordingStatus.ERROR
                    self._session.error = error_msg
            self._notify_state_change(RecordingStatus.ERROR)
            if self._on_error:
                self._on_error(error_msg)

    def _check_max_duration(self) -> None:
        """Timer callback to enforce max recording duration."""
        self.stop_recording()

    def _notify_state_change(self, status: RecordingStatus) -> None:
        """Notify state change callback."""
        if self._on_state_change:
            self._on_state_change(status)

    def _notify_skipped(self, reason: str) -> None:
        """Notify skipped callback."""
        if self._on_skipped:
            self._on_skipped(reason)
