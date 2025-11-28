"""Test script for audio capture module."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from push_to_talk_claude.core.audio_capture import AudioCapture

# Test 1: Check permissions
print("Test 1: Checking microphone permissions...")
has_permission = AudioCapture.check_permissions()
print(f"✓ Microphone permission: {has_permission}")

# Test 2: List devices
print("\nTest 2: Listing audio devices...")
devices = AudioCapture.list_devices()
print(f"✓ Found {len(devices)} input devices:")
for device in devices:
    print(f"  [{device.index}] {device.name} ({device.sample_rate}Hz, {device.channels}ch)")

# Test 3: Initialize capture
print("\nTest 3: Initializing audio capture...")
capture = AudioCapture(sample_rate=16000, channels=1, frame_size=1024)
print(f"✓ AudioCapture initialized")
print(f"  is_recording: {capture.is_recording}")
print(f"  duration_seconds: {capture.duration_seconds}")

# Test 4: Record for 2 seconds
print("\nTest 4: Recording for 2 seconds...")
capture.start_recording()
print(f"✓ Recording started, is_recording: {capture.is_recording}")
time.sleep(2)
audio_data = capture.stop_recording()
print(f"✓ Recording stopped")
print(f"  Audio shape: {audio_data.shape}")
print(f"  Audio dtype: {audio_data.dtype}")
print(f"  Duration: {capture.duration_seconds:.2f} seconds")
print(f"  Sample range: [{audio_data.min():.4f}, {audio_data.max():.4f}]")

# Test 5: Test cancel
print("\nTest 5: Testing cancel_recording...")
capture.start_recording()
time.sleep(0.5)
capture.cancel_recording()
print(f"✓ Recording cancelled, is_recording: {capture.is_recording}")

# Test 6: Context manager
print("\nTest 6: Testing context manager...")
with AudioCapture() as cap:
    cap.start_recording()
    time.sleep(0.5)
    audio = cap.stop_recording()
    print(f"✓ Context manager works, recorded {len(audio)} samples")

print("\n✓ All tests passed!")
