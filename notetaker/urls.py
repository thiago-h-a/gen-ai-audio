from django.http import JsonResponse
from django.urls import path
from django.conf import settings

from api.views import TranscribeView, SummarizeView

# Keep the external path shape identical to the previous app
API_PREFIX = settings.API_V1_STR.rstrip("/")


def health(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path(f"{API_PREFIX}/health", health, name="health"),
    path(f"{API_PREFIX}/note/transcribe", TranscribeView.as_view(), name="transcribe"),
    path(f"{API_PREFIX}/note/summarize", SummarizeView.as_view(), name="summarize"),
]
