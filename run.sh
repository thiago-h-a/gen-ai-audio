#! /bin/bash

# Purpose: keep the previous CLI flags while switching app to Django ASGI
# Usage: ./run.sh [--demo] [--host=0.0.0.0] [--port=8001] [other uvicorn flags]

set -e

if [ -f .env ]; then
    export $(grep -E '^(USE_LOCAL_MODELS|HOST|PORT|BACKEND_CORS_ALLOW_ALL|BACKEND_CORS_ORIGINS|DJANGO_SECRET_KEY)=' .env)
fi

if [ "$USE_LOCAL_MODELS" = "True" ] || [ "$USE_LOCAL_MODELS" = "true" ]; then
    poetry run python -u scripts/pull_local_model.py || true
else
    echo "Skipping model pull."
fi

# Warm-up for whisperx
poetry run python -u scripts/setup_transcription_models.py || true

# Parse args (preserve old UX)
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}
UVICORN_ARGS="--host $HOST --port $PORT"
DEMO=false

for arg in "$@"; do
    case $arg in
        --demo)
            DEMO=true
            ;;
        --host=*)
            HOST="${arg#*=}"
            ;;
        --port=*)
            PORT="${arg#*=}"
            ;;
        *)
            UVICORN_ARGS="$UVICORN_ARGS $arg"
            ;;
    esac
done

# Compose final args now that host/port may have changed
UVICORN_ARGS="--host $HOST --port $PORT $UVICORN_ARGS"

echo "Starting the Django (DRF) application via uvicorn..."
if [ "$DEMO" = true ]; then
    poetry run uvicorn notetaker.asgi:application $UVICORN_ARGS &
    echo "Starting Gradio demo..."
    poetry run python -u demo/ui.py
else
    poetry run uvicorn notetaker.asgi:application $UVICORN_ARGS
fi
