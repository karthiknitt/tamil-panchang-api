FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for pyswisseph
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download Swiss Ephemeris data files
RUN mkdir -p /app/ephe && \
    cd /app/ephe && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1 && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/semo_18.se1 && \
    wget -q https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/sepl_18.se1

# Copy application code and configuration
COPY app.py .
COPY mcp_server.py .
COPY supervisord.conf .

# Expose ports (FastAPI on 8000, MCP on 8001)
EXPOSE 8000 8001

# Health check (check both FastAPI and MCP server)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health'); urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Run both servers via supervisord
CMD ["/usr/local/bin/supervisord", "-c", "/app/supervisord.conf"]
