"""Tests for StatusPanel widget."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.status_pill import StatusPill
from push_to_talk_claude.core.recording_session import RecordingStatus


class StatusPanelTestApp(App):
    """Test app for StatusPanel widget."""

    def compose(self) -> ComposeResult:
        yield StatusPanel(id="status-panel")


@pytest.mark.asyncio
async def test_status_panel_creates_pills():
    """Test that StatusPanel creates all status pills."""
    async with StatusPanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)
        pills = pilot.app.query(StatusPill)
        assert len(list(pills)) == 6


@pytest.mark.asyncio
async def test_status_panel_set_status():
    """Test that set_status activates the correct pill."""
    async with StatusPanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)
        panel.set_status(RecordingStatus.RECORDING)

        pills = list(pilot.app.query(StatusPill))
        active_pills = [p for p in pills if p.active]
        assert len(active_pills) == 1
        assert active_pills[0].status == RecordingStatus.RECORDING


@pytest.mark.asyncio
async def test_status_panel_change_status():
    """Test that changing status deactivates previous pill."""
    async with StatusPanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)

        # Set to recording
        panel.set_status(RecordingStatus.RECORDING)

        # Change to transcribing
        panel.set_status(RecordingStatus.TRANSCRIBING)

        pills = list(pilot.app.query(StatusPill))
        active_pills = [p for p in pills if p.active]
        assert len(active_pills) == 1
        assert active_pills[0].status == RecordingStatus.TRANSCRIBING


@pytest.mark.asyncio
async def test_status_panel_current_status():
    """Test that current_status reactive attribute updates."""
    async with StatusPanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(StatusPanel)

        assert panel.current_status == RecordingStatus.IDLE

        panel.set_status(RecordingStatus.COMPLETE)
        assert panel.current_status == RecordingStatus.COMPLETE


@pytest.mark.asyncio
async def test_status_panel_pill_ids():
    """Test that pills have correct IDs."""
    async with StatusPanelTestApp().run_test() as pilot:
        recording_pill = pilot.app.query_one("#pill-recording", StatusPill)
        assert recording_pill.status == RecordingStatus.RECORDING

        complete_pill = pilot.app.query_one("#pill-complete", StatusPill)
        assert complete_pill.status == RecordingStatus.COMPLETE
