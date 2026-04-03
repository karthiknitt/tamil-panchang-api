# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Copy uv binary from official image (no extra layer, no uv version pinned in apt)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# System deps — wget for ephemeris data download
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

# uv settings: compile bytecode for faster startup; copy files from cache instead of symlinking
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install Python dependencies into /app/.venv
# Cached separately from app code — only re-runs when pyproject.toml or uv.lock change
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

# Download Swiss Ephemeris data files
RUN mkdir -p /app/ephe && \
    cd /app/ephe && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1 && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/semo_18.se1 && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sepl_18.se1

# Copy application code (after deps — so code changes don't bust the dep cache)
COPY app.py mcp_server.py mcp_server_stdio.py supervisord.conf ./

# Add venv to PATH so supervisord, uvicorn, etc. resolve without full path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health'); urllib.request.urlopen('http://localhost:8001/health')" || exit 1

CMD ["supervisord", "-c", "/app/supervisord.conf"]
