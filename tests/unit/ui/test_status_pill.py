"""Tests for StatusPill widget."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.ui.widgets.status_pill import StatusPill
from push_to_talk_claude.core.recording_session import RecordingStatus


class StatusPillTestApp(App):
    """Test app for StatusPill widget."""

    def compose(self) -> ComposeResult:
        yield StatusPill("Recording", "🔴", "$error", RecordingStatus.RECORDING)


@pytest.mark.asyncio
async def test_status_pill_initial_state():
    """Test that StatusPill starts inactive."""
    async with StatusPillTestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)
        assert pill.active is False
        assert "active" not in pill.classes


@pytest.mark.asyncio
async def test_status_pill_activate():
    """Test that StatusPill can be activated."""
    async with StatusPillTestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)
        assert pill.active is False
        pill.activate()
        assert pill.active is True
        assert "active" in pill.classes


@pytest.mark.asyncio
async def test_status_pill_deactivate():
    """Test that StatusPill can be deactivated."""
    async with StatusPillTestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)
        pill.activate()
        assert pill.active is True
        pill.deactivate()
        assert pill.active is False
        assert "active" not in pill.classes


@pytest.mark.asyncio
async def test_status_pill_properties():
    """Test that StatusPill stores its configuration."""
    async with StatusPillTestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)
        assert pill.label_text == "Recording"
        assert pill.emoji == "🔴"
        assert pill.color == "$error"
        assert pill.status == RecordingStatus.RECORDING


@pytest.mark.asyncio
async def test_status_pill_toggle():
    """Test toggling active state multiple times."""
    async with StatusPillTestApp().run_test() as pilot:
        pill = pilot.app.query_one(StatusPill)

        # Toggle on
        pill.activate()
        assert pill.active is True

        # Toggle off
        pill.deactivate()
        assert pill.active is False

        # Toggle on again
        pill.activate()
        assert pill.active is True
