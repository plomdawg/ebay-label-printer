# eBay Label Printer - Multi-stage Docker build
# Built with Python 3.11 on Ubuntu

# Build stage - for installing dependencies and building
FROM python:3.11-slim AS builder

# Install system dependencies needed for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage - minimal runtime environment
FROM python:3.11-slim AS production

# Install CUPS client tools for printing
RUN apt-get update && apt-get install -y \
    cups-client \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/ ./app/
COPY run.py .
COPY setup.py .

# Create directory for logs and state files
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Ensure user's local bin is in PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set environment variables for Python
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check to ensure application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.config import Config; c = Config(); exit(0 if c.validate() else 1)"

# Volume for persistent data (logs, state files)
VOLUME ["/app/data"]

# Default environment variables (can be overridden)
ENV POLLING_INTERVAL=300
ENV DRY_RUN=false
ENV LOG_LEVEL=INFO
ENV STATE_FILE=/app/data/seen_order_ids.json

# Run the application
CMD ["python", "run.py"]