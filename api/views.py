from typing import Any, Dict

from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from api.serializers import (
    TranscriptionRequestSerializer,
    SummaryRequestSerializer,
)
from api.services.transcription import TranscriptionService
from api.services.summarization import SummarizationService, NoteFormat


class TranscribeView(APIView):
    '''POST /routes/v1/note/transcribe

    Accepts an audio file as `audio_file` and optional flags `align` and
    `perform_diarization`. Returns the raw/aligned/diarized transcription JSON.
    '''

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request: Request):
        # Parse flags from query or body (mirroring the previous API contract)
        opts = TranscriptionRequestSerializer(data=request.query_params or request.data)
        opts.is_valid(raise_exception=True)
        align = bool(opts.validated_data.get("align", False))
        do_diar = bool(opts.validated_data.get("perform_diarization", False))

        file = request.FILES.get("audio_file")
        if not file:
            return JsonResponse(
                {"detail": "Missing file part 'audio_file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file.content_type not in [
            "audio/mpeg",
            "audio/wav",
            "audio/x-wav",
            "audio/x-m4a",
        ]:
            return JsonResponse(
                {"detail": "Invalid file type. Accepted types are mp3, wav, m4a."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tmp_path = f"/tmp/{file.name}"
        with open(tmp_path, "wb") as fh:
            for chunk in file.chunks():
                fh.write(chunk)

        svc = TranscriptionService()
        try:
            result, audio = svc.transcribe(tmp_path)
            if align:
                result = svc.align_transcription(result, audio)
            if do_diar:
                import whisperx
                diar = svc.perform_diarization(audio)
                result = whisperx.assign_word_speakers(diar, result)

            return JsonResponse({"transcript": result}, status=status.HTTP_200_OK, safe=False)
        except Exception as exc:  # pragma: no cover
            return JsonResponse(
                {"detail": f"Transcription failed: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            svc.cleanup_file(tmp_path)


class SummarizeView(APIView):
    '''POST /routes/v1/note/summarize

    Accepts JSON with a `transcript` field and optional `format` query param
    specifying the note format. Returns `{ "note": ... }`.
    '''

    parser_classes = (JSONParser,)

    def post(self, request: Request):
        body = SummaryRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        transcript_obj = body.validated_data["transcript"]
        fmt_str = request.query_params.get("format", NoteFormat.TEXT.value)

        # Normalize the requested format; default to TEXT when unknown
        try:
            fmt = NoteFormat(fmt_str)
        except Exception:
            fmt = NoteFormat.TEXT

        try:
            svc = SummarizationService()
            language = None
            # If the transcript dict has a language hint, pass it through
            if isinstance(transcript_obj, dict):
                language = transcript_obj.get("language")
            note = svc.summarize(transcript_obj, fmt=fmt, language=language)
            if not note:
                return JsonResponse(
                    {"detail": "Failed to generate a summary."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return JsonResponse({"note": note}, status=status.HTTP_200_OK, safe=False)
        except Exception as exc:
            return JsonResponse(
                {"detail": f"An error occurred: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
