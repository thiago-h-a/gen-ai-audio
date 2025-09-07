from typing import Iterable
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class SimpleCORSMiddleware(MiddlewareMixin):
    '''A tiny CORS layer that mirrors the former FastAPI config.

    - If BACKEND_CORS_ALLOW_ALL is true, allow '*'.
    - Otherwise, echo back only configured origins.
    - Always include typical method/header allowances.
    '''

    def process_response(self, request, response):
        allow_all: bool = getattr(settings, "BACKEND_CORS_ALLOW_ALL", False)
        origins: Iterable[str] = getattr(settings, "BACKEND_CORS_ORIGINS", [])
        origin = request.META.get("HTTP_ORIGIN")

        if allow_all:
            response["Access-Control-Allow-Origin"] = "*"
        elif origin and origin in origins:
            response["Access-Control-Allow-Origin"] = origin

        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = (
            "GET, POST, OPTIONS, PUT, DELETE, PATCH"
        )
        response["Access-Control-Allow-Headers"] = (
            "Authorization, Content-Type, X-Requested-With, Accept, Origin"
        )
        return response
