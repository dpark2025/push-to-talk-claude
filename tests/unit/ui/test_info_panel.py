"""Tests for InfoPanel widget."""

import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

from push_to_talk_claude.ui.widgets.info_panel import InfoPanel
from push_to_talk_claude.ui.widgets.recording_timer import RecordingTimer
from push_to_talk_claude.ui.models import AppInfo


class InfoPanelTestApp(App):
    """Test app for InfoPanel widget."""

    def __init__(self, app_info: AppInfo | None = None, **kwargs):
        super().__init__(**kwargs)
        self.app_info = app_info or AppInfo(
            hotkey="ctrl_r",
            whisper_model="tiny",
            injection_mode="focused",
            target_info="Active window",
        )

    def compose(self) -> ComposeResult:
        yield InfoPanel(self.app_info, id="info-panel")


@pytest.mark.asyncio
async def test_info_panel_displays_hotkey():
    """Test that InfoPanel displays hotkey configuration."""
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="tiny",
        injection_mode="focused",
        target_info="Active window",
    )
    async with InfoPanelTestApp(app_info).run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        # Verify the app_info was stored
        assert panel.app_info.hotkey == "ctrl_r"


@pytest.mark.asyncio
async def test_info_panel_displays_model():
    """Test that InfoPanel displays whisper model."""
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="base.en",
        injection_mode="focused",
        target_info="Active window",
    )
    async with InfoPanelTestApp(app_info).run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        assert panel.app_info.whisper_model == "base.en"


@pytest.mark.asyncio
async def test_info_panel_displays_mode():
    """Test that InfoPanel displays injection mode."""
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="tiny",
        injection_mode="tmux",
        target_info="main:0.0",
    )
    async with InfoPanelTestApp(app_info).run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        assert panel.app_info.injection_mode == "tmux"


@pytest.mark.asyncio
async def test_info_panel_displays_target():
    """Test that InfoPanel displays target info."""
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="tiny",
        injection_mode="tmux",
        target_info="main:0.1",
    )
    async with InfoPanelTestApp(app_info).run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        assert panel.app_info.target_info == "main:0.1"


@pytest.mark.asyncio
async def test_info_panel_contains_timer():
    """Test that InfoPanel contains a RecordingTimer widget."""
    async with InfoPanelTestApp().run_test() as pilot:
        timer = pilot.app.query_one("#recording-timer", RecordingTimer)
        assert timer is not None


@pytest.mark.asyncio
async def test_info_panel_update_info():
    """Test that update_info changes displayed values."""
    app_info = AppInfo(
        hotkey="ctrl_r",
        whisper_model="tiny",
        injection_mode="focused",
        target_info="Active window",
    )
    async with InfoPanelTestApp(app_info).run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)

        # Update with new info
        new_info = AppInfo(
            hotkey="ctrl_t",
            whisper_model="medium",
            injection_mode="tmux",
            target_info="dev:1.0",
        )
        panel.update_info(new_info)
        await pilot.pause()

        # Verify updates
        assert panel.app_info.hotkey == "ctrl_t"
        assert panel.app_info.whisper_model == "medium"


@pytest.mark.asyncio
async def test_info_panel_get_timer():
    """Test that get_timer returns the timer widget."""
    async with InfoPanelTestApp().run_test() as pilot:
        panel = pilot.app.query_one(InfoPanel)
        timer = panel.get_timer()
        assert timer is not None
        assert isinstance(timer, RecordingTimer)


@pytest.mark.asyncio
async def test_info_panel_has_title():
    """Test that InfoPanel has a title."""
    async with InfoPanelTestApp().run_test() as pilot:
        title = pilot.app.query_one("#title", Static)
        assert title is not None


@pytest.mark.asyncio
async def test_info_panel_has_instructions():
    """Test that InfoPanel displays usage instructions."""
    async with InfoPanelTestApp().run_test() as pilot:
        # Only instruction-1 remains (L/Q keys are shown in footer)
        instr1 = pilot.app.query_one("#instruction-1", Static)
        assert instr1 is not None


@pytest.mark.asyncio
async def test_info_panel_widget_structure():
    """Test that InfoPanel has all expected child widgets."""
    async with InfoPanelTestApp().run_test() as pilot:
        # Check all expected IDs exist
        assert pilot.app.query_one("#title", Static)
        assert pilot.app.query_one("#hotkey-info", Static)
        assert pilot.app.query_one("#model-info", Static)
        assert pilot.app.query_one("#mode-info", Static)
        assert pilot.app.query_one("#target-info", Static)
        assert pilot.app.query_one("#recording-timer", RecordingTimer)
        assert pilot.app.query_one("#divider", Static)
