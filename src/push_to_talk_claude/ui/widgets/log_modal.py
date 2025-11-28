"""LogModal screen - modal displaying console logs."""

from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import RichLog
from textual.containers import Container
from textual.binding import Binding

from push_to_talk_claude.ui.models import LogBuffer


class LogModal(ModalScreen):
    """Modal screen displaying console logs."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("l", "dismiss", "Close"),
    ]

    def __init__(self, log_buffer: LogBuffer, **kwargs) -> None:
        """Initialize log modal.

        Args:
            log_buffer: Buffer containing log entries to display
        """
        super().__init__(**kwargs)
        self.log_buffer = log_buffer

    def compose(self) -> ComposeResult:
        """Yield RichLog widget with log contents."""
        with Container(id="log-container"):
            yield RichLog(id="log-view", highlight=True, markup=True)

    def on_mount(self) -> None:
        """Populate log view with buffer contents on mount."""
        log_view = self.query_one("#log-view", RichLog)
        for entry in self.log_buffer:
            timestamp_str = f"{entry.timestamp:.2f}"
            level_color = self._get_level_color(entry.level)
            log_view.write(f"[{level_color}]{entry.level}[/] [{timestamp_str}] {entry.message}")

    def _get_level_color(self, level: str) -> str:
        """Get color for log level.

        Args:
            level: Log level string

        Returns:
            Color name for Rich markup
        """
        colors = {
            "DEBUG": "dim",
            "INFO": "blue",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold red",
        }
        return colors.get(level.upper(), "white")

    def action_dismiss(self) -> None:
        """Close the modal and return to main screen."""
        self.app.pop_screen()
