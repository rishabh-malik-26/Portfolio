# # FROM python:3.12.3-slim-bullseye
# FROM python:3.12-alpine

# # Set working directory
# WORKDIR /app

# # Install system dependencies for PostgreSQL, Kafka, and general compilation
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     libpq-dev \
#     pkg-config \
#     librdkafka-dev \
#     curl \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get clean

# # Copy requirements first for better caching
# COPY requirements.txt .

# # Install Python dependencies with specific optimizations
# RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
#     pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Create app user for security (avoid running as root)
# RUN useradd --create-home --shell /bin/bash app

# # Create necessary directories with proper permissions
# RUN mkdir -p /app/static/uploads /app/logs && \
#     chown -R app:app /app

# # Switch to app user
# USER app

# # Expose port
# EXPOSE 5000

# # Set environment variables for your stack
# ENV PYTHONPATH=/app \
#     FLASK_APP=app.py \
#     PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1 \
#     PORT=5000

# # Health check for container orchestration
# HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
#     CMD curl -f http://localhost:5000/health || exit 1

# # Run the application
# CMD ["python", "app.py"]


# Use Distroless or Alpine-based Python for better security
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (Alpine packages)
RUN apk update && apk upgrade && apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    postgresql-dev \
    librdkafka-dev \
    curl \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with specific optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create app user for security (avoid running as root)
RUN adduser -D -s /bin/sh app

# Create necessary directories with proper permissions
RUN mkdir -p /app/static/uploads /app/logs && \
    chown -R app:app /app

# Switch to app user
USER app

# Expose port
EXPOSE 5000

# Set environment variables for your stack
ENV PYTHONPATH=/app \
    FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "app.py"]