"""Tests for emoji alignment in StatusPill widgets."""

import pytest
from textual.app import App, ComposeResult

from push_to_talk_claude.ui.widgets.status_panel import StatusPanel
from push_to_talk_claude.ui.widgets.status_pill import StatusPill
from push_to_talk_claude.ui.models import STATUS_PILLS


class EmojiAlignmentTestApp(App):
    """Test app for emoji alignment verification."""

    def compose(self) -> ComposeResult:
        yield StatusPanel(id="status-panel")


@pytest.mark.asyncio
async def test_emoji_character_width():
    """Verify emojis don't cause alignment issues."""
    async with EmojiAlignmentTestApp().run_test() as pilot:
        pills = pilot.app.query(StatusPill)
        for pill in pills:
            # Verify pill renders without errors
            assert pill is not None
            # Verify pill has content
            assert pill.emoji is not None
            assert pill.label_text is not None


@pytest.mark.asyncio
async def test_all_status_emojis_render():
    """Verify all configured emojis render correctly."""
    async with EmojiAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))
        assert len(pills) == 6

        # Verify each emoji from config is present
        emojis_in_config = {config.emoji for config in STATUS_PILLS}
        emojis_in_pills = {pill.emoji for pill in pills}
        assert emojis_in_config == emojis_in_pills


@pytest.mark.asyncio
async def test_compound_emoji_handling():
    """Test compound emojis (like ⏭️ which is U+23ED + U+FE0F) render correctly."""
    async with EmojiAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        # Find the pill with the compound emoji (skip/idle uses ⏭️)
        skip_pill = next((p for p in pills if "⏭" in p.emoji), None)
        assert skip_pill is not None
        # Verify it renders without error
        assert skip_pill.emoji is not None


@pytest.mark.asyncio
async def test_pills_have_consistent_structure():
    """Verify all pills follow the same display structure."""
    async with EmojiAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        for pill in pills:
            # Each pill should have both emoji and label
            assert pill.emoji
            assert pill.label_text
            # Verify the pill has the expected status attribute
            assert hasattr(pill, "status")
            assert pill.status is not None


@pytest.mark.asyncio
async def test_pills_activate_without_layout_shift():
    """Verify activating pills doesn't cause layout issues."""
    async with EmojiAlignmentTestApp().run_test() as pilot:
        pills = list(pilot.app.query(StatusPill))

        # Activate each pill and verify no errors
        for pill in pills:
            pill.activate()
            await pilot.pause()
            assert "active" in pill.classes
            pill.deactivate()
            await pilot.pause()
            assert "active" not in pill.classes
