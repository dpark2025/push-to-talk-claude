"""StatusPanel widget - right panel containing vertically stacked status pills."""

from textual.containers import Container
from textual.app import ComposeResult
from textual.reactive import reactive

from push_to_talk_claude.core.recording_session import RecordingStatus
from push_to_talk_claude.ui.models import STATUS_PILLS
from push_to_talk_claude.ui.widgets.status_pill import StatusPill


class StatusPanel(Container):
    """Right panel containing vertically stacked status pills."""

    current_status: reactive[RecordingStatus] = reactive(RecordingStatus.IDLE)

    def __init__(self, **kwargs) -> None:
        """Initialize status panel with all status pills."""
        super().__init__(**kwargs)
        self._pills: dict[RecordingStatus, StatusPill] = {}

    def compose(self) -> ComposeResult:
        """Yield StatusPill widgets for each status type."""
        for config in STATUS_PILLS:
            pill = StatusPill(
                label=config.label,
                icon=config.icon,
                icon_color=config.icon_color,
                color=config.color,
                status=config.status,
                id=f"pill-{config.status.value}",
            )
            self._pills[config.status] = pill
            yield pill

    def set_status(self, status: RecordingStatus) -> None:
        """Update the active status pill.

        Args:
            status: The new active status
        """
        self.current_status = status

    def on_mount(self) -> None:
        """Deactivate all pills on mount - start with all dimmed."""
        for pill in self._pills.values():
            pill.deactivate()
        self._initialized = True

    def watch_current_status(self, status: RecordingStatus) -> None:
        """Activate the correct pill when status changes."""
        # Skip if not yet mounted (will be handled by on_mount)
        if not getattr(self, "_initialized", False):
            return
        for pill_status, pill in self._pills.items():
            if pill_status == status:
                pill.activate()
            else:
                pill.deactivate()
