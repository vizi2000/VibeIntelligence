# Backend Dockerfile with Vibecoding
# Following Directive 17: Sustainable multi-stage build

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies and build tools for Python packages
RUN apt-get update && apt-get install -y \
    libpq5 \
    git \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 zenith && chown -R zenith:zenith /app

# Switch to non-root user
USER zenith

# Expose port
EXPOSE 8000

# Health check for vibecoding wellness
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn directly
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]