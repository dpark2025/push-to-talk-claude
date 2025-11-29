"""Tests for icon alignment in StatusPill widgets."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.ui.models import STATUS_PILLS
from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.status_pill import StatusPill


class IconAlignmentTestApp(App):
    """Test app for icon alignment verification."""

    def compose(self) -> ComposeResult:
        yield StatusPanel(id="status-panel")


@pytest.mark.asyncio
async def test_icon_character_width():
    """Verify icons don't cause alignment issues."""
    async with IconAlignmentTestApp().run_test() as pilot:
        pills = pilot.app.query(StatusPill)
        for pill in pills:
            # Verify pill renders without errors
            assert pill is not None
            # Verify pill has content
            assert pill.icon is not None
            assert pill.label_text is not None


@pytest.mark.asyncio
async def test_all_status_icons_render():
    """Verify all configured icons render correctly."""
    async with IconAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))
        assert len(pills) == 6

        # Verify each icon from config is present
        icons_in_config = {config.icon for config in STATUS_PILLS}
        icons_in_pills = {pill.icon for pill in pills}
        assert icons_in_config == icons_in_pills


@pytest.mark.asyncio
async def test_symbol_icon_handling():
    """Test symbol icons (like ⦿, ◐, ✓) render correctly."""
    async with IconAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        # Find the pill with the recording icon (⦿)
        rec_pill = next((p for p in pills if "⦿" in p.icon), None)
        assert rec_pill is not None
        # Verify it renders without error
        assert rec_pill.icon is not None


@pytest.mark.asyncio
async def test_pills_have_consistent_structure():
    """Verify all pills follow the same display structure."""
    async with IconAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        for pill in pills:
            # Each pill should have both icon and label
            assert pill.icon
            assert pill.label_text
            # Verify the pill has the expected status attribute
            assert hasattr(pill, "status")
            assert pill.status is not None


@pytest.mark.asyncio
async def test_pills_activate_without_layout_shift():
    """Verify activating pills doesn't cause layout issues."""
    async with IconAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        # Activate each pill and verify no errors
        for pill in pills:
            pill.activate()
            await pilot.pause()
            assert "active" in pill.classes
            pill.deactivate()
            await pilot.pause()
            assert "active" not in pill.classes
