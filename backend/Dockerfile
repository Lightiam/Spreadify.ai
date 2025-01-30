FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Set environment variables
ENV PYTHONPATH="/app"
ENV DATABASE_URL="sqlite:///./test.db"

# Copy application code
COPY . .
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Create necessary directories
RUN mkdir -p /app/logs

# Set permissions
RUN chown -R nobody:nogroup /app && \
    chmod -R 755 /app

# Switch to non-root user
USER nobody

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
