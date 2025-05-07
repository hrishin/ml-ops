# Use Python 3.9 slim image for a smaller footprint
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PATH="$PATH:/root/.local/bin"

WORKDIR /app

# Install Poetry and dependencies
RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION" && \
    pip install setuptools && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-dev --no-root && \
    apt-get purge -y --auto-remove gcc build-essential

# Now create the runtime image with minimum dependencies
FROM base as runtime

# Copy application code
COPY . /app/

# Default command to start the API server
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port"]
CMD ["8000"]