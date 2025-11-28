from typing import Optional, List
from dataclasses import dataclass
import subprocess
import os


@dataclass
class TmuxPane:
    session_name: str
    window_index: int
    pane_index: int
    current_command: str
    is_active: bool


@dataclass
class ClaudeSession:
    session_name: str
    window_index: int
    pane_index: int
    target_string: str  # "session:window.pane" format


class SessionDetector:
    """Detect Claude Code sessions in tmux."""

    # Commands that indicate Claude Code is running
    CLAUDE_INDICATORS = ["claude", "claude-code", "npx claude"]

    def __init__(self) -> None:
        """Initialize session detector."""
        self._panes: List[TmuxPane] = []
        self.refresh()

    def list_all_panes(self) -> List[TmuxPane]:
        """List all panes across all tmux sessions."""
        return self._panes

    def find_claude_panes(self) -> List[ClaudeSession]:
        """Find all panes running Claude Code."""
        claude_sessions = []

        for pane in self._panes:
            command_lower = pane.current_command.lower()
            if any(indicator.lower() in command_lower for indicator in self.CLAUDE_INDICATORS):
                target_string = f"{pane.session_name}:{pane.window_index}.{pane.pane_index}"
                claude_sessions.append(ClaudeSession(
                    session_name=pane.session_name,
                    window_index=pane.window_index,
                    pane_index=pane.pane_index,
                    target_string=target_string
                ))

        return claude_sessions

    def get_best_target(self) -> Optional[ClaudeSession]:
        """
        Get the best Claude session to target.

        Priority:
        1. Active pane running Claude
        2. Any pane running Claude
        3. None if no Claude found
        """
        claude_panes = self.find_claude_panes()

        if not claude_panes:
            return None

        # Find active pane running Claude
        for pane in self._panes:
            if pane.is_active:
                command_lower = pane.current_command.lower()
                if any(indicator.lower() in command_lower for indicator in self.CLAUDE_INDICATORS):
                    target_string = f"{pane.session_name}:{pane.window_index}.{pane.pane_index}"
                    return ClaudeSession(
                        session_name=pane.session_name,
                        window_index=pane.window_index,
                        pane_index=pane.pane_index,
                        target_string=target_string
                    )

        # Return first Claude pane found
        return claude_panes[0]

    def refresh(self) -> None:
        """Refresh the pane list."""
        self._panes = []

        if not self.is_tmux_running():
            return

        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-a", "-F",
                 "#{session_name}|#{window_index}|#{pane_index}|#{pane_current_command}|#{pane_active}"],
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) != 5:
                    continue

                session_name, window_index, pane_index, current_command, pane_active = parts

                self._panes.append(TmuxPane(
                    session_name=session_name,
                    window_index=int(window_index),
                    pane_index=int(pane_index),
                    current_command=current_command,
                    is_active=(pane_active == "1")
                ))
        except subprocess.CalledProcessError:
            pass

    @staticmethod
    def is_tmux_running() -> bool:
        """Check if tmux server is running."""
        try:
            subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def get_current_session() -> Optional[str]:
        """Get current tmux session name if inside tmux."""
        tmux_env = os.environ.get("TMUX")
        if not tmux_env:
            return None

        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#{session_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
