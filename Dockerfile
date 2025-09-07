# Simple CUDA-enabled image similar to the original, adapted for Django
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive     PYTHONUNBUFFERED=1     PYTHON_VERSION=3.12

RUN apt-get update && apt-get install -y --no-install-recommends     software-properties-common     ffmpeg     curl     python3.12     python3-pip     python-is-python3     && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1     && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1     && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* ./
RUN pip install --no-cache-dir --upgrade pip setuptools poetry
RUN poetry config virtualenvs.create false

# Install deps early for better layer caching
RUN poetry install --only main --no-interaction --no-ansi || true

# Copy the rest of the repo
COPY . .

# Ensure prestart is executable
RUN chmod +x /app/prestart.sh || true

EXPOSE 8001
CMD ["/app/prestart.sh"]
