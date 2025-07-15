# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directory for volume mount
RUN mkdir -p /app/data/lotro_companion

# Create startup script
RUN echo '#!/usr/bin/env python3\n\
import os\n\
import uvicorn\n\
from web.config.config import WEB_HOST, WEB_PORT, WEB_WORKERS\n\
\n\
if __name__ == "__main__":\n\
    uvicorn.run(\n\
        "web.app:app",\n\
        host=WEB_HOST,\n\
        port=WEB_PORT,\n\
        workers=WEB_WORKERS if WEB_WORKERS > 1 else None\n\
    )\n\
' > /app/start_server.py && chmod +x /app/start_server.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with configurable settings
CMD ["python", "/app/start_server.py"] 