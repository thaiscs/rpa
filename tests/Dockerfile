FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-test.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-test.txt

# Install additional dependencies needed for tests
RUN pip install --no-cache-dir \
    fastapi \
    fastapi-users \
    sqlalchemy \
    alembic \
    cryptography \
    httpx \
    nicegui

# Copy source code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Default command
CMD ["pytest", "-v"]
