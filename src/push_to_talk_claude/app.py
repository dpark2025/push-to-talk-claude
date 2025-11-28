"""Main application orchestrator for push-to-talk voice interface."""

from typing import Optional
import signal
import sys
import logging

from .core.keyboard_monitor import KeyboardMonitor
from .core.audio_capture import AudioCapture
from .core.speech_to_text import SpeechToText
from .core.tmux_injector import TmuxInjector
from .core.recording_session import RecordingSessionManager, RecordingStatus
from .utils.config import Config
from .utils.sanitizer import InputSanitizer
from .utils.permissions import check_all_permissions, PermissionState
from .utils.session_detector import SessionDetector
from .ui.indicators import RecordingIndicator
from .ui.notifications import NotificationManager
from .ui.audio_feedback import AudioFeedback

logger = logging.getLogger(__name__)


class App:
    """Main application orchestrator for push-to-talk voice interface."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the application.

        Args:
            config: Configuration object, or None to load defaults
        """
        self.config = config or Config.load_default()
        self._running = False
        self._shutdown_requested = False

        # Core components
        self.keyboard_monitor: Optional[KeyboardMonitor] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.speech_to_text: Optional[SpeechToText] = None
        self.tmux_injector: Optional[TmuxInjector] = None
        self.session_manager: Optional[RecordingSessionManager] = None

        # Utilities
        self.sanitizer = InputSanitizer(self.config.sanitizer)
        self.session_detector = SessionDetector()

        # UI components
        self.indicator = RecordingIndicator(self.config.ui)
        self.notifications = NotificationManager(self.config.ui)
        self.audio_feedback = AudioFeedback(self.config.push_to_talk.audio_feedback)

        # Create core components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize all core components."""
        # Audio capture
        self.audio_capture = AudioCapture(
            device_index=self.config.audio.device_index,
            sample_rate=self.config.audio.sample_rate,
            channels=self.config.audio.channels,
            chunk_size=self.config.audio.chunk_size
        )

        # Speech to text
        self.speech_to_text = SpeechToText(self.config.transcription)

        # Tmux injector (session will be set later)
        self.tmux_injector = TmuxInjector(session_name="")

        # Recording session manager
        self.session_manager = RecordingSessionManager(
            audio_capture=self.audio_capture,
            speech_to_text=self.speech_to_text,
            on_state_change=self._on_state_change,
            on_transcription=self._on_transcription,
            on_error=self._on_error
        )

        # Keyboard monitor
        self.keyboard_monitor = KeyboardMonitor(
            hotkey=self.config.hotkey.key,
            modifiers=self.config.hotkey.modifiers,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release
        )

    def check_prerequisites(self) -> bool:
        """
        Check all prerequisites before starting.

        Returns:
            True if all prerequisites met, False otherwise
        """
        logger.info("Checking prerequisites...")

        # Check permissions
        permissions = check_all_permissions()

        if permissions.microphone != PermissionState.GRANTED:
            logger.error("Microphone permission not granted")
            self.notifications.show_error("Microphone permission required")
            return False

        if permissions.accessibility != PermissionState.GRANTED:
            logger.error("Accessibility permission not granted")
            self.notifications.show_error("Accessibility permission required for keyboard monitoring")
            return False

        # Check tmux available
        if not self.tmux_injector.is_tmux_available():
            logger.error("tmux not available")
            self.notifications.show_error("tmux is required but not available")
            return False

        # Find Claude session
        session_info = self.session_detector.find_claude_session()
        if not session_info:
            logger.error("No Claude session found")
            self.notifications.show_error("No active Claude Code session found in tmux")
            return False

        # Configure tmux injector with found session
        self.tmux_injector.session_name = session_info.session_name
        logger.info(f"Found Claude session: {session_info.session_name} (pane: {session_info.pane_id})")

        logger.info("All prerequisites met")
        return True

    def start(self) -> None:
        """Start the voice interface."""
        if self._running:
            logger.warning("Application already running")
            return

        logger.info("Starting push-to-talk voice interface...")

        # Setup signal handlers
        self._setup_signal_handlers()

        # Start keyboard monitor
        self.keyboard_monitor.start()

        self._running = True

        # Show startup banner
        hotkey_display = "+".join(self.config.hotkey.modifiers + [self.config.hotkey.key])
        print("\n" + "=" * 60)
        print("Push-to-Talk Voice Interface for Claude Code")
        print("=" * 60)
        print(f"Hotkey: {hotkey_display}")
        print(f"Session: {self.tmux_injector.session_name}")
        print(f"Transcription: {self.config.transcription.provider}")
        print("\nPress and hold the hotkey to record voice input")
        print("Press Ctrl+C to exit")
        print("=" * 60 + "\n")

        self.notifications.show_info("Voice interface started")

    def stop(self) -> None:
        """Stop the voice interface and cleanup."""
        if not self._running:
            return

        logger.info("Stopping voice interface...")

        # Stop components
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()

        if self.session_manager and self.session_manager.is_recording:
            self.session_manager.stop_recording()

        self._running = False

        # Show shutdown message
        print("\n" + "=" * 60)
        print("Voice interface stopped")
        print("=" * 60 + "\n")

        self.notifications.show_info("Voice interface stopped")

    def run(self) -> int:
        """
        Run the application (blocking).

        Returns:
            Exit code (0 for success)
        """
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return 1

            # Start the application
            self.start()

            # Block until interrupted
            while self._running and not self._shutdown_requested:
                try:
                    signal.pause()
                except AttributeError:
                    # signal.pause() not available on Windows
                    import time
                    time.sleep(0.1)

            return 0

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            return 0
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.notifications.show_error(f"Fatal error: {e}")
            return 1
        finally:
            self.stop()

    def _on_hotkey_press(self) -> None:
        """Handle hotkey press event."""
        if not self._running:
            return

        logger.debug("Hotkey pressed")
        self.audio_feedback.play_start()

        try:
            self.session_manager.start_recording()
        except Exception as e:
            logger.error(f"Error starting recording: {e}", exc_info=True)
            self._on_error(f"Failed to start recording: {e}")

    def _on_hotkey_release(self) -> None:
        """Handle hotkey release event."""
        if not self._running:
            return

        logger.debug("Hotkey released")
        self.audio_feedback.play_stop()

        try:
            self.session_manager.stop_recording()
        except Exception as e:
            logger.error(f"Error stopping recording: {e}", exc_info=True)
            self._on_error(f"Failed to stop recording: {e}")

    def _on_state_change(self, status: RecordingStatus) -> None:
        """Handle recording state changes."""
        logger.debug(f"Recording state changed: {status}")

        # Update indicator based on status
        if status == RecordingStatus.RECORDING:
            self.indicator.show_recording()
        elif status == RecordingStatus.PROCESSING:
            self.indicator.show_processing()
        elif status == RecordingStatus.IDLE:
            self.indicator.hide()

    def _on_transcription(self, text: str) -> None:
        """Handle completed transcription."""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Transcription received: {text}")

        # Sanitize the input
        sanitized = self.sanitizer.sanitize(text)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Sanitized text: {sanitized}")

        # Update indicator to show success
        self.indicator.show_success()

        # Inject into tmux
        try:
            self.tmux_injector.inject_text(sanitized)
            logger.info("Text injected successfully")
            self.notifications.show_success("Voice input sent")
        except Exception as e:
            logger.error(f"Error injecting text: {e}", exc_info=True)
            self._on_error(f"Failed to inject text: {e}")

    def _on_error(self, error: str) -> None:
        """Handle errors."""
        logger.error(f"Error: {error}")
        self.audio_feedback.play_error()
        self.notifications.show_error(error)
        self.indicator.show_error()

    def _setup_signal_handlers(self) -> None:
        """Setup SIGINT/SIGTERM handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self._shutdown_requested = True
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
