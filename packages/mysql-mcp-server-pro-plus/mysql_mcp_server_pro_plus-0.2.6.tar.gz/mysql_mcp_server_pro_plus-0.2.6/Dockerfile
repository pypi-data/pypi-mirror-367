# Multi-stage build for optimized production image
FROM python:3.12-slim AS builder

# Build arguments for flexibility
ARG UV_VERSION=0.4.15

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Set working directory
WORKDIR /app

# Optimize uv configuration for Docker builds
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/.uv-cache

# Install build dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    make \
    python3-dev \
    # Cleanup in same layer to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy dependency files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies with optimized caching
RUN --mount=type=cache,target=/tmp/.uv-cache \
    uv venv .venv && \
    uv sync --frozen --no-install-project

# Production stage
FROM python:3.12-slim AS production

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Cleanup in same layer
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy uv from builder stage
COPY --from=builder /bin/uv /bin/uv

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Set optimized environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy application files with optimal layering for caching
COPY pyproject.toml uv.lock README.md ./
COPY src/ /app/src
COPY tests/ /app/tests

# Final project sync to install the application itself
RUN --mount=type=cache,target=/tmp/.uv-cache \
    uv sync --frozen

# Command to run the server
CMD ["mysql_mcp_server_pro_plus"]
