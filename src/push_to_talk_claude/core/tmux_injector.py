"""Tmux session injection for sending text to Claude Code."""

from typing import Optional
from dataclasses import dataclass
import subprocess
import shutil


@dataclass
class TmuxTarget:
    """Represents a tmux target for text injection."""

    session_name: str
    window_index: int
    pane_index: int
    is_claude_code: bool


class TmuxInjector:
    """Inject text into tmux sessions."""

    def __init__(
        self,
        session_name: Optional[str] = None,
        auto_detect: bool = True
    ) -> None:
        """
        Initialize tmux injector.

        Args:
            session_name: Explicit session or None for auto-detect
            auto_detect: Whether to auto-find Claude Code session

        Raises:
            RuntimeError: If tmux is not installed
        """
        if not self.is_tmux_available():
            raise RuntimeError("tmux is not installed or not accessible")

        self._target: Optional[TmuxTarget] = None
        self._session_name = session_name
        self._auto_detect = auto_detect

        if auto_detect and not session_name:
            self._target = self.find_claude_session()
        elif session_name:
            # Use explicit session - get first window/pane
            self._target = self._get_first_pane(session_name)

    def inject_text(self, text: str) -> bool:
        """
        Send text to tmux target.

        Args:
            text: Text to inject (should already be sanitized)

        Returns:
            True if injection succeeded

        Raises:
            RuntimeError: If no valid target found
            ValueError: If text is empty
        """
        if not text:
            raise ValueError("Text cannot be empty")

        if not self._target:
            raise RuntimeError("No valid tmux target found")

        if not self.validate_target():
            raise RuntimeError("Target session/pane is no longer valid")

        target_str = f"{self._target.session_name}:{self._target.window_index}.{self._target.pane_index}"

        try:
            result = subprocess.run(
                ["tmux", "send-keys", "-t", target_str, "--", text],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    def find_claude_session(self) -> Optional[TmuxTarget]:
        """
        Find tmux session running Claude Code.

        Returns:
            TmuxTarget if found, None otherwise
        """
        try:
            # Get all sessions
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            sessions = result.stdout.strip().split('\n')
            if not sessions or sessions == ['']:
                return None

            # Check each session for Claude Code
            for session in sessions:
                session = session.strip()
                if not session:
                    continue

                # List panes in this session
                pane_result = subprocess.run(
                    ["tmux", "list-panes", "-t", session, "-F",
                     "#{window_index}:#{pane_index}:#{pane_current_command}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if pane_result.returncode != 0:
                    continue

                panes = pane_result.stdout.strip().split('\n')
                for pane in panes:
                    if not pane:
                        continue

                    parts = pane.split(':')
                    if len(parts) >= 3:
                        window_idx = int(parts[0])
                        pane_idx = int(parts[1])
                        command = ':'.join(parts[2:])  # Rejoin in case command has colons

                        if 'claude' in command.lower():
                            return TmuxTarget(
                                session_name=session,
                                window_index=window_idx,
                                pane_index=pane_idx,
                                is_claude_code=True
                            )

            return None

        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    def validate_target(self) -> bool:
        """Check if current target is valid and accessible."""
        if not self._target:
            return False

        target_str = f"{self._target.session_name}:{self._target.window_index}.{self._target.pane_index}"

        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-t", target_str, "-F", "#{pane_id}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    @property
    def target(self) -> Optional[TmuxTarget]:
        """Current injection target."""
        return self._target

    @staticmethod
    def is_tmux_available() -> bool:
        """Check if tmux is installed and accessible."""
        return shutil.which("tmux") is not None

    def _get_first_pane(self, session_name: str) -> Optional[TmuxTarget]:
        """Get the first pane in a session."""
        try:
            result = subprocess.run(
                ["tmux", "list-panes", "-t", session_name, "-F",
                 "#{window_index}:#{pane_index}:#{pane_current_command}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            panes = result.stdout.strip().split('\n')
            if not panes or panes == ['']:
                return None

            first_pane = panes[0]
            parts = first_pane.split(':')
            if len(parts) >= 2:
                window_idx = int(parts[0])
                pane_idx = int(parts[1])
                command = ':'.join(parts[2:]) if len(parts) > 2 else ''

                return TmuxTarget(
                    session_name=session_name,
                    window_index=window_idx,
                    pane_index=pane_idx,
                    is_claude_code='claude' in command.lower()
                )

            return None

        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
