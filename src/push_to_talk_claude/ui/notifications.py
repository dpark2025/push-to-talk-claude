from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class NotificationManager:
    """Manage user notifications and error messages."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize notification manager."""
        self.console = console or Console()

    def info(self, message: str) -> None:
        """Show info message."""
        self.console.print(f"[blue]ℹ️  {message}[/blue]")

    def success(self, message: str) -> None:
        """Show success message."""
        self.console.print(f"[green]✅ {message}[/green]")

    def warning(self, message: str) -> None:
        """Show warning message."""
        self.console.print(f"[yellow]⚠️  {message}[/yellow]")

    def error(self, message: str) -> None:
        """Show error message."""
        self.console.print(f"[red]❌ {message}[/red]")

    def permission_error(self, permission: str) -> None:
        """Show detailed permission error with instructions."""
        text = Text()
        text.append("❌ Permission Error\n\n", style="bold red")
        text.append(f"Missing permission: {permission}\n\n", style="red")
        text.append("To fix this on macOS:\n", style="bold yellow")
        text.append("1. Open System Settings\n", style="white")
        text.append("2. Go to Privacy & Security\n", style="white")
        text.append(f"3. Select '{permission}'\n", style="white")
        text.append("4. Enable access for your terminal app\n", style="white")
        text.append("5. Restart this application\n", style="white")

        title = "[bold red]Action Required[/bold red]"
        panel = Panel(text, border_style="red", padding=(1, 2), title=title)
        self.console.print(panel)

    def startup_banner(self, hotkey: str, model: str, injection_mode: str = "focused") -> None:
        """Show startup banner with configuration info."""
        text = Text()
        text.append("🎙️  Push-to-Talk Claude\n\n", style="bold cyan")
        text.append("Configuration:\n", style="bold white")
        text.append("  Hotkey: ", style="dim")
        text.append(f"{hotkey}\n", style="bold green")
        text.append("  Whisper Model: ", style="dim")
        text.append(f"{model}\n", style="bold green")
        text.append("  Injection Mode: ", style="dim")
        mode_desc = "focused (window)" if injection_mode == "focused" else "tmux (pane)"
        text.append(f"{mode_desc}\n\n", style="bold green")
        text.append("Press ", style="white")
        text.append(f"{hotkey}", style="bold green")
        text.append(" to start recording\n", style="white")
        text.append("Press Ctrl+C to exit", style="dim")

        title = "[bold cyan]Ready[/bold cyan]"
        panel = Panel(text, border_style="cyan", padding=(1, 2), title=title)
        self.console.print(panel)

    def shutdown_message(self) -> None:
        """Show shutdown message."""
        text = Text()
        text.append("👋 ", style="bold cyan")
        text.append("Push-to-Talk Claude shutdown complete", style="cyan")
        self.console.print(text)
