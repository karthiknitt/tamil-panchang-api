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

# Copy application code
COPY app.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
