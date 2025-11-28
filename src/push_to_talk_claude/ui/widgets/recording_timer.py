"""RecordingTimer widget - live timer showing recording duration."""

from time import monotonic

from textual.widgets import Static
from textual.reactive import reactive
from textual.timer import Timer


class RecordingTimer(Static):
    """Live timer showing recording duration."""

    elapsed: reactive[float] = reactive(0.0)
    is_warning: reactive[bool] = reactive(False)

    def __init__(
        self,
        warning_threshold: float = 50.0,
        max_duration: float = 60.0,
        **kwargs,
    ) -> None:
        """Initialize recording timer.

        Args:
            warning_threshold: Seconds at which to show warning
            max_duration: Maximum recording duration
        """
        super().__init__("00:00.00", **kwargs)
        self.warning_threshold = warning_threshold
        self.max_duration = max_duration
        self.start_time: float = 0.0
        self._timer: Timer | None = None
        self._is_running: bool = False

    def on_mount(self) -> None:
        """Set up the timer when widget is mounted."""
        self._timer = self.set_interval(1 / 10, self._update_elapsed, pause=True)

    def _update_elapsed(self) -> None:
        """Update elapsed time (called 10x per second)."""
        if self._is_running:
            self.elapsed = monotonic() - self.start_time

    def watch_elapsed(self, elapsed: float) -> None:
        """Update display when elapsed time changes."""
        minutes, seconds = divmod(elapsed, 60)
        self.update(f"{int(minutes):02d}:{seconds:05.2f}")

        # Update warning state
        new_warning = elapsed >= self.warning_threshold
        if new_warning != self.is_warning:
            self.is_warning = new_warning

    def watch_is_warning(self, is_warning: bool) -> None:
        """Toggle warning CSS class."""
        self.set_class(is_warning, "warning")

    def start(self) -> None:
        """Start the timer from zero."""
        self.start_time = monotonic()
        self.elapsed = 0.0
        self._is_running = True
        self.set_class(True, "active")
        if self._timer:
            self._timer.resume()

    def stop(self) -> float:
        """Stop the timer and return elapsed time.

        Returns:
            Final elapsed time in seconds
        """
        if self._timer:
            self._timer.pause()
        self._is_running = False
        self.set_class(False, "active")
        # Do one final update
        if self.start_time > 0:
            self.elapsed = monotonic() - self.start_time
        return self.elapsed

    def reset(self) -> None:
        """Reset timer to zero without starting."""
        if self._timer:
            self._timer.pause()
        self._is_running = False
        self.start_time = 0.0
        self.elapsed = 0.0
        self.is_warning = False
        self.set_class(False, "active")
        self.set_class(False, "warning")
