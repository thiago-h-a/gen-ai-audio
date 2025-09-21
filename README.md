# Notetaker AI

## Quickstart (Dev)

```bash
# optional: create and load a .env file (keys, model names, etc.)
poetry install
./run.sh --host=0.0.0.0 --port=8001
```

- Health: `GET /routes/v1/health`
- Transcription: `POST /routes/v1/note/transcribe` (`multipart/form-data` with `audio_file`)
- Summarization: `POST /routes/v1/note/summarize?format=SOAP|PKI%20HL7%20CDA|Therapy%20Assessment`

## Environment knobs

Relevant variables (defaults shown where reasonable):

- `USE_LOCAL_MODELS` (False) — switch to Ollama if True
- `OLLAMA_URL` — Ollama base URL
- `OPENAI_API_KEY` — for OpenAI-compatible LLMs
- `LLM_MODEL` — model name for LLM
- `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE`, `WHISPER_BATCH_SIZE`
- `HF_API_KEY` — Hugging Face token for diarization
- `BACKEND_CORS_ALLOW_ALL` (False), `BACKEND_CORS_ORIGINS`

## Demo mode

`./run.sh --demo` will launch the API and then run `demo/ui.py` exactly like before.

## Docker

```bash
docker compose up --build
```

The API is exposed on port 8001 by default. Healthcheck URL:
`http://localhost:8001/routes/v1/health`.
