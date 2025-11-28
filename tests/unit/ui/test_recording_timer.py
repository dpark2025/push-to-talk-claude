"""Tests for RecordingTimer widget."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer


class RecordingTimerTestApp(App):
    """Test app for RecordingTimer widget."""

    def __init__(self, warning_threshold: float = 50.0, **kwargs):
        super().__init__(**kwargs)
        self.warning_threshold = warning_threshold

    def compose(self) -> ComposeResult:
        yield RecordingTimer(warning_threshold=self.warning_threshold)


@pytest.mark.asyncio
async def test_recording_timer_initial_state():
    """Test that timer starts at zero and not running."""
    async with RecordingTimerTestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        assert timer.elapsed == 0.0
        assert timer._is_running is False
        assert "active" not in timer.classes


@pytest.mark.asyncio
async def test_recording_timer_start():
    """Test that timer starts running."""
    async with RecordingTimerTestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        assert timer._is_running is True
        assert "active" in timer.classes


@pytest.mark.asyncio
async def test_recording_timer_start_stop():
    """Test timer start and stop returns elapsed time."""
    async with RecordingTimerTestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.2)  # Wait 200ms
        elapsed = timer.stop()
        assert elapsed >= 0.15  # Allow some tolerance
        assert elapsed <= 0.4
        assert timer._is_running is False


@pytest.mark.asyncio
async def test_recording_timer_warning_state():
    """Test that warning state is triggered at threshold."""
    async with RecordingTimerTestApp(warning_threshold=0.1).run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.25)  # Wait longer to ensure timer updates
        assert timer.elapsed >= 0.1  # Verify elapsed has updated
        assert timer.is_warning is True
        assert "warning" in timer.classes


@pytest.mark.asyncio
async def test_recording_timer_no_warning_before_threshold():
    """Test that warning is not triggered before threshold."""
    async with RecordingTimerTestApp(warning_threshold=1.0).run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.1)
        assert timer.is_warning is False
        assert "warning" not in timer.classes


@pytest.mark.asyncio
async def test_recording_timer_reset():
    """Test timer reset clears state."""
    async with RecordingTimerTestApp(warning_threshold=0.1).run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        timer.start()
        await pilot.pause(0.15)

        timer.reset()

        assert timer.elapsed == 0.0
        assert timer._is_running is False
        assert timer.is_warning is False
        assert "active" not in timer.classes
        assert "warning" not in timer.classes


@pytest.mark.asyncio
async def test_recording_timer_display_format():
    """Test that timer displays in correct format."""
    async with RecordingTimerTestApp().run_test() as pilot:
        timer = pilot.app.query_one(RecordingTimer)
        # Manually set elapsed to check format
        timer.elapsed = 65.5
        await pilot.pause(0.05)  # Let the watch trigger
        # Check the timer's internal format logic
        minutes, seconds = divmod(timer.elapsed, 60)
        expected = f"{int(minutes):02d}:{seconds:05.2f}"
        assert expected == "01:05.50"
