from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from typing import Optional
import threading


class RecordingIndicator:
    """Visual indicator showing recording status."""

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize indicator."""
        self.console = console or Console()
        self.live: Optional[Live] = None
        self.current_duration: float = 0.0
        self._lock = threading.Lock()

    def show_recording(self) -> None:
        """Show recording indicator (red dot or similar)."""
        with self._lock:
            self._stop_live()
            text = Text()
            text.append("🔴 ", style="bold red")
            text.append("[Recording]", style="bold red")
            text.append(f" {self.current_duration:.1f}s", style="dim")
            panel = Panel(text, border_style="red", padding=(0, 1))
            self.live = Live(panel, console=self.console, refresh_per_second=10)
            self.live.start()

    def show_transcribing(self) -> None:
        """Show transcribing indicator."""
        with self._lock:
            self._stop_live()
            text = Text()
            text.append("⏳ ", style="bold yellow")
            text.append("[Transcribing...]", style="bold yellow")
            panel = Panel(text, border_style="yellow", padding=(0, 1))
            self.live = Live(panel, console=self.console, refresh_per_second=10)
            self.live.start()

    def show_injecting(self) -> None:
        """Show injecting indicator."""
        with self._lock:
            self._stop_live()
            text = Text()
            text.append("💉 ", style="bold blue")
            text.append("[Injecting...]", style="bold blue")
            panel = Panel(text, border_style="blue", padding=(0, 1))
            self.live = Live(panel, console=self.console, refresh_per_second=10)
            self.live.start()

    def show_complete(self, text: str) -> None:
        """Show completion with transcribed text preview."""
        with self._lock:
            self._stop_live()
            display_text = Text()
            display_text.append("✅ ", style="bold green")
            display_text.append("[Complete] ", style="bold green")

            # Truncate to first 50 chars
            preview = text[:50]
            if len(text) > 50:
                preview += "..."
            display_text.append(preview, style="dim")

            panel = Panel(display_text, border_style="green", padding=(0, 1))
            self.console.print(panel)

    def show_error(self, message: str) -> None:
        """Show error message."""
        with self._lock:
            self._stop_live()
            text = Text()
            text.append("❌ ", style="bold red")
            text.append("[Error] ", style="bold red")
            text.append(message, style="red")
            panel = Panel(text, border_style="red", padding=(0, 1))
            self.console.print(panel)

    def hide(self) -> None:
        """Hide the indicator."""
        with self._lock:
            self._stop_live()
            self.current_duration = 0.0

    def update_duration(self, seconds: float) -> None:
        """Update recording duration display."""
        with self._lock:
            self.current_duration = seconds
            if self.live and self.live.is_started:
                text = Text()
                text.append("🔴 ", style="bold red")
                text.append("[Recording]", style="bold red")
                text.append(f" {self.current_duration:.1f}s", style="dim")
                panel = Panel(text, border_style="red", padding=(0, 1))
                self.live.update(panel)

    def _stop_live(self) -> None:
        """Stop the live display if running."""
        if self.live and self.live.is_started:
            self.live.stop()
            self.live = None
