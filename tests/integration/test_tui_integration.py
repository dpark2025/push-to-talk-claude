"""Integration tests for TUI with recording session flow."""

import pytest
from unittest.mock import Mock

from push_to_talk_claude.ui.tui_app import PushToTalkTUI
from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.info_panel import InfoPanel
from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer
from push_to_talk_claude.core.recording_session import RecordingStatus


def create_test_config():
    """Create a mock config object for testing."""
    config = Mock()
    config.push_to_talk.hotkey = "ctrl_r"
    config.whisper.model = "tiny"
    config.injection.mode = "focused"
    config.tmux.session_name = "main"
    config.tmux.window_index = 0
    config.tmux.pane_index = 0
    return config


@pytest.mark.asyncio
async def test_full_recording_flow():
    """Test complete recording cycle through TUI."""
    mock_session = Mock()
    config = create_test_config()

    async with PushToTalkTUI(config, mock_session).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        # Initial state should be IDLE
        assert status_panel.current_status == RecordingStatus.IDLE

        # Simulate state change to RECORDING
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.1)
        assert status_panel.current_status == RecordingStatus.RECORDING

        # Timer should be running
        timer = pilot.app.query_one(RecordingTimer)
        assert timer._is_running is True

        # Simulate transcribing
        pilot.app._update_status(RecordingStatus.TRANSCRIBING)
        await pilot.pause(0.1)
        assert status_panel.current_status == RecordingStatus.TRANSCRIBING
        assert timer._is_running is False

        # Simulate injecting
        pilot.app._update_status(RecordingStatus.INJECTING)
        await pilot.pause(0.1)
        assert status_panel.current_status == RecordingStatus.INJECTING

        # Simulate transcription complete
        pilot.app._log_transcription("Hello world test transcription")
        pilot.app._update_status(RecordingStatus.COMPLETE)
        await pilot.pause(0.1)

        assert status_panel.current_status == RecordingStatus.COMPLETE


@pytest.mark.asyncio
async def test_error_flow():
    """Test error handling flow through TUI."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        # Start recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.1)

        # Simulate error
        pilot.app._log_error("Test error occurred")
        await pilot.pause(0.1)

        # Status should be ERROR
        assert status_panel.current_status == RecordingStatus.ERROR

        # Log buffer should have error
        assert len(pilot.app.log_buffer) > 0


@pytest.mark.asyncio
async def test_skipped_flow():
    """Test skipped recording flow through TUI."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        # Start recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.1)

        # Simulate skipped (too short)
        pilot.app._log_skipped("Recording too short")
        await pilot.pause(0.1)

        # Status should be IDLE (skipped)
        assert status_panel.current_status == RecordingStatus.IDLE


@pytest.mark.asyncio
async def test_log_modal_with_history():
    """Test log modal shows recorded history."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        # Add some log entries through state changes
        pilot.app._update_status(RecordingStatus.RECORDING)
        pilot.app._update_status(RecordingStatus.TRANSCRIBING)
        pilot.app._log_transcription("Test transcription")
        await pilot.pause(0.1)

        # Open logs
        await pilot.press("l")
        await pilot.pause()

        # Modal should be open
        assert len(pilot.app.screen_stack) == 2

        # Close with escape
        await pilot.press("escape")
        await pilot.pause()

        assert len(pilot.app.screen_stack) == 1


@pytest.mark.asyncio
async def test_timer_warning_state():
    """Test timer warning state during long recording."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        info_panel = pilot.app.query_one(InfoPanel)
        timer = info_panel.get_timer()

        # Override warning threshold for faster test
        timer.warning_threshold = 0.1

        # Start recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.2)

        # Timer should be in warning state
        assert timer.is_warning is True
        assert "warning" in timer.classes


@pytest.mark.asyncio
async def test_app_quit():
    """Test app quit functionality."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        # App should be running
        assert pilot.app.is_running

        # Press Q to quit
        await pilot.press("q")
        await pilot.pause()

        # Test completes without hanging


@pytest.mark.asyncio
async def test_multiple_recording_cycles():
    """Test multiple consecutive recording cycles."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        # First cycle
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.05)
        pilot.app._update_status(RecordingStatus.TRANSCRIBING)
        await pilot.pause(0.05)
        pilot.app._update_status(RecordingStatus.COMPLETE)
        await pilot.pause(0.05)

        assert status_panel.current_status == RecordingStatus.COMPLETE

        # Reset timer
        pilot.app.reset_timer()
        await pilot.pause(0.05)

        # Second cycle
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.05)

        assert status_panel.current_status == RecordingStatus.RECORDING

        # Timer should be running again
        timer = pilot.app.query_one(RecordingTimer)
        assert timer._is_running is True


@pytest.mark.asyncio
async def test_terminal_resize_during_recording():
    """Test terminal resize doesn't crash during recording."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test(size=(80, 24)) as pilot:
        # Start recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause(0.1)

        # Simulate resize by changing the terminal size
        await pilot.resize_terminal(120, 40)
        await pilot.pause(0.1)

        # App should still be running
        assert pilot.app.is_running

        # Resize back smaller
        await pilot.resize_terminal(60, 20)
        await pilot.pause(0.1)

        # Should still be recording
        status_panel = pilot.app.query_one(StatusPanel)
        assert status_panel.current_status == RecordingStatus.RECORDING


@pytest.mark.asyncio
async def test_terminal_resize_with_modal():
    """Test terminal resize doesn't crash with modal open."""
    config = create_test_config()

    async with PushToTalkTUI(config).run_test(size=(80, 24)) as pilot:
        # Open log modal
        await pilot.press("l")
        await pilot.pause()

        # Simulate resize
        await pilot.resize_terminal(100, 30)
        await pilot.pause(0.1)

        # Modal should still be open
        assert len(pilot.app.screen_stack) == 2

        # Resize smaller
        await pilot.resize_terminal(50, 15)
        await pilot.pause(0.1)

        # App should still be running with modal
        assert len(pilot.app.screen_stack) == 2
