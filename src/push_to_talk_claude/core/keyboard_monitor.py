"""Keyboard monitoring for push-to-talk hotkey detection."""

import threading
from collections.abc import Callable
from enum import Enum
from typing import Any

# Map user-friendly key names to pynput Key objects
# These will be resolved at runtime when pynput is imported
SUPPORTED_HOTKEYS: dict[str, str] = {
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

    # Watchdog timeout - fallback if polling fails (e.g., Quartz unavailable)
    STUCK_KEY_TIMEOUT = 30.0

    # Polling interval for checking key state (more reliable than release events)
    POLL_INTERVAL = 0.1  # 100ms

    def __init__(
        self, hotkey: str, on_press: Callable[[], None], on_release: Callable[[], None]
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
        self._listener: Any | None = None
        self._is_listening = threading.Event()
        self._watchdog_timer: threading.Timer | None = None
        self._poll_thread: threading.Thread | None = None
        self._stop_polling = threading.Event()

    def start(self) -> None:
        """Start listening for keyboard events. Non-blocking."""
        from pynput.keyboard import Listener

        if self._listener is not None:
            return

        def on_press(key):
            with self._state_lock:
                if key == self._hotkey and self._state == HotkeyState.IDLE:
                    self._state = HotkeyState.PRESSED
                    # Start watchdog timer in case release event is missed
                    self._start_watchdog()
                    # Start polling for key release (more reliable than events with Textual)
                    self._start_polling()
                    self._on_press()

        def on_release(key):
            with self._state_lock:
                if key == self._hotkey and self._state == HotkeyState.PRESSED:
                    self._state = HotkeyState.IDLE
                    self._cancel_watchdog()
                    self._stop_polling.set()
                    self._on_release()

        self._listener = Listener(on_press=on_press, on_release=on_release)
        self._listener.start()
        self._is_listening.set()

    def _start_polling(self) -> None:
        """Start polling thread to detect key release."""
        self._stop_polling.clear()
        self._poll_thread = threading.Thread(target=self._poll_key_state, daemon=True)
        self._poll_thread.start()

    def _poll_key_state(self) -> None:
        """Poll keyboard state to detect when key is released.

        This is more reliable than relying on release events when Textual
        is controlling the terminal.
        """
        import time

        while not self._stop_polling.is_set():
            time.sleep(self.POLL_INTERVAL)

            # Check if key is still pressed using Quartz (macOS)
            if not self._is_key_pressed():
                with self._state_lock:
                    if self._state == HotkeyState.PRESSED:
                        self._state = HotkeyState.IDLE
                        self._cancel_watchdog()
                        self._on_release()
                break

    def _is_key_pressed(self) -> bool:
        """Check if the hotkey is currently pressed using system APIs."""
        try:
            # Use Quartz on macOS to check modifier key state
            import Quartz

            # Map hotkey names to Quartz modifier flags
            modifier_map = {
                "ctrl_r": Quartz.kCGEventFlagMaskControl,
                "ctrl_l": Quartz.kCGEventFlagMaskControl,
                "alt_r": Quartz.kCGEventFlagMaskAlternate,
                "alt_l": Quartz.kCGEventFlagMaskAlternate,
                "cmd_r": Quartz.kCGEventFlagMaskCommand,
                "cmd_l": Quartz.kCGEventFlagMaskCommand,
                "shift_r": Quartz.kCGEventFlagMaskShift,
                "shift_l": Quartz.kCGEventFlagMaskShift,
            }

            if self._hotkey_name in modifier_map:
                # Get current modifier flags
                flags = Quartz.CGEventSourceFlagsState(Quartz.kCGEventSourceStateHIDSystemState)
                return bool(flags & modifier_map[self._hotkey_name])

            # For function keys, check using CGEventSourceKeyState
            # Map F-key names to key codes
            fkey_map = {
                "f1": 122,
                "f2": 120,
                "f3": 99,
                "f4": 118,
                "f5": 96,
                "f6": 97,
                "f7": 98,
                "f8": 100,
                "f9": 101,
                "f10": 109,
                "f11": 103,
                "f12": 111,
                "f13": 105,
                "f14": 107,
                "f15": 113,
                "f16": 106,
                "f17": 64,
                "f18": 79,
                "f19": 80,
                "f20": 90,
            }

            if self._hotkey_name in fkey_map:
                return Quartz.CGEventSourceKeyState(
                    Quartz.kCGEventSourceStateHIDSystemState, fkey_map[self._hotkey_name]
                )

            # Default: assume still pressed
            return True
        except Exception:
            # If Quartz not available, assume still pressed
            return True

    def _start_watchdog(self) -> None:
        """Start watchdog timer to detect stuck key."""
        self._cancel_watchdog()
        self._watchdog_timer = threading.Timer(self.STUCK_KEY_TIMEOUT, self._force_release)
        self._watchdog_timer.daemon = True
        self._watchdog_timer.start()

    def _cancel_watchdog(self) -> None:
        """Cancel watchdog timer."""
        if self._watchdog_timer is not None:
            self._watchdog_timer.cancel()
            self._watchdog_timer = None

    def _force_release(self) -> None:
        """Force key release if watchdog fires (key release event was missed)."""
        with self._state_lock:
            if self._state == HotkeyState.PRESSED:
                self._state = HotkeyState.IDLE
                self._on_release()

    def stop(self) -> None:
        """Stop listening and cleanup resources."""
        self._cancel_watchdog()
        self._stop_polling.set()  # Stop polling thread
        if self._listener is not None:
            self._is_listening.clear()
            try:
                # Stop the listener - this signals it to stop
                self._listener.stop()
                # Join with timeout to prevent hanging
                if hasattr(self._listener, "join"):
                    self._listener.join(timeout=1.0)
            except Exception:
                pass  # Ignore errors during cleanup
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
