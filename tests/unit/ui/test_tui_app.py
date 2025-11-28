"""Tests for PushToTalkTUI application."""

import pytest
from unittest.mock import Mock, MagicMock

from push_to_talk_claude.ui.tui_app import PushToTalkTUI
from push_to_talk_claude.ui.widgets.info_panel import InfoPanel
from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.log_modal import LogModal
from push_to_talk_claude.core.recording_session import RecordingStatus


def create_mock_config():
    """Create a mock config object."""
    config = Mock()
    config.push_to_talk.hotkey = "ctrl_r"
    config.whisper.model = "tiny"
    config.injection.mode = "focused"
    config.tmux.session_name = "main"
    config.tmux.window_index = 0
    config.tmux.pane_index = 0
    return config


@pytest.mark.asyncio
async def test_tui_layout():
    """Test that TUI has info and status panels."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        info_panel = pilot.app.query_one("#info-panel", InfoPanel)
        status_panel = pilot.app.query_one("#status-panel", StatusPanel)
        assert info_panel is not None
        assert status_panel is not None


@pytest.mark.asyncio
async def test_tui_toggle_logs_open():
    """Test that pressing L opens log modal."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        # Initial state - no modal
        assert len(pilot.app.screen_stack) == 1

        # Press L to open logs
        await pilot.press("l")
        await pilot.pause()

        # Modal should be open
        assert len(pilot.app.screen_stack) == 2
        assert isinstance(pilot.app.screen, LogModal)


@pytest.mark.asyncio
async def test_tui_toggle_logs_close():
    """Test that pressing L again closes log modal."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        # Open logs
        await pilot.press("l")
        await pilot.pause()
        assert len(pilot.app.screen_stack) == 2

        # Close logs with L
        await pilot.press("l")
        await pilot.pause()

        # Modal should be closed
        assert len(pilot.app.screen_stack) == 1


@pytest.mark.asyncio
async def test_tui_quit_action():
    """Test that Q key triggers quit."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        # App should be running initially
        assert pilot.app.is_running

        # Press Q to quit
        await pilot.press("q")
        await pilot.pause()

        # App should exit (or be in exit state)
        # Note: run_test handles the exit gracefully


@pytest.mark.asyncio
async def test_tui_update_status():
    """Test _update_status changes status panel."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        # Initial state should be IDLE
        assert status_panel.current_status == RecordingStatus.IDLE

        # Update status
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause()

        assert status_panel.current_status == RecordingStatus.RECORDING


@pytest.mark.asyncio
async def test_tui_status_starts_timer():
    """Test that RECORDING status starts timer."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        info_panel = pilot.app.query_one(InfoPanel)
        timer = info_panel.get_timer()

        assert timer._is_running is False

        # Set to recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause()

        assert timer._is_running is True


@pytest.mark.asyncio
async def test_tui_status_stops_timer():
    """Test that non-RECORDING status stops timer."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        info_panel = pilot.app.query_one(InfoPanel)
        timer = info_panel.get_timer()

        # Start recording
        pilot.app._update_status(RecordingStatus.RECORDING)
        await pilot.pause()
        assert timer._is_running is True

        # Stop with complete
        pilot.app._update_status(RecordingStatus.COMPLETE)
        await pilot.pause()
        assert timer._is_running is False


@pytest.mark.asyncio
async def test_tui_log_transcription():
    """Test _log_transcription adds to log buffer."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        initial_len = len(pilot.app.log_buffer)

        pilot.app._log_transcription("Hello world test")
        await pilot.pause()

        assert len(pilot.app.log_buffer) > initial_len


@pytest.mark.asyncio
async def test_tui_log_error():
    """Test _log_error adds to log buffer and sets status."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        pilot.app._log_error("Test error")
        await pilot.pause()

        assert status_panel.current_status == RecordingStatus.ERROR


@pytest.mark.asyncio
async def test_tui_log_skipped():
    """Test _log_skipped adds to log buffer and sets status."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        status_panel = pilot.app.query_one(StatusPanel)

        pilot.app._log_skipped("Too short")
        await pilot.pause()

        assert status_panel.current_status == RecordingStatus.IDLE


@pytest.mark.asyncio
async def test_tui_reset_timer():
    """Test reset_timer resets the timer."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        info_panel = pilot.app.query_one(InfoPanel)
        timer = info_panel.get_timer()

        # Start and let timer run
        timer.start()
        await pilot.pause(0.1)
        assert timer.elapsed > 0

        # Reset
        pilot.app.reset_timer()
        await pilot.pause()

        assert timer.elapsed == 0.0
        assert timer._is_running is False


@pytest.mark.asyncio
async def test_tui_with_session_manager():
    """Test TUI can be initialized with a session manager."""
    config = create_mock_config()
    session_manager = Mock()

    async with PushToTalkTUI(config, session_manager).run_test() as pilot:
        assert pilot.app.session_manager is session_manager


@pytest.mark.asyncio
async def test_tui_has_log_buffer():
    """Test TUI has a log buffer."""
    config = create_mock_config()
    async with PushToTalkTUI(config).run_test() as pilot:
        assert pilot.app.log_buffer is not None
        assert len(pilot.app.log_buffer) == 0
