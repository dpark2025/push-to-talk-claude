"""Speech-to-text transcription using Whisper.

Uses a separate process for transcription to avoid file descriptor conflicts
with Textual TUI. The 'spawn' multiprocessing method ensures the child process
doesn't inherit parent's FDs.
"""

import os
import tempfile
import time
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import numpy as np


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_ms: int


def _transcribe_in_process(
    audio_path: str,
    model_name: str,
    device: str,
    language: Optional[str],
    result_path: str
) -> None:
    """Worker function that runs in a separate process.

    This function loads whisper and does transcription in complete isolation
    from the parent process, avoiding FD inheritance issues with Textual.
    """
    import warnings
    warnings.filterwarnings("ignore")

    # Set single-threaded mode
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"

    import torch
    torch.set_num_threads(1)

    import whisper

    try:
        # Load audio from temp file
        audio = np.load(audio_path)

        # Load model
        model = whisper.load_model(model_name, device=device)

        # Transcribe
        options = {}
        if language:
            options["language"] = language

        result = model.transcribe(audio, **options)

        # Extract results
        text = result.get("text", "").strip()
        detected_language = result.get("language", language or "en")
        no_speech_prob = result.get("no_speech_prob", 0.5)
        confidence = 1.0 - no_speech_prob

        # Write result to file
        import json
        with open(result_path, 'w') as f:
            json.dump({
                "text": text,
                "language": detected_language,
                "confidence": confidence,
                "error": None
            }, f)
    except Exception as e:
        import json
        with open(result_path, 'w') as f:
            json.dump({
                "text": "",
                "language": language or "en",
                "confidence": 0.0,
                "error": str(e)
            }, f)


class SpeechToText:
    """Transcribe audio using local Whisper model.

    Uses subprocess-based transcription to avoid FD conflicts with Textual TUI.
    """

    AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large"]

    def __init__(
        self,
        model_name: str = "small",
        device: str = "auto",
        language: Optional[str] = "en"
    ) -> None:
        """
        Initialize Whisper transcription config.

        Args:
            model_name: Model size (tiny, base, small, medium, large)
            device: Compute device (auto, cpu, cuda)
            language: Language code or None for auto-detect

        Raises:
            ValueError: If model_name is invalid
        """
        if model_name not in self.AVAILABLE_MODELS:
            raise ValueError(
                f"Invalid model_name '{model_name}'. "
                f"Must be one of: {', '.join(self.AVAILABLE_MODELS)}"
            )

        self._model_name = model_name
        self._language = language
        self._device = self._resolve_device(device)
        self._model = None  # Kept for API compatibility

    def _resolve_device(self, device: str) -> str:
        """Resolve device string to actual device."""
        if device == "auto":
            # For subprocess-based transcription, always use CPU
            # to avoid GPU context issues across processes
            return "cpu"
        if device == "mps":
            return "cpu"  # MPS doesn't work well across processes
        return device

    def preload_model(self, timeout_seconds: float = 60.0) -> tuple[bool, str]:
        """Pre-load/download the Whisper model.

        Runs a subprocess to download and cache the model so first transcription is fast.

        Args:
            timeout_seconds: Maximum time to wait for model loading

        Returns:
            Tuple of (success: bool, message: str)
        """
        import subprocess

        script = f'''
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import warnings
warnings.filterwarnings("ignore")

import torch
torch.set_num_threads(1)

import whisper
model = whisper.load_model("{self._model_name}", device="{self._device}")
print("Model loaded successfully")
'''

        try:
            proc = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                timeout=timeout_seconds,
                text=True
            )

            if proc.returncode == 0:
                return True, f"Model '{self._model_name}' loaded"
            else:
                error = proc.stderr.strip() if proc.stderr else "Unknown error"
                return False, f"Failed to load model: {error}"

        except subprocess.TimeoutExpired:
            return False, f"Model loading timed out after {timeout_seconds}s"
        except Exception as e:
            return False, f"Model loading error: {e}"

    def _load_model(self) -> None:
        """Pre-load model to warm up (optional, for API compatibility)."""
        # In subprocess mode, model is loaded in the child process
        # This method exists for API compatibility
        pass

    def transcribe(
        self,
        audio: np.ndarray,
        timeout_seconds: float = 30.0
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using a subprocess.

        Args:
            audio: Float32 numpy array at 16kHz
            timeout_seconds: Maximum transcription time

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            TimeoutError: If transcription exceeds timeout
            RuntimeError: If transcription fails
        """
        import subprocess
        import json

        # Check for empty or very short audio
        if audio.size == 0 or len(audio) < 1600:  # < 0.1s at 16kHz
            return TranscriptionResult(
                text="",
                language=self._language or "en",
                confidence=0.0,
                duration_ms=0
            )

        start_time = time.time()

        # Create temp files for audio and result
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as audio_file:
            audio_path = audio_file.name
            np.save(audio_path, audio)

        result_path = audio_path + '.result.json'

        try:
            # Run transcription in a completely separate Python process
            # This avoids all FD inheritance issues
            script = f'''
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import torch
torch.set_num_threads(1)

import whisper
import json

audio = np.load("{audio_path}")
model = whisper.load_model("{self._model_name}", device="{self._device}")

options = {{}}
language = {repr(self._language)}
if language:
    options["language"] = language

result = model.transcribe(audio, **options)

text = result.get("text", "").strip()
detected_language = result.get("language", language or "en")
no_speech_prob = result.get("no_speech_prob", 0.5)
confidence = 1.0 - no_speech_prob

with open("{result_path}", "w") as f:
    json.dump({{"text": text, "language": detected_language, "confidence": confidence, "error": None}}, f)
'''

            proc = subprocess.run(
                ["python", "-c", script],
                capture_output=True,
                timeout=timeout_seconds,
                text=True
            )

            duration_ms = int((time.time() - start_time) * 1000)

            if proc.returncode != 0:
                error_msg = proc.stderr or "Unknown error"
                raise RuntimeError(f"Transcription subprocess failed: {error_msg}")

            # Read result
            if not Path(result_path).exists():
                raise RuntimeError("Transcription produced no result")

            with open(result_path) as f:
                result_data = json.load(f)

            if result_data.get("error"):
                raise RuntimeError(f"Transcription error: {result_data['error']}")

            return TranscriptionResult(
                text=result_data["text"],
                language=result_data["language"],
                confidence=result_data["confidence"],
                duration_ms=duration_ms
            )

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Transcription exceeded timeout of {timeout_seconds}s")
        except Exception as e:
            if "Transcription" in str(e):
                raise
            raise RuntimeError(f"Transcription failed: {e}")
        finally:
            # Cleanup temp files
            try:
                Path(audio_path).unlink(missing_ok=True)
                Path(result_path).unlink(missing_ok=True)
            except Exception:
                pass

    @property
    def model_name(self) -> str:
        """Currently configured model name."""
        return self._model_name

    @property
    def is_loaded(self) -> bool:
        """Whether ready to transcribe (always True for subprocess mode)."""
        return True

    @staticmethod
    def available_models() -> List[str]:
        """List available Whisper model names."""
        return SpeechToText.AVAILABLE_MODELS.copy()
