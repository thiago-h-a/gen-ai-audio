# Minimal ASGI entrypoint so we can continue using uvicorn like before.
# Uvicorn target: `notetaker.asgi:application`
# This mirrors the prior FastAPI launch approach so existing run scripts remain
# familiar and the demo UI doesn't need to change.
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notetaker.settings")
application = get_asgi_application()
