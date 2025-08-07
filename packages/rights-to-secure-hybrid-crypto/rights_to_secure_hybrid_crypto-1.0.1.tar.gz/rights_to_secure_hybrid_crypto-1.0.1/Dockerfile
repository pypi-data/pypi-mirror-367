# RightsToSecure Hybrid Crypto Wrapper - Dockerfile
# Quantum-resistant hybrid cryptography library container

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Praveen Naidu <contact@arkaenterprises.com>"
LABEL description="RightsToSecure Hybrid Crypto Wrapper - Quantum-resistant cryptography library"
LABEL version="1.0.0"
LABEL vendor="RightsToSecure"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "examples/api_example.py"]

# Alternative commands for different use cases
# CMD ["python", "examples/demo_key_exchange.py"]  # Run key exchange demo
# CMD ["python", "examples/demo_signing.py"]       # Run signature demo
# CMD ["pytest", "tests/"]                         # Run tests 