# Multi-stage build for smaller production image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    PATH=/home/flaskuser/.local/bin:$PATH

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/flaskuser/.local

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Create directories and set permissions
RUN mkdir -p /app/logs && \
    chown -R flaskuser:flaskuser /app

# Switch to non-root user
USER flaskuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose the port
EXPOSE 5000

# Use gunicorn with dynamic worker configuration
CMD gunicorn --bind 0.0.0.0:5000 \
    --workers ${WORKERS:-4} \
    --timeout ${TIMEOUT:-30} \
    --keepalive ${KEEPALIVE:-2} \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level ${LOG_LEVEL:-info} \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"
