Fetch a model from an Ollama server if configured.
from __future__ import annotations

from ollama import Client
import os

OLLAMA_URL = os.environ.get("OLLAMA_URL")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3")

if __name__ == "__main__":
    try:
        if not OLLAMA_URL:
            print("OLLAMA_URL not set; skipping local model pull.")
        else:
            client = Client(host=OLLAMA_URL)
            print(f"Pulling model '{LLM_MODEL}' from Ollama at '{OLLAMA_URL}'...")
            client.pull(LLM_MODEL)
            print(f"Successfully pulled model '{LLM_MODEL}'.")
    except Exception as e:
        print(f"Failed to pull model '{LLM_MODEL}': {e}")
