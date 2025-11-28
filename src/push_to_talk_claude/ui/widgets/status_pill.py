"""StatusPill widget - individual status indicator that lights up when active."""

from textual.widgets import Static
from textual.reactive import reactive

from push_to_talk_claude.core.recording_session import RecordingStatus


class StatusPill(Static):
    """Individual status indicator that lights up when active."""

    active: reactive[bool] = reactive(False)

    def __init__(
        self,
        label: str,
        emoji: str,
        color: str,
        status: RecordingStatus,
        **kwargs,
    ) -> None:
        """Initialize status pill.

        Args:
            label: Display text (e.g., "Recording")
            emoji: Emoji indicator (e.g., "🔴")
            color: CSS color variable when active (e.g., "$error")
            status: The RecordingStatus this pill represents
        """
        super().__init__(f"{emoji} {label}", **kwargs)
        self.label_text = label
        self.emoji = emoji
        self.color = color
        self.status = status

    def watch_active(self, active: bool) -> None:
        """Toggle CSS class when active state changes."""
        self.set_class(active, "active")

    def activate(self) -> None:
        """Set pill to active (illuminated) state."""
        self.active = True

    def deactivate(self) -> None:
        """Set pill to inactive (dimmed) state."""
        self.active = False
