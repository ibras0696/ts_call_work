FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (ffmpeg for pydub, build tools for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Install dependencies
COPY pyproject.toml /code/
RUN python -m pip install --upgrade pip \
 && pip install -e .[dev]

# Copy sources
COPY app /code/app
COPY alembic.ini /code/
COPY migrations /code/migrations

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
