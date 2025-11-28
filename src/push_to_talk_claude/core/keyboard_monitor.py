"""Keyboard monitoring for push-to-talk hotkey detection."""

from typing import Dict, Any, Callable, Optional
from enum import Enum
import threading

# Map user-friendly key names to pynput Key objects
# These will be resolved at runtime when pynput is imported
SUPPORTED_HOTKEYS: Dict[str, str] = {
    # Modifier keys
    "ctrl_r": "Key.ctrl_r",
    "ctrl_l": "Key.ctrl_l",
    "alt_r": "Key.alt_r",
    "alt_l": "Key.alt_l",
    "cmd_r": "Key.cmd_r",
    "cmd_l": "Key.cmd_l",
    "shift_r": "Key.shift_r",
    "shift_l": "Key.shift_l",

    # Function keys (F13-F20 are great for dedicated hotkeys)
    "f13": "Key.f13",
    "f14": "Key.f14",
    "f15": "Key.f15",
    "f16": "Key.f16",
    "f17": "Key.f17",
    "f18": "Key.f18",
    "f19": "Key.f19",
    "f20": "Key.f20",

    # Standard function keys
    "f1": "Key.f1",
    "f2": "Key.f2",
    "f3": "Key.f3",
    "f4": "Key.f4",
    "f5": "Key.f5",
    "f6": "Key.f6",
    "f7": "Key.f7",
    "f8": "Key.f8",
    "f9": "Key.f9",
    "f10": "Key.f10",
    "f11": "Key.f11",
    "f12": "Key.f12",
}


def get_pynput_key(hotkey_name: str):
    """Convert hotkey name to pynput Key object.

    Resolves a user-friendly hotkey name to the corresponding pynput Key object
    at runtime. This allows configuration to use string names while maintaining
    type safety through pynput's Key enum.

    Args:
        hotkey_name: User-friendly key name from SUPPORTED_HOTKEYS mapping.
                     Example: "f13", "ctrl_r", "cmd_l"

    Returns:
        pynput.keyboard.Key object corresponding to the hotkey name.

    Raises:
        ValueError: If hotkey_name is not in SUPPORTED_HOTKEYS.
                    Includes list of supported hotkeys in error message.
    """
    from pynput.keyboard import Key

    if hotkey_name not in SUPPORTED_HOTKEYS:
        supported = ", ".join(sorted(SUPPORTED_HOTKEYS.keys()))
        raise ValueError(f"Unsupported hotkey: {hotkey_name}. Supported: {supported}")

    key_attr = SUPPORTED_HOTKEYS[hotkey_name].replace("Key.", "")
    return getattr(Key, key_attr)


def is_valid_hotkey(hotkey_name: str) -> bool:
    """Check if hotkey name is valid.

    Performs a quick validation check to determine if a given hotkey name
    is supported without attempting to resolve it to a pynput Key object.
    Useful for configuration validation before attempting to use the hotkey.

    Args:
        hotkey_name: Key name to validate.

    Returns:
        True if hotkey_name is in SUPPORTED_HOTKEYS, False otherwise.
    """
    return hotkey_name in SUPPORTED_HOTKEYS


class HotkeyState(Enum):
    """State of the monitored hotkey."""
    IDLE = "idle"
    PRESSED = "pressed"


class KeyboardMonitor:
    """Monitor keyboard for push-to-talk hotkey events."""

    def __init__(
        self,
        hotkey: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None]
    ) -> None:
        """
        Initialize keyboard monitor.

        Args:
            hotkey: Key name from SUPPORTED_HOTKEYS (e.g., "ctrl_r", "f13")
            on_press: Callback when hotkey is pressed
            on_release: Callback when hotkey is released

        Raises:
            ValueError: If hotkey is not supported
        """
        if not is_valid_hotkey(hotkey):
            supported = ", ".join(sorted(SUPPORTED_HOTKEYS.keys()))
            raise ValueError(f"Unsupported hotkey: {hotkey}. Supported: {supported}")

        self._hotkey_name = hotkey
        self._hotkey = get_pynput_key(hotkey)
        self._on_press = on_press
        self._on_release = on_release

        self._state = HotkeyState.IDLE
        self._state_lock = threading.Lock()
        self._listener: Optional[Any] = None
        self._is_listening = threading.Event()

    def start(self) -> None:
        """Start listening for keyboard events. Non-blocking."""
        from pynput.keyboard import Listener

        if self._listener is not None:
            return

        def on_press(key):
            with self._state_lock:
                if key == self._hotkey and self._state == HotkeyState.IDLE:
                    self._state = HotkeyState.PRESSED
                    self._on_press()

        def on_release(key):
            with self._state_lock:
                if key == self._hotkey and self._state == HotkeyState.PRESSED:
                    self._state = HotkeyState.IDLE
                    self._on_release()

        self._listener = Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        self._is_listening.set()

    def stop(self) -> None:
        """Stop listening and cleanup resources."""
        if self._listener is not None:
            self._is_listening.clear()
            self._listener.stop()
            self._listener = None
            with self._state_lock:
                self._state = HotkeyState.IDLE

    @property
    def state(self) -> HotkeyState:
        """Current hotkey state."""
        with self._state_lock:
            return self._state

    @property
    def is_listening(self) -> bool:
        """Whether monitor is actively listening."""
        return self._is_listening.is_set()

    @staticmethod
    def check_permissions() -> bool:
        """Check if accessibility permissions are granted."""
        from pynput.keyboard import Listener

        try:
            listener = Listener(on_press=lambda k: None)
            listener.start()
            listener.stop()
            return True
        except Exception:
            return False
