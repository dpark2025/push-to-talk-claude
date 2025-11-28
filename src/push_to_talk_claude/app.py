"""Main application orchestrator for push-to-talk voice interface."""

from typing import Optional
from pathlib import Path
from datetime import datetime
import signal
import sys
import logging
import threading

from .core.keyboard_monitor import KeyboardMonitor
from .core.audio_capture import AudioCapture
from .core.speech_to_text import SpeechToText
from .core.tmux_injector import TmuxInjector
from .core.focused_injector import FocusedInjector
from .core.recording_session import RecordingSessionManager, RecordingStatus
from .utils.config import Config
from .utils.sanitizer import InputSanitizer
from .utils.permissions import check_all_permissions, PermissionState
from .utils.session_detector import SessionDetector
from .ui.indicators import RecordingIndicator
from .ui.notifications import NotificationManager
from .ui.audio_feedback import AudioFeedback
from .ui.tui_app import PushToTalkTUI

logger = logging.getLogger(__name__)


class App:
    """Main application orchestrator for push-to-talk voice interface."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the application.

        Args:
            config: Configuration object, or None to load defaults
        """
        self.config = config or Config.load()
        self._running = False
        self._shutdown_requested = False

        # Validate config
        errors = self.config.validate()
        if errors:
            for error in errors:
                logger.error(f"Config error: {error}")
            raise ValueError(f"Invalid configuration: {errors[0]}")

        # Utilities
        self.sanitizer = InputSanitizer(self.config.security.max_input_length)
        self.session_detector = SessionDetector()

        # UI components
        self.indicator = RecordingIndicator()
        self.notifications = NotificationManager()
        self.audio_feedback = AudioFeedback(self.config.push_to_talk.audio_feedback)

        # TUI (initialized after session_manager is available)
        self.tui: Optional[PushToTalkTUI] = None
        self._use_tui = True  # Flag to enable/disable TUI mode

        # Core components (initialized later)
        self.keyboard_monitor: Optional[KeyboardMonitor] = None
        self.audio_capture: Optional[AudioCapture] = None
        self.speech_to_text: Optional[SpeechToText] = None
        self.injector = None  # FocusedInjector or TmuxInjector based on config
        self.session_manager: Optional[RecordingSessionManager] = None

    def _initialize_components(self) -> None:
        """Initialize all core components."""
        # Audio capture with defaults (16kHz mono for Whisper)
        self.audio_capture = AudioCapture()

        # Speech to text with config
        # Uses subprocess-based transcription to avoid FD conflicts with Textual TUI
        self.speech_to_text = SpeechToText(
            model_name=self.config.whisper.model,
            device=self.config.whisper.device,
            language=self.config.whisper.language
        )

        # Setup injector based on config
        if self.config.injection.mode == "focused":
            # Type into whatever window has focus
            self.injector = FocusedInjector()
        else:
            # Use tmux injection
            if self.config.tmux.session_name and not self.config.tmux.auto_detect:
                # Use explicit config
                self.injector = TmuxInjector(
                    session_name=self.config.tmux.session_name,
                    window_index=self.config.tmux.window_index,
                    pane_index=self.config.tmux.pane_index,
                    auto_detect=False
                )
            else:
                # Auto-detect Claude session
                claude_session = self.session_detector.get_best_target()
                if claude_session:
                    self.injector = TmuxInjector(
                        session_name=claude_session.session_name,
                        window_index=claude_session.window_index,
                        pane_index=claude_session.pane_index,
                        auto_detect=False
                    )
                else:
                    self.injector = TmuxInjector(auto_detect=True)

        # Recording session manager
        self.session_manager = RecordingSessionManager(
            audio_capture=self.audio_capture,
            speech_to_text=self.speech_to_text,
            tmux_injector=self.injector,  # Works with either FocusedInjector or TmuxInjector
            sanitizer=self.sanitizer,
            on_state_change=self._on_state_change,
            on_transcription=self._on_transcription,
            on_error=self._on_error,
            on_skipped=self._on_skipped
        )

        # Keyboard monitor
        self.keyboard_monitor = KeyboardMonitor(
            hotkey=self.config.push_to_talk.hotkey,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release
        )

        # Initialize TUI if enabled
        if self._use_tui:
            self.tui = PushToTalkTUI(
                config=self.config,
                session_manager=self.session_manager
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
            self.notifications.permission_error("Microphone")
            return False

        if permissions.accessibility != PermissionState.GRANTED:
            logger.error("Accessibility permission not granted")
            self.notifications.permission_error("Accessibility")
            return False

        # Check tmux requirements only if using tmux injection mode
        if self.config.injection.mode == "tmux":
            # Check tmux available
            if not TmuxInjector.is_tmux_available():
                logger.error("tmux not available")
                self.notifications.error("tmux is required but not installed. Run: brew install tmux")
                return False

            # Check for Claude session
            if not self.session_detector.is_tmux_running():
                logger.warning("tmux server not running")
                self.notifications.warning("tmux server not running. Start with: tmux new-session -s claude 'claude'")
                return False

            claude_session = self.session_detector.get_best_target()
            if not claude_session:
                logger.warning("No Claude session found")
                self.notifications.warning("No Claude Code session found. Start with: tmux new-session -s claude 'claude'")
                return False

            logger.info(f"Found Claude session: {claude_session.target_string}")
            if not self._use_tui:
                self.notifications.success(f"Found Claude session: {claude_session.target_string}")
        else:
            logger.info("Using focused injection mode (typing into active window)")

        logger.info("All prerequisites met")
        return True

    def start(self) -> None:
        """Start the voice interface."""
        if self._running:
            logger.warning("Application already running")
            return

        logger.info("Starting push-to-talk voice interface...")

        # Initialize components
        self._initialize_components()

        # Setup signal handlers
        self._setup_signal_handlers()

        # Start keyboard monitor
        self.keyboard_monitor.start()

        self._running = True

        # Show startup banner only in legacy (non-TUI) mode
        if not self._use_tui:
            self.notifications.startup_banner(
                hotkey=self.config.push_to_talk.hotkey,
                model=self.config.whisper.model,
                injection_mode=self.config.injection.mode
            )

    def stop(self) -> None:
        """Stop the voice interface and cleanup."""
        if not self._running:
            return

        logger.info("Stopping voice interface...")

        # Stop components
        if self.keyboard_monitor:
            self.keyboard_monitor.stop()

        if self.session_manager:
            self.session_manager.cancel()

        self._running = False

        # Show shutdown message only in legacy (non-TUI) mode
        if not self._use_tui:
            self.notifications.shutdown_message()

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

            # Run based on mode
            if self._use_tui and self.tui:
                # Textual TUI mode - run the TUI (blocking)
                self.tui.run()
            else:
                # Legacy mode - Block until interrupted
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
            self.notifications.error(f"Fatal error: {e}")
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

        # Route to TUI if available and running
        if self._use_tui and self.tui and self.tui.is_running:
            self.tui.handle_state_change(status)
        else:
            # Update indicator based on status (legacy mode)
            if status == RecordingStatus.RECORDING:
                self.indicator.show_recording()
            elif status == RecordingStatus.TRANSCRIBING:
                self.indicator.show_transcribing()
            elif status == RecordingStatus.INJECTING:
                self.indicator.show_injecting()
            elif status == RecordingStatus.COMPLETE:
                self.indicator.hide()
            elif status == RecordingStatus.ERROR:
                self.indicator.hide()

    def _on_transcription(self, text: str) -> None:
        """Handle completed transcription."""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Transcription received: {text}")

        if text and text.strip():
            # Route to TUI if available
            if self._use_tui and self.tui:
                self.tui.handle_transcription(text)
            else:
                self.indicator.show_complete(text)

            logger.info(f"Transcription: {text[:50]}...")

            # Save transcript if enabled
            if self.config.logging.save_transcripts:
                self._save_transcript(text)

    def _save_transcript(self, text: str) -> None:
        """Save transcription to file."""
        try:
            import time
            transcripts_dir = Path(self.config.logging.transcripts_dir)
            transcripts_dir.mkdir(parents=True, exist_ok=True)

            epoch_ms = int(time.time() * 1000)
            filename = transcripts_dir / f"transcript_{epoch_ms}.txt"

            with open(filename, 'w') as f:
                f.write(f"Timestamp: {epoch_ms}\n")
                f.write(f"Text: {text}\n")

            logger.debug(f"Transcript saved to {filename}")
        except Exception as e:
            logger.warning(f"Failed to save transcript: {e}")

    def _on_error(self, error: str) -> None:
        """Handle errors."""
        logger.error(f"Error: {error}")
        self.audio_feedback.play_error()

        # Route to TUI if available
        if self._use_tui and self.tui:
            self.tui.handle_error(error)
        else:
            self.notifications.error(error)
            self.indicator.show_error(error)

    def _on_skipped(self, reason: str) -> None:
        """Handle skipped recordings (too short, no speech, etc.)."""
        logger.debug(f"Recording skipped: {reason}")

        # Route to TUI if available
        if self._use_tui and self.tui:
            self.tui.handle_skipped(reason)
        else:
            self.indicator.show_skipped(reason)

    def _setup_signal_handlers(self) -> None:
        """Setup SIGINT/SIGTERM handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self._shutdown_requested = True
            self._running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
