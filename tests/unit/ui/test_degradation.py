"""Tests for graceful degradation on limited terminals."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.core.recording_session import RecordingStatus
from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer
from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.status_pill import StatusPill


class DegradationTestApp(App):
    """Test app for degradation testing."""

    def compose(self) -> ComposeResult:
        yield StatusPanel(id="status-panel")
        yield RecordingTimer(id="timer")


@pytest.mark.asyncio
async def test_app_runs_without_crash():
    """Verify app can run in test environment without crashing."""
    async with DegradationTestApp().run_test() as pilot:
        # App should mount successfully
        assert pilot.app is not None
        panel = pilot.app.query_one(StatusPanel)
        assert panel is not None


@pytest.mark.asyncio
async def test_status_transitions_work():
    """Verify all status transitions work without errors."""
    async with DegradationTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)

        # Cycle through all statuses
        for status in RecordingStatus:
            panel.set_status(status)
            await pilot.pause()
            assert panel.current_status == status


@pytest.mark.asyncio
async def test_timer_functions_work():
    """Verify timer works in limited environment."""
    async with DegradationTestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)

        # Start/stop/reset should all work
        timer.start()
        await pilot.pause(0.1)
        assert timer._is_running is True

        elapsed = timer.stop()
        assert elapsed >= 0

        timer.reset()
        assert timer.elapsed == 0.0


@pytest.mark.asyncio
async def test_widgets_handle_rapid_updates():
    """Verify widgets handle rapid state changes without errors."""
    async with DegradationTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)

        # Rapid status changes
        for _ in range(10):
            panel.set_status(RecordingStatus.RECORDING)
            panel.set_status(RecordingStatus.TRANSCRIBING)
            panel.set_status(RecordingStatus.COMPLETE)

        await pilot.pause()
        # Should end in COMPLETE state
        assert panel.current_status == RecordingStatus.COMPLETE


@pytest.mark.asyncio
async def test_pills_render_text_content():
    """Verify pills have renderable text content."""
    async with DegradationTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        for pill in pills:
            # Pills should have text content that can be rendered
            assert pill.label_text
            # Text should be a simple string
            assert isinstance(pill.label_text, str)
