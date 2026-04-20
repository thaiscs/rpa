FROM python:3.11-slim
WORKDIR /app
# Install dependencies first (better caching)
COPY api/requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --retries 5 -r requirements.txt

COPY api/ api/
COPY shared/shared/ shared/

# Module importing requires /app to be in PYTHONPATH
ENV PYTHONPATH=/app

# FastAPI server
# TODO: remove reload in production
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]