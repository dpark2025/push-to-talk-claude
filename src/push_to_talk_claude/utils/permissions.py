import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PermissionState(Enum):
    GRANTED = "granted"
    DENIED = "denied"
    NOT_DETERMINED = "not_determined"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


@dataclass
class PermissionStatus:
    microphone: PermissionState
    accessibility: PermissionState
    checked_at: datetime


def check_microphone_permission() -> PermissionState:
    """Check if microphone permission is granted.

    Uses: system_profiler SPAudioDataType to check for input devices
    and attempts a quick PyAudio test if available.
    """
    try:
        # First check if we have any input devices
        result = subprocess.run(
            ["system_profiler", "SPAudioDataType"], capture_output=True, text=True, timeout=5
        )

        if result.returncode != 0:
            return PermissionState.UNKNOWN

        # Check if there are input devices listed
        if "Input Device" not in result.stdout and "input" not in result.stdout.lower():
            return PermissionState.DENIED

        # Try to import and test PyAudio if available
        try:
            import pyaudio

            p = pyaudio.PyAudio()

            # Check if we can get input device count
            input_devices = 0
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info.get("maxInputChannels", 0) > 0:
                    input_devices += 1

            p.terminate()

            if input_devices > 0:
                return PermissionState.GRANTED
            else:
                return PermissionState.DENIED

        except ImportError:
            # PyAudio not available, assume granted if system shows devices
            return PermissionState.GRANTED
        except Exception:
            return PermissionState.DENIED

    except subprocess.TimeoutExpired:
        return PermissionState.UNKNOWN
    except Exception:
        return PermissionState.UNKNOWN


def check_accessibility_permission() -> PermissionState:
    """Check if accessibility permission is granted.

    On macOS, uses osascript to test if we can observe keyboard events.
    Returns GRANTED if pynput listener can be created.
    """
    try:
        # Try to import pynput and create a listener
        from pynput import keyboard

        # Attempt to create a listener (this will fail if accessibility not granted)
        test_listener = keyboard.Listener(on_press=lambda key: None)

        # Try to start and stop it quickly
        test_listener.start()
        test_listener.stop()
        test_listener.join(timeout=2.0)  # Wait for thread to fully terminate

        return PermissionState.GRANTED

    except ImportError:
        # pynput not available, try osascript test
        try:
            script = """
            tell application "System Events"
                keystroke "test" using command down
            end tell
            """
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=2
            )

            # If we get an error about not being allowed, permission is denied
            if "not allowed assistive access" in result.stderr.lower():
                return PermissionState.DENIED
            else:
                return PermissionState.GRANTED

        except subprocess.TimeoutExpired:
            return PermissionState.UNKNOWN
        except Exception:
            return PermissionState.UNKNOWN

    except Exception as e:
        # If we get specific permission error, it's denied
        error_str = str(e).lower()
        if "accessibility" in error_str or "permission" in error_str:
            return PermissionState.DENIED
        return PermissionState.UNKNOWN


def check_all_permissions() -> PermissionStatus:
    """Check all required permissions."""
    return PermissionStatus(
        microphone=check_microphone_permission(),
        accessibility=check_accessibility_permission(),
        checked_at=datetime.now(),
    )


def get_permission_instructions(permission: str) -> str:
    """Get human-readable instructions for granting permission.

    Args:
        permission: 'microphone' or 'accessibility'

    Returns:
        Multi-line string with step-by-step instructions
    """
    if permission.lower() == "microphone":
        return """To grant microphone permission:

1. Open System Settings
2. Go to Privacy & Security
3. Select Microphone (in the left sidebar)
4. Find your Terminal or Python application in the list
5. Toggle the switch to enable microphone access
6. Restart your application

Path: System Settings > Privacy & Security > Microphone"""

    elif permission.lower() == "accessibility":
        return """To grant accessibility permission:

1. Open System Settings
2. Go to Privacy & Security
3. Select Accessibility (in the left sidebar)
4. Click the lock icon to make changes (enter your password)
5. Click the '+' button to add your Terminal or Python application
6. Or toggle the switch next to your application if it's already listed
7. Restart your application

Path: System Settings > Privacy & Security > Accessibility"""

    else:
        return f"Unknown permission type: {permission}"


def check_tmux_available() -> bool:
    """Check if tmux is installed and accessible."""
    try:
        result = subprocess.run(["which", "tmux"], capture_output=True, text=True, timeout=2)
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except Exception:
        return False


def check_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed (needed for some audio formats)."""
    try:
        result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True, timeout=2)
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except Exception:
        return False
