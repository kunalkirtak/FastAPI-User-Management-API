# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr --
# both make container logs behave the way `docker logs` expects.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first, in their own layer, so Docker only re-installs
# them when requirements.txt actually changes -- not on every code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code and migration environment.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Run as a non-root user (defense-in-depth: a container escape or RCE in a
# dependency doesn't hand the attacker root inside the container).
RUN useradd --create-home --shell /bin/bash appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Docker/orchestrator-level liveness check, reusing the same /health
# endpoint documented in the README. Uses the stdlib instead of curl/wget so
# no extra OS packages are needed in the image.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
