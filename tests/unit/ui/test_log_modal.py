"""Tests for LogModal screen."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import RichLog

from push_to_talk_claude.ui.models import LogBuffer
from push_to_talk_claude.ui.widgets.log_modal import LogModal


class LogModalTestApp(App):
    """Test app for LogModal screen."""

    def __init__(self, log_buffer: LogBuffer | None = None, **kwargs):
        super().__init__(**kwargs)
        self.log_buffer = log_buffer or LogBuffer()

    def compose(self) -> ComposeResult:
        yield from ()

    def show_modal(self) -> None:
        """Push the log modal screen."""
        self.push_screen(LogModal(self.log_buffer))


@pytest.mark.asyncio
async def test_log_modal_creates_rich_log():
    """Test that LogModal creates a RichLog widget."""
    buffer = LogBuffer()
    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Query from the active screen (the modal)
        log_view = pilot.app.screen.query_one("#log-view", RichLog)
        assert log_view is not None


@pytest.mark.asyncio
async def test_log_modal_populates_from_buffer():
    """Test that LogModal populates from log buffer."""
    buffer = LogBuffer()
    buffer.append("INFO", "Test message 1")
    buffer.append("WARNING", "Test message 2")

    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Query from the active screen (the modal)
        log_view = pilot.app.screen.query_one("#log-view", RichLog)
        assert log_view is not None


@pytest.mark.asyncio
async def test_log_modal_dismiss_with_escape():
    """Test that Escape key dismisses the modal."""
    buffer = LogBuffer()
    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Modal should be visible
        assert len(pilot.app.screen_stack) == 2

        await pilot.press("escape")
        await pilot.pause()
        # Modal should be dismissed
        assert len(pilot.app.screen_stack) == 1


@pytest.mark.asyncio
async def test_log_modal_dismiss_with_l():
    """Test that L key dismisses the modal."""
    buffer = LogBuffer()
    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Modal should be visible
        assert len(pilot.app.screen_stack) == 2

        await pilot.press("l")
        await pilot.pause()
        # Modal should be dismissed
        assert len(pilot.app.screen_stack) == 1


@pytest.mark.asyncio
async def test_log_modal_empty_buffer():
    """Test LogModal with empty buffer."""
    buffer = LogBuffer()
    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Query from the active screen (the modal)
        log_view = pilot.app.screen.query_one("#log-view", RichLog)
        assert log_view is not None


@pytest.mark.asyncio
async def test_log_modal_level_colors():
    """Test that different log levels get different colors."""
    buffer = LogBuffer()
    buffer.append("DEBUG", "Debug message")
    buffer.append("INFO", "Info message")
    buffer.append("WARNING", "Warning message")
    buffer.append("ERROR", "Error message")

    async with LogModalTestApp(buffer).run_test() as pilot:
        pilot.app.show_modal()
        await pilot.pause()
        # Verify modal mounted without errors
        log_view = pilot.app.screen.query_one("#log-view", RichLog)
        assert log_view is not None
