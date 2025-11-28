"""Speech-to-text transcription using Whisper."""

from typing import Optional, List
from dataclasses import dataclass
import numpy as np
import time
import concurrent.futures
import torch
import whisper


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_ms: int


class SpeechToText:
    """Transcribe audio using local Whisper model."""

    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(
        self,
        model_name: str = "tiny",
        device: str = "auto",
        language: Optional[str] = "en"
    ) -> None:
        """
        Initialize Whisper model.

        Args:
            model_name: Model size (tiny, base, small, medium, large)
            device: Compute device (auto, cpu, mps, cuda)
            language: Language code or None for auto-detect

        Raises:
            ValueError: If model_name is invalid
            RuntimeError: If model loading fails
        """
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model_name '{model_name}'. "
                f"Must be one of: {', '.join(self.AVAILABLE_MODELS)}"
            )

        self._model_name = model_name
        self._language = language
        self._model = None
        self._device = self._resolve_device(device)

    def _resolve_device(self, device: str) -> str:
        """Resolve device string to actual device."""
        if device == "auto":
            if torch.backends.mps.is_available():
                return "mps"
            elif torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return device

    def _load_model(self) -> None:
        """Load Whisper model if not already loaded."""
        if self._model is None:
            try:
                self._model = whisper.load_model(self._model_name, device=self._device)
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe(
        self,
        audio: np.ndarray,
        timeout_seconds: float = 5.0
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio: Float32 numpy array at 16kHz
            timeout_seconds: Maximum transcription time

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            TimeoutError: If transcription exceeds timeout
            RuntimeError: If transcription fails
        """
        # Load model if not loaded
        self._load_model()

        # Check for empty or very short audio
        if audio.size == 0 or len(audio) < 1600:  # < 0.1s at 16kHz
            return TranscriptionResult(
                text="",
                language=self._language or "en",
                confidence=0.0,
                duration_ms=0
            )

        # Transcribe with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._transcribe_audio, audio)
            try:
                result = future.result(timeout=timeout_seconds)
                return result
            except concurrent.futures.TimeoutError:
                raise TimeoutError(
                    f"Transcription exceeded timeout of {timeout_seconds}s"
                )
            except Exception as e:
                raise RuntimeError(f"Transcription failed: {e}")

    def _transcribe_audio(self, audio: np.ndarray) -> TranscriptionResult:
        """Internal transcription method."""
        start_time = time.time()

        # Transcribe with Whisper
        options = {}
        if self._language:
            options["language"] = self._language

        result = self._model.transcribe(audio, **options)

        duration_ms = int((time.time() - start_time) * 1000)

        # Extract text and clean
        text = result.get("text", "").strip()

        # Extract language
        language = result.get("language", self._language or "en")

        # Calculate confidence from no_speech_prob
        no_speech_prob = result.get("no_speech_prob", 0.5)
        confidence = 1.0 - no_speech_prob

        return TranscriptionResult(
            text=text,
            language=language,
            confidence=confidence,
            duration_ms=duration_ms
        )

    @property
    def model_name(self) -> str:
        """Currently loaded model name."""
        return self._model_name

    @property
    def is_loaded(self) -> bool:
        """Whether model is loaded and ready."""
        return self._model is not None

    @staticmethod
    def available_models() -> List[str]:
        """List available Whisper model names."""
        return SpeechToText.AVAILABLE_MODELS.copy()
