# Multi-stage build for optimal production image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set labels for metadata
LABEL org.opencontainers.image.title="Airtable AI Agent"
LABEL org.opencontainers.image.description="The most comprehensive AI Agent for Airtable operations"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Rashid Azarang"
LABEL org.opencontainers.image.source="https://github.com/rashidazarang/airtable-ai-agent"

# Create non-root user for security
RUN groupadd -g 1000 aiagent && \
    useradd -r -u 1000 -g aiagent aiagent

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=aiagent:aiagent . .

# Create directories for data and cache
RUN mkdir -p /app/data /app/.cache /app/logs && \
    chown -R aiagent:aiagent /app

# Switch to non-root user
USER aiagent

# Set environment variables
ENV PYTHONPATH="/app"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL="INFO"
ENV CACHE_DIR="/app/.cache"
ENV DATA_DIR="/app/data"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.agent", "--server"]