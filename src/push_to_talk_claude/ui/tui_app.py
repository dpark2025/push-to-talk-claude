"""PushToTalkTUI - Main Textual application for push-to-talk interface."""

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer
from textual.worker import Worker, get_current_worker

from push_to_talk_claude.core.recording_session import RecordingStatus
from push_to_talk_claude.ui.models import AppInfo, LogBuffer
from push_to_talk_claude.ui.widgets.info_panel import InfoPanel
from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.log_modal import LogModal

if TYPE_CHECKING:
    from push_to_talk_claude.utils.config import Config
    from push_to_talk_claude.core.recording_session import RecordingSessionManager
    from push_to_talk_claude.core.speech_to_text import SpeechToText
    from push_to_talk_claude.app import App as AppController


class PushToTalkTUI(App):
    """Main Textual application for push-to-talk interface."""

    CSS_PATH = Path(__file__).parent / "styles.tcss"

    BINDINGS = [
        Binding("a", "toggle_auto_return", "Auto-Return"),
        Binding("t", "toggle_transcript_logging", "Transcript Logging"),
        Binding("s", "toggle_tts_hook", "Speak Responses"),
        Binding("l", "toggle_logs", "Console Logs"),
        Binding("q", "quit", "Quit"),
        # Rename default command palette from "Palette" to "Options"
        Binding("ctrl+backslash", "command_palette", "Options"),
    ]

    def __init__(
        self,
        config: "Config",
        session_manager: "RecordingSessionManager | None" = None,
        app_controller: "AppController | None" = None,
        **kwargs,
    ) -> None:
        """Initialize TUI application.

        Args:
            config: Application configuration
            session_manager: Recording session manager instance
            app_controller: Parent App instance for toggle operations
        """
        super().__init__(**kwargs)
        self.config = config
        self.session_manager = session_manager
        self.app_controller = app_controller
        self.app_info = AppInfo.from_config(config)
        self.log_buffer = LogBuffer()
        self._log_modal_visible = False
        self.theme = config.ui.theme  # Load theme from config (after config is set)

    def watch_theme(self, theme: str) -> None:
        """Save theme changes to config file."""
        # Skip if not yet fully initialized
        if not hasattr(self, 'config') or self.config is None:
            return
        if not hasattr(self, 'log_buffer') or self.log_buffer is None:
            return
        if self.config.ui.theme != theme:
            self.config.ui.theme = theme
            # Save to config file
            from push_to_talk_claude.utils.config import Config
            config_path = Config.ensure_config_exists()
            self.config.save(config_path)
            self.log_buffer.append("INFO", f"Theme changed to: {theme}")

    def compose(self) -> ComposeResult:
        """Compose the main layout with info and status panels."""
        with Horizontal(id="main-layout"):
            yield InfoPanel(self.app_info, id="info-panel")
            yield StatusPanel(id="status-panel")
        yield Footer()

    def action_toggle_logs(self) -> None:
        """Toggle the log modal visibility."""
        # Use screen_stack length as single source of truth to avoid race conditions
        if len(self.screen_stack) > 1:
            # Modal is open, close it
            self.pop_screen()
        else:
            # No modal open, open one
            self.push_screen(LogModal(self.log_buffer))

    def action_toggle_auto_return(self) -> None:
        """Toggle auto-return setting via app controller."""
        if self.app_controller:
            new_value = self.app_controller.toggle_auto_return()
            # Update InfoPanel indicator
            info_panel = self.query_one(InfoPanel)
            info_panel.update_auto_return(new_value)
            # Show notification
            status_text = "ON" if new_value else "OFF"
            self.notify(f"Auto-Return: {status_text}", timeout=2)
            self.log_buffer.append("INFO", f"Auto-Return toggled to: {status_text}")

    def action_toggle_transcript_logging(self) -> None:
        """Toggle transcript logging setting via app controller."""
        if self.app_controller:
            new_value, path = self.app_controller.toggle_transcript_logging()
            # Update InfoPanel indicator
            info_panel = self.query_one(InfoPanel)
            info_panel.update_transcript_logging(new_value, path)
            # Show notification
            if new_value:
                self.notify(f"Transcript Logging: {path}", timeout=2)
                self.log_buffer.append("INFO", f"Transcript logging enabled: {path}")
            else:
                self.notify("Transcript Logging: OFF", timeout=2)
                self.log_buffer.append("INFO", "Transcript logging disabled")

    def action_toggle_tts_hook(self) -> None:
        """Toggle TTS hook setting via app controller."""
        if self.app_controller:
            new_value = self.app_controller.toggle_tts_hook()
            # Update InfoPanel indicator
            info_panel = self.query_one(InfoPanel)
            info_panel.update_tts_hook(new_value)
            # Show notification
            status_text = "ON" if new_value else "OFF"
            self.notify(f"Speak Responses: {status_text}", timeout=2)
            self.log_buffer.append("INFO", f"TTS hook toggled to: {status_text}")

    def handle_state_change(self, status: RecordingStatus) -> None:
        """Handle recording state change from background thread.

        Args:
            status: New recording status
        """
        if not self.is_running:
            return
        try:
            self.call_from_thread(self._update_status, status)
        except RuntimeError:
            # App is shutting down, ignore
            pass

    def _update_status(self, status: RecordingStatus) -> None:
        """Update status on main thread.

        Args:
            status: New recording status
        """
        self.query_one(StatusPanel).set_status(status)

        # Start/stop timer based on status
        info_panel = self.query_one(InfoPanel)
        timer = info_panel.get_timer()

        if status == RecordingStatus.RECORDING:
            timer.start()
        elif status in (
            RecordingStatus.TRANSCRIBING,
            RecordingStatus.COMPLETE,
            RecordingStatus.ERROR,
            RecordingStatus.IDLE,
        ):
            timer.stop()

        # Log the state change
        self.log_buffer.append("INFO", f"Status changed to: {status.value}")

    def handle_transcription(self, text: str) -> None:
        """Handle completed transcription from background thread.

        Args:
            text: Transcribed text
        """
        if not self.is_running:
            return
        try:
            self.call_from_thread(self._log_transcription, text)
        except RuntimeError:
            pass

    def _log_transcription(self, text: str) -> None:
        """Log transcription on main thread.

        Args:
            text: Transcribed text
        """
        self.log_buffer.append("INFO", f"Transcribed: {text[:50]}...")

    def handle_error(self, error: str) -> None:
        """Handle error from background thread.

        Args:
            error: Error message
        """
        if not self.is_running:
            return
        try:
            self.call_from_thread(self._log_error, error)
        except RuntimeError:
            pass

    def _log_error(self, error: str) -> None:
        """Log error on main thread.

        Args:
            error: Error message
        """
        self.log_buffer.append("ERROR", error)
        self.query_one(StatusPanel).set_status(RecordingStatus.ERROR)

    def handle_skipped(self, reason: str) -> None:
        """Handle skipped recording from background thread.

        Args:
            reason: Skip reason
        """
        if not self.is_running:
            return
        try:
            self.call_from_thread(self._log_skipped, reason)
        except RuntimeError:
            pass

    def _log_skipped(self, reason: str) -> None:
        """Log skipped recording on main thread.

        Args:
            reason: Skip reason
        """
        self.log_buffer.append("WARNING", f"Skipped: {reason}")
        self.query_one(StatusPanel).set_status(RecordingStatus.IDLE)

    def reset_timer(self) -> None:
        """Reset the recording timer."""
        info_panel = self.query_one(InfoPanel)
        timer = info_panel.get_timer()
        timer.reset()

    def show_model_loading(self) -> None:
        """Show that the model is loading."""
        self.log_buffer.append("INFO", "Loading Whisper model (first run may download ~244MB)...")

    def show_model_loaded(self, message: str) -> None:
        """Show that the model loaded successfully."""
        self.log_buffer.append("INFO", message)

    def show_model_error(self, error: str) -> None:
        """Show model loading error."""
        self.log_buffer.append("ERROR", f"Model loading failed: {error}")
        self.notify(f"⚠️ Model error: {error}", severity="error", timeout=10)
