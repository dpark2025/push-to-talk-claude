from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional
import threading


class RecordingIndicator:
    """Visual indicator showing recording status (thread-safe)."""

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize indicator."""
        self.console = console or Console()
        self.current_duration: float = 0.0
        self._lock = threading.Lock()

    def show_recording(self) -> None:
        """Show recording indicator."""
        with self._lock:
            text = Text()
            text.append("🔴 ", style="bold red")
            text.append("[Recording...]", style="bold red")
            text.append(" (release key when done)", style="dim")
            panel = Panel(text, border_style="red", padding=(0, 1))
            self.console.print(panel)

    def show_transcribing(self) -> None:
        """Show transcribing indicator."""
        with self._lock:
            text = Text()
            text.append("⏳ ", style="bold yellow")
            text.append("[Transcribing...]", style="bold yellow")
            panel = Panel(text, border_style="yellow", padding=(0, 1))
            self.console.print(panel)

    def show_injecting(self) -> None:
        """Show injecting indicator."""
        with self._lock:
            text = Text()
            text.append("💉 ", style="bold blue")
            text.append("[Injecting...]", style="bold blue")
            panel = Panel(text, border_style="blue", padding=(0, 1))
            self.console.print(panel)

    def show_complete(self, text: str) -> None:
        """Show completion with transcribed text preview."""
        with self._lock:
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
            text = Text()
            text.append("❌ ", style="bold red")
            text.append("[Error] ", style="bold red")
            text.append(message, style="red")
            panel = Panel(text, border_style="red", padding=(0, 1))
            self.console.print(panel)

    def hide(self) -> None:
        """Hide the indicator (no-op for simple prints)."""
        with self._lock:
            self.current_duration = 0.0

    def update_duration(self, seconds: float) -> None:
        """Update recording duration."""
        with self._lock:
            self.current_duration = seconds
