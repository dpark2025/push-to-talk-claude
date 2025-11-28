"""InfoPanel widget - left panel displaying app configuration and instructions."""

from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static

from push_to_talk_claude.ui.models import AppInfo
from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer


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
        yield Static(f"Hotkey: {self.app_info.hotkey}", id="hotkey-info")
        yield Static(f"Model: {self.app_info.whisper_model}", id="model-info")
        yield Static(f"Mode: {self.app_info.injection_mode}", id="mode-info")
        yield Static(f"Target: {self.app_info.target_info}", id="target-info")
        yield Static("", id="spacer-2")
        yield RecordingTimer(id="recording-timer")
        yield Static("", id="spacer-3")
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

    def get_timer(self) -> RecordingTimer:
        """Get the recording timer widget.

        Returns:
            The RecordingTimer widget instance
        """
        return self.query_one("#recording-timer", RecordingTimer)
