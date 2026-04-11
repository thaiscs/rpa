FROM python:3.11-slim as base
WORKDIR /app
# Install dependencies first (better caching)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- MIGRATION STAGE FOR CI/CD ---
FROM base as migrations
COPY alembic/migration-requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=100 --retries 5 -r migration-requirements.txt
    
# Alembic will run HERE, not in app image
COPY alembic/ alembic/
COPY alembic.ini .
COPY shared/shared/ shared/

# Module importing requires /app to be in PYTHONPATH
ENV PYTHONPATH=/app

CMD ["sh", "-c", "set -eux; alembic upgrade head; alembic current"]