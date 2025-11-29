"""Audio capture module for push-to-talk functionality."""

import threading
from dataclasses import dataclass

import numpy as np
import pyaudio


@dataclass
class AudioDevice:
    """Represents an audio input device."""

    index: int
    name: str
    sample_rate: int
    channels: int


class AudioCapture:
    """Capture audio from microphone during push-to-talk sessions."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        frame_size: int = 1024,
        device_index: int | None = None,
    ) -> None:
        """
        Initialize audio capture.

        Args:
            sample_rate: Sample rate in Hz (default: 16000 for Whisper)
            channels: Number of channels (default: 1 for mono)
            frame_size: Frames per buffer (default: 1024)
            device_index: Specific device or None for default

        Raises:
            PermissionError: If microphone permission not granted
            RuntimeError: If audio device initialization fails
        """
        self._sample_rate = sample_rate
        self._channels = channels
        self._frame_size = frame_size
        self._device_index = device_index

        self._pyaudio = pyaudio.PyAudio()
        self._stream: pyaudio.Stream | None = None
        self._frames: list[bytes] = []
        self._lock = threading.Lock()
        self._is_recording = False
        self._start_time: float | None = None

        # Verify device exists and is accessible
        try:
            if device_index is not None:
                device_info = self._pyaudio.get_device_info_by_index(device_index)
                if device_info["maxInputChannels"] < channels:
                    raise RuntimeError(
                        f"Device {device_index} does not support {channels} input channels"
                    )
        except Exception as e:
            self._pyaudio.terminate()
            raise RuntimeError(f"Audio device initialization failed: {e}") from e

    def start_recording(self) -> None:
        """Begin capturing audio frames to internal buffer."""
        with self._lock:
            if self._is_recording:
                return

            self._frames = []

            def callback(in_data, frame_count, time_info, status):
                with self._lock:
                    if self._is_recording:
                        self._frames.append(in_data)
                return (None, pyaudio.paContinue)

            self._stream = self._pyaudio.open(
                format=pyaudio.paFloat32,
                channels=self._channels,
                rate=self._sample_rate,
                input=True,
                input_device_index=self._device_index,
                frames_per_buffer=self._frame_size,
                stream_callback=callback,
                start=False,
            )

            self._is_recording = True
            self._stream.start_stream()

    def stop_recording(self) -> np.ndarray:
        """
        Stop capture and return recorded audio.

        Returns:
            numpy array of float32 audio samples normalized to [-1, 1]
        """
        with self._lock:
            if not self._is_recording:
                return np.array([], dtype=np.float32)

            self._is_recording = False

            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None

            if not self._frames:
                return np.array([], dtype=np.float32)

            # Concatenate all frames
            audio_data = b"".join(self._frames)

            # Convert bytes to numpy array (already float32 from PyAudio)
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            return audio_array

    def cancel_recording(self) -> None:
        """Stop capture and discard audio buffer."""
        with self._lock:
            if not self._is_recording:
                return

            self._is_recording = False

            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None

            self._frames = []

    @property
    def is_recording(self) -> bool:
        """Whether currently recording."""
        with self._lock:
            return self._is_recording

    @property
    def duration_seconds(self) -> float:
        """Duration of current/last recording in seconds."""
        with self._lock:
            if not self._frames:
                return 0.0

            total_frames = sum(len(frame) for frame in self._frames)
            # Each sample is 4 bytes (float32), divide by channels
            num_samples = (total_frames // 4) // self._channels
            return num_samples / self._sample_rate

    @staticmethod
    def list_devices() -> list[AudioDevice]:
        """List available audio input devices."""
        p = pyaudio.PyAudio()
        devices = []

        try:
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info["maxInputChannels"] > 0:
                    devices.append(
                        AudioDevice(
                            index=i,
                            name=info["name"],
                            sample_rate=int(info["defaultSampleRate"]),
                            channels=info["maxInputChannels"],
                        )
                    )
        finally:
            p.terminate()

        return devices

    @staticmethod
    def check_permissions() -> bool:
        """Check if microphone permission is granted."""
        p = pyaudio.PyAudio()
        try:
            # Try to open a stream briefly to check permissions
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
                start=False,
            )
            stream.close()
            return True
        except Exception:
            return False
        finally:
            p.terminate()

    def __del__(self) -> None:
        """Clean up PyAudio resources."""
        if hasattr(self, "_stream") and self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if hasattr(self, "_pyaudio"):
            self._pyaudio.terminate()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cancel_recording()
        if self._stream:
            self._stream.close()
        self._pyaudio.terminate()
        return False
