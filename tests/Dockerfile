FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements before source so Docker can cache this layer
COPY requirements-test.txt api/requirements.txt ./api/

RUN pip install --no-cache-dir -r requirements-test.txt -r api/requirements.txt

# Copy source code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Default command
CMD ["pytest", "-v"]
