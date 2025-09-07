Warm up whisperx models so first request is fast.
from __future__ import annotations

import os
import whisperx

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
HF_API_KEY = os.environ.get("HF_API_KEY", "")

if __name__ == "__main__":
    print("Initializing transcription models...")
    _ = whisperx.load_model(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
    )
    _, _ = whisperx.load_align_model(
        language_code="en",
        device=WHISPER_DEVICE,
    )
    _ = whisperx.DiarizationPipeline(
        use_auth_token=HF_API_KEY, device=WHISPER_DEVICE
    )
    print("Successfully initialized transcription models.")
