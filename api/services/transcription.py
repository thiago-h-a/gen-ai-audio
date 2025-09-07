# Speech-to-text helpers built on whisperx.
# The service encapsulates model loading and the main operations used by the
# endpoint: raw transcription, optional alignment, and optional diarization.
from __future__ import annotations

import os
from typing import Tuple, Any

import numpy as np
from numpy.typing import NDArray
import whisperx
from django.conf import settings


class TranscriptionService:
    """A small façade around whisperx to keep the view clean.

    The instance lazily loads models using configuration drawn from Django settings.
    """

    def __init__(self) -> None:
        self.device = settings.WHISPER_DEVICE
        # Preload primary model; this keeps behavior similar to the old service.
        self.model = whisperx.load_model(
            settings.WHISPER_MODEL,
            device=self.device,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )

    # ------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------
    def transcribe(self, file_path: str) -> Tuple[dict, NDArray[np.float32]]:
        """Transcribe the audio at *file_path* and return (result, audio_array).
        The result is a dictionary as returned by whisperx for easy JSON emission.
        """
        try:
            audio = whisperx.load_audio(file_path)
            result = self.model.transcribe(
                audio, batch_size=settings.WHISPER_BATCH_SIZE
            )
            return result, audio
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Transcription error: {exc}") from exc

    def align_transcription(self, transcription_result: dict, audio: NDArray[np.float32]) -> dict:
        """Return a word-aligned transcription for the given *transcription_result*.
        """
        try:
            model_a, metadata = whisperx.load_align_model(
                language_code=transcription_result.get("language"),
                device=self.device,
            )
            aligned = whisperx.align(
                transcription_result["segments"],
                model_a,
                metadata,
                audio,
                self.device,
                return_char_alignments=False,
            )
            return aligned
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Alignment error: {exc}") from exc

    def perform_diarization(self, audio: NDArray[np.float32]) -> Any:
        """Compute diarized segments for *audio* using whisperx' pipeline.
        """
        try:
            diar = whisperx.DiarizationPipeline(
                use_auth_token=settings.HF_API_KEY,
                device=self.device,
            )
            return diar(audio)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Diarization error: {exc}") from exc

    # ------------------------------------------------------------
    # Housekeeping
    # ------------------------------------------------------------
    def cleanup_file(self, file_path: str) -> None:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
