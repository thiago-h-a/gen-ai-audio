#!/bin/bash
set -e -x

if [ "$USE_LOCAL_MODELS" = "True" ] || [ "$USE_LOCAL_MODELS" = "true" ]; then
    python -u scripts/pull_local_model.py || true
else
    echo "Skipping model pull."
fi

python -u scripts/setup_transcription_models.py || true

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8001}

echo "Starting ASGI server (Django + DRF)"
uvicorn notetaker.asgi:application --host "$HOST" --port "$PORT"
