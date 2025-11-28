"""Tests for UI data models."""

import pytest
from unittest.mock import Mock

from push_to_talk_claude.ui.models import (
    StatusPillConfig,
    LogEntry,
    LogBuffer,
    AppInfo,
    TimerState,
    STATUS_PILLS,
)
from push_to_talk_claude.core.recording_session import RecordingStatus


class TestStatusPillConfig:
    """Tests for StatusPillConfig dataclass."""

    def test_create_status_pill_config(self):
        config = StatusPillConfig(
            status=RecordingStatus.RECORDING,
            label="Recording",
            emoji="🔴",
            color="$error",
        )
        assert config.status == RecordingStatus.RECORDING
        assert config.label == "Recording"
        assert config.emoji == "🔴"
        assert config.color == "$error"

    def test_status_pills_default_list(self):
        assert len(STATUS_PILLS) == 6
        statuses = [pill.status for pill in STATUS_PILLS]
        assert RecordingStatus.RECORDING in statuses
        assert RecordingStatus.TRANSCRIBING in statuses
        assert RecordingStatus.COMPLETE in statuses


class TestLogEntry:
    """Tests for LogEntry dataclass."""

    def test_create_log_entry(self):
        entry = LogEntry(timestamp=1234567890.0, level="INFO", message="Test message")
        assert entry.timestamp == 1234567890.0
        assert entry.level == "INFO"
        assert entry.message == "Test message"

    def test_log_entry_str(self):
        entry = LogEntry(timestamp=1234567890.0, level="INFO", message="Test message")
        result = str(entry)
        assert "[INFO]" in result
        assert "Test message" in result


class TestLogBuffer:
    """Tests for LogBuffer class."""

    def test_log_buffer_max_size(self):
        buffer = LogBuffer(max_size=3)
        buffer.append("INFO", "msg1")
        buffer.append("INFO", "msg2")
        buffer.append("INFO", "msg3")
        buffer.append("INFO", "msg4")
        assert len(buffer) == 3
        assert list(buffer)[0].message == "msg2"

    def test_log_buffer_append(self):
        buffer = LogBuffer(max_size=10)
        buffer.append("INFO", "test message")
        assert len(buffer) == 1
        entry = list(buffer)[0]
        assert entry.level == "INFO"
        assert entry.message == "test message"

    def test_log_buffer_iteration(self):
        buffer = LogBuffer(max_size=5)
        buffer.append("INFO", "msg1")
        buffer.append("ERROR", "msg2")
        messages = [e.message for e in buffer]
        assert messages == ["msg1", "msg2"]

    def test_log_buffer_clear(self):
        buffer = LogBuffer(max_size=10)
        buffer.append("INFO", "test")
        buffer.clear()
        assert len(buffer) == 0

    def test_log_buffer_invalid_max_size(self):
        with pytest.raises(ValueError):
            LogBuffer(max_size=0)
        with pytest.raises(ValueError):
            LogBuffer(max_size=-1)


class TestAppInfo:
    """Tests for AppInfo dataclass."""

    def test_create_app_info(self):
        info = AppInfo(
            hotkey="ctrl_r",
            whisper_model="tiny",
            injection_mode="focused",
            target_info="Active window",
        )
        assert info.hotkey == "ctrl_r"
        assert info.whisper_model == "tiny"
        assert info.injection_mode == "focused"
        assert info.target_info == "Active window"

    def test_app_info_from_config_focused(self):
        mock_config = Mock()
        mock_config.push_to_talk.hotkey = "ctrl_r"
        mock_config.whisper.model = "tiny"
        mock_config.injection.mode = "focused"

        info = AppInfo.from_config(mock_config)
        assert info.hotkey == "ctrl_r"
        assert info.whisper_model == "tiny"
        assert info.injection_mode == "focused"
        assert info.target_info == "Active window"

    def test_app_info_from_config_tmux(self):
        mock_config = Mock()
        mock_config.push_to_talk.hotkey = "ctrl_r"
        mock_config.whisper.model = "base"
        mock_config.injection.mode = "tmux"
        mock_config.tmux.session_name = "claude"
        mock_config.tmux.window_index = 0
        mock_config.tmux.pane_index = 1

        info = AppInfo.from_config(mock_config)
        assert info.injection_mode == "tmux"
        assert info.target_info == "claude:0.1"


class TestTimerState:
    """Tests for TimerState dataclass."""

    def test_timer_state_warning(self):
        state = TimerState(elapsed=51.0, warning_threshold=50.0)
        assert state.is_warning is True

    def test_timer_state_no_warning(self):
        state = TimerState(elapsed=49.0, warning_threshold=50.0)
        assert state.is_warning is False

    def test_timer_state_formatted(self):
        state = TimerState(elapsed=65.5)
        assert state.formatted == "01:05.50"

    def test_timer_state_formatted_zero(self):
        state = TimerState(elapsed=0.0)
        assert state.formatted == "00:00.00"

    def test_timer_state_formatted_under_minute(self):
        state = TimerState(elapsed=30.25)
        assert state.formatted == "00:30.25"

    def test_timer_state_invalid_threshold(self):
        with pytest.raises(ValueError):
            TimerState(warning_threshold=60.0, max_duration=60.0)

    def test_timer_state_defaults(self):
        state = TimerState()
        assert state.start_time == 0.0
        assert state.elapsed == 0.0
        assert state.is_running is False
        assert state.warning_threshold == 50.0
        assert state.max_duration == 60.0
