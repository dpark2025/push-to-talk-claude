"""Data models for the Textual TUI interface."""

from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from typing import TYPE_CHECKING
import time

from push_to_talk_claude.core.recording_session import RecordingStatus

if TYPE_CHECKING:
    from push_to_talk_claude.utils.config import Config


@dataclass
class StatusPillConfig:
    """Configuration for each status indicator pill in the status panel."""

    status: RecordingStatus
    label: str
    icon: str
    icon_color: str  # Rich markup color for the icon
    color: str  # Textual CSS color variable for active state


# Default status pill configurations
# Using single-width Unicode symbols to avoid terminal width calculation issues
STATUS_PILLS = [
    StatusPillConfig(RecordingStatus.RECORDING, "Recording", "⦿", "red", "$error"),
    StatusPillConfig(RecordingStatus.TRANSCRIBING, "Transcribing", "◐", "yellow", "$warning"),
    StatusPillConfig(RecordingStatus.INJECTING, "Injecting", "▶", "dodger_blue", "$primary"),
    StatusPillConfig(RecordingStatus.COMPLETE, "Complete", "✓", "green", "$success"),
    StatusPillConfig(RecordingStatus.ERROR, "Error", "✗", "red", "$error"),
    StatusPillConfig(RecordingStatus.IDLE, "Skipped", "»", "dim", "$surface"),
]


@dataclass
class LogEntry:
    """Single entry in the console log buffer."""

    timestamp: float
    level: str
    message: str

    def __str__(self) -> str:
        time_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        return f"[{time_str}] [{self.level}] {self.message}"


class LogBuffer:
    """Circular buffer storing recent log entries for the log modal."""

    def __init__(self, max_size: int = 100):
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        self.max_size = max_size
        self.entries: deque[LogEntry] = deque(maxlen=max_size)

    def append(self, level: str, message: str) -> None:
        """Add a new log entry to the buffer."""
        self.entries.append(
            LogEntry(timestamp=time.time(), level=level, message=message)
        )

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def clear(self) -> None:
        """Clear all entries from the buffer."""
        self.entries.clear()


@dataclass
class AppInfo:
    """Application configuration displayed in the info panel."""

    hotkey: str
    whisper_model: str
    injection_mode: str
    target_info: str
    auto_return: bool
    transcript_logging: str

    @classmethod
    def from_config(cls, config: "Config") -> "AppInfo":
        """Create AppInfo from a Config object."""
        if config.injection.mode == "focused":
            target = "Active window"
        else:
            target = f"{config.tmux.session_name}:{config.tmux.window_index}.{config.tmux.pane_index}"

        if config.logging.save_transcripts:
            from pathlib import Path
            transcript_logging = str(Path(config.logging.transcripts_dir).resolve())
        else:
            transcript_logging = "OFF"

        return cls(
            hotkey=config.push_to_talk.hotkey,
            whisper_model=config.whisper.model,
            injection_mode=config.injection.mode,
            target_info=target,
            auto_return=config.injection.auto_return,
            transcript_logging=transcript_logging,
        )


@dataclass
class TimerState:
    """State for the recording duration timer."""

    start_time: float = 0.0
    elapsed: float = 0.0
    is_running: bool = False
    warning_threshold: float = 50.0  # Show warning at 50s of 60s max
    max_duration: float = 60.0

    def __post_init__(self):
        if self.warning_threshold >= self.max_duration:
            raise ValueError("warning_threshold must be less than max_duration")

    @property
    def is_warning(self) -> bool:
        """Check if elapsed time has passed the warning threshold."""
        return self.elapsed >= self.warning_threshold

    @property
    def formatted(self) -> str:
        """Format elapsed time as MM:SS.ss."""
        minutes, seconds = divmod(self.elapsed, 60)
        return f"{int(minutes):02d}:{seconds:05.2f}"
