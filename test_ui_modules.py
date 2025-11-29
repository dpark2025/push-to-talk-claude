#!/usr/bin/env python3
"""Test UI modules functionality."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from push_to_talk_claude.ui.indicators import RecordingIndicator
from push_to_talk_claude.ui.notifications import NotificationManager


def test_recording_indicator():
    """Test RecordingIndicator functionality."""
    print("\n=== Testing RecordingIndicator ===\n")

    indicator = RecordingIndicator()

    # Test recording with duration updates
    print("1. Testing recording indicator with duration updates...")
    indicator.show_recording()
    for i in range(1, 4):
        time.sleep(0.5)
        indicator.update_duration(i * 0.5)
    indicator.hide()
    time.sleep(0.5)

    # Test transcribing
    print("2. Testing transcribing indicator...")
    indicator.show_transcribing()
    time.sleep(1)
    indicator.hide()
    time.sleep(0.5)

    # Test injecting
    print("3. Testing injecting indicator...")
    indicator.show_injecting()
    time.sleep(1)
    indicator.hide()
    time.sleep(0.5)

    # Test complete with short text
    print("4. Testing complete indicator (short text)...")
    indicator.show_complete("Hello, this is a test transcription")
    time.sleep(1)

    # Test complete with long text
    print("5. Testing complete indicator (long text - should truncate)...")
    long_text = "This is a much longer transcription that should be truncated at 50 chars"
    indicator.show_complete(long_text)
    time.sleep(1)

    # Test error
    print("6. Testing error indicator...")
    indicator.show_error("Test error message")
    time.sleep(1)


def test_notification_manager():
    """Test NotificationManager functionality."""
    print("\n=== Testing NotificationManager ===\n")

    manager = NotificationManager()

    # Test info
    print("1. Testing info message...")
    manager.info("This is an info message")
    time.sleep(0.5)

    # Test success
    print("2. Testing success message...")
    manager.success("Operation completed successfully")
    time.sleep(0.5)

    # Test warning
    print("3. Testing warning message...")
    manager.warning("This is a warning message")
    time.sleep(0.5)

    # Test error
    print("4. Testing error message...")
    manager.error("This is an error message")
    time.sleep(0.5)

    # Test startup banner
    print("5. Testing startup banner...")
    manager.startup_banner("cmd+shift+space", "base")
    time.sleep(1)

    # Test permission error
    print("6. Testing permission error...")
    manager.permission_error("Microphone")
    time.sleep(1)

    # Test shutdown message
    print("7. Testing shutdown message...")
    manager.shutdown_message()


if __name__ == "__main__":
    test_recording_indicator()
    test_notification_manager()
    print("\n=== All tests complete ===\n")
