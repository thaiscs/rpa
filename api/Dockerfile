FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and API code
COPY shared/shared/ shared/
COPY api/ api/

# Module importing requires /app to be in PYTHONPATH
ENV PYTHONPATH=/app

# FastAPI server
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]