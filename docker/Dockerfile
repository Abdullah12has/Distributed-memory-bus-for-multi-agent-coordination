# syntax=docker/dockerfile:1.7
#
# Memory-bus + benchmark runtime image (CPU / MPS-friendly).
#
# This image is the deployable artifact described in §6.1 of the plan: a single-
# machine reference implementation that the FCG platform team can adopt. It is
# explicitly *not* the training image — MLX and PEFT live on the host so we can
# touch the Apple Silicon GPU directly.
#
# Build:
#   docker build -f docker/Dockerfile -t m6-thesis:dev .
# Run (compose):
#   docker compose -f docker/docker-compose.yml up

ARG PYTHON_VERSION=3.11.10
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# ----- Stage 1: system deps ---------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
        libgomp1 \
        libsqlite3-0 \
        sqlite3 \
        tini \
    && rm -rf /var/lib/apt/lists/*

# ----- Stage 2: deps cache layer ---------------------------------------------
FROM base AS builder
WORKDIR /build
COPY requirements.txt ./
# We exclude MLX + llama-cpp-python from the slim image: MLX is mac-only and the
# slim image is for the memory bus service, not local inference. Inference
# happens on the host (MLX) or in a sidecar container.
RUN sed -e '/^mlx/d' -e '/^mlx-lm/d' -e '/^llama-cpp-python/d' \
        requirements.txt > requirements.slim.txt \
 && pip install --prefix=/install -r requirements.slim.txt

# ----- Stage 3: runtime ------------------------------------------------------
FROM base AS runtime

# Create a non-root user. Service runs as `m6` (uid 1001).
ARG UID=1001
ARG GID=1001
RUN groupadd -g ${GID} m6 \
 && useradd -u ${UID} -g ${GID} -ms /bin/bash m6

WORKDIR /app

# Pull installed wheels from the builder stage.
COPY --from=builder /install /usr/local

# Copy source last so editable installs do not bust the deps cache.
COPY --chown=m6:m6 pyproject.toml README.md ./
COPY --chown=m6:m6 src/ ./src/

RUN pip install --no-deps -e .

# Runtime configuration. Override at `docker run -e`.
ENV M6_HOST=0.0.0.0 \
    M6_PORT=8080 \
    M6_LOG_LEVEL=INFO \
    M6_DB_PATH=/app/data/audit.sqlite \
    M6_FAISS_PATH=/app/data/index.faiss

RUN mkdir -p /app/data && chown -R m6:m6 /app

USER m6

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsSL http://localhost:8080/healthz || exit 1

# tini reaps zombies properly when uvicorn spawns workers.
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "m6.memory_bus.api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
