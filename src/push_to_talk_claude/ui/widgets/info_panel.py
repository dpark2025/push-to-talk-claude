"""InfoPanel widget - left panel displaying app configuration and instructions."""

from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static

from push_to_talk_claude.ui.models import AppInfo
from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer


class StartupConfigBox(Container):
    """Bordered container for startup configuration items."""
    pass


class InfoPanel(Container):
    """Left panel displaying app configuration and instructions."""

    def __init__(self, app_info: AppInfo, **kwargs) -> None:
        """Initialize info panel.

        Args:
            app_info: Application configuration to display
        """
        super().__init__(**kwargs)
        self.app_info = app_info

    def compose(self) -> ComposeResult:
        """Yield widgets for app info display."""
        yield Static("🎤 Push-to-Talk Claude", id="title")
        yield Static("", id="spacer-1")

        # Startup Configuration box
        with StartupConfigBox(id="startup-config-box"):
            yield Static("─ Startup Configuration ─", id="startup-config-label")
            yield Static(f"Hotkey: {self.app_info.hotkey}", id="hotkey-info")
            yield Static(f"Model: {self.app_info.whisper_model}", id="model-info")
            yield Static(f"Mode: {self.app_info.injection_mode}", id="mode-info")
            yield Static(f"Target: {self.app_info.target_info}", id="target-info")

        yield Static("", id="spacer-2")

        # Runtime-toggleable options (outside the startup config box)
        auto_return_text = "ON" if self.app_info.auto_return else "OFF"
        yield Static(f"Auto-Return: {auto_return_text}", id="auto-return-info")
        transcript_logging_widget = Static(
            f"Transcript Logging: {self.app_info.transcript_logging}",
            id="transcript-logging-info"
        )
        if self.app_info.transcript_logging != "OFF":
            transcript_logging_widget.add_class("enabled")
        yield transcript_logging_widget

        yield Static("", id="spacer-3")
        yield RecordingTimer(id="recording-timer")
        yield Static("", id="spacer-4")
        yield Static("─" * 20, id="divider")
        yield Static(self._get_instruction_text(), id="instruction-1")

    def _get_instruction_text(self) -> str:
        """Get instruction text based on injection mode."""
        if self.app_info.injection_mode == "focused":
            return "Hold hotkey to record to the focused window."
        else:
            return f"Hold hotkey to record to tmux session {self.app_info.target_info}."

    def update_info(self, app_info: AppInfo) -> None:
        """Update displayed app information.

        Args:
            app_info: New app configuration
        """
        self.app_info = app_info
        self.query_one("#hotkey-info", Static).update(f"Hotkey: {app_info.hotkey}")
        self.query_one("#model-info", Static).update(f"Model: {app_info.whisper_model}")
        self.query_one("#mode-info", Static).update(f"Mode: {app_info.injection_mode}")
        self.query_one("#target-info", Static).update(f"Target: {app_info.target_info}")
        self.query_one("#instruction-1", Static).update(self._get_instruction_text())
        auto_return_text = "ON" if app_info.auto_return else "OFF"
        self.query_one("#auto-return-info", Static).update(f"Auto-Return: {auto_return_text}")

    def update_auto_return(self, enabled: bool) -> None:
        """Update the auto-return indicator.

        Args:
            enabled: Whether auto-return is enabled
        """
        self.app_info.auto_return = enabled
        auto_return_text = "ON" if enabled else "OFF"
        self.query_one("#auto-return-info", Static).update(f"Auto-Return: {auto_return_text}")

    def update_transcript_logging(self, enabled: bool, path: str) -> None:
        """Update the transcript logging indicator.

        Args:
            enabled: Whether transcript logging is enabled
            path: Path to transcripts directory
        """
        widget = self.query_one("#transcript-logging-info", Static)
        if enabled:
            self.app_info.transcript_logging = path
            widget.update(f"Transcript Logging: {path}")
            widget.add_class("enabled")
        else:
            self.app_info.transcript_logging = "OFF"
            widget.update("Transcript Logging: OFF")
            widget.remove_class("enabled")

    def get_timer(self) -> RecordingTimer:
        """Get the recording timer widget.

        Returns:
            The RecordingTimer widget instance
        """
        return self.query_one("#recording-timer", RecordingTimer)
