FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules and API code
COPY shared/shared/ shared/
COPY api/ api/

# Add flask CLI support
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# Module importing requires /app to be in PYTHONPATH
ENV PYTHONPATH=/app

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080", "--reload"]