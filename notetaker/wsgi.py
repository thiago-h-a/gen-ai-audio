# WSGI entrypoint (not used by uvicorn; included for completeness).
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notetaker.settings")
application = get_wsgi_application()
