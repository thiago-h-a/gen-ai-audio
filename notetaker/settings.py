import os
from pathlib import Path

# ------------------------------------------------------------
# Core Django settings (intentionally concise and env-driven)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-not-for-production")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Accept the same broad host policy as before unless restricted by env
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    # Custom tiny CORS layer to match previous FastAPI behavior
    "api.middleware.SimpleCORSMiddleware",
]

ROOT_URLCONF = "notetaker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

WSGI_APPLICATION = "notetaker.wsgi.application"
ASGI_APPLICATION = "notetaker.asgi.application"

# No relational persistence is strictly required; use SQLite for simplicity.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

STATIC_URL = "static/"

# ---- CORS knobs (to mirror the old app/middlewares.py behavior) ----
BACKEND_CORS_ALLOW_ALL = os.environ.get("BACKEND_CORS_ALLOW_ALL", "False").lower() == "true"
BACKEND_CORS_ORIGINS = [
    o.strip() for o in os.environ.get("BACKEND_CORS_ORIGINS", "").split(",") if o.strip()
]

# ---- App configuration migrated from the legacy Settings model ----
PROJECT_NAME = os.environ.get("PROJECT_NAME", "Notetaker AI")
API_V1_STR = os.environ.get("API_V1_STR", "/routes/v1")
VERSION = os.environ.get("VERSION", "0.0.1")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OLLAMA_URL = os.environ.get("OLLAMA_URL")
HF_API_KEY = os.environ.get("HF_API_KEY", "")

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
WHISPER_BATCH_SIZE = int(os.environ.get("WHISPER_BATCH_SIZE", "8"))

LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
USE_LOCAL_MODELS = os.environ.get("USE_LOCAL_MODELS", "False").lower() == "true"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}
